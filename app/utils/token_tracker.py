"""Persist Ollama prompt/output token counts per logical service (SQLite)."""

from __future__ import annotations

import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from app.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

_lock = threading.Lock()

_DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "token_usage.db"


def _db_path() -> str:
    return os.getenv("TOKEN_USAGE_DB", str(_DEFAULT_DB))


def _ensure_parent(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS token_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            service TEXT NOT NULL,
            model TEXT,
            input_tokens INTEGER NOT NULL DEFAULT 0,
            output_tokens INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_token_events_ts ON token_events(ts)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_token_events_service_ts ON token_events(service, ts)"
    )


def init_db_if_needed() -> None:
    path = _db_path()
    _ensure_parent(path)
    with _lock:
        conn = sqlite3.connect(path)
        try:
            _init_db(conn)
            conn.commit()
        finally:
            conn.close()


def ollama_response_to_counts(response: Any) -> tuple[int, int]:
    """
    Map Ollama chat response to (prompt tokens, completion tokens).
    Uses prompt_eval_count / eval_count when present; otherwise (0, 0).
    """
    data: dict[str, Any]
    if isinstance(response, dict):
        data = response
    elif hasattr(response, "model_dump"):
        data = response.model_dump()
    elif hasattr(response, "dict"):
        data = response.dict()  # type: ignore[assignment]
    else:
        data = {
            "prompt_eval_count": getattr(response, "prompt_eval_count", None),
            "eval_count": getattr(response, "eval_count", None),
        }
    inp = int(data.get("prompt_eval_count") or 0)
    out = int(data.get("eval_count") or 0)
    return inp, out


def record_usage(
    *,
    service: str,
    response: Any,
    model: str | None = None,
) -> None:
    """Append one usage row. Safe to call from worker threads."""
    if not service:
        return
    inp, out = ollama_response_to_counts(response)
    if inp == 0 and out == 0:
        logger.debug("token_tracker: no counts on response for service=%s", service)
    ts = int(datetime.now(timezone.utc).timestamp())
    path = _db_path()
    _ensure_parent(path)
    with _lock:
        conn = sqlite3.connect(path)
        try:
            _init_db(conn)
            conn.execute(
                """
                INSERT INTO token_events (ts, service, model, input_tokens, output_tokens)
                VALUES (?, ?, ?, ?, ?)
                """,
                (ts, service, model, inp, out),
            )
            conn.commit()
            logger.info(
                "token_tracker: service=%s model=%s prompt_tokens=%s completion_tokens=%s",
                service,
                model or "",
                inp,
                out,
            )
        finally:
            conn.close()


# Initialize schema on import so first write is fast in typical runs
try:
    init_db_if_needed()
except OSError as e:
    logger.warning("token_tracker: could not init DB at %s: %s", _db_path(), e)

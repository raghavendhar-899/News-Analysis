"""Read-only access to Ollama token_usage SQLite (same file as app.utils.token_tracker)."""

from __future__ import annotations

import os
import sqlite3
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


def _db_path() -> str:
    explicit = os.getenv("TOKEN_USAGE_DB")
    if explicit:
        return explicit
    return str(Path(__file__).resolve().parents[2] / "data" / "token_usage.db")


def _connect() -> sqlite3.Connection:
    path = _db_path()
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def list_services() -> list[str]:
    try:
        conn = _connect()
    except sqlite3.OperationalError:
        return []
    try:
        rows = conn.execute(
            "SELECT DISTINCT service FROM token_events ORDER BY service"
        ).fetchall()
        return [r[0] for r in rows]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def _period_key(ts: int, granularity: str, tz: ZoneInfo) -> str:
    dt = datetime.fromtimestamp(ts, tz=tz)
    g = granularity.lower()
    if g == "hour":
        return dt.strftime("%Y-%m-%d %H:00:00")
    if g == "day":
        return dt.strftime("%Y-%m-%d")
    if g == "month":
        return dt.strftime("%Y-%m")
    return dt.strftime("%Y")


def _build_buckets(
    by_period: dict[str, dict[str, dict[str, int]]],
    sorted_periods: list[str],
) -> list[dict[str, Any]]:
    buckets: list[dict[str, Any]] = []
    for period in sorted_periods:
        svc_map = by_period[period]
        total_in = 0
        total_out = 0
        by_service: dict[str, Any] = {}
        for svc in sorted(svc_map.keys()):
            inn = svc_map[svc]["input_tokens"]
            out = svc_map[svc]["output_tokens"]
            total_in += inn
            total_out += out
            by_service[svc] = {
                "input_tokens": inn,
                "output_tokens": out,
            }
        buckets.append(
            {
                "period": period,
                "by_service": by_service,
                "total": {
                    "input_tokens": total_in,
                    "output_tokens": total_out,
                },
            }
        )
    buckets.sort(key=lambda b: b["period"])
    return buckets


def aggregate(
    granularity: str,
    *,
    limit: int = 100,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    g = granularity.lower()
    if g not in ("hour", "day", "month", "year"):
        g = "day"

    tz: ZoneInfo | None = None
    tz_effective = "UTC"
    if timezone_name and timezone_name.strip():
        try:
            tz = ZoneInfo(timezone_name.strip())
            tz_effective = timezone_name.strip()
        except Exception:
            tz = None
            tz_effective = "UTC"

    try:
        conn = _connect()
    except sqlite3.OperationalError as e:
        return {
            "error": "database_unavailable",
            "detail": str(e),
            "granularity": g,
            "buckets": [],
            "services": [],
            "timezone": tz_effective,
        }

    try:
        services = list_services()

        if tz is None:
            if g == "hour":
                period_expr = (
                    "strftime('%Y-%m-%d %H:00:00', datetime(ts, 'unixepoch'))"
                )
            elif g == "day":
                period_expr = "strftime('%Y-%m-%d', datetime(ts, 'unixepoch'))"
            elif g == "month":
                period_expr = "strftime('%Y-%m', datetime(ts, 'unixepoch'))"
            else:
                period_expr = "strftime('%Y', datetime(ts, 'unixepoch'))"

            sql = f"""
                SELECT
                  {period_expr} AS period,
                  service,
                  SUM(input_tokens) AS input_tokens,
                  SUM(output_tokens) AS output_tokens
                FROM token_events
                GROUP BY 1, service
                ORDER BY 1 DESC
            """
            rows = conn.execute(sql).fetchall()

            by_period: dict[str, dict[str, dict[str, int]]] = defaultdict(
                lambda: defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0})
            )
            for row in rows:
                p = row["period"]
                svc = row["service"]
                by_period[p][svc]["input_tokens"] = int(row["input_tokens"] or 0)
                by_period[p][svc]["output_tokens"] = int(row["output_tokens"] or 0)

            sorted_periods = sorted(by_period.keys(), reverse=True)[: max(1, limit)]
            buckets = _build_buckets(by_period, sorted_periods)

            return {
                "granularity": g,
                "services": services,
                "buckets": buckets,
                "timezone": tz_effective,
            }

        rows = conn.execute(
            "SELECT ts, service, input_tokens, output_tokens FROM token_events"
        ).fetchall()

        by_period = defaultdict(
            lambda: defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0})
        )
        for row in rows:
            ts = int(row["ts"])
            p = _period_key(ts, g, tz)
            svc = row["service"]
            by_period[p][svc]["input_tokens"] += int(row["input_tokens"] or 0)
            by_period[p][svc]["output_tokens"] += int(row["output_tokens"] or 0)

        sorted_all = sorted(by_period.keys(), reverse=True)
        lim = max(1, limit)
        if g == "hour":
            cur = _period_key(int(time.time()), g, tz)
            if cur not in by_period:
                _ = by_period[cur]
            selected = set(sorted_all[:lim])
            selected.add(cur)
            sorted_periods = sorted(selected, reverse=True)[:lim]
        else:
            sorted_periods = sorted_all[:lim]

        buckets = _build_buckets(by_period, sorted_periods)

        return {
            "granularity": g,
            "services": services,
            "buckets": buckets,
            "timezone": tz_effective,
        }
    finally:
        conn.close()


def totals_all_time() -> dict[str, Any]:
    try:
        conn = _connect()
    except sqlite3.OperationalError as e:
        return {"error": "database_unavailable", "detail": str(e), "by_service": {}, "total": {}}
    try:
        rows = conn.execute(
            """
            SELECT service,
                   SUM(input_tokens) AS input_tokens,
                   SUM(output_tokens) AS output_tokens
            FROM token_events
            GROUP BY service
            ORDER BY service
            """
        ).fetchall()
        total_in = 0
        total_out = 0
        by_service: dict[str, Any] = {}
        for row in rows:
            inn = int(row["input_tokens"] or 0)
            out = int(row["output_tokens"] or 0)
            total_in += inn
            total_out += out
            by_service[row["service"]] = {
                "input_tokens": inn,
                "output_tokens": out,
            }
        return {
            "by_service": by_service,
            "total": {
                "input_tokens": total_in,
                "output_tokens": total_out,
            },
        }
    finally:
        conn.close()

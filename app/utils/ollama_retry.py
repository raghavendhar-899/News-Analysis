"""On Ollama runner failures, delete the model, pull it once, and retry the request."""

from __future__ import annotations

import ollama
from ollama import ResponseError

from app.utils.logger import get_logger

logger = get_logger(__name__)


def _is_recoverable_runner_error(err: ResponseError) -> bool:
    msg = (getattr(err, "error", None) or str(err)).lower()
    if getattr(err, "status_code", None) == 500:
        return True
    if "runner" in msg or "unexpectedly stopped" in msg or "model runner" in msg:
        return True
    return False


def reset_ollama_model(model: str) -> None:
    """Remove local model files and pull again so the runner reloads clean."""
    logger.warning("Ollama recovery: deleting model %s", model)
    try:
        ollama.delete(model)
    except Exception as e:
        logger.warning("ollama.delete(%s) failed (may already be gone): %s", model, e)
    logger.warning("Ollama recovery: pulling model %s", model)
    ollama.pull(model, stream=False)


def chat_with_reset_retry(model: str, messages: list, **kwargs):
    """
    Run ollama.chat. On a single recoverable runner error, delete model, pull, retry once.
    """
    try:
        return ollama.chat(model=model, messages=messages, **kwargs)
    except ResponseError as e:
        if not _is_recoverable_runner_error(e):
            raise
        logger.warning("Ollama chat failed (%s); reset model and retry once", e)
        reset_ollama_model(model)
        return ollama.chat(model=model, messages=messages, **kwargs)

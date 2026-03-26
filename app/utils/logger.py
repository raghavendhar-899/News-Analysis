"""Centralized logger configuration for the project.

Usage:
    from app.utils.logger import get_logger, configure_logging
    configure_logging()           # once during app startup
    logger = get_logger(__name__)

The configuration reads LOG_LEVEL from the environment (defaults to INFO).
It avoids adding duplicate handlers if already configured.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def configure_logging(level: str | None = None) -> None:
    """Configure root logger with a console handler and a standard formatter.

    Safe to call multiple times; it won't add duplicate handlers.
    """
    root = logging.getLogger()

    if level is None:
        level = LOG_LEVEL

    # Convert to logging level int if necessary
    try:
        levelno = int(level)
    except Exception:
        levelno = getattr(logging, str(level).upper(), logging.INFO)

    root.setLevel(levelno)

    # If handlers already exist, assume logging already configured by environment/framework.
    if root.handlers:
        return

    handler = logging.StreamHandler()
    # ISO8601-like time format
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a module/logger instance. Ensure logging is configured lazily.

    Call `configure_logging()` at app startup for predictable behavior.
    """
    # Ensure minimal configuration exists so imports can log immediately.
    if not logging.getLogger().handlers:
        configure_logging()
    return logging.getLogger(name)

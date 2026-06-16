"""Configuración de logging de la aplicación."""

from __future__ import annotations

import logging
import sys

from app.core.config import settings

_CONFIGURED = False


def setup_logging() -> None:
    """Configura el logging raíz una sola vez (idempotente)."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Reducir ruido de librerías de terceros.
    for noisy in ("httpx", "httpcore", "urllib3", "sentence_transformers"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Devuelve un logger con la configuración aplicada."""
    setup_logging()
    return logging.getLogger(name)

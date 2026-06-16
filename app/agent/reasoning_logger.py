"""Bitácora de razonamiento en formato JSONL.

Registra cada paso del pipeline (llamadas a herramientas, decisiones, salidas)
para auditoría y para evidenciar la *cadena de pensamiento* del agente
(requisito de la diapositiva 08 del proyecto).
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ReasoningLogger:
    """Escribe eventos estructurados a un archivo .jsonl (y al log estándar)."""

    def __init__(self, log_file: Path | None = None) -> None:
        self.log_file = log_file or settings.reasoning_log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.trace_id = uuid.uuid4().hex[:12]

    def log(self, event: str, **data: Any) -> None:
        """Registra un evento con marca de tiempo y trace_id."""
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "trace_id": self.trace_id,
            "event": event,
            **data,
        }
        try:
            with self.log_file.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as exc:  # no romper el flujo por un fallo de logging
            logger.warning("No se pudo escribir la bitácora de razonamiento: %s", exc)
        logger.debug("[%s] %s %s", self.trace_id, event, data)

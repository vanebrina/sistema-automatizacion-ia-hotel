"""Fábrica del modelo de lenguaje (LLM).

Centraliza la creación de instancias de `ChatGroq` para que el resto de la
aplicación no dependa directamente del proveedor. Cambiar de proveedor (p. ej.
OpenAI) solo requeriría tocar este módulo.
"""

from __future__ import annotations

from functools import lru_cache

from langchain_groq import ChatGroq

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def build_llm(temperature: float | None = None) -> ChatGroq:
    """Construye un `ChatGroq` con la configuración del proyecto.

    Args:
        temperature: sobreescribe la temperatura por defecto del LLM.
    """
    if not settings.groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY no está configurada. Defínela en el archivo .env "
            "(consíguela gratis en https://console.groq.com/keys)."
        )

    temp = settings.llm_temperature if temperature is None else temperature
    logger.debug("Creando ChatGroq model=%s temperature=%s", settings.llm_model, temp)
    return ChatGroq(
        model=settings.llm_model,
        temperature=temp,
        api_key=settings.groq_api_key,
        max_retries=2,
    )


@lru_cache
def get_chat_llm() -> ChatGroq:
    """LLM principal del agente (cacheado)."""
    return build_llm(settings.llm_temperature)


@lru_cache
def get_extraction_llm() -> ChatGroq:
    """LLM determinista para extracción estructurada (cacheado)."""
    return build_llm(settings.extraction_temperature)

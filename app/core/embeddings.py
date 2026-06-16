"""Fábrica de modelos de embeddings para el RAG.

Permite cambiar de proveedor con una sola variable de entorno
(`EMBEDDINGS_PROVIDER`). Por defecto usa un modelo multilingüe de HuggingFace
que funciona offline y sin API key, adecuado para reseñas en español.
"""

from __future__ import annotations

from functools import lru_cache

from langchain_core.embeddings import Embeddings

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@lru_cache
def get_embeddings() -> Embeddings:
    """Devuelve el modelo de embeddings configurado (cacheado)."""
    provider = settings.embeddings_provider
    logger.info("Inicializando embeddings: provider=%s model=%s", provider, settings.embeddings_model)

    if provider == "huggingface":
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=settings.embeddings_model,
            encode_kwargs={"normalize_embeddings": True},
        )

    if provider == "fastembed":
        # Ligero (ONNX, sin torch). Requiere `pip install fastembed`.
        from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

        return FastEmbedEmbeddings(model_name=settings.embeddings_model)

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        if not settings.openai_api_key:
            raise RuntimeError("EMBEDDINGS_PROVIDER=openai requiere OPENAI_API_KEY.")
        return OpenAIEmbeddings(model=settings.embeddings_model, api_key=settings.openai_api_key)

    raise ValueError(f"Proveedor de embeddings no soportado: {provider!r}")

"""Vector store sobre PostgreSQL + pgvector (langchain-postgres).

Una sola instancia de Postgres sirve para datos relacionales y para los vectores
del RAG, simplificando la infraestructura (un solo servicio externo).
"""

from __future__ import annotations

from functools import lru_cache

from langchain_postgres import PGVector

from app.core.config import settings
from app.core.embeddings import get_embeddings
from app.core.logging import get_logger

logger = get_logger(__name__)


@lru_cache
def get_vector_store() -> PGVector:
    """Devuelve el vector store PGVector (cacheado).

    `use_jsonb=True` almacena los metadatos como JSONB (recomendado).
    La extensión `vector` se habilita vía init SQL del contenedor de Postgres.
    """
    logger.info(
        "Conectando PGVector colección=%s", settings.pgvector_collection
    )
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=settings.pgvector_collection,
        connection=settings.database_url,
        use_jsonb=True,
    )

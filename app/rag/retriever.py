"""Indexado (ingesta) y recuperación de políticas del hotel para el RAG."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.core.logging import get_logger
from app.rag.vector_store import get_vector_store

logger = get_logger(__name__)


def _load_policy_documents(policies_dir: Path) -> list[Document]:
    """Carga los .md/.txt de la carpeta de políticas como documentos."""
    docs: list[Document] = []
    if not policies_dir.exists():
        logger.warning("Carpeta de políticas no encontrada: %s", policies_dir)
        return docs

    for path in sorted(policies_dir.glob("*")):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        docs.append(Document(page_content=text, metadata={"source": path.name}))
    logger.info("Cargados %d documentos de política desde %s", len(docs), policies_dir)
    return docs


def ingest_policies(*, force: bool = False) -> int:
    """Vectoriza las políticas del hotel y las guarda en PGVector.

    Args:
        force: si False y la colección ya tiene contenido, no reindexar.

    Returns:
        Número de fragmentos (chunks) indexados.
    """
    store = get_vector_store()

    if not force:
        try:
            existing = store.similarity_search("hotel", k=1)
            if existing:
                logger.info("La colección ya contiene vectores; se omite la ingesta.")
                return 0
        except Exception:  # colección aún no creada
            pass

    documents = _load_policy_documents(settings.policies_dir)
    if not documents:
        logger.warning("No hay documentos de política para indexar.")
        return 0

    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
    chunks = splitter.split_documents(documents)
    store.add_documents(chunks)
    logger.info("Indexados %d fragmentos de política en PGVector.", len(chunks))
    return len(chunks)


def get_retriever() -> VectorStoreRetriever:
    """Retriever de similitud con el top-k configurado."""
    return get_vector_store().as_retriever(search_kwargs={"k": settings.rag_top_k})

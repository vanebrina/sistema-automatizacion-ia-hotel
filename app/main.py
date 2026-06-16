"""Punto de entrada de la aplicación FastAPI.

Arranca la API, inicializa la base de datos y (si AUTO_INIT) siembra las reservas y
vectoriza las políticas del hotel para que el sistema quede listo para la demo.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.db.base import init_db, session_scope
from app.db.seed import seed_reservations

logger = get_logger(__name__)


def _bootstrap() -> None:
    """Crea tablas y, si AUTO_INIT, siembra datos e indexa políticas."""
    init_db()
    if not settings.auto_init:
        logger.info("AUTO_INIT desactivado; se omite seed/ingesta.")
        return

    with session_scope() as session:
        seed_reservations(session)

    # Import diferido: la ingesta carga el modelo de embeddings (puede tardar la
    # primera vez mientras se descarga).
    try:
        from app.rag.retriever import ingest_policies

        ingest_policies()
    except Exception as exc:  # no impedir el arranque si el RAG falla
        logger.warning("No se pudo indexar las políticas al arranque: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Iniciando %s (%s)…", settings.app_name, settings.environment)
    _bootstrap()
    logger.info("Aplicación lista.")
    yield
    logger.info("Apagando aplicación.")


app = FastAPI(
    title=settings.app_name,
    description="Automatización de gestión de reseñas de huéspedes con LangChain (Nivel 2).",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/info", tags=["infra"])
def info() -> dict:
    return {"app": settings.app_name, "version": "2.0.0", "environment": settings.environment}

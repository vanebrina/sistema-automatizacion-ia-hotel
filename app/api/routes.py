"""Rutas HTTP (FastAPI).

Expone tanto una interfaz web sencilla (formulario, para la demo en vivo) como una
API JSON. El formulario equivale al "Form Trigger" del flujo n8n.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.logging import get_logger
from app.db.base import session_scope
from app.db.repositories import ReviewRepository
from app.pipeline.review_pipeline import get_pipeline
from app.rag.retriever import ingest_policies
from app.schemas.review import ReviewInput, ReviewResult

logger = get_logger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


@router.get("/health", tags=["infra"])
def health() -> dict:
    """Healthcheck para Docker / orquestadores."""
    return {
        "status": "ok",
        "environment": settings.environment,
        "llm_model": settings.llm_model,
        "telegram": settings.enable_telegram,
        "email": settings.enable_email,
    }


@router.get("/", response_class=HTMLResponse, tags=["web"])
def form_page(request: Request) -> HTMLResponse:
    """Formulario web del 'Buzón' de reseñas (demo)."""
    return templates.TemplateResponse(request, "form.html", {"app_name": settings.app_name})


@router.post("/reviews", response_class=HTMLResponse, tags=["web"])
def submit_form(
    request: Request,
    nombre_huesped: str = Form(...),
    resena: str = Form(...),
) -> HTMLResponse:
    """Procesa el formulario y renderiza el resultado (interfaz web)."""
    result = get_pipeline().process(ReviewInput(nombre_huesped=nombre_huesped, resena=resena))
    return templates.TemplateResponse(request, "result.html", {"r": result})


@router.post("/api/reviews", response_model=ReviewResult, tags=["api"])
def submit_api(review: ReviewInput) -> ReviewResult:
    """Procesa una reseña vía API JSON."""
    return get_pipeline().process(review)


@router.get("/api/reviews", tags=["api"])
def list_reviews(limit: int = 20) -> JSONResponse:
    """Lista las reseñas procesadas más recientes."""
    with session_scope() as session:
        records = ReviewRepository(session).list_recent(limit)
        data = [
            {
                "id": r.id,
                "fecha": r.fecha.isoformat(),
                "nombre": r.nombre,
                "sentimiento": r.sentimiento,
                "categoria": r.categoria,
                "respuesta_ia": r.respuesta_ia,
                "habitacion": r.habitacion,
                "tipo_cliente": r.tipo_cliente,
                "email_enviado": r.email_enviado,
                "alerta_enviada": r.alerta_enviada,
            }
            for r in records
        ]
    return JSONResponse(content=data)


@router.post("/admin/ingest", tags=["infra"])
def trigger_ingest(force: bool = False) -> dict:
    """Reindexa las políticas del hotel en el vector store (RAG)."""
    n = ingest_policies(force=force)
    return {"chunks_indexados": n}

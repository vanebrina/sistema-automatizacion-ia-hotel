"""Orquestación del pipeline de reseñas (réplica del flujo n8n en código).

Flujo (equivalente al workflow de n8n del Nivel 2):

    Reseña ─▶ Agente IA (+tools, RAG) ─▶ Extracción estructurada
           ─▶ Persistencia (Postgres)
           ─▶ ¿VIP/frecuente?  ─▶ Email de compensación (SMTP)
           ─▶ ¿Sentimiento != Positivo?  ─▶ Alerta Telegram

A diferencia del agente, los efectos secundarios (email, Telegram, persistencia) se
ejecutan aquí de forma determinista: más predecible, testeable y auditable.
"""

from __future__ import annotations

from functools import lru_cache

from app.agent.analyzer import ReviewAnalyzer
from app.agent.reasoning_logger import ReasoningLogger
from app.core.logging import get_logger
from app.db.base import session_scope
from app.db.models import ReviewRecord
from app.db.repositories import ReservationRepository, ReviewRepository
from app.schemas.review import ReviewInput, ReviewResult
from app.services.email import send_compensation_email
from app.services.notifications import send_critical_alert

logger = get_logger(__name__)

# Tipos de cliente que disparan compensación proactiva (regla de negocio n8n).
_COMPENSABLE = {"vip", "frecuente"}


class ReviewPipeline:
    """Coordina análisis, persistencia y notificaciones de una reseña."""

    def __init__(self) -> None:
        self.analyzer = ReviewAnalyzer()

    def process(self, review: ReviewInput) -> ReviewResult:
        reasoning = ReasoningLogger()
        reasoning.log("pipeline_start", huesped=review.nombre_huesped)

        # 1) Análisis con el agente + extracción estructurada.
        output = self.analyzer.analyze(review.nombre_huesped, review.resena, reasoning)
        analysis = output.analysis

        # 2) Lookup determinista de la reserva (para compensación y persistencia).
        with session_scope() as session:
            reserva = ReservationRepository(session).find_by_guest(review.nombre_huesped)

        # 3) ¿Compensación? Solo huéspedes VIP o frecuentes.
        email_enviado = False
        if reserva and reserva.tipo_cliente in _COMPENSABLE:
            reasoning.log("decision", regla="compensacion_vip", tipo=reserva.tipo_cliente)
            email_enviado = send_compensation_email(reserva, analysis)

        # 4) ¿Alerta crítica? Cualquier reseña no positiva (igual que el IF de n8n).
        alerta_enviada = False
        if analysis.sentimiento != "Positivo":
            reasoning.log("decision", regla="alerta_critica", sentimiento=analysis.sentimiento)
            alerta_enviada = send_critical_alert(review.nombre_huesped, analysis)

        # 5) Persistir el registro (reemplaza Google Sheets).
        with session_scope() as session:
            record = ReviewRepository(session).add(
                ReviewRecord(
                    nombre=review.nombre_huesped,
                    resena=review.resena,
                    sentimiento=analysis.sentimiento,
                    categoria=analysis.categoria,
                    respuesta_ia=analysis.respuesta_automatica,
                    habitacion=reserva.habitacion if reserva else None,
                    tipo_cliente=reserva.tipo_cliente if reserva else None,
                    email_enviado=email_enviado,
                    alerta_enviada=alerta_enviada,
                )
            )
            record_id = record.id

        reasoning.log("pipeline_end", id_registro=record_id, email=email_enviado, alerta=alerta_enviada)

        return ReviewResult(
            nombre_huesped=review.nombre_huesped,
            resena=review.resena,
            analisis=analysis,
            reserva=reserva,
            email_compensacion_enviado=email_enviado,
            alerta_telegram_enviada=alerta_enviada,
            id_registro=record_id,
        )


@lru_cache
def get_pipeline() -> ReviewPipeline:
    """Instancia única del pipeline (cacheada)."""
    return ReviewPipeline()

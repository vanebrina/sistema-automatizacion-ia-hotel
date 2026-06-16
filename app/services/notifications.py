"""Servicio de notificaciones por Telegram (alerta de reclamos críticos).

Equivale al nodo "Send a text message" de n8n. Si Telegram no está configurado,
la función se desactiva silenciosamente (devuelve False) sin romper el flujo.
"""

from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.review import ReviewAnalysis

logger = get_logger(__name__)

_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_critical_alert(nombre_huesped: str, analysis: ReviewAnalysis) -> bool:
    """Envía una alerta de reclamo crítico al chat de Telegram configurado.

    Returns:
        True si se envió; False si está desactivado o falló.
    """
    if not settings.enable_telegram:
        logger.info("Telegram desactivado (faltan credenciales); se omite la alerta.")
        return False

    texto = (
        "🚨 ¡ALERTA RECLAMO CRÍTICO DE HUÉSPED! 🚨\n"
        f"🏨 Categoría afectada: {analysis.categoria}\n"
        f"👤 Huésped: {nombre_huesped}\n"
        f"😟 Sentimiento: {analysis.sentimiento}\n"
        f"📝 Respuesta sugerida por la IA: {analysis.respuesta_automatica}"
    )

    try:
        response = httpx.post(
            _API_URL.format(token=settings.telegram_bot_token),
            json={"chat_id": settings.telegram_chat_id, "text": texto},
            timeout=15,
        )
        response.raise_for_status()
        logger.info("Alerta de Telegram enviada para el huésped %s.", nombre_huesped)
        return True
    except httpx.HTTPError as exc:
        logger.error("Fallo al enviar alerta de Telegram: %s", exc)
        return False

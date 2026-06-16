"""Servicio de correo de compensación vía SMTP.

Equivale al nodo "Send a message" (Gmail) de n8n. A diferencia del flujo original
—que enviaba a una dirección fija— aquí el correo se dirige al email del huésped
registrado en su reserva. Si SMTP no está configurado, se desactiva sin romper el flujo.
"""

from __future__ import annotations

import smtplib
from email.message import EmailMessage
from string import Template

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.review import ReservationInfo, ReviewAnalysis

logger = get_logger(__name__)

_HTML_TEMPLATE = """\
<div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto;
            border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
  <div style="background-color: #1a237e; padding: 25px; text-align: center;">
    <h2 style="color: #fff; margin: 0; font-size: 22px;">DIRECCIÓN DE GESTIÓN DE CALIDAD</h2>
    <p style="color: #c5cae9; margin: 5px 0 0; font-size: 12px; text-transform: uppercase;">
      Servicio de Atención Prioritaria · $tipo_cliente</p>
  </div>
  <div style="padding: 30px; background-color: #fff; color: #333; line-height: 1.6; font-size: 15px;">
    <p style="white-space: pre-line;">$respuesta</p>
    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
    <p style="font-size: 13px; color: #777; text-align: center;">
      Este es un canal automatizado de resolución preferencial.
      Por favor, no responda directamente a este mensaje.</p>
  </div>
  <div style="background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #9e9e9e;">
    &copy; 2026 Sistema de Experiencia del Huésped | Hotel Luxury
  </div>
</div>
"""


def send_compensation_email(reserva: ReservationInfo, analysis: ReviewAnalysis) -> bool:
    """Envía el correo de compensación formal al huésped VIP/frecuente.

    Returns:
        True si se envió; False si está desactivado o falló.
    """
    if not settings.enable_email:
        logger.info("SMTP desactivado (faltan credenciales); se omite el correo.")
        return False

    destinatario = reserva.email or settings.email_default_to
    if not destinatario:
        logger.warning("Sin email del huésped ni EMAIL_DEFAULT_TO; no se envía correo.")
        return False

    msg = EmailMessage()
    msg["Subject"] = "Compensación Formal y Disculpas — Dirección de Calidad"
    msg["From"] = settings.email_from
    msg["To"] = destinatario
    msg.set_content(analysis.respuesta_automatica)  # versión texto plano (fallback)
    html_body = Template(_HTML_TEMPLATE).safe_substitute(
        respuesta=analysis.respuesta_automatica,
        tipo_cliente=reserva.tipo_cliente.upper(),
    )
    msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        logger.info("Correo de compensación enviado a %s.", destinatario)
        return True
    except (smtplib.SMTPException, OSError) as exc:
        logger.error("Fallo al enviar el correo de compensación: %s", exc)
        return False

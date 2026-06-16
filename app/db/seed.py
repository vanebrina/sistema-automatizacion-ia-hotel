"""Datos semilla de reservas.

Replica la base simulada del Code Tool de n8n y añade un email por huésped
(necesario para el correo de compensación, que en LangChain se envía al huésped
y no a una dirección fija como en el flujo original).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models import Reservation

logger = get_logger(__name__)

SEED_RESERVATIONS = [
    {
        "nombre": "marta gomez",
        "habitacion": "204",
        "noches": 3,
        "estado_pago": "completado",
        "tipo_cliente": "vip",
        "email": "marta.gomez@example.com",
    },
    {
        "nombre": "carlos mendoza",
        "habitacion": "105",
        "noches": 1,
        "estado_pago": "completado",
        "tipo_cliente": "regular",
        "email": "carlos.mendoza@example.com",
    },
    {
        "nombre": "sebastian",
        "habitacion": "312",
        "noches": 5,
        "estado_pago": "pendiente",
        "tipo_cliente": "frecuente",
        "email": "sebastian@example.com",
    },
]


def seed_reservations(session: Session, *, force: bool = False) -> int:
    """Inserta las reservas semilla si la tabla está vacía.

    Returns:
        Número de reservas insertadas.
    """
    existing = session.scalar(select(Reservation).limit(1))
    if existing and not force:
        logger.info("Reservas ya existentes; se omite el seed.")
        return 0

    inserted = 0
    for data in SEED_RESERVATIONS:
        session.add(Reservation(**data))
        inserted += 1
    session.flush()
    logger.info("Insertadas %d reservas semilla.", inserted)
    return inserted

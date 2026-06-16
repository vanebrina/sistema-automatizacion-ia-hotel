"""Repositorios: acceso a datos encapsulado (patrón Repository)."""

from __future__ import annotations

import unicodedata

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Reservation, ReviewRecord
from app.schemas.review import ReservationInfo


def _normalize(text: str) -> str:
    """Minúsculas, sin acentos y sin espacios extra (igual que el Code Tool n8n)."""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return " ".join(text.split())


class ReservationRepository:
    """Consulta de reservas de huéspedes."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_guest(self, nombre: str) -> ReservationInfo | None:
        """Busca una reserva por nombre con coincidencia flexible.

        Replica la lógica del Code Tool de n8n: coincide si el término buscado
        contiene el nombre registrado o viceversa (ignorando acentos/mayúsculas).
        """
        needle = _normalize(nombre)
        if not needle:
            return None

        for reserva in self.session.scalars(select(Reservation)):
            registrado = _normalize(reserva.nombre)
            if registrado in needle or needle in registrado:
                return ReservationInfo(
                    nombre=reserva.nombre,
                    habitacion=reserva.habitacion,
                    noches=reserva.noches,
                    estado_pago=reserva.estado_pago,
                    tipo_cliente=reserva.tipo_cliente,  # type: ignore[arg-type]
                    email=reserva.email,
                )
        return None


class ReviewRepository:
    """Persistencia del historial de reseñas procesadas."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, record: ReviewRecord) -> ReviewRecord:
        self.session.add(record)
        self.session.flush()  # asigna el id sin cerrar la transacción
        return record

    def list_recent(self, limit: int = 20) -> list[ReviewRecord]:
        stmt = select(ReviewRecord).order_by(ReviewRecord.fecha.desc()).limit(limit)
        return list(self.session.scalars(stmt))

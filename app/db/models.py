"""Modelos ORM (tablas) del sistema.

- `Reservation`: reemplaza la "base de datos simulada" del Code Tool de n8n.
- `ReviewRecord`: reemplaza el log de Google Sheets de n8n (persistencia).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Reservation(Base):
    """Reserva activa de un huésped (catálogo del hotel)."""

    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    habitacion: Mapped[str] = mapped_column(String(10), nullable=False)
    noches: Mapped[int] = mapped_column(Integer, nullable=False)
    estado_pago: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo_cliente: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(180), nullable=True)


class ReviewRecord(Base):
    """Registro persistido de cada reseña procesada (historial / auditoría)."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    resena: Mapped[str] = mapped_column(Text, nullable=False)
    sentimiento: Mapped[str] = mapped_column(String(20), nullable=False)
    categoria: Mapped[str] = mapped_column(String(60), nullable=False)
    respuesta_ia: Mapped[str] = mapped_column(Text, nullable=False)
    habitacion: Mapped[str | None] = mapped_column(String(10), nullable=True)
    tipo_cliente: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email_enviado: Mapped[bool] = mapped_column(default=False)
    alerta_enviada: Mapped[bool] = mapped_column(default=False)

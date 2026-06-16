"""Conexión y sesión de base de datos (SQLAlchemy 2.0)."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos ORM."""


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # reconecta si la conexión murió (útil en contenedores)
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provee una sesión transaccional con commit/rollback automático."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Crea las tablas declaradas si no existen.

    Nota: para un proyecto productivo serio se recomienda Alembic (migraciones).
    Aquí `create_all` es suficiente para el alcance del Nivel 2.
    """
    # Importa los modelos para que queden registrados en el metadata.
    from app.db import models  # noqa: F401

    logger.info("Creando tablas (si no existen)…")
    Base.metadata.create_all(bind=engine)

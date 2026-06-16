"""Tests unitarios offline (sin red, sin LLM, sin Postgres).

Cubren la lógica determinista del sistema:
- Normalización y coincidencia de nombres de huésped.
- Validación del esquema de salida estructurada del LLM.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Reservation
from app.db.repositories import ReservationRepository, _normalize
from app.schemas.review import ReviewAnalysis


@pytest.fixture
def session():
    """Sesión SQLite en memoria con datos de prueba."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    sess = factory()
    sess.add_all(
        [
            Reservation(
                nombre="marta gomez", habitacion="204", noches=3,
                estado_pago="completado", tipo_cliente="vip", email="m@example.com",
            ),
            Reservation(
                nombre="sebastian", habitacion="312", noches=5,
                estado_pago="pendiente", tipo_cliente="frecuente",
            ),
        ]
    )
    sess.commit()
    yield sess
    sess.close()


def test_normalize_quita_acentos_y_espacios():
    assert _normalize("  Martá   GÓMEZ ") == "marta gomez"


@pytest.mark.parametrize(
    "query,esperado",
    [
        ("Marta Gómez", "204"),                     # match exacto (con acento)
        ("marta", "204"),                           # query es subcadena del registro
        ("Hola, soy Sebastián, mi cuarto...", "312"),  # registro es subcadena de la query
        ("Pedro Pérez", None),                      # sin coincidencia
    ],
)
def test_find_by_guest(session, query, esperado):
    reserva = ReservationRepository(session).find_by_guest(query)
    assert (reserva.habitacion if reserva else None) == esperado


def test_review_analysis_valido():
    a = ReviewAnalysis(
        sentimiento="Negativo",
        categoria="Habitaciones y Limpieza",
        respuesta_automatica="Lamentamos lo ocurrido…",
    )
    assert a.sentimiento == "Negativo"


def test_review_analysis_rechaza_valores_fuera_de_dominio():
    with pytest.raises(ValidationError):
        ReviewAnalysis(
            sentimiento="Malo",  # no pertenece al dominio
            categoria="Otra cosa",
            respuesta_automatica="x",
        )

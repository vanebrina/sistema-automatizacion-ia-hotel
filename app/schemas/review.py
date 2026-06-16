"""Modelos de datos (contratos) del dominio de reseñas.

Estos `BaseModel` de Pydantic cumplen dos funciones:
1. Validar la entrada/salida de la API.
2. Definir el esquema de *structured output* que el LLM debe rellenar
   (equivalente al nodo "Information Extractor" de n8n).
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

# Valores cerrados — reflejan exactamente las opciones del flujo n8n original.
Sentimiento = Literal["Positivo", "Neutral", "Negativo"]
Categoria = Literal[
    "Habitaciones y Limpieza",
    "Instalaciones y Servicios",
    "Atención al Cliente",
    "Alimentos y Bebidas",
]
TipoCliente = Literal["vip", "frecuente", "regular"]


class ReviewInput(BaseModel):
    """Reseña entrante (equivale al formulario 'Buzón' de n8n)."""

    nombre_huesped: str = Field(..., min_length=1, description="Nombre del huésped.")
    resena: str = Field(..., min_length=1, description="Texto de la reseña del hotel.")


class ReviewAnalysis(BaseModel):
    """Salida estructurada del análisis (lo que produce el LLM).

    El docstring y las descripciones se envían al modelo como esquema, por eso
    están redactadas como instrucciones.
    """

    sentimiento: Sentimiento = Field(
        ..., description="Sentimiento general de la reseña: Positivo, Neutral o Negativo."
    )
    categoria: Categoria = Field(
        ...,
        description=(
            "Categoría principal del comentario: 'Habitaciones y Limpieza', "
            "'Instalaciones y Servicios', 'Atención al Cliente' o 'Alimentos y Bebidas'."
        ),
    )
    respuesta_automatica: str = Field(
        ...,
        description=(
            "Respuesta amable, profesional y breve en español dirigida al huésped. "
            "Si la reseña es positiva, agradece; si es negativa, discúlpate y ofrece "
            "revisar el caso. Si se conocen datos de la reserva (habitación, noches), "
            "menciónalos para personalizar."
        ),
    )


class ReservationInfo(BaseModel):
    """Datos de la reserva de un huésped (consulta a la base de datos)."""

    nombre: str
    habitacion: str
    noches: int
    estado_pago: str
    tipo_cliente: TipoCliente
    email: Optional[str] = None


class ReviewResult(BaseModel):
    """Resultado completo del pipeline (lo que devuelve la API)."""

    nombre_huesped: str
    resena: str
    analisis: ReviewAnalysis
    reserva: Optional[ReservationInfo] = None
    email_compensacion_enviado: bool = False
    alerta_telegram_enviada: bool = False
    id_registro: Optional[int] = None

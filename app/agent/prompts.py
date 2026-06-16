"""Plantillas de prompts (ChatPromptTemplate).

Contiene:
- El prompt del *agente* (con herramientas + cadena de pensamiento ReAct).
- El prompt de la *cadena de extracción* (salida estructurada).

Adaptado del system message del nodo "AI Agent" de n8n.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# --- Prompt del Agente (razonamiento + uso de herramientas) ------------------

AGENT_SYSTEM_PROMPT = """Eres un asistente de IA experto en hotelería y moderación de \
opiniones del Hotel Luxury. Tu trabajo es analizar la reseña de un huésped y preparar \
una respuesta personalizada y profesional en español.

REGLAS DE OPERACIÓN CON HERRAMIENTAS (obligatorias):
1. SIEMPRE usa primero la herramienta `consultar_reserva` con el nombre del huésped \
para verificar si tiene una reserva activa (habitación, noches, estado de pago y tipo \
de cliente).
2. Usa la herramienta `buscar_politica_hotel` para consultar la política interna \
relevante al problema mencionado (climatización, limpieza, A&B, servicios, etc.) y \
fundamentar la respuesta y la posible compensación.
3. Si encuentras datos reales de la reserva (número de habitación, noches), DEBES \
usarlos en tu respuesta para demostrarle al huésped que ya estás revisando su caso \
específico. No vuelvas a pedir datos que ya obtuviste.

Razona paso a paso: decide qué herramienta usar, observa el resultado y continúa hasta \
tener suficiente información. Luego redacta tu análisis final del caso en español, \
incluyendo: el sentimiento de la reseña, la categoría del problema y una respuesta \
amable y concreta para el huésped (con disculpas y solución si el caso es negativo, o \
agradecimiento si es positivo).
"""

AGENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", AGENT_SYSTEM_PROMPT),
        ("human", "Huésped: {nombre_huesped}\nReseña: {resena}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


# --- Prompt de extracción estructurada (equivale al Information Extractor) ----

EXTRACTION_SYSTEM_PROMPT = """Eres un extractor de información. A partir del análisis \
del caso, devuelve únicamente los campos estructurados solicitados.

- 'sentimiento': solo 'Positivo', 'Neutral' o 'Negativo'.
- 'categoria': solo una de 'Habitaciones y Limpieza', 'Instalaciones y Servicios', \
'Atención al Cliente' o 'Alimentos y Bebidas'.
- 'respuesta_automatica': la respuesta final amable y profesional para el huésped, en \
español, breve y personalizada con los datos de la reserva si están disponibles.
"""

EXTRACTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", EXTRACTION_SYSTEM_PROMPT),
        (
            "human",
            "Reseña original del huésped {nombre_huesped}:\n{resena}\n\n"
            "Análisis del agente (incluye datos de reserva y políticas):\n{analisis}",
        ),
    ]
)

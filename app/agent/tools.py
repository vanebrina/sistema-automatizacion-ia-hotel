"""Herramientas (Tools) que el agente LangChain puede invocar.

- `consultar_reserva`: equivale al "Code Tool" de n8n (base de datos del hotel),
  ahora respaldado por PostgreSQL.
- `buscar_politica_hotel`: nueva capacidad RAG (no existía en n8n) que recupera la
  política interna relevante desde el vector store.

Ambas son de solo lectura (seguras para que el agente las llame libremente). Los
efectos secundarios (email, Telegram) se ejecutan de forma determinista en el
pipeline, no como herramientas del agente.
"""

from __future__ import annotations

from langchain_core.tools import BaseTool, tool

from app.agent.reasoning_logger import ReasoningLogger
from app.core.logging import get_logger
from app.db.base import session_scope
from app.db.repositories import ReservationRepository
from app.rag.retriever import get_retriever

logger = get_logger(__name__)


def build_tools(reasoning: ReasoningLogger) -> list[BaseTool]:
    """Crea las herramientas del agente enlazadas a una bitácora de razonamiento."""

    @tool
    def consultar_reserva(nombre: str) -> str:
        """Consulta la base de datos del hotel por el nombre o apellido del huésped.

        Úsala para verificar si el huésped tiene una reserva activa y obtener su
        número de habitación, noches de estancia, estado de pago y tipo de cliente
        (vip, frecuente o regular).
        """
        reasoning.log("tool_call", tool="consultar_reserva", input=nombre)
        with session_scope() as session:
            reserva = ReservationRepository(session).find_by_guest(nombre)

        if reserva is None:
            result = (
                f"Sistema del Hotel: No se encontró ninguna reserva activa que "
                f'coincida con "{nombre}".'
            )
        else:
            result = (
                f"Sistema del Hotel: Reserva activa para {reserva.nombre.upper()}. "
                f"Habitación: {reserva.habitacion}, Estancia: {reserva.noches} noches, "
                f"Pago: {reserva.estado_pago}, Tipo de Cliente: {reserva.tipo_cliente}."
            )
        reasoning.log("tool_result", tool="consultar_reserva", output=result)
        return result

    @tool
    def buscar_politica_hotel(consulta: str) -> str:
        """Busca en el manual de políticas internas del hotel (RAG).

        Úsala para fundamentar la respuesta y la compensación según la categoría del
        problema: climatización, limpieza, instalaciones, atención al cliente o
        alimentos y bebidas.
        """
        reasoning.log("tool_call", tool="buscar_politica_hotel", input=consulta)
        try:
            docs = get_retriever().invoke(consulta)
        except Exception as exc:  # el RAG no debe tumbar el flujo
            logger.warning("Fallo en recuperación RAG: %s", exc)
            reasoning.log("tool_error", tool="buscar_politica_hotel", error=str(exc))
            return "No fue posible consultar las políticas en este momento."

        if not docs:
            return "No se encontró una política específica para esa consulta."

        fragmentos = "\n\n".join(
            f"[{d.metadata.get('source', 'politica')}] {d.page_content.strip()}"
            for d in docs
        )
        reasoning.log(
            "tool_result",
            tool="buscar_politica_hotel",
            fuentes=[d.metadata.get("source") for d in docs],
        )
        return f"Políticas relevantes del hotel:\n{fragmentos}"

    return [consultar_reserva, buscar_politica_hotel]

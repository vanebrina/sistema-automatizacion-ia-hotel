"""Análisis de reseñas: Agente (ReAct) + Cadena de extracción (LCEL).

Pipeline de razonamiento en dos pasos, equivalente a n8n
("AI Agent" -> "Information Extractor"):

1. AGENTE (`create_tool_calling_agent` + `AgentExecutor`): razona con cadena de
   pensamiento estilo ReAct y usa herramientas (consultar reserva + RAG de políticas)
   para producir un análisis enriquecido del caso.
2. CADENA LCEL (`with_structured_output`): convierte ese análisis en el objeto
   estructurado `ReviewAnalysis` (sentimiento, categoría, respuesta).
"""

from __future__ import annotations

from dataclasses import dataclass

from langchain.agents import AgentExecutor, create_tool_calling_agent

from app.agent.prompts import AGENT_PROMPT, EXTRACTION_PROMPT
from app.agent.reasoning_logger import ReasoningLogger
from app.agent.tools import build_tools
from app.core.llm import get_chat_llm, get_extraction_llm
from app.core.logging import get_logger
from app.schemas.review import ReviewAnalysis

logger = get_logger(__name__)


@dataclass
class AnalysisOutput:
    """Resultado del análisis del LLM."""

    analysis: ReviewAnalysis
    agent_text: str


class ReviewAnalyzer:
    """Encapsula el agente y la cadena de extracción."""

    def __init__(self) -> None:
        self.llm = get_chat_llm()
        self.extraction_chain = EXTRACTION_PROMPT | get_extraction_llm().with_structured_output(
            ReviewAnalysis
        )

    def _build_executor(self, reasoning: ReasoningLogger) -> AgentExecutor:
        tools = build_tools(reasoning)
        agent = create_tool_calling_agent(self.llm, tools, AGENT_PROMPT)
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            max_iterations=6,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
        )

    def analyze(self, nombre_huesped: str, resena: str, reasoning: ReasoningLogger) -> AnalysisOutput:
        """Ejecuta agente + extracción y devuelve el análisis estructurado."""
        executor = self._build_executor(reasoning)

        reasoning.log("agent_start", nombre=nombre_huesped)
        result = executor.invoke({"nombre_huesped": nombre_huesped, "resena": resena})
        agent_text = result.get("output", "")

        # Registrar la cadena de pensamiento (pasos intermedios) para auditoría.
        for action, observation in result.get("intermediate_steps", []):
            reasoning.log(
                "agent_step",
                herramienta=getattr(action, "tool", None),
                entrada=getattr(action, "tool_input", None),
                observacion=str(observation)[:500],
            )
        reasoning.log("agent_output", texto=agent_text[:800])

        # Paso 2: extracción estructurada (LCEL).
        analysis: ReviewAnalysis = self.extraction_chain.invoke(
            {"nombre_huesped": nombre_huesped, "resena": resena, "analisis": agent_text}
        )
        reasoning.log(
            "extraction",
            sentimiento=analysis.sentimiento,
            categoria=analysis.categoria,
        )
        return AnalysisOutput(analysis=analysis, agent_text=agent_text)

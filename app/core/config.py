"""Configuración central de la aplicación.

Toda la configuración se carga desde variables de entorno (o un archivo `.env`)
usando `pydantic-settings`. Esto mantiene los secretos fuera del código y permite
cambiar el comportamiento entre desarrollo y producción sin tocar el código.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Raíz del proyecto (… /app/core/config.py -> sube 3 niveles)
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Configuración tipada y validada de la aplicación."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Aplicación ---------------------------------------------------------
    app_name: str = "Sistema Automatizacion IA Hotel"
    environment: Literal["development", "production"] = "development"
    debug: bool = True
    log_level: str = "INFO"
    auto_init: bool = True
    log_dir: Path = BASE_DIR / "logs"

    # --- LLM (Groq) ---------------------------------------------------------
    groq_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.3
    extraction_temperature: float = 0.0

    # --- Base de datos ------------------------------------------------------
    database_url: str = "postgresql+psycopg://hotel:hotel@localhost:5432/hoteldb"

    # --- RAG / Embeddings ---------------------------------------------------
    embeddings_provider: Literal["huggingface", "fastembed", "openai"] = "huggingface"
    embeddings_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    pgvector_collection: str = "politicas_hotel"
    rag_top_k: int = 3
    policies_dir: Path = BASE_DIR / "data" / "policies"
    openai_api_key: str = ""

    # --- Telegram (opcional) ------------------------------------------------
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # --- Correo SMTP (opcional) ---------------------------------------------
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    email_from: str = "Dirección de Calidad <calidad@hotel-luxury.com>"
    email_default_to: str = ""

    # --- Propiedades derivadas (feature flags) ------------------------------
    @property
    def enable_telegram(self) -> bool:
        """La alerta de Telegram solo se activa si hay token y chat id."""
        return bool(self.telegram_bot_token and self.telegram_chat_id)

    @property
    def enable_email(self) -> bool:
        """El correo de compensación solo se activa si hay servidor y usuario SMTP."""
        return bool(self.smtp_host and self.smtp_user)

    @property
    def reasoning_log_file(self) -> Path:
        return self.log_dir / "reasoning.jsonl"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia única (cacheada) de la configuración."""
    return Settings()


settings = get_settings()

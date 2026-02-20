"""Application configuration via pydantic-settings."""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    app_env: str = "development"
    mock_llm: bool = True

    # AWS Bedrock
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    # Bedrock model IDs
    orchestrator_model_id: str = "us.anthropic.claude-opus-4-20250514-v1:0"
    policy_model_id: str = "us.anthropic.claude-3-5-haiku-20241022-v1:0"

    # Google Vertex AI
    gcp_project_id: str = ""
    gcp_location: str = "us-central1"
    google_application_credentials: str = ""
    research_model_id: str = "gemini-2.5-flash"

    # OpenAI
    openai_api_key: str = ""
    comms_model_id: str = "gpt-4o"

    # Gmail
    gmail_enabled: bool = False
    gmail_sender: str = ""
    gmail_app_password: str = ""
    gmail_recipient: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Orchestrator thresholds
    confidence_threshold: float = 0.7

    # Internal base URL for mock API calls
    base_url: str = "http://127.0.0.1:8000"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.google_application_credentials:
        os.environ.setdefault(
            "GOOGLE_APPLICATION_CREDENTIALS",
            settings.google_application_credentials,
        )
    return settings

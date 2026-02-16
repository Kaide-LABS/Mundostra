"""Application configuration via pydantic-settings."""

from __future__ import annotations

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
    orchestrator_model_id: str = "us.anthropic.claude-opus-4-0-20250514"
    policy_model_id: str = "us.anthropic.claude-haiku-4-0-20250514"

    # Google Vertex AI
    gcp_project_id: str = ""
    gcp_location: str = "us-central1"
    research_model_id: str = "gemini-2.0-flash"

    # OpenAI
    openai_api_key: str = ""
    comms_model_id: str = "gpt-4o"

    # Slack
    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    slack_enabled: bool = False
    slack_default_channel: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Orchestrator thresholds
    confidence_threshold: float = 0.7

    # Internal base URL for mock API calls
    base_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()

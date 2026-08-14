"""Agent Settings Pydantic v2 Settings class."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Local JARVIS Agent Settings."""

    env: str = "development"
    log_level: str = "INFO"
    local_host: str = "127.0.0.1"
    local_port: int = 8765

    # Cloud & Provider settings
    cloud_api_url: str | None = None
    device_id: str | None = None
    openai_api_key: str | None = None
    ollama_base_url: str = "http://127.0.0.1:11434"

    # Execution limits & security
    workspace_root: str = "."
    max_tool_execution_seconds: int = 60
    max_output_bytes: int = 65536  # 64 KB

    model_config = SettingsConfigDict(
        env_prefix="JARVIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> AgentSettings:
    """Return cached instance of AgentSettings."""
    return AgentSettings()

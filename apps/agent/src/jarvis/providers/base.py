"""
Abstract Base Class for LLM Providers (OpenAI, Ollama, Cloud API).
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ProviderResponse(BaseModel):
    """Normalized response from LLM inference provider."""

    content: str | None = Field(None, description="Text completion message")
    tool_calls: list[dict[str, Any]] = Field(default_factory=list, description="Requested tool invocations")
    raw_response: dict[str, Any] = Field(default_factory=dict)
    prompt_tokens: int = Field(0)
    completion_tokens: int = Field(0)


class BaseLLMProvider(ABC):
    """Abstract interface that all LLM providers must implement."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    @abstractmethod
    async def generate_plan(
        self,
        user_prompt: str,
        available_tools: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> ProviderResponse:
        """Generate a structured response or tool invocation sequence."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider connectivity and status."""

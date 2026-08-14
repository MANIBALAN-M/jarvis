"""
Abstract Base Class for all JARVIS Tools.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from jarvis.core.contracts import RiskLevel


class ToolExecutionResult(BaseModel):
    """Standard result returned by any tool execution."""

    status: str = Field(..., description="'success', 'denied', 'failed', or 'error'")
    output_summary: str = Field(..., description="Compact summary for LLM context window")
    full_output: str = Field("", description="Complete output content")
    exit_code: int = Field(0, description="Process exit code")
    truncated: bool = Field(False, description="Whether output exceeded maximum byte limit")
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseTool(ABC):
    """Base class that every JARVIS tool must inherit from."""

    tool_id: str
    description: str
    risk_level: RiskLevel
    args_schema: type[BaseModel]

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolExecutionResult:
        """Execute tool logic with validated keyword arguments."""

    def get_schema(self) -> dict[str, Any]:
        """Return OpenAPI-compatible JSON schema declaration for LLM planner."""
        return {
            "tool_id": self.tool_id,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "parameters": self.args_schema.model_json_schema(),
        }

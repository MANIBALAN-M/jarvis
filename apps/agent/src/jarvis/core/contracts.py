"""
Pydantic contracts for Commands, Task Plans, Policy Decisions, and Verification Results.
"""

from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Tool execution risk classifications."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CommandSource(str, Enum):
    """Origin of a command request."""

    TEXT_UI = "text_ui"
    VOICE = "voice"
    HOTKEY = "hotkey"
    SCHEDULED = "scheduled"
    CLOUD_API = "cloud_api"


class Command(BaseModel):
    """User command ingress payload."""

    command_id: str = Field(default_factory=lambda: str(uuid4()))
    raw_text: str = Field(..., description="Unprocessed natural language input text")
    source: CommandSource = Field(default=CommandSource.TEXT_UI)
    device_id: str | None = Field(None, description="Requesting device identifier")
    created_at_ts: float = Field(..., description="Unix timestamp of command intake")
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskStep(BaseModel):
    """Single step within a multi-step task execution plan."""

    step_id: str = Field(default_factory=lambda: str(uuid4()))
    step_number: int = Field(..., ge=1)
    tool_id: str = Field(..., description="Unique tool identifier, e.g. 'filesystem.read'")
    tool_input: dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel = Field(default=RiskLevel.LOW)
    status: str = Field(default="pending", description="'pending', 'approved', 'running', 'success', 'failed', 'blocked'")
    requires_approval: bool = Field(default=False)
    description: str = Field("", description="Human readable step description")


class TaskPlan(BaseModel):
    """Structured plan containing ordered tool steps."""

    task_id: str = Field(default_factory=lambda: str(uuid4()))
    command_id: str = Field(...)
    goal_summary: str = Field(..., description="High-level target goal summary")
    steps: list[TaskStep] = Field(default_factory=list)
    status: str = Field(default="created", description="'created', 'in_progress', 'completed', 'failed', 'cancelled'")


class PolicyDecision(str, Enum):
    """Result of policy evaluation for a proposed tool execution."""

    ALLOW = "allow"
    ASK_USER = "ask_user"
    BLOCK = "block"


class PolicyResult(BaseModel):
    """Policy Engine evaluation outcome."""

    decision: PolicyDecision
    reason: str
    risk_level: RiskLevel
    tool_id: str
    evaluated_args: dict[str, Any] = Field(default_factory=dict)


class CommandResult(BaseModel):
    """Final outcome returned after command processing completes."""

    command_id: str
    task_id: str
    status: str = Field(..., description="'success', 'failed', 'cancelled'")
    summary: str
    steps_executed: int = Field(0)
    error_message: str | None = None
    output_data: dict[str, Any] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    """Validation result checking if task outcome matches intent."""

    verified: bool
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    details: str
    metrics: dict[str, Any] = Field(default_factory=dict)

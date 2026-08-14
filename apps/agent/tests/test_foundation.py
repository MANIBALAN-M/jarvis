"""
Foundation tests verifying Phase 0 Pydantic contracts and base classes.
"""

import time

import pytest
from pydantic import BaseModel, Field

from jarvis.config.settings import get_settings
from jarvis.core.contracts import (
    Command,
    CommandSource,
    PolicyDecision,
    RiskLevel,
    TaskPlan,
    TaskStep,
)
from jarvis.security.policy import BasePolicyEngine
from jarvis.tools.base import BaseTool, ToolExecutionResult


def test_settings_default_values():
    settings = get_settings()
    assert settings.local_host == "127.0.0.1"
    assert settings.local_port == 8765
    assert settings.env == "development"


def test_command_creation():
    cmd = Command(
        raw_text="Check git status",
        source=CommandSource.TEXT_UI,
        created_at_ts=time.time(),
    )
    assert cmd.command_id is not None
    assert cmd.raw_text == "Check git status"
    assert cmd.source == CommandSource.TEXT_UI


def test_task_plan_creation():
    step1 = TaskStep(
        step_number=1,
        tool_id="git.status",
        tool_input={"repo_path": "."},
        risk_level=RiskLevel.LOW,
    )
    plan = TaskPlan(
        command_id="cmd-123",
        goal_summary="Check repository status",
        steps=[step1],
    )
    assert len(plan.steps) == 1
    assert plan.steps[0].tool_id == "git.status"
    assert plan.steps[0].risk_level == RiskLevel.LOW


def test_policy_engine_evaluation():
    policy = BasePolicyEngine()

    # Low risk
    res_low = policy.evaluate("filesystem.read", {"file_path": "README.md"}, RiskLevel.LOW)
    assert res_low.decision == PolicyDecision.ALLOW

    # Medium risk
    res_med = policy.evaluate("terminal.run", {"command": "npm test"}, RiskLevel.MEDIUM)
    assert res_med.decision == PolicyDecision.ASK_USER

    # Critical risk
    res_crit = policy.evaluate("disk.format", {"drive": "C:"}, RiskLevel.CRITICAL)
    assert res_crit.decision == PolicyDecision.BLOCK


class SampleInputSchema(BaseModel):
    target: str = Field(..., description="Target string parameter")


class DummyTool(BaseTool):
    tool_id = "test.dummy"
    description = "Dummy test tool"
    risk_level = RiskLevel.LOW
    args_schema = SampleInputSchema

    async def execute(self, target: str) -> ToolExecutionResult:
        return ToolExecutionResult(
            status="success",
            output_summary=f"Processed {target}",
            full_output=f"Processed {target} successfully",
        )


@pytest.mark.asyncio
async def test_dummy_tool_execution():
    tool = DummyTool()
    schema = tool.get_schema()
    assert schema["tool_id"] == "test.dummy"
    assert schema["risk_level"] == "low"

    res = await tool.execute(target="test_value")
    assert res.status == "success"
    assert "test_value" in res.output_summary

"""Agent Planner for deconstructing goals into TaskPlans."""

from jarvis.core.contracts import Command, RiskLevel, TaskPlan, TaskStep
from jarvis.providers.base import BaseLLMProvider


class AgentPlanner:
    """Deconstructs complex user requests into structured TaskPlan step sequences."""

    def __init__(self, provider: BaseLLMProvider | None = None):
        self.provider = provider

    async def plan_command(self, command: Command, available_tools: list[dict]) -> TaskPlan:
        raw = command.raw_text.strip().lower()

        # Fallback rule-based planner for Phase 1 when LLM provider is offline
        if "check git status" in raw or "git status" in raw:
            return TaskPlan(
                command_id=command.command_id,
                goal_summary="Check git repository status",
                steps=[
                    TaskStep(
                        step_number=1,
                        tool_id="terminal.run",
                        tool_input={"command": "git", "args": ["status"]},
                        risk_level=RiskLevel.MEDIUM,
                        description="Run git status command",
                    )
                ],
            )

        if "search files" in raw or "find files" in raw:
            return TaskPlan(
                command_id=command.command_id,
                goal_summary="Search workspace for matching files",
                steps=[
                    TaskStep(
                        step_number=1,
                        tool_id="filesystem.search",
                        tool_input={"search_dir": ".", "pattern": "*"},
                        risk_level=RiskLevel.LOW,
                        description="Search workspace files",
                    )
                ],
            )

        # Default multi-step fallback plan
        return TaskPlan(
            command_id=command.command_id,
            goal_summary=f"Execute multi-step task: {command.raw_text}",
            steps=[
                TaskStep(
                    step_number=1,
                    tool_id="system.info",
                    tool_input={},
                    risk_level=RiskLevel.LOW,
                    description="Gather system status for planning",
                )
            ],
        )

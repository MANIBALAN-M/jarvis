"""Agent Planner for deconstructing goals into TaskPlans."""

import urllib.parse

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

        if "notepad" in raw and ("write" in raw or "create" in raw or "file" in raw):
            content = "hi"
            if "write " in raw:
                content = command.raw_text.split("write ", 1)[-1].strip()

            target_file = "notes.txt"
            return TaskPlan(
                command_id=command.command_id,
                goal_summary=f"Create file '{target_file}' and launch Notepad",
                steps=[
                    TaskStep(
                        step_number=1,
                        tool_id="filesystem.write",
                        tool_input={"file_path": target_file, "content": content},
                        risk_level=RiskLevel.MEDIUM,
                        description=f"Write content to {target_file}",
                    ),
                    TaskStep(
                        step_number=2,
                        tool_id="application.open",
                        tool_input={"app_name": "notepad", "target_path": target_file},
                        risk_level=RiskLevel.LOW,
                        description=f"Launch Notepad with {target_file}",
                    ),
                ],
            )

        if ("search" in raw or "google" in raw) and any(kw in raw for kw in ["chrome", "browser", "edge", "google", "online", "web"]):
            query = "python"
            if "search " in raw:
                query = command.raw_text.split("search ", 1)[-1].strip()
            elif "for " in raw:
                query = command.raw_text.split("for ", 1)[-1].strip()

            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            app_target = "chrome" if "chrome" in raw else ("edge" if "edge" in raw else "browser")

            return TaskPlan(
                command_id=command.command_id,
                goal_summary=f"Search '{query}' in web browser",
                steps=[
                    TaskStep(
                        step_number=1,
                        tool_id="application.open",
                        tool_input={"app_name": app_target, "target_path": search_url},
                        risk_level=RiskLevel.LOW,
                        description=f"Launch {app_target} with Google Search for '{query}'",
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

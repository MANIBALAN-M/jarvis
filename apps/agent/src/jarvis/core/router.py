"""Command Router for fast deterministic routing vs LLM planning."""

from jarvis.core.contracts import Command, RiskLevel, TaskPlan, TaskStep


class CommandRouter:
    """Classifies user commands into fast-path deterministic actions or multi-step plans."""

    def route(self, command: Command) -> tuple[str, TaskPlan | None]:
        raw = command.raw_text.strip().lower()

        # Deterministic fast-path mappings
        if any(kw in raw for kw in ["system info", "cpu info", "os info", "system status"]):
            plan = TaskPlan(
                command_id=command.command_id,
                goal_summary="Retrieve local system information",
                steps=[
                    TaskStep(
                        step_number=1,
                        tool_id="system.info",
                        tool_input={},
                        risk_level=RiskLevel.LOW,
                        description="Inspect CPU and OS metrics",
                    )
                ],
            )
            return "deterministic", plan

        if raw.startswith("open ") or raw.startswith("launch "):
            app_name = raw.replace("open ", "").replace("launch ", "").strip()
            plan = TaskPlan(
                command_id=command.command_id,
                goal_summary=f"Launch application '{app_name}'",
                steps=[
                    TaskStep(
                        step_number=1,
                        tool_id="application.open",
                        tool_input={"app_name": app_name},
                        risk_level=RiskLevel.LOW,
                        description=f"Launch {app_name}",
                    )
                ],
            )
            return "deterministic", plan

        if raw.startswith("read file ") or raw.startswith("inspect file "):
            file_path = raw.replace("read file ", "").replace("inspect file ", "").strip()
            plan = TaskPlan(
                command_id=command.command_id,
                goal_summary=f"Read contents of '{file_path}'",
                steps=[
                    TaskStep(
                        step_number=1,
                        tool_id="filesystem.read",
                        tool_input={"file_path": file_path},
                        risk_level=RiskLevel.LOW,
                        description=f"Read {file_path}",
                    )
                ],
            )
            return "deterministic", plan

        # Default: complex agent request requiring Planner
        return "agent_planner", None

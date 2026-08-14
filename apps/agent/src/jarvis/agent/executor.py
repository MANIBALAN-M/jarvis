"""Task Executor engine running tool steps with security policy enforcement."""

from typing import Any

from jarvis.agent.verifier import OutcomeVerifier
from jarvis.core.contracts import CommandResult, PolicyDecision, PolicyResult, TaskPlan
from jarvis.core.errors import sanitize_user_error
from jarvis.security.approval import verify_approval
from jarvis.security.audit import AuditLogger
from jarvis.security.policy import BasePolicyEngine
from jarvis.storage.repositories.task_repository import SQLiteTaskRepository
from jarvis.storage.sqlite import get_sqlite_manager
from jarvis.tools.registry import ToolRegistry, get_tool_registry


class TaskExecutor:
    """Sequential task plan execution engine."""

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        policy_engine: BasePolicyEngine | None = None,
        audit_logger: AuditLogger | None = None,
        task_repo: SQLiteTaskRepository | None = None,
    ):
        self.registry = registry or get_tool_registry()
        self.policy_engine = policy_engine or BasePolicyEngine()
        self.audit_logger = audit_logger or AuditLogger()
        if task_repo is None:
            manager = get_sqlite_manager()
            task_repo = SQLiteTaskRepository(manager)
        self.task_repo = task_repo
        self.verifier = OutcomeVerifier()

    async def execute_plan(self, plan: TaskPlan) -> CommandResult:
        plan.status = "in_progress"
        self.task_repo.save_task_plan(plan)

        steps_executed = 0
        last_summary = ""
        output_data: dict[str, Any] = {}

        for step in plan.steps:
            if step.status == "success":
                steps_executed += 1
                continue

            tool = self.registry.get_tool(step.tool_id)
            if not tool:
                step.status = "failed"
                step.description += " [Error: Tool not found]"
                self.task_repo.update_step_result(step.step_id, "failed", error_message="Tool not found")
                plan.status = "failed"
                self.task_repo.update_task_status(plan.task_id, "failed")
                return CommandResult(
                    command_id=plan.command_id,
                    task_id=plan.task_id,
                    status="failed",
                    summary=f"Tool '{step.tool_id}' is not registered.",
                    steps_executed=steps_executed,
                    error_message=f"Tool '{step.tool_id}' not found.",
                )

            # Evaluate Security Policy
            pol_res: PolicyResult = self.policy_engine.evaluate(step.tool_id, step.tool_input, step.risk_level)

            # Log audit record
            self.audit_logger.log_action(
                event_type="policy_evaluation",
                tool_id=step.tool_id,
                risk_level=pol_res.risk_level.value,
                decision=pol_res.decision.value,
                args=step.tool_input,
            )

            if pol_res.decision == PolicyDecision.BLOCK:
                step.status = "blocked"
                self.task_repo.update_step_result(step.step_id, "blocked", error_message="Policy blocked action")
                plan.status = "failed"
                self.task_repo.update_task_status(plan.task_id, "failed")
                return CommandResult(
                    command_id=plan.command_id,
                    task_id=plan.task_id,
                    status="failed",
                    summary=f"Execution blocked by policy for tool '{step.tool_id}'.",
                    steps_executed=steps_executed,
                    error_message=pol_res.reason,
                )

            # Require cryptographic proof for ASK_USER policy decision
            is_approved = verify_approval(plan.task_id, step, step.approval_token)
            if pol_res.decision == PolicyDecision.ASK_USER and not is_approved:
                step.status = "awaiting_approval"
                step.requires_approval = True
                self.task_repo.update_step_result(
                    step.step_id,
                    "awaiting_approval",
                    output_summary=pol_res.reason,
                )
                plan.status = "awaiting_approval"
                self.task_repo.update_task_status(plan.task_id, "awaiting_approval")
                return CommandResult(
                    command_id=plan.command_id,
                    task_id=plan.task_id,
                    status="awaiting_approval",
                    summary=f"Action '{step.tool_id}' requires cryptographic user approval before execution.",
                    steps_executed=steps_executed,
                    output_data={"step_id": step.step_id, "tool_id": step.tool_id, "reason": pol_res.reason},
                )

            # Execute tool
            step.status = "running"
            self.task_repo.update_step_result(step.step_id, "running")

            try:
                tool_res = await tool.execute(**step.tool_input)
                v_res = self.verifier.verify_step(step, tool_res)

                if v_res.verified:
                    step.status = "success"
                    steps_executed += 1
                    last_summary = tool_res.output_summary
                    output_data[step.tool_id] = tool_res.metadata or tool_res.output_summary
                    self.task_repo.update_step_result(step.step_id, "success", output_summary=tool_res.output_summary)
                else:
                    step.status = "failed"
                    self.task_repo.update_step_result(step.step_id, "failed", output_summary=tool_res.output_summary, error_message=v_res.details)
                    plan.status = "failed"
                    self.task_repo.update_task_status(plan.task_id, "failed")
                    return CommandResult(
                        command_id=plan.command_id,
                        task_id=plan.task_id,
                        status="failed",
                        summary=tool_res.output_summary,
                        steps_executed=steps_executed,
                        error_message=v_res.details,
                    )

            except Exception as e:  # noqa: BLE001
                user_msg = sanitize_user_error(e)
                step.status = "failed"
                self.task_repo.update_step_result(step.step_id, "failed", error_message=user_msg)
                plan.status = "failed"
                self.task_repo.update_task_status(plan.task_id, "failed")
                return CommandResult(
                    command_id=plan.command_id,
                    task_id=plan.task_id,
                    status="failed",
                    summary=user_msg,
                    steps_executed=steps_executed,
                    error_message=user_msg,
                )

        plan.status = "completed"
        self.task_repo.update_task_status(plan.task_id, "completed")
        return CommandResult(
            command_id=plan.command_id,
            task_id=plan.task_id,
            status="success",
            summary=last_summary or f"Task '{plan.goal_summary}' completed successfully.",
            steps_executed=steps_executed,
            output_data=output_data,
        )

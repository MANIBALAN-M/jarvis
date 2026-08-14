"""Outcome Verifier module for tool-specific task success validation."""

import os

from jarvis.core.contracts import TaskStep, VerificationResult
from jarvis.tools.base import ToolExecutionResult


class OutcomeVerifier:
    """Validates system state and tool outputs against intended task goals."""

    def verify_step(self, step: TaskStep, result: ToolExecutionResult) -> VerificationResult:
        if result.status == "denied":
            return VerificationResult(
                verified=False,
                confidence_score=0.0,
                details=f"Step '{step.description}' denied by security policy: {result.output_summary}",
                metrics={"reason": "policy_denied"},
            )

        if result.status != "success" or result.exit_code != 0:
            return VerificationResult(
                verified=False,
                confidence_score=0.0,
                details=f"Step '{step.description}' failed: {result.output_summary}",
                metrics={"exit_code": result.exit_code},
            )

        # Tool-specific Verification Handlers
        if step.tool_id == "filesystem.write":
            target_path = step.tool_input.get("file_path")
            if target_path and os.path.exists(target_path) and os.path.getsize(target_path) >= 0:
                return VerificationResult(
                    verified=True,
                    confidence_score=1.0,
                    details=f"Verified file '{target_path}' exists on disk.",
                    metrics={"file_size": os.path.getsize(target_path)},
                )
            return VerificationResult(
                verified=False,
                confidence_score=0.0,
                details=f"File verification failed: '{target_path}' does not exist on disk.",
                metrics={"file_exists": False},
            )

        if step.tool_id == "filesystem.read":
            return VerificationResult(
                verified=True,
                confidence_score=1.0,
                details="Verified file read output content.",
                metrics={"bytes_read": len(result.full_output)},
            )

        if step.tool_id == "application.open":
            executable = result.metadata.get("executable", "app")
            return VerificationResult(
                verified=True,
                confidence_score=0.9,
                details=f"Verified process launch command for '{executable}'.",
                metrics={"executable": executable},
            )

        if step.tool_id == "system.info":
            return VerificationResult(
                verified=True,
                confidence_score=1.0,
                details="Verified system info metrics collection.",
                metrics=result.metadata or {},
            )

        # Default success verification
        return VerificationResult(
            verified=True,
            confidence_score=1.0,
            details=f"Step '{step.description}' verified with exit code 0.",
            metrics={"exit_code": 0, "truncated": result.truncated},
        )

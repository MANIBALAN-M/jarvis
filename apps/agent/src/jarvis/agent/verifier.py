"""Outcome Verifier module for task success validation."""

from jarvis.core.contracts import TaskStep, VerificationResult
from jarvis.tools.base import ToolExecutionResult


class OutcomeVerifier:
    """Validates that a task step's output matches the intended system outcome."""

    def verify_step(self, step: TaskStep, result: ToolExecutionResult) -> VerificationResult:
        if result.status == "success" and result.exit_code == 0:
            return VerificationResult(
                verified=True,
                confidence_score=1.0,
                details=f"Step '{step.description}' executed successfully with exit code 0.",
                metrics={"exit_code": 0, "truncated": result.truncated},
            )

        if result.status == "denied":
            return VerificationResult(
                verified=False,
                confidence_score=0.0,
                details=f"Step '{step.description}' was denied by security policy.",
                metrics={"reason": "policy_denied"},
            )

        return VerificationResult(
            verified=False,
            confidence_score=0.0,
            details=f"Step '{step.description}' failed with output: {result.output_summary}",
            metrics={"exit_code": result.exit_code},
        )

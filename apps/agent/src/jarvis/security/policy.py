"""Base Policy Engine implementation."""

from typing import Any

from jarvis.core.contracts import PolicyDecision, PolicyResult, RiskLevel
from jarvis.security.risk import classify_risk


class BasePolicyEngine:
    """Evaluates policy decisions for proposed tool calls."""

    def evaluate(self, tool_id: str, tool_args: dict[str, Any], declared_risk: RiskLevel) -> PolicyResult:
        effective_risk = classify_risk(tool_id, declared_risk)

        if effective_risk == RiskLevel.CRITICAL:
            return PolicyResult(
                decision=PolicyDecision.BLOCK,
                reason="Operation classified as CRITICAL and is blocked by security policy.",
                risk_level=effective_risk,
                tool_id=tool_id,
                evaluated_args=tool_args,
            )

        if effective_risk in (RiskLevel.HIGH, RiskLevel.MEDIUM):
            return PolicyResult(
                decision=PolicyDecision.ASK_USER,
                reason=f"Operation requires user approval due to {effective_risk.value} risk level.",
                risk_level=effective_risk,
                tool_id=tool_id,
                evaluated_args=tool_args,
            )

        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            reason="Operation permitted under default read-only / low-risk policy.",
            risk_level=effective_risk,
            tool_id=tool_id,
            evaluated_args=tool_args,
        )

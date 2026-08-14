"""Risk classification utility function."""

from jarvis.core.contracts import RiskLevel


def classify_risk(tool_id: str, default_risk: RiskLevel = RiskLevel.LOW) -> RiskLevel:
    """Classify tool execution risk level based on tool taxonomy rules."""
    high_risk_prefixes = ("filesystem.delete", "git.reset", "database.drop", "system.shutdown")
    critical_risk_prefixes = ("disk.format", "system.privilege_escalation", "raw_shell.exec")

    for prefix in critical_risk_prefixes:
        if tool_id.startswith(prefix):
            return RiskLevel.CRITICAL

    for prefix in high_risk_prefixes:
        if tool_id.startswith(prefix):
            return RiskLevel.HIGH

    return default_risk

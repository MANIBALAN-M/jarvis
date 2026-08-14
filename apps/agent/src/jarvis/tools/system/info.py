"""System Info Tool implementation."""

import os
import platform
from typing import Any

from pydantic import BaseModel

from jarvis.core.contracts import RiskLevel
from jarvis.tools.base import BaseTool, ToolExecutionResult


class SystemInfoInput(BaseModel):
    """Input parameters for system.info (none required)."""

    verbose: bool = False


class SystemInfoTool(BaseTool):
    """Tool returning system CPU/OS/Architecture metrics."""

    tool_id = "system.info"
    description = "Inspect local system CPU, operating system, platform architecture, and environment."
    risk_level = RiskLevel.LOW
    args_schema = SystemInfoInput

    async def execute(self, verbose: bool = False) -> ToolExecutionResult:
        info: dict[str, Any] = {
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
        }

        summary = f"OS: {info['os']} {info['os_release']} ({info['architecture']}), Python: {info['python_version']}, CPUs: {info['cpu_count']}"
        return ToolExecutionResult(
            status="success",
            output_summary=summary,
            full_output=str(info),
            exit_code=0,
            metadata=info,
        )

"""Application Open Tool implementation."""

import asyncio
import platform
import subprocess

from pydantic import BaseModel, Field

from jarvis.core.contracts import RiskLevel
from jarvis.tools.base import BaseTool, ToolExecutionResult


class ApplicationOpenInput(BaseModel):
    app_name: str = Field(..., description="Approved application name to launch (e.g. 'notepad', 'vscode', 'calc', 'browser')")
    target_path: str | None = Field(None, description="Optional target file/workspace path to open with application")


APPROVED_APPS = {
    "notepad": "notepad.exe",
    "calc": "calc.exe",
    "calculator": "calc.exe",
    "vscode": "code",
    "code": "code",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "browser": "msedge.exe" if platform.system() == "Windows" else "google-chrome",
}


def _launch_app_sync(cmd: list[str]) -> None:
    subprocess.Popen(cmd, shell=False)


class ApplicationOpenTool(BaseTool):
    """Tool launching policy-approved desktop applications."""

    tool_id = "application.open"
    description = "Launch policy-approved desktop applications (notepad, vscode, calculator, browser, etc.)."
    risk_level = RiskLevel.LOW
    args_schema = ApplicationOpenInput

    async def execute(self, app_name: str, target_path: str | None = None) -> ToolExecutionResult:
        normalized_name = app_name.lower().strip()
        if normalized_name not in APPROVED_APPS:
            return ToolExecutionResult(
                status="denied",
                output_summary=f"Application '{app_name}' is not in approved application allowlist.",
                exit_code=1,
            )

        executable = APPROVED_APPS[normalized_name]
        cmd: list[str] = [executable]
        if target_path:
            cmd.append(target_path)

        try:
            await asyncio.to_thread(_launch_app_sync, cmd)
            return ToolExecutionResult(
                status="success",
                output_summary=f"Successfully launched '{app_name}' ({executable}).",
                exit_code=0,
                metadata={"app_name": app_name, "executable": executable},
            )
        except Exception as e:  # noqa: BLE001
            return ToolExecutionResult(
                status="failed",
                output_summary=f"Failed to launch '{app_name}': {e!s}",
                exit_code=1,
            )

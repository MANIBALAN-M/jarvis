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
    "chrome": "chrome.exe" if platform.system() == "Windows" else "google-chrome",
    "edge": "msedge.exe" if platform.system() == "Windows" else "microsoft-edge",
    "explorer": "explorer.exe",
    "paint": "mspaint.exe",
    "terminal": "wt.exe" if platform.system() == "Windows" else "xterm",
}

APP_ALIASES = {
    "note pad": "notepad",
    "text editor": "notepad",
    "vs code": "vscode",
    "visual studio code": "vscode",
    "command prompt": "cmd",
    "power shell": "powershell",
    "file explorer": "explorer",
    "ms paint": "paint",
    "microsoft edge": "edge",
    "google chrome": "chrome",
}


def resolve_executable_path(executable: str) -> str:
    import os
    import shutil

    if shutil.which(executable):
        return executable

    if platform.system() == "Windows":
        name = os.path.basename(executable).lower()
        if "chrome" in name:
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            ]
            for p in paths:
                if os.path.exists(p):
                    return p
        if "edge" in name:
            paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ]
            for p in paths:
                if os.path.exists(p):
                    return p

        if name in ("chrome.exe", "msedge.exe", "browser"):
            return "explorer.exe"

    return executable


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
        normalized_name = APP_ALIASES.get(normalized_name, normalized_name)
        clean_name = normalized_name.replace(" ", "").replace("-", "")

        executable = APPROVED_APPS.get(normalized_name) or APPROVED_APPS.get(clean_name)
        if not executable:
            # Check if any known approved app name or alias exists as a substring
            for alias, app_key in APP_ALIASES.items():
                if alias in normalized_name:
                    executable = APPROVED_APPS.get(app_key)
                    break
            if not executable:
                for key, exe in APPROVED_APPS.items():
                    if len(key) >= 3 and key in normalized_name:
                        executable = exe
                        break

        if not executable:
            return ToolExecutionResult(
                status="denied",
                output_summary=f"Application '{app_name}' is not in approved application allowlist.",
                exit_code=1,
            )
        resolved_exe = resolve_executable_path(executable)
        cmd: list[str] = [resolved_exe]
        if target_path:
            cmd.append(target_path)

        try:
            await asyncio.to_thread(_launch_app_sync, cmd)
            return ToolExecutionResult(
                status="success",
                output_summary=f"Successfully launched '{app_name}' ({resolved_exe}).",
                exit_code=0,
                metadata={"app_name": app_name, "executable": resolved_exe},
            )
        except Exception as e:  # noqa: BLE001
            return ToolExecutionResult(
                status="failed",
                output_summary=f"Failed to launch '{app_name}': {e!s}",
                exit_code=1,
            )

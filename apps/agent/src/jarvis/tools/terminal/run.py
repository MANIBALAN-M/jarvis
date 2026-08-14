"""Controlled Terminal Executor Tool."""

import asyncio

from pydantic import BaseModel, Field

from jarvis.core.contracts import RiskLevel
from jarvis.tools.base import BaseTool, ToolExecutionResult


class TerminalRunInput(BaseModel):
    command: str = Field(..., description="Allowlisted command binary (e.g. 'git', 'pytest', 'python', 'npm', 'dir', 'echo')")
    args: list[str] = Field(default_factory=list, description="List of argument strings passed to executable")
    cwd: str | None = Field(None, description="Working directory path")
    timeout_seconds: int = Field(60, ge=1, le=300, description="Process timeout limit in seconds")


ALLOWED_COMMANDS = {
    "git", "pytest", "python", "pip", "node", "npm", "dir", "echo",
    "type", "ls", "docker", "uvicorn", "cargo", "rustc"
}


class TerminalRunTool(BaseTool):
    """Tool running allowlisted terminal commands with bounded output and timeouts."""

    tool_id = "terminal.run"
    description = "Execute allowlisted shell commands with timeouts, cancellation, and output limits."
    risk_level = RiskLevel.MEDIUM
    args_schema = TerminalRunInput

    async def execute(
        self,
        command: str,
        args: list[str] | None = None,
        cwd: str | None = None,
        timeout_seconds: int = 60,
    ) -> ToolExecutionResult:
        cmd_base = command.lower().strip()
        if cmd_base not in ALLOWED_COMMANDS:
            return ToolExecutionResult(
                status="denied",
                output_summary=f"Command '{command}' is not in approved command allowlist.",
                exit_code=1,
            )

        args_list = args or []
        cmd_full = [command] + args_list

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd_full,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    process.communicate(), timeout=timeout_seconds
                )
            except TimeoutError:
                process.kill()
                return ToolExecutionResult(
                    status="failed",
                    output_summary=f"Terminal command timed out after {timeout_seconds} seconds.",
                    exit_code=124,
                )

            stdout_str = stdout_data.decode("utf-8", errors="replace")
            stderr_str = stderr_data.decode("utf-8", errors="replace")
            combined_output = stdout_str + ("\n" + stderr_str if stderr_str else "")

            max_bytes = 65536
            truncated = len(combined_output.encode("utf-8")) > max_bytes
            summary = combined_output[:256] + ("..." if truncated else "")

            status = "success" if process.returncode == 0 else "failed"
            return ToolExecutionResult(
                status=status,
                output_summary=summary,
                full_output=combined_output[:max_bytes],
                exit_code=process.returncode or 0,
                truncated=truncated,
            )

        except Exception as e:
            return ToolExecutionResult(
                status="failed",
                output_summary=f"Terminal execution error: {e!s}",
                exit_code=1,
            )

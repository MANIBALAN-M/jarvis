"""Sandboxed Workspace Filesystem Tools."""

import asyncio
import os
from pathlib import Path

from pydantic import BaseModel, Field

from jarvis.config.settings import get_settings
from jarvis.core.contracts import RiskLevel
from jarvis.tools.base import BaseTool, ToolExecutionResult


def is_path_safe(target_path: str, workspace_root: str | None = None) -> bool:
    """Validate that path resolution stays strictly within trusted workspace root."""
    try:
        root = workspace_root if workspace_root is not None else get_settings().workspace_root
        resolved_target = Path(target_path).resolve()
        resolved_root = Path(root).resolve()
        return resolved_target == resolved_root or resolved_root in resolved_target.parents
    except (OSError, ValueError, RuntimeError):
        return False


# --- Filesystem Read ---
class FileReadInput(BaseModel):
    file_path: str = Field(..., description="Target file path to read")
    max_bytes: int = Field(65536, ge=1, le=500000, description="Max bytes to read (default: 64KB)")


def _read_file_sync(file_path: str, max_bytes: int) -> tuple[str, bool]:
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read(max_bytes)
    truncated = os.path.getsize(file_path) > max_bytes
    return content, truncated


class FileReadTool(BaseTool):
    tool_id = "filesystem.read"
    description = "Read file content within approved workspace directory with byte limits."
    risk_level = RiskLevel.LOW
    args_schema = FileReadInput

    async def execute(self, file_path: str, max_bytes: int = 65536) -> ToolExecutionResult:
        if not is_path_safe(file_path):
            return ToolExecutionResult(
                status="denied",
                output_summary=f"Access denied: path '{file_path}' resolves outside allowed workspace root.",
                exit_code=1,
            )

        if not os.path.exists(file_path):
            return ToolExecutionResult(
                status="failed",
                output_summary=f"File not found: '{file_path}'",
                exit_code=1,
            )

        try:
            content, truncated = await asyncio.to_thread(_read_file_sync, file_path, max_bytes)
            summary = content[:256] + ("..." if truncated else "")
            return ToolExecutionResult(
                status="success",
                output_summary=summary,
                full_output=content,
                exit_code=0,
                truncated=truncated,
            )
        except OSError as e:
            return ToolExecutionResult(
                status="failed",
                output_summary=f"File system error reading '{file_path}': {e.strerror or str(e)}",
                exit_code=1,
            )


# --- Filesystem Write ---
class FileWriteInput(BaseModel):
    file_path: str = Field(..., description="Target file path to create/write")
    content: str = Field(..., description="Text content to write")


def _write_file_sync(file_path: str, content: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


class FileWriteTool(BaseTool):
    tool_id = "filesystem.write"
    description = "Create or modify file content within approved workspace directory."
    risk_level = RiskLevel.MEDIUM
    args_schema = FileWriteInput

    async def execute(self, file_path: str, content: str) -> ToolExecutionResult:
        if not is_path_safe(file_path):
            return ToolExecutionResult(
                status="denied",
                output_summary=f"Access denied: target path '{file_path}' resolves outside allowed workspace root.",
                exit_code=1,
            )

        try:
            await asyncio.to_thread(_write_file_sync, file_path, content)
            return ToolExecutionResult(
                status="success",
                output_summary=f"Successfully wrote {len(content)} characters to '{file_path}'.",
                exit_code=0,
            )
        except OSError as e:
            return ToolExecutionResult(
                status="failed",
                output_summary=f"File system error writing '{file_path}': {e.strerror or str(e)}",
                exit_code=1,
            )


# --- Filesystem Search ---
class FileSearchInput(BaseModel):
    search_dir: str = Field(".", description="Directory path to search")
    pattern: str = Field("*", description="Glob pattern or file extension filter (e.g. '*.py')")


def _search_files_sync(search_dir: str, pattern: str) -> list[str]:
    matched: list[str] = []
    for path in Path(search_dir).rglob(pattern):
        if not any(part.startswith(".") for part in path.parts):
            matched.append(str(path))
        if len(matched) >= 100:
            break
    return matched


class FileSearchTool(BaseTool):
    tool_id = "filesystem.search"
    description = "Search files matching glob pattern inside workspace."
    risk_level = RiskLevel.LOW
    args_schema = FileSearchInput

    async def execute(self, search_dir: str = ".", pattern: str = "*") -> ToolExecutionResult:
        if not is_path_safe(search_dir):
            return ToolExecutionResult(
                status="denied",
                output_summary=f"Access denied: directory '{search_dir}' resolves outside allowed workspace root.",
                exit_code=1,
            )

        try:
            matched = await asyncio.to_thread(_search_files_sync, search_dir, pattern)
            summary = f"Found {len(matched)} matching files."
            return ToolExecutionResult(
                status="success",
                output_summary=summary,
                full_output="\n".join(matched),
                exit_code=0,
                metadata={"file_count": len(matched)},
            )
        except OSError as e:
            return ToolExecutionResult(
                status="failed",
                output_summary=f"Search failed in '{search_dir}': {e.strerror or str(e)}",
                exit_code=1,
            )

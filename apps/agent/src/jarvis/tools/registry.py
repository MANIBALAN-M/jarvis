"""Tool Registry managing available tool instances and schemas."""


from jarvis.tools.applications.open import ApplicationOpenTool
from jarvis.tools.base import BaseTool
from jarvis.tools.filesystem.workspace import (
    FileReadTool,
    FileSearchTool,
    FileWriteTool,
)
from jarvis.tools.system.info import SystemInfoTool
from jarvis.tools.terminal.run import TerminalRunTool


class ToolRegistry:
    """Registry maintaining available tool implementations."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}
        self._register_default_tools()

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.tool_id] = tool

    def get_tool(self, tool_id: str) -> BaseTool | None:
        return self._tools.get(tool_id)

    def list_tools(self) -> list[dict[str, str]]:
        return [tool.get_schema() for tool in self._tools.values()]

    def _register_default_tools(self) -> None:
        self.register(SystemInfoTool())
        self.register(ApplicationOpenTool())
        self.register(FileReadTool())
        self.register(FileWriteTool())
        self.register(FileSearchTool())
        self.register(TerminalRunTool())


_registry_instance: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ToolRegistry()
    return _registry_instance

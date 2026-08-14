"""Unit tests for controlled tools suite."""

import pytest

from jarvis.tools.applications.open import ApplicationOpenTool
from jarvis.tools.filesystem.workspace import (
    FileReadTool,
    FileSearchTool,
    FileWriteTool,
)
from jarvis.tools.system.info import SystemInfoTool
from jarvis.tools.terminal.run import TerminalRunTool


@pytest.mark.asyncio
async def test_system_info_tool():
    tool = SystemInfoTool()
    res = await tool.execute()
    assert res.status == "success"
    assert "OS:" in res.output_summary
    assert res.metadata["cpu_count"] is not None


@pytest.mark.asyncio
async def test_application_open_allowlist():
    tool = ApplicationOpenTool()
    # Denied unapproved app
    res_denied = await tool.execute(app_name="malware_app")
    assert res_denied.status == "denied"
    assert "not in approved" in res_denied.output_summary

    # Approved app test (notepad / calc)
    res_approved = await tool.execute(app_name="notepad")
    assert res_approved.status == "success"


@pytest.mark.asyncio
async def test_filesystem_write_and_read(tmp_path):
    write_tool = FileWriteTool()
    read_tool = FileReadTool()

    target_file = str(tmp_path / "test_output.txt")
    test_content = "Hello JARVIS Automation Agent!"

    # Write test
    w_res = await write_tool.execute(file_path=target_file, content=test_content)
    assert w_res.status == "success"

    # Read test
    r_res = await read_tool.execute(file_path=target_file)
    assert r_res.status == "success"
    assert r_res.full_output == test_content


@pytest.mark.asyncio
async def test_filesystem_search(tmp_path):
    search_tool = FileSearchTool()
    (tmp_path / "sample.py").write_text("print('hello')")

    res = await search_tool.execute(search_dir=str(tmp_path), pattern="*.py")
    assert res.status == "success"
    assert "sample.py" in res.full_output


@pytest.mark.asyncio
async def test_terminal_run_tool():
    term_tool = TerminalRunTool()

    # Allowed command test (python version)
    res = await term_tool.execute(command="python", args=["--version"])
    assert res.status == "success"
    assert "Python" in res.output_summary or "Python" in res.full_output

    # Denied command test
    res_denied = await term_tool.execute(command="format")
    assert res_denied.status == "denied"

"""Unit tests for controlled tools suite."""

from unittest.mock import patch

import pytest

from jarvis.config.settings import get_settings
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

    res_denied = await tool.execute(app_name="malware_app")
    assert res_denied.status == "denied"

    with patch("jarvis.tools.applications.open._launch_app_sync") as mock_launch:
        res_approved = await tool.execute(app_name="notepad")

    assert res_approved.status == "success"
    mock_launch.assert_called_once_with(["notepad.exe"])


@pytest.mark.asyncio
async def test_application_open_aliases():
    tool = ApplicationOpenTool()

    with patch("jarvis.tools.applications.open._launch_app_sync") as mock_launch:
        res1 = await tool.execute(app_name="note pad")
        assert res1.status == "success"
        mock_launch.assert_called_with(["notepad.exe"])

    with patch("jarvis.tools.applications.open._launch_app_sync") as mock_launch:
        res2 = await tool.execute(app_name="VS Code")
        assert res2.status == "success"
        mock_launch.assert_called_with(["code"])



@pytest.mark.asyncio
async def test_filesystem_write_and_read(tmp_path, monkeypatch):
    write_tool = FileWriteTool()
    read_tool = FileReadTool()

    monkeypatch.setattr(get_settings(), "workspace_root", str(tmp_path))
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
async def test_filesystem_search(tmp_path, monkeypatch):
    search_tool = FileSearchTool()
    monkeypatch.setattr(get_settings(), "workspace_root", str(tmp_path))
    (tmp_path / "sample.py").write_text("print('hello')")

    res = await search_tool.execute(search_dir=str(tmp_path), pattern="*.py")
    assert res.status == "success"
    assert "sample.py" in res.full_output


@pytest.mark.asyncio
async def test_filesystem_security_traversal(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "secret.txt"
    outside.write_text("classified data")

    monkeypatch.setattr(get_settings(), "workspace_root", str(workspace))

    read_tool = FileReadTool()
    write_tool = FileWriteTool()
    search_tool = FileSearchTool()

    # 1. Relative ../ traversal attack
    res_trav = await read_tool.execute(file_path=str(workspace / ".." / "secret.txt"))
    assert res_trav.status == "denied"

    # 2. Absolute path outside workspace
    res_abs = await read_tool.execute(file_path=str(outside))
    assert res_abs.status == "denied"

    # 3. Write outside workspace
    res_w = await write_tool.execute(file_path=str(workspace / ".." / "pawn.txt"), content="hack")
    assert res_w.status == "denied"

    # 4. Search outside workspace
    res_s = await search_tool.execute(search_dir=str(tmp_path))
    assert res_s.status == "denied"


def test_is_path_safe_boundary_cases(tmp_path):
    from jarvis.tools.filesystem.workspace import is_path_safe

    workspace = tmp_path / "safe_workspace"
    workspace.mkdir()
    inside_file = workspace / "sub" / "file.txt"
    outside_file = tmp_path / "outside.txt"

    ws_str = str(workspace)

    assert is_path_safe(str(workspace), workspace_root=ws_str) is True
    assert is_path_safe(str(inside_file), workspace_root=ws_str) is True
    assert is_path_safe(str(outside_file), workspace_root=ws_str) is False
    assert is_path_safe(str(workspace / ".." / "outside.txt"), workspace_root=ws_str) is False


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


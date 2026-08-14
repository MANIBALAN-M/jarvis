"""Unit tests for Command Router, Task Executor, and Policy Engine integration."""

import time

import pytest

from jarvis.agent.executor import TaskExecutor
from jarvis.core.contracts import Command, CommandSource
from jarvis.core.router import CommandRouter
from jarvis.storage.repositories.task_repository import SQLiteTaskRepository
from jarvis.storage.sqlite import SQLiteManager


@pytest.mark.asyncio
async def test_command_router_fast_path():
    router = CommandRouter()
    cmd = Command(
        raw_text="system info",
        source=CommandSource.TEXT_UI,
        created_at_ts=time.time(),
    )
    route_type, plan = router.route(cmd)
    assert route_type == "deterministic"
    assert plan is not None
    assert plan.steps[0].tool_id == "system.info"


@pytest.mark.asyncio
async def test_task_executor_success(tmp_path):
    db_file = str(tmp_path / "test_exec.db")
    sq_mgr = SQLiteManager(db_file)
    task_repo = SQLiteTaskRepository(sq_mgr)

    executor = TaskExecutor(task_repo=task_repo)
    router = CommandRouter()

    cmd = Command(
        raw_text="system info",
        source=CommandSource.TEXT_UI,
        created_at_ts=time.time(),
    )
    _, plan = router.route(cmd)

    result = await executor.execute_plan(plan)
    assert result.status == "success"
    assert result.steps_executed == 1
    assert "system.info" in result.output_data

    # Verify saved task in database
    saved_plan = task_repo.get_task_plan(plan.task_id)
    assert saved_plan is not None
    assert saved_plan.status == "completed"

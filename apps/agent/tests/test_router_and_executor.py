"""Unit tests for Command Router, Task Executor, and Policy Engine integration."""

import time

import pytest

from jarvis.agent.executor import TaskExecutor
from jarvis.core.contracts import Command, CommandSource, RiskLevel, TaskPlan, TaskStep
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


@pytest.mark.asyncio
async def test_task_executor_ask_user_approval_flow(tmp_path):
    db_file = str(tmp_path / "test_approval.db")
    sq_mgr = SQLiteManager(db_file)
    task_repo = SQLiteTaskRepository(sq_mgr)

    executor = TaskExecutor(task_repo=task_repo)

    step = TaskStep(
        step_number=1,
        tool_id="terminal.run",
        tool_input={"command": "python", "args": ["--version"]},
        risk_level=RiskLevel.MEDIUM,
        description="Run terminal command",
    )
    plan = TaskPlan(
        command_id="cmd-medium-risk",
        goal_summary="Run terminal command",
        steps=[step],
    )

    # 1. First execution should pause for approval
    res1 = await executor.execute_plan(plan)
    assert res1.status == "awaiting_approval"
    assert plan.steps[0].status == "awaiting_approval"

    # 2. Mark step as approved and re-run executor
    plan.steps[0].status = "approved"
    res2 = await executor.execute_plan(plan)
    assert res2.status == "success"
    assert res2.steps_executed == 1

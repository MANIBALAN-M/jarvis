"""Unit tests for Command Router, Task Executor, and Policy Engine integration."""

import time

import pytest

from jarvis.agent.executor import TaskExecutor
from jarvis.core.contracts import Command, CommandSource, RiskLevel, TaskPlan, TaskStep
from jarvis.core.router import CommandRouter
from jarvis.security.approval import generate_approval_token
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

    # 2. Attach cryptographic approval token and re-run executor
    token = generate_approval_token(
        plan.task_id,
        step.step_id,
        step.tool_id,
        step.risk_level.value,
        step.tool_input,
    )
    plan.steps[0].approval_token = token

    res2 = await executor.execute_plan(plan)
    assert res2.status == "success"
    assert res2.steps_executed == 1


def test_approval_token_tampered_arguments():
    from jarvis.security.approval import verify_approval

    step = TaskStep(
        step_number=1,
        tool_id="terminal.run",
        tool_input={"command": "python", "args": ["--version"]},
        risk_level=RiskLevel.MEDIUM,
    )
    task_id = "task-security-test"

    # Valid token generated for original arguments
    token = generate_approval_token(
        task_id,
        step.step_id,
        step.tool_id,
        step.risk_level.value,
        step.tool_input,
    )
    assert verify_approval(task_id, step, token) is True

    # Tamper with step tool input after token generation
    step.tool_input = {"command": "format", "args": ["C:"]}
    assert verify_approval(task_id, step, token) is False


def test_approval_token_invalid_or_empty():
    from jarvis.security.approval import verify_approval

    step = TaskStep(
        step_number=1,
        tool_id="terminal.run",
        tool_input={"command": "python"},
        risk_level=RiskLevel.MEDIUM,
    )
    task_id = "task-invalid-test"

    assert verify_approval(task_id, step, None) is False
    assert verify_approval(task_id, step, "") is False
    assert verify_approval(task_id, step, "bad_token_hex_12345") is False


def test_approval_token_custom_secret():
    step = TaskStep(
        step_number=1,
        tool_id="terminal.run",
        tool_input={"command": "python"},
        risk_level=RiskLevel.MEDIUM,
    )
    task_id = "task-secret-test"

    t1 = generate_approval_token(task_id, step.step_id, step.tool_id, step.risk_level.value, step.tool_input, secret_key="secret_A")
    t2 = generate_approval_token(task_id, step.step_id, step.tool_id, step.risk_level.value, step.tool_input, secret_key="secret_B")
    assert t1 != t2


def test_approval_token_expiry():
    from jarvis.security.approval import verify_approval

    step = TaskStep(
        step_number=1,
        tool_id="terminal.run",
        tool_input={"command": "python"},
        risk_level=RiskLevel.MEDIUM,
    )
    task_id = "task-expiry-test"

    # Token generated with expired timestamp (expires_at in past)
    expired_token = generate_approval_token(
        task_id, step.step_id, step.tool_id, step.risk_level.value, step.tool_input, expires_at=1000000000, nonce="abc12345"
    )
    assert verify_approval(task_id, step, expired_token) is False



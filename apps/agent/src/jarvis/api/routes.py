"""FastAPI REST and WebSocket Router."""

import json
import time

from fastapi import APIRouter, Depends, Header, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from jarvis.agent.executor import TaskExecutor
from jarvis.agent.planner import AgentPlanner
from jarvis.config.settings import get_settings
from jarvis.core.contracts import Command, CommandResult, CommandSource
from jarvis.core.router import CommandRouter
from jarvis.security.approval import generate_approval_token
from jarvis.storage.repositories.audit_repository import SQLiteAuditRepository
from jarvis.storage.repositories.task_repository import SQLiteTaskRepository
from jarvis.storage.sqlite import get_sqlite_manager
from jarvis.tools.registry import get_tool_registry

router = APIRouter(prefix="/api/v1")

command_router = CommandRouter()
agent_planner = AgentPlanner()
task_executor = TaskExecutor()
sqlite_manager = get_sqlite_manager()
task_repo = SQLiteTaskRepository(sqlite_manager)
audit_repo = SQLiteAuditRepository(sqlite_manager)


async def verify_api_auth(
    authorization: str | None = Header(None),
    x_jarvis_api_key: str | None = Header(None),
) -> None:
    """Verify local API authentication token when configured in AgentSettings."""
    settings = get_settings()
    expected_token = settings.api_auth_token
    if not expected_token:
        return

    provided = None
    if authorization and authorization.startswith("Bearer "):
        provided = authorization[7:].strip()
    elif x_jarvis_api_key:
        provided = x_jarvis_api_key.strip()

    if not provided or provided != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: invalid or missing API authentication token.",
        )


class CommandRequestPayload(BaseModel):
    raw_text: str
    source: CommandSource | None = CommandSource.TEXT_UI
    device_id: str | None = None


class StepApprovalPayload(BaseModel):
    step_id: str


@router.get("/health")
async def health_check():
    """Local Agent Health Check endpoint."""
    settings = get_settings()
    res = {
        "status": "healthy",
        "agent": "jarvis-local",
        "version": "0.2.0",
        "host": settings.local_host,
        "port": settings.local_port,
    }
    if settings.env == "development":
        res["api_auth_token"] = settings.api_auth_token
    return res


@router.post("/command", response_model=CommandResult, dependencies=[Depends(verify_api_auth)])
async def process_command(payload: CommandRequestPayload):
    """Process natural language user command."""
    cmd = Command(
        raw_text=payload.raw_text,
        source=payload.source or CommandSource.TEXT_UI,
        device_id=payload.device_id,
        created_at_ts=time.time(),
    )

    route_type, plan = command_router.route(cmd)
    if route_type == "agent_planner" or plan is None:
        registry = get_tool_registry()
        plan = await agent_planner.plan_command(cmd, registry.list_tools())

    result = await task_executor.execute_plan(plan)
    return result


@router.get("/tasks/{task_id}", dependencies=[Depends(verify_api_auth)])
async def get_task(task_id: str):
    """Retrieve task state and steps by task_id."""
    plan = task_repo.get_task_plan(task_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return plan.model_dump()


@router.post("/tasks/{task_id}/approve", response_model=CommandResult, dependencies=[Depends(verify_api_auth)])
async def approve_task_step(task_id: str, payload: StepApprovalPayload):
    """Approve a pending task step with HMAC approval token and resume execution."""
    plan = task_repo.get_task_plan(task_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")

    step = next((s for s in plan.steps if s.step_id == payload.step_id), None)
    if not step:
        raise HTTPException(status_code=404, detail=f"Step '{payload.step_id}' not found in task '{task_id}'.")

    risk_str = step.risk_level.value if hasattr(step.risk_level, "value") else str(step.risk_level)
    token = generate_approval_token(
        task_id=task_id,
        step_id=step.step_id,
        tool_id=step.tool_id,
        risk_level=risk_str,
        tool_input=step.tool_input,
    )
    step.approval_token = token
    plan.status = "in_progress"
    task_repo.save_task_plan(plan)

    result = await task_executor.execute_plan(plan)
    return result


@router.post("/tasks/{task_id}/reject", response_model=CommandResult, dependencies=[Depends(verify_api_auth)])
async def reject_task_step(task_id: str, payload: StepApprovalPayload):
    """Reject a pending task step and fail task execution."""
    plan = task_repo.get_task_plan(task_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")

    step = next((s for s in plan.steps if s.step_id == payload.step_id), None)
    if not step:
        raise HTTPException(status_code=404, detail=f"Step '{payload.step_id}' not found in task '{task_id}'.")

    step.status = "blocked"
    task_repo.update_step_result(step.step_id, "blocked", error_message="User denied permission.")
    plan.status = "failed"
    task_repo.update_task_status(task_id, "failed")

    return CommandResult(
        command_id=plan.command_id,
        task_id=plan.task_id,
        status="failed",
        summary=f"User rejected step '{step.step_id}'.",
        steps_executed=0,
        error_message="User denied permission.",
    )


@router.get("/audit", dependencies=[Depends(verify_api_auth)])
async def query_audit_logs(limit: int = 50):
    """Query recent audit events."""
    return audit_repo.query_events(limit=limit)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time task streaming WebSocket endpoint."""
    settings = get_settings()
    expected_token = settings.api_auth_token
    if expected_token:
        provided = websocket.query_params.get("token") or websocket.headers.get("x-jarvis-api-key")
        if not provided and websocket.headers.get("authorization"):
            auth_h = websocket.headers.get("authorization", "")
            if auth_h.startswith("Bearer "):
                provided = auth_h[7:].strip()
        if not provided or provided != expected_token:
            await websocket.close(code=1008, reason="Unauthorized")
            return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            cmd_text = payload.get("raw_text", "")
            if cmd_text:
                cmd = Command(
                    raw_text=cmd_text,
                    source=CommandSource.TEXT_UI,
                    created_at_ts=time.time(),
                )
                _route_type, plan = command_router.route(cmd)
                if plan is None:
                    registry = get_tool_registry()
                    plan = await agent_planner.plan_command(cmd, registry.list_tools())

                await websocket.send_json({"event": "plan_created", "plan": plan.model_dump()})
                result = await task_executor.execute_plan(plan)
                await websocket.send_json({"event": "task_completed", "result": result.model_dump()})
    except WebSocketDisconnect:
        pass

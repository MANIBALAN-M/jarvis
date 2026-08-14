"""FastAPI REST and WebSocket Router."""

import json
import time

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from jarvis.agent.executor import TaskExecutor
from jarvis.agent.planner import AgentPlanner
from jarvis.core.contracts import Command, CommandResult, CommandSource
from jarvis.core.router import CommandRouter
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


class CommandRequestPayload(BaseModel):
    raw_text: str
    source: CommandSource | None = CommandSource.TEXT_UI
    device_id: str | None = None


@router.get("/health")
async def health_check():
    """Local Agent Health Check endpoint."""
    return {
        "status": "healthy",
        "agent": "jarvis-local",
        "version": "0.1.0",
        "host": "127.0.0.1",
        "port": 8765,
    }


@router.post("/command", response_model=CommandResult)
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


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Retrieve task state and steps by task_id."""
    plan = task_repo.get_task_plan(task_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return plan.model_dump()


@router.get("/audit")
async def query_audit_logs(limit: int = 50):
    """Query recent audit events."""
    return audit_repo.query_events(limit=limit)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time task streaming WebSocket endpoint."""
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
                route_type, plan = command_router.route(cmd)
                if plan is None:
                    registry = get_tool_registry()
                    plan = await agent_planner.plan_command(cmd, registry.list_tools())

                await websocket.send_json({"event": "plan_created", "plan": plan.model_dump()})
                result = await task_executor.execute_plan(plan)
                await websocket.send_json({"event": "task_completed", "result": result.model_dump()})
    except WebSocketDisconnect:
        pass

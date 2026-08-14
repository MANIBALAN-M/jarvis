"""Integration tests for FastAPI REST & WebSocket routes."""

import pytest
from httpx import ASGITransport, AsyncClient

from jarvis.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_process_command_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {"raw_text": "system info"}
        res = await client.post("/api/v1/command", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["steps_executed"] >= 1


@pytest.mark.asyncio
async def test_audit_logs_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/api/v1/audit")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

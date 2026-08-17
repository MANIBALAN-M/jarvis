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
        assert data["version"] == "0.2.0"


def get_auth_headers() -> dict[str, str]:
    from jarvis.config.settings import get_settings
    token = get_settings().api_auth_token
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_process_command_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {"raw_text": "system info"}
        res = await client.post("/api/v1/command", json=payload, headers=get_auth_headers())
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["steps_executed"] >= 1


@pytest.mark.asyncio
async def test_audit_logs_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/api/v1/audit", headers=get_auth_headers())
        assert res.status_code == 200
        assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_approve_and_reject_task_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.post("/api/v1/tasks/nonexistent-id/approve", json={"step_id": "s1"}, headers=get_auth_headers())
        assert res.status_code == 404
        res_rej = await client.post("/api/v1/tasks/nonexistent-id/reject", json={"step_id": "s1"}, headers=get_auth_headers())
        assert res_rej.status_code == 404


@pytest.mark.asyncio
async def test_api_auth_token_protection(monkeypatch):
    from jarvis.config.settings import get_settings

    monkeypatch.setattr(get_settings(), "api_auth_token", "secret-bearer-123")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {"raw_text": "system info"}

        # 1. Unauthenticated request fails with 401
        res_unauth = await client.post("/api/v1/command", json=payload)
        assert res_unauth.status_code == 401

        # 2. Authenticated request with Bearer header succeeds with 200
        headers = {"Authorization": "Bearer secret-bearer-123"}
        res_auth = await client.post("/api/v1/command", json=payload, headers=headers)
        assert res_auth.status_code == 200

        # 3. Authenticated request with X-JARVIS-API-KEY header succeeds with 200
        key_headers = {"X-JARVIS-API-KEY": "secret-bearer-123"}
        res_key = await client.post("/api/v1/command", json=payload, headers=key_headers)
        assert res_key.status_code == 200


@pytest.mark.asyncio
async def test_cors_preflight():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        headers = {
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        }
        res = await client.options("/api/v1/health", headers=headers)
        assert res.status_code == 200
        assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"




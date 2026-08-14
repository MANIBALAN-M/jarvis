# JARVIS — Desktop Automation Agent Monorepo

> **Secure, Local-First, Cloud-Assisted Computer Automation Agent**  
> Version: `v0.1.0` (Phase 1 Complete)

---

## 🚀 Overview

JARVIS is a production-oriented desktop automation platform. The system processes natural language text or voice commands, creates multi-step task plans, evaluates security policies, executes sandboxed operating system tools, verifies outcomes, and records structured audit trails.

---

## 📋 Prerequisites

- **Python**: 3.11 or 3.12 (`python --version`)
- **Node.js**: v18+ LTS (`node --version`)
- **Rust**: Latest stable (`rustc --version`)

---

## 🛠️ Step-by-Step Setup & Running Guide

### Step 1: Open PowerShell and Navigate to Monorepo Root
```powershell
cd D:\Sample\jarvis
```

### Step 2: Create Python Virtual Environment
```powershell
python -m venv .venv
```

### Step 3: Activate Virtual Environment

- **From Repository Root (`D:\Sample\jarvis`):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **From Agent Subdirectory (`D:\Sample\jarvis\apps\agent`):**
  ```powershell
  ..\..\.venv\Scripts\Activate.ps1
  ```
- **To deactivate:**
  ```powershell
  deactivate
  ```

### Step 4: Install Dependencies from `requirements.txt`
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Install Agent Package in Editable Mode
```powershell
cd D:\Sample\jarvis\apps\agent
pip install -e ".[dev]"
```

### Step 6: Run Code Linter & Automated Test Suite
```powershell
# Run Ruff code linter
python -m ruff check src tests

# Run Pytest suite
python -m pytest -v
```

### Step 7: Launch Local Agent API Server
Start the local FastAPI server bound exclusively to `127.0.0.1:8765`:

```powershell
# From apps/agent directory:
uvicorn jarvis.main:app --host 127.0.0.1 --port 8765 --reload
```

---

## 🌐 API & WebSocket Endpoints (`127.0.0.1:8765`)

| Endpoint | Type | Description |
| :--- | :--- | :--- |
| `GET /health` | REST | Agent health check (`{"status": "healthy", "version": "0.1.0"}`) |
| `POST /api/v1/command` | REST | Submit natural language command payload |
| `GET /api/v1/tasks/{task_id}`| REST | Retrieve task status and step details |
| `GET /api/v1/audit` | REST | Query append-only audit event logs |
| `WS /api/v1/ws` | WebSocket | Real-time task step execution streaming |

### Example Command Request (PowerShell):
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8765/api/v1/command" -Method Post -ContentType "application/json" -Body '{"raw_text": "system info"}'
```

---

## 🛡️ Security & Architecture Principles

1. **Central Workspace Enforcement**: Filesystem and terminal `cwd` operations resolve strictly against trusted `AgentSettings.workspace_root`.
2. **HMAC Cryptographic Approval Proof**: Medium/high-risk actions (`ASK_USER`) require a HMAC-SHA256 token (`generate_approval_token`) before execution.
3. **Non-Blocking Async Execution**: Filesystem I/O and process launches run on dedicated threadpools via `asyncio.to_thread`.
4. **Tool-Specific Outcome Verification**: `OutcomeVerifier` checks file existence, size, exit codes, and process execution.
5. **User Error Sanitization**: Sanitizes raw Python stack traces into user-friendly error summaries.
6. **Audit Data Minimization**: Redacts passwords, tokens, secrets, and content fields in SQLite audit logs.

---

## 📂 Repository Layout

```
jarvis/
├── .venv/                      # Centralized Python virtual environment
├── requirements.txt            # Global project Python dependencies
├── LICENSE                     # MIT License
├── apps/
│   ├── desktop/                # Desktop Front-End (Tauri + React + TypeScript)
│   └── agent/                  # Local Python Runtime & Execution Engine
│       ├── pyproject.toml      # Package build metadata
│       ├── requirements.txt    # Agent dependencies
│       ├── src/jarvis/
│       │   ├── api/            # FastAPI REST & WebSocket routers
│       │   ├── core/           # Data contracts, Router, Error sanitization
│       │   ├── security/       # Policy Engine, HMAC Approval, Audit logger
│       │   ├── storage/        # SQLite persistence (`jarvis_local.db`)
│       │   └── tools/          # Controlled tools (system, apps, files, terminal)
│       └── tests/              # Automated test suite (16 tests)
├── services/
│   └── cloud-api/              # Cloud Control Plane (FastAPI for Cloud Run)
├── packages/                   # Shared Multi-Package Contracts
├── database/                   # Database DDL schemas & Alembic migrations
├── infrastructure/             # Docker, Cloud Run & Cloudflare manifests
├── JARVIS.md                   # Architecture & Roadmap documentation
├── ARCHITECTURE.md             # Complete Engineering Technical Specification
└── README.md                   # Setup & Running Guide (this file)
```

---

## 💻 Phase Execution Roadmap

- [x] **Phase 0 (v0.0.1)**: Monorepo layout, Pydantic type contracts, CI pipeline.
- [x] **Phase 1 (v0.1.0)**: Local agent server (`127.0.0.1:8765`), SQLite persistence, router, executor, verifier, controlled tools, HMAC security.
- [ ] **Phase 2 (v0.2.0)**: React + Tauri desktop shell, system tray, and approval popup UI.

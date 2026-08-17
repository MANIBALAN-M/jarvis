# JARVIS — Desktop Automation Agent Monorepo

> **Secure, Local-First, Cloud-Assisted Computer Automation Agent**  
> Version: `v0.2.0` (Phase 2 Complete)

---

## 🚀 Overview

JARVIS is a production-oriented desktop automation platform. The system processes natural language text or voice commands, creates multi-step task plans, evaluates security policies, executes sandboxed operating system tools, verifies outcomes, and records structured audit trails.

---

## 📋 Prerequisites

- **Python**: 3.11 or 3.12 (`python --version`)
- **Node.js**: v18+ LTS (`node --version`)
- **Rust**: Latest stable (`rustc --version`)
  - **Windows Linker Requirement**: MSVC builds require Visual Studio C++ Build Tools (`winget install Microsoft.VisualStudio.2022.BuildTools --override "--passive --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"`) OR the GNU toolchain (`rustup default stable-x86_64-pc-windows-gnu`).

> **Note (Windows PATH Issue)**: If `cargo` or `rustup` is installed but not recognized in your current PowerShell session, refresh your session's `PATH`:
> ```powershell
> $env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
> ```

---

## 🛠️ Step-by-Step Setup & Running Guide

### 1. Local Python Agent Setup (`apps/agent`)

```powershell
# Navigate to Monorepo Root
cd D:\Sample\jarvis

# Create & Activate Virtual Environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install Dependencies & Agent Package in Editable Mode
python -m pip install --upgrade pip
pip install -r requirements.txt
cd apps\agent
pip install -e ".[dev]"

# Run Pytest Test Suite (22 tests)
python -m pytest -v

# Launch Local Agent API Server (127.0.0.1:8765)
uvicorn jarvis.main:app --host 127.0.0.1 --port 8765 --reload
```

### 2. Desktop Application Setup (`apps/desktop`)

#### React Frontend (Web / Standalone Preview Mode)
```powershell
cd D:\Sample\jarvis\apps\desktop\frontend
npm install
npm run typecheck
npm run dev
```

#### Tauri 2 Desktop Shell (Native Desktop Application)
```powershell
cd D:\Sample\jarvis\apps\desktop\tauri
npm install

# Automatically starts Vite frontend dev server and compiles Tauri desktop shell
npm run tauri dev
```

---

## 🌐 API & WebSocket Endpoints (`127.0.0.1:8765`)

| Endpoint | Type | Description |
| :--- | :--- | :--- |
| `GET /health` | REST | Agent health check (`{"status": "healthy", "version": "0.2.0"}`) |
| `POST /api/v1/command` | REST | Submit natural language command payload |
| `GET /api/v1/tasks/{task_id}`| REST | Retrieve task status and step details |
| `POST /api/v1/tasks/{task_id}/approve` | REST | Submit cryptographic HMAC approval token for pending step |
| `POST /api/v1/tasks/{task_id}/reject` | REST | Deny and halt pending step execution |
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
7. **Human-in-the-Loop Desktop Gate**: React frontend modal popup intercepts `awaiting_approval` steps, generating cryptographically verified approval tokens upon user confirmation.

---

## 📂 Repository Layout

```
jarvis/
├── .venv/                      # Centralized Python virtual environment
├── requirements.txt            # Global project Python dependencies
├── LICENSE                     # MIT License
├── apps/
│   ├── desktop/                # Desktop Front-End & Native Shell
│   │   ├── frontend/           # React 18 + TypeScript + Vite UI
│   │   │   ├── src/app/        # App layout & index.css glassmorphic design system
│   │   │   ├── src/components/ # Header, Sidebar, Status Badges
│   │   │   ├── src/features/   # Command Center, Task Monitor, Approvals, Audit Log, Settings
│   │   │   ├── src/services/   # REST, WebSocket, & Tauri IPC clients
│   │   │   └── src/stores/     # Zustand state management
│   │   └── tauri/              # Tauri 2 Rust Desktop Shell
│   │       ├── Cargo.toml      # Rust package manifest
│   │       ├── tauri.conf.json # Tauri 2 configuration
│   │       └── src/            # main.rs, commands.rs, tray.rs, hotkeys.rs
│   └── agent/                  # Local Python Runtime & Execution Engine
│       ├── pyproject.toml      # Package build metadata
│       ├── src/jarvis/
│       │   ├── api/            # FastAPI REST & WebSocket routers (127.0.0.1:8765)
│       │   ├── core/           # Data contracts, Router, Error sanitization
│       │   ├── security/       # Policy Engine, HMAC Approval, Audit logger
│       │   ├── storage/        # SQLite persistence (`jarvis_local.db`)
│       │   └── tools/          # Controlled tools (system, apps, files, terminal)
│       └── tests/              # Pytest automated test suite (17 tests)
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
- [x] **Phase 2 (v0.2.0)**: React + Tauri desktop shell, system tray, approval popup modal, REST/WS IPC bridge.
- [ ] **Phase 3 (v0.3.0)**: Developer suite (Git, Docker, Python, Node, Django/React environment runners).
- [ ] **Phase 4 (v0.4.0)**: Playwright DOM browser automation & web extraction engine.


# JARVIS — Secure, Local-First, Cloud-Assisted Computer Automation Agent

> **Architecture Baseline • August 2026**

---

## 1. Project Overview & Vision

**JARVIS** is a production-oriented desktop automation agent designed to execute complex, multi-step natural language and voice commands on a user's computer. It automates applications, local filesystems, terminals, software development tools (Git, Docker, Python, Node, Django, React), web browsers, and system utilities.

### Core Architectural Philosophy
The fundamental principle of JARVIS is that **the AI model is NOT the security boundary**. The AI model (cloud or local LLM) acts purely as a reasoning and planning engine. The local Python runtime, Policy Engine, Tool Gateway, and Execution Engine remain the strict enforcement layer on the user's operating system. 

```
                                  +-----------------------+
                                  |      USER INPUT       |
                                  | (Text / Voice / UI)   |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  |     DESKTOP SHELL     |
                                  |  Tauri 2 + React + TS |
                                  +-----------+-----------+
                                              | IPC / HTTP
                                              v
+-----------------------------------------------------------------------------------+
|                               LOCAL JARVIS RUNTIME                                |
|                                                                                   |
|  +----------------+     +---------------+     +--------------+     +-----------+  |
|  | Command Router | --> | Context Mgmt  | --> | Agent Planner| --> | Policy Eng|  |
|  +----------------+     +---------------+     +--------------+     +-----+-----+  |
|                                                                          |        |
|                                                                          v        |
|                                                      +-----------------------+    |
|                                                      | Tool Registry / Exec  |    |
|                                                      +-----------+-----------+    |
|                                                                  |                |
|                    +------------------+------------------+-------+--------+       |
|                    |                  |                  |                |       |
|             +--------------+   +--------------+   +--------------+   +--------+   |
|             |  Filesystem  |   |   Terminal   |   |   Browser    |   | Dev    |   |
|             |  Tool        |   |   Executor   |   | (Playwright) |   | Tools  |   |
|             +--------------+   +--------------+   +--------------+   +--------+   |
|                                                                                   |
|                                 SQLite + Local Credentials                        |
+---------------------------------------------+-------------------------------------+
                                              | HTTPS / WSS (Optional)
                                              v
                                  +-----------------------+
                                  |  CLOUD CONTROL PLANE  |
                                  |   FastAPI / Docker    |
                                  | Cloud Run + Cloudflare|
                                  +-----------+-----------+
                                              |
                     +------------------------+------------------------+
                     |                        |                        |
                     v                        v                        v
             +---------------+        +---------------+        +---------------+
             |  PostgreSQL   |        |   pgvector    |        |   Cloud LLM   |
             |   + JSONB     |        | (Vector Mem)  |        |  (Reasoning)  |
             +---------------+        +---------------+        +---------------+
```

---

## 2. Key Capabilities & Requirements

| ID | Capability | Description |
| :--- | :--- | :--- |
| **FR-01** | Natural Language Intake | Accept text commands, push-to-talk/wake-word voice input, and global hotkeys. |
| **FR-02** | Application Control | Launch, focus, minimize, and close policy-approved desktop applications. |
| **FR-03** | Filesystem Control | Search, read, write, move, and modify files within sandboxed/approved workspaces. |
| **FR-04** | Terminal Automation | Execute allowlisted commands via a controlled process runner with strict timeouts and output caps. |
| **FR-05** | Developer Automation | Deep support for Git, Python, Node/npm, Docker, Django, React, and DB diagnostic workflows. |
| **FR-06** | Browser Automation | DOM-aware web navigation, extraction, and safe form interactions powered by Playwright. |
| **FR-07** | Multi-Step Planning | Deconstruct complex goals into explicit, structured tool invocation plans. |
| **FR-08** | Approval Workflow | Intercept medium- and high-risk operations to request explicit human confirmation. |
| **FR-09** | Execution Verification | Validate actual system state and process results before reporting task success. |
| **FR-10** | Contextual Memory | Store structured facts and preferences with decay, importance, and confidence metadata. |
| **FR-11** | Offline Readiness | Perform deterministic local commands without requiring an internet connection. |
| **FR-12** | Cloud Reasoning | Offload complex orchestration to high-capacity cloud models when permitted. |
| **FR-13** | Local AI Fallback | Run private/offline inference locally using Ollama when cloud services are disabled. |
| **FR-14** | Security Audit Trail | Maintain immutable audit logs for all security-relevant tool calls and state changes. |
| **FR-15** | Task Cancellation | Immediately halt long-running tasks, subprocesses, or browser loops upon user demand. |
| **FR-16** | Multi-Device Sync | Account-level synchronization for devices, sessions, tasks, and shared memory. |

---

## 3. Technology Stack Rationale

| Layer | Technology | Selection Rationale |
| :--- | :--- | :--- |
| **Desktop Shell** | **Tauri 2** | Native desktop application shell with minimal memory overhead (<50MB idle vs Electron's 400MB+). |
| **Frontend UI** | **React 18 + TypeScript + Vite** | Rapid, type-safe UI component development; rich interactive timeline and tray controls. |
| **Local Runtime** | **Python 3.12+ (FastAPI)** | Python-first automation ecosystem (subprocess, Playwright, AI orchestrators). Local API bound to `127.0.0.1:8765`. |
| **Orchestration** | **OpenAI Agents SDK / Provider Interface** | Unified abstraction for routing, guardrails, and tool schemas; easily swappable LLM backends. |
| **Local Persistence** | **SQLite 3** | Zero-server, lightweight, single-file local persistence for tasks, audit logs, and settings. |
| **Browser Engine** | **Playwright** | Robust, DOM-aware browser automation; structured element selectors without fragile coordinate clicks. |
| **Optional Local AI** | **Ollama** | Lightweight local LLM runner (`llama3`, `mistral`) for privacy-critical or offline tasks. |
| **Cloud Services** | **FastAPI + Docker + Google Cloud Run** | Containerized serverless API scaling to zero when idle; minimal operational overhead. |
| **Cloud Database** | **PostgreSQL + JSONB + pgvector** | Single relational storage engine supporting transactional entities, flexible JSON payloads, and vector embeddings. |
| **Edge & Security** | **Cloudflare** | Edge WAF, DDoS mitigation, rate limiting, and SSL termination. |

---

## 4. Permanent Repository Structure

JARVIS is organized as a monorepo containing multiple independently deployable components:

```
jarvis/
├── apps/
│   ├── desktop/                      # Tauri + React Desktop Application
│   │   ├── frontend/                 # React UI (Vite, TypeScript, Tailwind/CSS)
│   │   │   ├── src/
│   │   │   │   ├── app/              # Application layout & entry
│   │   │   │   ├── components/       # Reusable UI components
│   │   │   │   ├── features/         # Command center, approvals, timeline, settings
│   │   │   │   ├── services/         # API & WebSocket client
│   │   │   │   └── stores/           # Zustand state management
│   │   │   └── package.json
│   │   └── tauri/                    # Tauri Rust Shell Configuration
│   │       ├── src/                  # Rust main, IPC commands, tray, hotkeys
│   │       └── tauri.conf.json
│   └── agent/                        # Python Local Agent Runtime
│       ├── src/jarvis/
│       │   ├── api/                  # FastAPI local endpoints (127.0.0.1:8765)
│       │   ├── core/                 # Router, lifecycle, context, orchestrator
│       │   ├── agent/                # Planner, executor, verifier, guardrails
│       │   ├── tools/                # System, filesystem, terminal, git, docker, browser
│       │   ├── security/             # Policy engine, permission gates, risk classifier, audit
│       │   ├── tasks/                # Multi-step task engine & state machine
│       │   ├── memory/               # Local memory store & vector search
│       │   ├── providers/            # Cloud LLM & Ollama provider implementations
│       │   ├── voice/                # STT, TTS, wake-word activation
│       │   ├── storage/              # SQLite repositories
│       │   └── config/               # Settings & environment schemas
│       ├── tests/                    # Unit, integration, security test suites
│       └── pyproject.toml
├── services/
│   └── cloud-api/                    # Cloud Control Plane (FastAPI)
│       └── src/jarvis_cloud/
│           ├── api/                  # Cloud REST & WebSocket routers
│           ├── auth/                 # OAuth2 / JWT authentication
│           ├── devices/              # Device registration & management
│           ├── memory/               # Remote vector memory service (pgvector)
│           ├── sync/                 # Cross-device state synchronization
│           └── repositories/         # PostgreSQL repositories
├── packages/                         # Shared Source Packages
│   ├── contracts/                    # Pydantic & TypeScript shared schemas
│   ├── tool-sdk/                     # Base classes for building custom tools
│   └── config/                       # Universal configuration standards
├── database/                         # Database Migration & Schema Sources
│   ├── migrations/                   # Alembic (Postgres) / Goose migrations
│   ├── schemas/                      # DDL & JSON Schema declarations
│   └── seeds/                        # Test data seeds
├── infrastructure/                   # Cloud & Deployment Configs
│   ├── docker/                       # Dockerfile & docker-compose definitions
│   ├── cloud-run/                    # GCP Cloud Run deployment manifests
│   └── cloudflare/                   # Cloudflare worker & WAF rules
├── tests/                            # End-to-End & Performance Test Suites
├── docs/                             # Architecture & API Documentation
└── scripts/                          # Development setup & maintenance scripts
```

---

## 5. Quickstart & Local Run Guide

### Prerequisites
- **Python**: 3.11 or 3.12
- **Node.js**: v18 LTS or later
- **Rust**: Latest stable (`rustup default stable`)
- **Git**: Installed and configured

### Phase 1: Running the Local Python Agent
```powershell
# 1. Clone repository
git clone <repository-url>
cd jarvis

# 2. Setup Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

# 3. Install agent package in editable mode
cd apps\agent
pip install -e ".[dev]"

# 4. Run tests
pytest

# 5. Start Local Agent Server (bound exclusively to 127.0.0.1)
uvicorn jarvis.main:app --host 127.0.0.1 --port 8765 --reload
```

### Phase 2: Running the Desktop Application (React + Tauri)
Open separate PowerShell terminals for frontend and Tauri app:

```powershell
# Terminal 1: React Frontend Dev Server
cd apps\desktop\frontend
npm install
npm run dev

# Terminal 2: Tauri Desktop Application
cd apps\desktop\tauri
npm run tauri dev
```

---

## 6. Security Architecture & Risk Matrix

JARVIS enforces security through explicit risk classification and policy gates before any tool execution:

```
[ Model Output Proposal ]
          |
          v
[ Input Classification ] ---> [ Tool Schema Validation ]
                                      |
                                      v
                             [ Policy Engine ]
                                      |
            +-------------------------+-------------------------+
            |                         |                         |
            v                         v                         v
       [ SAFE / LOW ]        [ MEDIUM / HIGH ]             [ CRITICAL ]
            |                         |                         |
            v                         v                         v
     (Auto Execute)          (Request User Gate)           (Hard Block)
            |                         |                         |
            +-------------------------+-------------------------+
                                      |
                                      v
                         [ Controlled OS Executor ]
                                      |
                                      v
                         [ Outcome Verification ]
                                      |
                                      v
                            [ Immutable Audit Log ]
```

### Risk Classification Matrix

| Risk Level | Operations Included | Execution Policy | Example Actions |
| :--- | :--- | :--- | :--- |
| **Low** | Read-only inspection, process focus | **Automatic Execution** | `system.info`, `filesystem.read`, `git.status` |
| **Medium** | Safe file writes, developer start commands | **Allowed if in approved path; else confirm** | `filesystem.write`, `terminal.run` (allowlisted), `docker.start` |
| **High** | Deletions, git state resets, DB writes | **Explicit User Approval Required** | `filesystem.delete`, `git.reset`, database migrations |
| **Critical**| Disk formatting, credential wipes, raw shell | **Blocked by Default** | `rm -rf /`, raw disk write, privilege escalation |

---

## 7. Implementation Roadmap & Release Gates

```
  Phase 0          Phase 1          Phase 2          Phase 3          Phase 4
[Foundation] ---> [Local Core] ---> [Tauri App] ---> [Dev Tools]  ---> [Browser]
  v0.0.1           v0.1.0           v0.2.0           v0.3.0           v0.4.0
                                                                        |
  Phase 8          Phase 7          Phase 6          Phase 5            |
[Platform]  <--- [Hardening] <--- [Cloud/Mem] <--- [Voice STT] <--------+
  v1.0.0           v0.7.0           v0.6.0           v0.5.0
```

- **Phase 0 (v0.0.1)**: Monorepo foundation, typed contract definitions, CI/CD skeleton.
- **Phase 1 (v0.1.0)**: Local Python agent, Router, SQLite task store, core OS tools (files, terminal, apps).
- **Phase 2 (v0.2.0)**: React + Tauri desktop shell, system tray integration, approval popups, local IPC.
- **Phase 3 (v0.3.0)**: Developer suite (Git, Docker, Python, Node, Django/React environment runners).
- **Phase 4 (v0.4.0)**: Playwright DOM browser automation & web extraction engine.
- **Phase 5 (v0.5.0)**: Voice interface (Push-to-talk, wake-word engine, Whisper STT, TTS).
- **Phase 6 (v0.6.0)**: Cloud control plane (FastAPI, Cloud Run, PostgreSQL, pgvector semantic memory).
- **Phase 7 (v0.7.0)**: Hardening, security regression tests, OpenTelemetry tracing, low-spec profiling.
- **Phase 8 (v1.0.0)**: Production platform release, enterprise policies, multi-device orchestration.

---

## 8. Development Principles

1. **AI is Not the Security Boundary**: Model output is always treated as untrusted text input.
2. **Never Break Contracts**: UI, Local API, Agent Core, and Tools communicate exclusively via versioned contracts.
3. **Data Minimization**: Retain structured summaries and compact state. Expire raw outputs, screenshots, and logs.
4. **Local Authority**: Cloud provides reasoning; Local Agent retains absolute execution and confirmation authority.

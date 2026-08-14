# JARVIS Desktop Automation Agent — Comprehensive Architecture & Technical Blueprint

> **Baseline Specifications • August 2026**

---

## 1. Executive Architecture Principles

JARVIS is engineered as a **Secure, Local-First, Cloud-Assisted Desktop Automation Agent**. It bridges human intent (natural language text and voice commands) with deterministic desktop computer execution.

### Architectural Invariants
1. **The Model is NOT the Security Boundary**: Model predictions, LLM tool-use calls, and generated parameters are untrusted inputs. All actions must undergo schema validation, static policy checks, permission evaluation, human-in-the-loop gates, and sandboxed execution.
2. **Local Enforcement Authority**: Computer control, operating system calls, secret storage, policy checks, and local deterministic routing reside entirely on the user's local machine.
3. **Cloud-Assisted Reasoning Plane**: The cloud API provides high-capacity reasoning, optional LLM inference, multi-device synchronization, and semantic memory retrieval. The cloud *never* directly executes operating system calls on the user's PC.
4. **Data Minimization & Pruning**: Persist compact task state, execution summaries, and user-approved facts with importance/confidence/retention metadata. Raw terminal streams, transient DOM snapshots, and screenshots are purged automatically.
5. **Contract-Driven Decoupling**: Subsystems (UI, Agent Runtime, Tool Registry, Cloud API) communicate through typed, versioned contracts (Pydantic / TypeScript schemas). Phase implementations must extend through adapters, never by rewriting core contracts.

---

## 2. Full System Architecture & Boundary Diagram

```
+---------------------------------------------------------------------------------------------------------+
|                                             USER INTERFACE                                              |
|                                       (Tauri 2 + React + TypeScript)                                    |
|                                                                                                         |
|   +-----------------------+     +-----------------------+     +-----------------------+                 |
|   |  Command Center UI    |     |  Task Timeline View   |     | Approval Modal / Gate |                 |
|   +-----------+-----------+     +-----------+-----------+     +-----------+-----------+                 |
|               |                             |                             |                             |
|               +-----------------------------+-----------------------------+                             |
|                                             | IPC / HTTP (127.0.0.1:8765)                               |
+---------------------------------------------|-----------------------------------------------------------+
                                              v
+---------------------------------------------------------------------------------------------------------+
|                                         LOCAL PYTHON AGENT RUNTIME                                      |
|                                         (Python 3.12+ / FastAPI)                                        |
|                                                                                                         |
|  +-------------------+        +--------------------+        +---------------------+                     |
|  |  Command Ingress  | -----> |   Command Router   | -----> |   Context Manager   |                     |
|  +-------------------+        +---------+----------+        +----------+----------+                     |
|                                         |                              |                                |
|                                         v                              v                                |
|                               +--------------------+        +---------------------+                     |
|                               | Deterministic Exec |        |    Agent Planner    |                     |
|                               +--------------------+        +----------+----------+                     |
|                                                                        |                                |
|                                                                        v                                |
|  +-------------------+        +--------------------+        +---------------------+                     |
|  | Execution Engine  | <----- |   Policy Engine    | <----- |    Tool Registry    |                     |
|  +---------+---------+        +--------------------+        +---------------------+                     |
|            |                                                                                            |
|            +-------------------+-------------------+-------------------+-------------------+            |
|            |                   |                   |                   |                   |            |
|            v                   v                   v                   v                   v            |
|     +--------------+    +--------------+    +--------------+    +--------------+    +--------------+    |
|     |  Filesystem  |    |   Terminal   |    |  App Control |    |  Playwright  |    |  Dev Tools   |    |
|     |   Tools      |    |   Executor   |    |   Tool       |    |  Browser     |    | (Git/Docker) |    |
|     +--------------+    +--------------+    +--------------+    +--------------+    +--------------+    |
|            |                   |                   |                   |                   |            |
|            +-------------------+-------------------+-------------------+-------------------+            |
|                                        |                                                                |
|                                        v                                                                |
|                             +----------------------+                                                    |
|                             | Verification Engine  |                                                    |
|                             +----------+-----------+                                                    |
|                                        |                                                                |
|                                        v                                                                |
|                             SQLite Local Database                                                       |
|                             (Tasks, Steps, Audits)                                                      |
+----------------------------------------+----------------------------------------------------------------+
                                         | HTTPS / WebSockets (TLS)
                                         v
+---------------------------------------------------------------------------------------------------------+
|                                           CLOUD CONTROL PLANE                                           |
|                                    (Google Cloud Run + Cloudflare Edge)                                 |
|                                                                                                         |
|   +---------------------+   +---------------------+   +---------------------+   +--------------------+  |
|   | Auth & Identity API |   | Device Sync Engine  |   | Cloud Task Store    |   | Vector Memory API  |  |
|   +----------+----------+   +----------+----------+   +----------+----------+   +---------+----------+  |
|              |                         |                         |                        |             |
|              +-------------------------+-------------------------+------------------------+             |
|                                                |                                                        |
|                                                v                                                        |
|                                PostgreSQL + JSONB + pgvector                                            |
|                                                |                                                        |
|                                                v                                                        |
|                                     Cloud LLM Provider (API)                                            |
+---------------------------------------------------------------------------------------------------------+
```

---

## 3. Functional Subsystem Breakdown

### 1. User Interface Layer
- **Tauri Shell**: Provides native OS tray integration, global keyboard shortcut hooks (`Ctrl+Space`), native desktop notifications, and secure IPC bridges.
- **React Frontend**: Rendered via Vite. Manages user conversation state, real-time task execution timelines, permission approval popups, settings, and memory management UI.

### 2. Command Ingress & Router
- **Command Ingress**: Receives input streams from text chat, voice STT transcripts, hotkeys, or scheduled triggers.
- **Command Router**: Evaluates input intent. Routes straightforward commands (e.g., "open VS Code", "git status") directly to deterministic execution functions without incurring LLM latency or cost. Passes complex goals to the Agent Planner.

### 3. Context Manager & Memory Service
- **Context Manager**: Constructs compact prompt contexts. Selects relevant system environment metadata, active project paths, allowed tools, and top-k semantic memories.
- **Memory Service**: Manages local SQLite memory cache and synchronizes with cloud `pgvector`. Facts are annotated with `importance_score`, `confidence`, `last_used_at`, and `ttl_seconds`.

### 4. Agent Planner & Tool Registry
- **Agent Planner**: Uses the Provider Abstraction (supporting OpenAI SDK or Ollama) to translate natural language goals into a structured, typed execution plan (DAG of tool steps).
- **Tool Registry**: Maintains typed tool declarations. Exposes JSON Schema contracts for input parameters, risk classifications, and expected response payloads.

### 5. Policy, Permission & Audit Engine
- **Policy Engine**: Enforces security policies before any tool call runs. Validates workspace path roots, argument allowlists, shell token sanitization, and execution boundaries.
- **Permission Engine**: Triggers UI confirmation popups for medium/high-risk actions.
- **Audit Engine**: Writes structured, append-only logs for every tool invocation, input payload summary, user response, exit code, and security event.

### 6. Execution & Verification Engines
- **Execution Engine**: Executes validated tools using isolated subprocesses, enforced timeouts, bounded output buffers, and cancellation token monitors.
- **Verification Engine**: Validates task success by checking actual system outcomes (e.g., HTTP status 200, process listening on port, file exists on disk) rather than assuming model planning success.

---

## 4. Subsystem & Folder Structure Mapping

```
jarvis/
├── apps/
│   ├── desktop/                         # Desktop Front-End Application
│   │   ├── frontend/                    # React 18 + TS UI
│   │   │   ├── src/
│   │   │   │   ├── app/                 # Root App layout, providers, themes
│   │   │   │   ├── components/          # Buttons, Cards, Inputs, Modals
│   │   │   │   ├── features/
│   │   │   │   │   ├── command-center/  # Chat interface & prompt bar
│   │   │   │   │   ├── task-monitor/    # Live step-by-step task execution DAG
│   │   │   │   │   ├── approvals/       # Human approval confirmation gates
│   │   │   │   │   ├── memory/          # Memory inspection & pruning UI
│   │   │   │   │   └── settings/        # API key, local model, & policy settings
│   │   │   │   ├── services/            # Axios API & WebSocket streaming client
│   │   │   │   ├── stores/              # Zustand global state stores
│   │   │   │   └── types/               # TypeScript interface contracts
│   │   │   └── package.json
│   │   └── tauri/                       # Native Desktop Shell
│   │       ├── src/
│   │       │   ├── main.rs              # Tauri Rust entrypoint
│   │       │   ├── commands.rs          # Native IPC command handlers
│   │       │   ├── tray.rs              # System tray menu & events
│   │       │   └── hotkeys.rs           # Global shortcut listener
│   │       └── tauri.conf.json
│   └── agent/                           # Python Agent Local Runtime
│       ├── src/jarvis/
│       │   ├── api/                     # FastAPI local API server (127.0.0.1:8765)
│       │   ├── core/                    # Lifecycle, router, context, orchestrator
│       │   ├── agent/                   # Planner, executor, verifier, guardrails
│       │   ├── tools/                   # Tool implementations
│       │   │   ├── system/              # Process, CPU, application launcher
│       │   │   ├── filesystem/          # Sandboxed search, read, write, edit
│       │   │   ├── terminal/            # Controlled command executor
│       │   │   ├── git/                 # Repository status, diff, commit, log
│       │   │   ├── docker/              # Container status, logs, start/stop
│       │   │   └── browser/             # Playwright DOM interaction engine
│       │   ├── security/                # Policy engine, permission gates, audit log
│       │   ├── tasks/                   # Task state machine & async execution
│       │   ├── memory/                  # Memory SQLite store & vector client
│       │   ├── providers/               # OpenAI & Ollama LLM provider adapters
│       │   ├── voice/                   # Audio recording, wake-word, Whisper STT, TTS
│       │   ├── storage/                 # SQLite repository implementations
│       │   └── config/                  # Pydantic environment & app settings
│       ├── tests/                       # Pytest unit, integration & security tests
│       └── pyproject.toml
├── services/
│   └── cloud-api/                       # Google Cloud Run FastAPI Backend
│       └── src/jarvis_cloud/
│           ├── api/                     # REST routers for auth, sync, tasks
│           ├── auth/                    # OAuth2 / JWT authentication service
│           ├── devices/                 # Device token registration & pairing
│           ├── memory/                  # Remote vector storage & query engine
│           ├── sync/                    # WebSocket real-time state synchronizer
│           └── repositories/            # SQLAlchemy / AsyncPG Postgres repositories
├── packages/                            # Shared Multi-Package Contracts
│   ├── contracts/                       # Shared Pydantic / TypeScript data models
│   ├── tool-sdk/                        # Custom tool SDK base interfaces
│   └── config/                          # Shared linting & formatting standards
├── database/                            # Schema Migrations & Storage Definitions
│   ├── migrations/                      # Postgres Alembic database migration scripts
│   ├── schemas/                         # SQLite & Postgres DDL declarations
│   └── seeds/                           # Development environment seed data
├── infrastructure/                      # Deployment Configurations
│   ├── docker/                          # Cloud API Dockerfile & docker-compose
│   ├── cloud-run/                       # GCP Cloud Run deployment YAML configs
│   └── cloudflare/                      # Cloudflare WAF & Worker scripts
└── docs/                                # Project Architecture & Specifications
```

---

## 5. Tool Contract Specifications

Tools in JARVIS are strongly typed, contract-governed objects. Tools **never** accept arbitrary shell strings generated by models without schema isolation.

### Standard Tool Schema Pattern (Pydantic)

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Dict, Any

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ToolExecutionResult(BaseModel):
    status: str = Field(..., description="'success', 'denied', 'failed', or 'error'")
    output_summary: str = Field(..., description="Compact summary for LLM context window")
    full_output: Optional[str] = Field(None, description="Full output stored locally/temp")
    exit_code: int = Field(0, description="Process exit code")
    truncated: bool = Field(False, description="Whether output exceeded max_bytes")
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Example Tool Contract: filesystem.read_file
class ReadFileInput(BaseModel):
    file_path: str = Field(..., description="Absolute or workspace-relative target file path")
    max_bytes: int = Field(64000, ge=1, le=500000, description="Maximum bytes to read")
    start_line: Optional[int] = Field(1, ge=1, description="1-indexed line number to begin reading")
    end_line: Optional[int] = Field(None, ge=1, description="1-indexed line number to stop reading")
```

### Core Recommended Initial Tools

| Tool ID | Input Schema Summary | Risk Level | Sandbox / Policy Requirement |
| :--- | :--- | :--- | :--- |
| `system.info` | None | `Low` | Read-only OS stats. |
| `application.open` | `app_name: str, args: list` | `Low` | Must match approved application allowlist. |
| `filesystem.search` | `query: str, root_dir: str` | `Low` | `root_dir` must be within approved workspace roots. |
| `filesystem.read` | `file_path: str, max_bytes: int` | `Low` | Path traversal prevention (`..` checks). Bounded read. |
| `filesystem.write` | `file_path: str, content: str` | `Medium` | Write within workspace. Trigger confirmation if replacing non-repo files. |
| `terminal.run` | `command: str, args: list, cwd: str` | `Medium` | Command binary must exist in allowlist. Argument sanitization. |
| `git.status` | `repo_path: str` | `Low` | Read-only git workspace check. |
| `git.commit` | `repo_path: str, message: str` | `Medium` | Local git tree state modification. |
| `docker.logs` | `container_name: str, tail: int` | `Low` | Read-only log extraction. |
| `docker.start` | `service_name: str` | `Medium` | Service name allowlist validation. |
| `browser.navigate` | `url: str` | `Low/Medium` | Protocol restriction (HTTPS only). Domain policy filter. |
| `browser.interact` | `action: str, selector: str, value: str` | `Medium` | DOM-aware interaction. Web text treated as untrusted context. |

---

## 6. Database Architecture & Data Minimization

### Storage Dual Engine Design
- **Local Engine (User PC)**: **SQLite 3**. Zero installation overhead, instant response, low memory footprint. Holds active tasks, step states, local audit events, and cached app settings.
- **Cloud Engine (Cloud Run)**: **PostgreSQL 16 + JSONB + pgvector**. Manages multi-device users, device registrations, cloud task history, and semantic memory vectors.

```
                  +-----------------------------------+
                  |        STORAGE MINIMIZATION       |
                  +-----------------+-----------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
[ LOCAL PERSISTENCE: SQLite ]                   [ CLOUD PERSISTENCE: PostgreSQL ]
• Active tasks & step states                    • User identities & registered devices
• Append-only local audit logs                  • Long-term structured task records
• Ephemeral operational cache                   • JSONB flexible payload dumps
• Configs & local secrets (OS Keychain)          • pgvector semantic memory embeddings
```

### Storage Minimization & Data Retention Strategy

| Data Type | Primary Storage | Retention Policy | Minimization Action |
| :--- | :--- | :--- | :--- |
| **Tasks & Steps** | SQLite (Local) / Postgres (Cloud) | 30 to 90 Days | Store compact step summaries rather than full raw LLM chats. |
| **Tool Outputs** | Temp File / Local SQLite | 7 Days | Truncate outputs at 64KB max; summarize long text streams. |
| **Screenshots** | Temp Disk Storage | 24 Hours | Captured exclusively on-demand. Discarded immediately after execution. |
| **Terminal Output** | Temp Local Log | 48 Hours | Buffer raw streams; persist only exit codes and 50-line tail excerpts. |
| **User Memory** | SQLite + pgvector | Persistent until expired | Annotate facts with `importance`, `confidence`, `last_used`, and decay scores. |
| **Secrets & Tokens**| OS Credential Store (Keyring) | Permanent | **NEVER** write secrets to SQLite, Postgres, logs, or LLM contexts. |

---

## 7. Agent Execution Lifecycle & Sequence

```
USER                REACTION UI         LOCAL AGENT         POLICY ENGINE         LOCAL OS
  |                      |                   |                    |                  |
  |--- 1. Send Command ->|                   |                    |                  |
  |    ("Start HMS dev") |--- 2. Post Command|                    |                  |
  |                      |---> (127.0.0.1)   |                    |                  |
  |                      |                   |--- 3. Classify     |                  |
  |                      |                   |    Intent          |                  |
  |                      |                   |--- 4. Generate Plan|                  |
  |                      |                   |    (Tool DAG)      |                  |
  |                      |                   |                    |                  |
  |                      |                   |--- 5. For each Tool|                  |
  |                      |                   |       Invocation ->|                  |
  |                      |                   |                    |-- 6. Evaluate    |
  |                      |                   |                    |   Policy Path    |
  |                      |<-- 7. Confirm (If Medium/High Risk) ---|                  |
  |--- 8. Confirm Click -|                   |                    |                  |
  |    ("Allow Action") -|------------------>|                    |                  |
  |                      |                   |                    |-- 9. Pass Gate ->|
  |                      |                   |---------------------------------------|-- 10. Execute Tool
  |                      |                   |                                       |       (Subprocess)
  |                      |                   |<--------------------------------------|-- 11. Tool Outcome
  |                      |                   |--- 12. Run Verification --------------|-- 13. System Check
  |                      |                   |--- 14. Audit Record -> SQLite         |
  |                      |<-- 15. Stream ----|
  |                      |    Timeline Output|
```

---

## 8. Phase-by-Phase Technical Blueprint

```
+-------------------------------------------------------------------------------------------------------+
| PHASE 0: FOUNDATION (v0.0.1)                                                                          |
| • Establish monorepo structure: apps/desktop, apps/agent, packages/*, database/, infrastructure/     |
| • Define Pydantic base contracts for Commands, Tool Schemas, Policy Rules, and Verification Results   |
| • Setup Python dev environment, pytest suite, ESLint/TypeScript configurations, and GitHub Actions CI  |
+-------------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+-------------------------------------------------------------------------------------------------------+
| PHASE 1: LOCAL AGENT CORE (v0.1.0)                                                                    |
| • Build FastAPI agent server bound exclusively to 127.0.0.1:8765                                     |
| • Implement Router, Planner, SQLite Task Engine, Policy Engine, and Audit Logger                     |
| • Build core deterministic tools: filesystem.read/write, terminal.run, application.open               |
+-------------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+-------------------------------------------------------------------------------------------------------+
| PHASE 2: DESKTOP APPLICATION (v0.2.0)                                                                 |
| • Develop React 18 + TypeScript frontend using Vite                                                   |
| • Scaffold Tauri 2 Rust desktop shell with system tray, hotkeys (Ctrl+Space), and IPC bridge          |
| • Implement approval popup modal for intercepting medium/high-risk tool actions                       |
+-------------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+-------------------------------------------------------------------------------------------------------+
| PHASE 3: DEVELOPER AUTOMATION SUITE (v0.3.0)                                                          |
| • Add specialized developer tool modules: Git, Docker, Python virtualenv, Node/npm, Django, React    |
| • Implement workspace path allowlists and developer task verification checks                          |
+-------------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+-------------------------------------------------------------------------------------------------------+
| PHASE 4: BROWSER AUTOMATION ENGINE (v0.4.0)                                                           |
| • Integrate Playwright for headless/headful DOM-aware web navigation                                  |
| • Enforce domain permission policies and treat web contents strictly as untrusted data inputs         |
+-------------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+-------------------------------------------------------------------------------------------------------+
| PHASE 5: VOICE INTERFACE (v0.5.0)                                                                     |
| • Add push-to-talk microphone ingress and wake-word activation engine                                 |
| • Integrate Whisper STT for local/cloud transcription and TTS audio playback responses                 |
+-------------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+-------------------------------------------------------------------------------------------------------+
| PHASE 6: CLOUD CONTROL PLANE & MEMORY (v0.6.0)                                                        |
| • Deploy FastAPI cloud API to Google Cloud Run behind Cloudflare WAF                                  |
| • Setup PostgreSQL + JSONB + pgvector database for user account sync and semantic memory retrieval    |
+-------------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+-------------------------------------------------------------------------------------------------------+
| PHASE 7 & 8: HARDENING & PRODUCTION PLATFORM (v0.7.0 -> v1.0.0)                                      |
| • Execute security regression testing, prompt-injection defense validation, OpenTelemetry tracing   |
| • Package self-contained Tauri production installers (.msi / .exe) with auto-update capabilities      |
+-------------------------------------------------------------------------------------------------------+
```

---

## 9. Security & Hardening Architecture

1. **Path Traversal Defenses**: All filesystem operations resolve target paths against approved workspace root lists using strict path normalization. Operations outside approved workspaces are rejected automatically.
2. **Command Injection Prevention**: Terminal execution tools reject raw shell invocation strings (e.g., `cmd /c` or `bash -c`) whenever possible. Executables are passed as distinct argument lists to `subprocess.Popen` without `shell=True`.
3. **Secret Isolation**: API tokens, private keys, and passwords are retrieved at execution time directly from the native Windows Credential Manager or macOS Keychain by the local tool runtime. Credentials are stripped from LLM prompts and task logs.
4. **Prompt Injection Mitigation**: File contents, DOM text, and web page content are wrapped in strict data-boundary tags (e.g., `<untrusted_content>`) in LLM prompts. Web text is never permitted to modify systemic tool permissions or policy rules.
5. **Output Bounding**: Terminal command streams and file reads enforce strict byte limits (default: 64KB). Overflows set a `truncated=true` flag and truncate content safely.

---

## 10. Performance Strategy for Lower-End Systems

- **No Always-On Inference**: Idle state relies exclusively on lightweight event listeners and tray processes. Continuous vision/screen-scraping or continuous LLM polling loops are forbidden.
- **Deterministic Shortcut Bypass**: Known routine requests (e.g., "Check git status", "Open VS Code") execute directly in <20ms via local Python handlers, completely bypassing LLM inference calls.
- **On-Demand Vision**: Screen captures and DOM snapshots are generated strictly when requested for a specific step and immediately freed from memory after processing.
- **Scale-to-Zero Cloud Backend**: The Cloud Run container scales to zero instances when idle, minimizing infrastructure costs while maintaining rapid cold-start capabilities.

---

## 11. CI/CD Pipeline & Development Commands

### Local Verification Commands (PowerShell)

```powershell
# 1. Run Python Unit & Security Tests
cd apps\agent
pytest --maxfail=1 --disable-warnings -v

# 2. Type Check Python Agent
mypy src/jarvis

# 3. Lint & Type Check React Frontend
cd ..\desktop\frontend
npm run lint
npm run typecheck

# 4. Build Desktop Tauri Application
cd ..\tauri
npm run tauri build
```

### GitHub Actions Workflow Structure (`.github/workflows/`)
- `agent-ci.yml`: Python linting (Ruff), type checking (Mypy), and Pytest execution.
- `frontend-ci.yml`: Node.js dependency installation, ESLint, TypeScript check, and Vite build test.
- `cloud-api.yml`: Cloud API container build validation, migration testing, and Google Cloud Run deployment.
- `release.yml`: Multi-platform Tauri installer packaging (`.exe`, `.msi`, `.dmg`, `.AppImage`).

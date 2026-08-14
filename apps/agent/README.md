# JARVIS Local Agent Core (`apps/agent`)

> Version: `v0.1.0` (Phase 1 Complete)

Local Agent Core runtime, FastAPI server (`127.0.0.1:8765`), SQLite task engine, Policy & Security Engine, Command Router, Task Executor, Outcome Verifier, and controlled tools suite.

---

## ⚡ Quick Running Commands

### 1. Activate Virtual Environment
```powershell
# From D:\Sample\jarvis\apps\agent
..\..\.venv\Scripts\Activate.ps1
```

### 2. Install Package Dependencies
```powershell
pip install -e ".[dev]"
```

### 3. Run Code Linter & Unit Tests
```powershell
# Run Ruff code linter
python -m ruff check src tests

# Run Pytest suite (16 tests)
python -m pytest -v
```

### 4. Launch Local Agent API Server
```powershell
uvicorn jarvis.main:app --host 127.0.0.1 --port 8765 --reload
```

---

## 🛡️ Architecture & Security Features

- **Central Workspace Enforcement**: Sandboxing via `is_path_safe` tied to `AgentSettings.workspace_root`.
- **Terminal `cwd` Boundary**: Path safety checks for process execution working directories.
- **HMAC Cryptographic Approval Proof**: Token-based validation (`verify_approval`) for `ASK_USER` policy decisions.
- **Outcome Verification**: `OutcomeVerifier` checks file existence, size, exit codes, and execution outcomes.
- **Error Sanitization**: Exposes clean summaries (`sanitize_user_error`) instead of raw stack traces.
- **Audit Minimization**: Data redacting for passwords, secrets, and content in SQLite logs.

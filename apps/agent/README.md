# JARVIS Local Agent Core (`apps/agent`)

This sub-package contains the Python local runtime, Policy Engine, Command Router, and Execution Engine for JARVIS.

---

## ⚡ How to Run & Test from `apps/agent`

### 1. Activate the Root Virtual Environment
Since `.venv` is located at the repository root (`../../.venv`), activate it using relative pathing:

```powershell
# From D:\Sample\jarvis\apps\agent
..\..\.venv\Scripts\Activate.ps1
```

### 2. Install Package Dependencies
```powershell
pip install -e ".[dev]"
```

### 3. Run Pytest Suite
```powershell
python -m pytest -v
```

### 4. Package Structure
- `src/jarvis/config/`: Settings & environment models.
- `src/jarvis/core/`: `Command`, `TaskPlan`, `PolicyResult` data contracts.
- `src/jarvis/providers/`: LLM provider interfaces (`BaseLLMProvider`).
- `src/jarvis/security/`: Policy Engine (`BasePolicyEngine`) and Risk Classifier.
- `src/jarvis/tools/`: `BaseTool` & `ToolExecutionResult`.
- `tests/`: Automated unit tests.

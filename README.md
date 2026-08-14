# JARVIS — Desktop Automation Agent Monorepo

> **Secure, Local-First, Cloud-Assisted Computer Automation Agent**  
> Version: `v0.0.1-foundation` (Phase 0)

---

## 📋 Prerequisites

Before starting, ensure you have the following installed on your machine:
- **Python**: 3.11 or 3.12 (`python --version`)
- **Node.js**: v18+ LTS (`node --version`)
- **Rust**: Latest stable (`rustc --version`)

---

## 🛠️ Step-by-Step Installation & Running Guide

Follow these exact steps to set up and run JARVIS on your computer:

### Step 1: Open PowerShell and Navigate to Repository Root
```powershell
cd D:\Sample\jarvis
```

### Step 2: Create Python Virtual Environment
Create the centralized virtual environment `.venv`:
```powershell
python -m venv .venv
```

### Step 3: Activate Virtual Environment

Depending on your current working directory in terminal:

- **If you are at Root (`D:\Sample\jarvis`):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **If you are inside Agent folder (`D:\Sample\jarvis\apps\agent`):**
  ```powershell
  ..\..\.venv\Scripts\Activate.ps1
  ```
- **To deactivate at any time:**
  ```powershell
  deactivate
  ```

*(You will see `(.venv)` appear on the left side of your PowerShell prompt when activated.)*

### Step 4: Upgrade `pip`
```powershell
python -m pip install --upgrade pip
```

### Step 5: Install Dependencies using `requirements.txt`
Install all required packages from `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### Step 6: Install Agent Package in Editable Mode
Install the local agent package so Python can resolve imports (`jarvis` package):
```powershell
cd D:\Sample\jarvis\apps\agent
pip install -e ".[dev]"
```

### Step 7: Run Automated Test Suite
Verify that all Pydantic contracts, policies, and base classes pass tests:
```powershell
python -m pytest -v
```

---

## 📂 Monorepo Repository Structure

```
jarvis/
├── .venv/                      # Centralized Python virtual environment
├── requirements.txt            # Global project Python dependencies
├── apps/
│   ├── desktop/                # Desktop Front-End (Tauri + React + TypeScript)
│   │   ├── frontend/           # React 18 UI components & state
│   │   └── tauri/              # Tauri Rust native window shell
│   └── agent/                  # Local Python Runtime & Execution Engine
│       ├── requirements.txt    # Agent specific dependencies
│       ├── pyproject.toml      # Agent package build metadata
│       ├── src/jarvis/         # Main Python source package
│       │   ├── config/         # Agent settings (127.0.0.1:8765)
│       │   ├── core/           # Data Contracts, Router, Lifecycle
│       │   ├── providers/      # LLM Provider Abstractions (OpenAI, Ollama)
│       │   ├── security/       # Policy Engine & Risk Classifier
│       │   └── tools/          # Tool Registry & Execution Engine
│       └── tests/              # Pytest unit & integration tests
├── services/
│   └── cloud-api/              # Cloud Control Plane (FastAPI for Cloud Run)
├── packages/                   # Shared Multi-Package Contracts
│   ├── contracts/              # Shared Pydantic data models
│   ├── tool-sdk/               # Custom Tool SDK base interfaces
│   └── config/                 # Security, linting & styling standards
├── database/                   # Database DDL schemas & Alembic migrations
├── infrastructure/             # Docker, Cloud Run & Cloudflare manifests
├── JARVIS.md                   # Architecture & Roadmap documentation
├── ARCHITECTURE.md             # Complete Engineering Technical Specification
└── README.md                   # Complete Setup & Running Guide (this file)
```

---

## 💻 Phase Roadmap Summary

1. **Phase 0 (Foundation - Complete)**: Monorepo layout, Pydantic type contracts, policy engine base, `requirements.txt`, 100% test pass.
2. **Phase 1 (Local Agent Core - Next)**: FastAPI server on `127.0.0.1:8765`, SQLite task store, local tools (`filesystem`, `terminal`, `apps`).
3. **Phase 2 (Desktop UI)**: React frontend + Tauri desktop shell with tray & risk approval popups.

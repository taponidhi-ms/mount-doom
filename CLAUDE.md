# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mount Doom is a fullstack AI agent simulation platform for multi-agent conversations using Azure AI Projects and Cosmos DB. The system enables persona generation, conversation simulation, and transcript parsing.

**Key Technologies:**
- Backend: FastAPI (Python 3.9+), Azure AI Projects, Azure Cosmos DB
- Frontend: Next.js 15, TypeScript, Ant Design
- Authentication: Azure DefaultAzureCredential (automatic token refresh)

**Documentation Structure:**
- This file contains essential project information and critical policies
- Detailed documentation is organized in `.claude/rules/` directory:
  - `backend/` - Backend architecture, conventions, API patterns, Azure integration
  - `frontend/` - Frontend architecture and conventions
  - `database.md` - Database architecture and patterns
  - `features.md` - All 9 features documentation
  - `logging.md` - Logging configuration and best practices

## Documentation Update Policy

**CRITICAL: Always update documentation BEFORE committing code changes.**

### Workflow for Code Changes

When making code changes, follow this workflow:

1. **Make code changes** - Implement the feature, bug fix, or improvement
2. **Update documentation** - Update all relevant documentation files (see below)
3. **Stage files** - Add both code and documentation files to git staging
4. **Create commit** - Commit with a message documenting both code and documentation changes

**NEVER commit code changes without updating documentation first.**

### Documentation Files to Update

Before creating any git commit, you MUST update the following documentation files to reflect your changes:

1. **README files** - Update if making user-facing changes:
   - `README.md` (root) - New features, setup changes, architecture overview
   - `backend/README.md` - Backend API changes, new endpoints, configuration
   - `frontend/README.md` - Frontend features, component changes, UI updates

2. **CLAUDE.md** (this file) - Update if making changes to:
   - Project overview
   - Development commands
   - Critical policies (Server Management, Python venv, Documentation Update Policy)
   - Environment configuration

3. **`.claude/rules/` files** - Update relevant rule files when making changes to:
   - Architecture (`backend/architecture.md` or `frontend/architecture.md`)
   - Conventions (`backend/conventions.md` or `frontend/conventions.md`)
   - API patterns (`backend/api-patterns.md`)
   - Azure integration (`backend/azure-integration.md`)
   - Features (`features.md`)
   - Database patterns (`database.md`)
   - Logging (`logging.md`)

### Commit Message Format

- Include what was changed AND which documentation was updated
- Example: `feat: Add multi-agent download feature\n\nUpdated features.md and README.md with multi-agent download documentation`

### Examples

**Good workflow:**
```
1. Add conversation limit feature to backend and frontend
2. Update .claude/rules/features.md with limit feature documentation
3. Update README.md with multi-agent download instructions
4. Update backend/README.md with new API endpoints
5. git add [code files] .claude/rules/features.md README.md backend/README.md
6. git commit -m "feat: Add conversation limits..."
```

**Bad workflow (DO NOT DO THIS):**
```
1. Add conversation limit feature to backend and frontend
2. git add [code files]
3. git commit -m "feat: Add conversation limits..."
4. [Documentation never updated or updated in separate commit]
```

## Development Commands

### Backend

```bash
# Setup
cd backend
python -m venv .venv

# Activate virtual environment:
# Linux/Mac:
source .venv/bin/activate

# Windows PowerShell (requires execution policy):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser  # One-time setup
.\.venv\Scripts\Activate.ps1

# Windows CMD:
.\.venv\Scripts\activate.bat

# Windows Git Bash:
source .venv/Scripts/activate

# Install dependencies and configure
pip install -r requirements.txt
cp .env.example .env  # Configure Azure credentials

# Run development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Or: python app/main.py

# API Documentation
# http://localhost:8000/docs (Swagger)
# http://localhost:8000/redoc (ReDoc)
```

### Frontend

```bash
# Setup
cd frontend
npm install
cp .env.local.example .env.local  # Set NEXT_PUBLIC_API_URL

# Run development server
npm run dev  # http://localhost:3000

# Build and run production
npm run build
npm start

# Lint
npm run lint
```

## Critical Policies

### Server Management Policy

**CRITICAL: Never start servers as background tasks**

- **DO NOT** run backend or frontend servers using background task execution (run_in_background parameter)
- **DO NOT** use bash commands with `&` to background the server processes
- The user will start both servers manually in separate terminal windows
- This allows the user to monitor live logs and have direct control over server processes
- Only perform dependency installation, code changes, and other non-server tasks

**Examples of what NOT to do:**
```bash
# Bad: Starting server in background
cd backend && .venv/Scripts/python.exe -m uvicorn app.main:app --reload &

# Bad: Using run_in_background parameter
Bash tool with run_in_background=true to start npm run dev
```

**What you CAN do:**
- Install dependencies (`pip install`, `npm install`)
- Run build commands (`npm run build`)
- Run tests
- Make code changes
- Any other non-server operations

### Python Virtual Environment Usage

**CRITICAL: Always use the virtual environment for backend operations**

When working with the backend, you MUST always use the Python virtual environment located at `backend/.venv/`. This ensures all dependencies are correctly installed and isolated.

**How to Use Virtual Environment in Commands**

**Correct approach** - Use the venv Python directly:
```bash
# Good: Direct path to venv Python
cd C:/Users/ttulsi/GithubProjects/mount-doom/backend
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -c "import some_module"
.venv/Scripts/python.exe app/main.py
```

**Incorrect approach** - Using global Python:
```bash
# Bad: Uses global Python installation
cd backend
python -m pip install ...
python -c "import some_module"
```

**Key Points**:
- **Always** prefix Python commands with `.venv/Scripts/python.exe` when running commands from bash
- **Never** use bare `python` or `pip` commands - they may use the global Python installation
- When installing dependencies, always use: `.venv/Scripts/python.exe -m pip install -r requirements.txt`
- When testing imports, always use: `.venv/Scripts/python.exe -c "import ..."`
- When running the server, always use: `.venv/Scripts/python.exe -m uvicorn app.main:app --reload`

**Path Notes**:
- Use forward slashes `/` in paths for bash compatibility
- The venv path is: `backend/.venv/Scripts/python.exe` (Windows) or `backend/.venv/bin/python` (Linux/Mac)

## Environment Configuration

### Backend (.env)
```env
AZURE_AI_PROJECT_CONNECTION_STRING=your_connection_string
COSMOS_DB_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOS_DB_DATABASE_NAME=mount_doom_db
COSMOS_DB_USE_EMULATOR=false  # true for local emulator
default_model_deployment=gpt-4.1
```

For local Cosmos DB Emulator:
```env
COSMOS_DB_ENDPOINT=https://localhost:8081
COSMOS_DB_USE_EMULATOR=true
COSMOS_DB_KEY=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Git Workflow

### Branches
- main: production-ready code
- feature/: new features
- fix/: bug fixes
- docs/: documentation updates

### Commits
- Clear, descriptive messages
- Follow conventional commits
- One logical change per commit
- Reference issues when applicable

## Documentation Policy

**IMPORTANT**: Documentation should ONLY exist in the following locations:
- `README.md` files (root, backend, frontend)
- `CLAUDE.md` (this file) - Essential project information and critical policies
- `.claude/rules/` directory - Detailed documentation organized by topic
- Code comments and docstrings where necessary

**DO NOT CREATE**:
- Summary markdown files (e.g., IMPLEMENTATION_SUMMARY.md, FIX_SUMMARY.md)
- Status markdown files (e.g., PROJECT_STATUS.md, PR_SUMMARY.md)
- Checklist markdown files (e.g., VERIFICATION_CHECKLIST.md)
- Guide markdown files (e.g., UI_CHANGES_GUIDE.md, VISUAL_FIX_GUIDE.md)
- Diagram markdown files (e.g., REFACTORING_DIAGRAM.md)
- Any other temporary or planning markdown files

**Rationale**:
- These files clutter the repository
- Information becomes stale and inconsistent
- All relevant information should be in README files, CLAUDE.md, or `.claude/rules/`
- Planning and notes should be done in PR descriptions or issues, not committed files

## Local Tooling Conventions

### CXA Evals Runner
- `cxa_evals/` is a repo-root folder for running CXA AI Evals locally
- The CLI executable `Microsoft.CXA.AIEvals.Cli.exe` is manually downloaded and must not be committed
- The `output/` directory under `cxa_evals/` must not be committed (results are gitignored)
- Evals now run for `SimulationAgent` at once - no need for separate per-agent runs
- The `scenario_name` field in input files distinguishes between different agent types
- Config files: `default_config.json` (default metrics) and `cutom_config.json` (custom rules)
- Input files are stored in `cxa_evals/input/` directory

## Important Notes

**Authentication:**
- DefaultAzureCredential automatically handles token refresh
- No manual token management needed
- Use `az login` for local development

**Azure AI References:**
- [AIProjectClient Documentation](https://learn.microsoft.com/en-us/python/api/azure-ai-projects/azure.ai.projects.aio.aiprojectclient?view=azure-python-preview)
- [Code Samples](https://github.com/Azure/azure-sdk-for-python/tree/azure-ai-projects_2.0.0b3/sdk/ai/azure-ai-projects/samples/agents)

**Configuration Loading:**
- Backend: Settings loaded from `backend/.env` via absolute path (works when starting from repo root)
- Frontend: Environment variables must have `NEXT_PUBLIC_` prefix for client-side access

**Detailed Documentation:**
For detailed information on architecture, conventions, features, and patterns, refer to the files in `.claude/rules/` directory.

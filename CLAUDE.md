# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mount Doom is a fullstack AI agent simulation platform for multi-agent conversations using Azure AI Projects and Cosmos DB. The system enables persona generation, conversation simulation, and transcript parsing.

**Key Technologies:**
- Backend: FastAPI (Python 3.9+), Azure AI Projects, Azure Cosmos DB
- Frontend: Next.js 15, TypeScript, Ant Design
- Authentication: Azure DefaultAzureCredential (automatic token refresh)

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

## Python Virtual Environment Usage

**CRITICAL: Always use the virtual environment for backend operations**

When working with the backend, you MUST always use the Python virtual environment located at `backend/.venv/`. This ensures all dependencies are correctly installed and isolated.

### How to Use Virtual Environment in Commands

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

### Key Points
- **Always** prefix Python commands with `.venv/Scripts/python.exe` when running commands from bash
- **Never** use bare `python` or `pip` commands - they may use the global Python installation
- When installing dependencies, always use: `.venv/Scripts/python.exe -m pip install -r requirements.txt`
- When testing imports, always use: `.venv/Scripts/python.exe -c "import ..."`
- When running the server, always use: `.venv/Scripts/python.exe -m uvicorn app.main:app --reload`

### Path Notes
- Use forward slashes `/` in paths for bash compatibility
- The venv path is: `backend/.venv/Scripts/python.exe` (Windows) or `backend/.venv/bin/python` (Linux/Mac)

## Architecture Overview

### Backend: Clean Architecture with Vertical Slices

The backend uses **lazy initialization** for Azure AI and Cosmos DB clients (initialized on first use, not on import) to speed up dev mode restarts.

**Key Directories:**
- `app/core/` - Configuration and logging setup
- `app/infrastructure/` - Shared infrastructure services (AzureAIService, CosmosDBService)
- `app/models/` - Shared Pydantic schemas
- `app/modules/` - Feature modules organized as vertical slices

**Unified API Architecture:**

1. **Single Agents API** (`app/modules/agents/`)
   - **Centralized registry**: All agent configurations in `config.py` (AGENT_REGISTRY)
   - **Centralized instructions**: All agent instructions in `instructions.py`
   - **Unified endpoints**: Single API for all agents (`/api/v1/agents/{agent_id}/invoke`)
   - **Generic service**: `agents_service.py` handles any agent by agent_id
   - Four agents: persona_distribution, persona_generator, transcript_parser, c2_message_generation

2. **Workflows API** (`app/modules/workflows/`)
   - Multi-agent workflows with configuration registry in `config.py`
   - Workflow listing endpoints (`/api/v1/workflows/list`)
   - Example: conversation_simulation workflow (C1 + C2 agents)

**Infrastructure Services (Singletons):**
- **AzureAIService** - Client factory only. Creates agents with `create_agent(name, instructions, model)`. No business logic.
- **CosmosDBService** - Generic DB operations. Uses conversation_id from Azure AI as document ID. Supports local emulator and cloud.

**Agent Versioning:**
- Versions generated from instruction SHA256 hash (first 8 chars): `f"v{hash[:8]}"`
- When instructions change, new versions are automatically created
- All agent details (name, version, instructions, model) saved to Cosmos DB

**Important Patterns:**
- Services contain business logic and database persistence
- Routes are thin: validate → call service → return response
- All timestamps use `datetime.now(timezone.utc)` (not deprecated `utcnow()`)
- Structured logging with `structlog` (configured in `app/core/logging.py`)

### Frontend: Next.js with App Router

**Template-Based UI:**
- **SingleAgentTemplate** - For single-agent features (persona generation, parsing)
  - Three tabs: Generate, Batch Processing, History
  - Configured via `SingleAgentConfig` object
- **MultiAgentTemplate** - For multi-agent workflows (conversation simulation)
  - Three tabs: Simulate, Batch Processing, History
  - Configured via `MultiAgentConfig` object

**Global Timezone Support:**
- Context provider: `TimezoneProvider` in layout.tsx
- Hook: `useTimezone()` returns `{ timezone, formatTimestamp, formatTime }`
- Supported: UTC, IST (default: IST)
- Persisted to localStorage

**Key Files:**
- `app/` - Next.js pages (App Router)
- `components/` - Reusable components (PageLayout, templates)
- `lib/api-client.ts` - Type-safe API client
- `lib/types.ts` - Shared TypeScript types
- `lib/timezone-context.tsx` - Global timezone management

## Multi-Agent Conversation Pattern

**Shared Conversation Workflow:**
1. Single conversation created at start
2. Conversation reused across all agent invocations for context continuity
3. Agents operate sequentially by adding messages and creating responses
4. Pattern: C1 (service rep) → C2 (customer) → check completion → repeat

**Conversation API Usage:**
```python
# Create conversation
conversation = openai_client.conversations.create(
    items=[{"type": "message", "role": "user", "content": prompt}]
)

# Add messages
openai_client.conversations.items.create(
    conversation_id=conversation.id,
    items=[{"type": "message", "role": "user", "content": message}]
)

# Create agent response
response = openai_client.responses.create(
    conversation=conversation.id,
    extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
    input=""
)
```

## Database Architecture

**Cosmos DB Strategy:**
- One container per feature (auto-created if missing)
- Partition key: `/id`
- Document ID: `conversation_id` from Azure AI (ensures uniqueness)
- All results stored automatically with complete metrics

**Document Structure:**
- Core fields: id, prompt/input, response, timestamp
- Metrics: tokens_used, time_taken_ms, start_time, end_time
- Agent details: agent_name, agent_version, instructions, model, created_at
- Optional: parsed_output (for JSON-based agents like persona generation)

**Local Development:**
- Supports Cosmos DB Emulator (set `COSMOS_DB_USE_EMULATOR=true`)
- No Azure authentication needed for emulator (uses emulator key)

## Key Conventions

### Backend Code Style
- Follow PEP 8
- Type hints required for all function parameters and returns
- Async/await for I/O operations
- Pydantic for data validation
- **CRITICAL**: Use `datetime.now(timezone.utc)` not `datetime.utcnow()`
- Error handling with HTTPException
- Structured logging with key-value pairs

### Frontend Code Style
- TypeScript for all files
- 'use client' directive for client components
- Ant Design for all UI components
- Always use `useTimezone()` hook for timestamp formatting (never raw `toLocaleString()`)

### Adding New Features

**Single Agent:**
1. Add instructions to `backend/app/modules/agents/instructions.py`
2. Register in `AGENT_REGISTRY` in `backend/app/modules/agents/config.py`
3. Add container constant to `cosmos_db_service.py`
4. Update frontend navigation in `PageLayout.tsx`
5. Frontend will automatically work via unified agents API

**Multi-Agent Workflow:**
1. Create directory: `backend/app/modules/workflows/{workflow_name}/`
2. Add agent instructions to `modules/agents/instructions.py`
3. Create `agents.py` (agent factories), `models.py` (schemas), `{workflow}_service.py` (orchestration), `routes.py`
4. Register router in `main.py`
5. Add container constant to `cosmos_db_service.py`
6. Register in `modules/workflows/config.py`
7. Create frontend page in `app/workflows/{workflow_id}/page.tsx`
8. Update frontend navigation

### Response Metrics to Track
All API responses should include:
- `response_text` - The generated text
- `tokens_used` - Token count from Azure AI
- `time_taken_ms` - Calculated with `time.time() * 1000`
- `start_time` - ISO timestamp (`datetime.now(timezone.utc)`)
- `end_time` - ISO timestamp
- `agent_details` - Complete agent information

## Logging (Verbose Development Mode)

**Configuration:**
- Structured logging with `structlog` (colored console output)
- Configured in `app/core/logging.py` before importing routes
- DEBUG level when `settings.api_debug=True`, INFO otherwise
- Dual output: console (colored) and file (`logs/mount_doom.log`)
- File rotation: 10MB max, 5 backups

**External library logs suppressed to WARNING:**
- Azure SDK (`azure`, `azure.core`, `azure.ai.projects`)
- OpenAI client (`openai`)
- HTTP clients (`httpx`, `httpcore`, `urllib3`)

**Logging Best Practices:**
- Use key-value pairs: `logger.info("Message", key1=value1, key2=value2)`
- `logger.info()` for key operations, milestones, state changes
- `logger.debug()` for detailed operational info
- `logger.error()` with `error=str(e)` and `exc_info=True` for errors

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

## Memory Banks Protocol

### Before Making Any Changes

**REQUIRED**: Always read the memory banks in the `.memory-banks/` directory before making any changes to the codebase. The memory banks contain critical project context:

1. **Read First**: Always read these files before starting any work:
   - `.memory-banks/architecture.md` - Project architecture and structure
   - `.memory-banks/conventions.md` - Development conventions and patterns
   - `.memory-banks/features.md` - Detailed feature descriptions

2. **Why This Matters**: Memory banks contain:
   - Architectural decisions and patterns
   - Coding conventions and best practices
   - Feature workflows and requirements
   - Important context that may not be obvious from code alone

### After Making Changes

**REQUIRED**: Always update the memory banks when making changes that affect:

1. **Architecture Changes** → Update `.memory-banks/architecture.md`
   - New services, components, or modules
   - Changes to data flow or structure
   - New integration patterns

2. **Convention Changes** → Update `.memory-banks/conventions.md`
   - New coding standards or patterns
   - Changes to naming conventions
   - New error handling approaches
   - Updates to testing strategies

3. **Feature Changes** → Update `.memory-banks/features.md`
   - New features
   - Changes to existing workflows
   - New metrics or tracking requirements
   - Updates to agent/model configurations

### Memory Bank Update Process
1. Make your code changes
2. Identify which memory bank files are affected
3. Update the relevant memory bank files to reflect the changes
4. Ensure consistency between code and documentation
5. Include memory bank updates in your commit

**Remember**: Memory banks are living documentation that must stay synchronized with the codebase. Failing to update them makes future work harder and can lead to inconsistencies.

## Feature Change Validation

When making changes to any feature, **ALWAYS validate compatibility between backend and frontend**:

### 1. API Contract Validation
- Verify request schemas match between `backend/app/modules/[feature]/models.py` and `frontend/lib/api-client.ts`
- Verify response schemas match between backend Pydantic models and frontend TypeScript types
- Check that field names, types, and optional/required status are consistent

### 2. Endpoint Validation
- Confirm route paths in `backend/app/modules/[feature]/routes.py` match API calls in `frontend/lib/api-client.ts`
- Verify HTTP methods (GET, POST, etc.) are consistent
- Check query parameters and request body structures

### 3. Type Alignment Checklist
- Backend Pydantic `BaseModel` ↔ Frontend TypeScript `interface`
- Backend `Optional[X]` ↔ Frontend `X | null` or `X?`
- Backend `datetime` ↔ Frontend `string` (ISO format)
- Backend `List[X]` ↔ Frontend `X[]`
- Backend `Dict[str, Any]` ↔ Frontend `Record<string, any>`

### 4. Test After Changes
- Run the backend server and verify endpoints respond correctly
- Test frontend API calls to ensure no type mismatches or 422 errors
- Check browser console for any parsing or type errors

## Important Notes

**Notes Directory Policy:**
- The `notes/` directory is for personal notes and ad-hoc artifacts
- Do not read, parse, or reference files in `notes/` for context
- Do not import or depend on `notes/` contents from application code
- Only `.memory-banks/` governs project context

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

**Documentation Policy:**
- Only maintain README files and `.memory-banks/` directory
- Do NOT create summary/status/checklist markdown files (they clutter the repo)
- Planning and notes go in PR descriptions or issues, not committed files

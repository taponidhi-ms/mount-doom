# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mount Doom is a fullstack AI agent simulation platform for multi-agent conversations using Azure AI Projects and Cosmos DB. The system enables persona generation, conversation simulation, and transcript parsing.

**Key Technologies:**
- Backend: FastAPI (Python 3.9+), Azure AI Projects, Azure Cosmos DB
- Frontend: Next.js 15, TypeScript, Ant Design
- Authentication: Azure DefaultAzureCredential (automatic token refresh)

## Documentation Update Policy

**CRITICAL: Always update documentation before committing code changes.**

Before creating any git commit, you MUST update the following documentation files to reflect your changes:

1. **CLAUDE.md** (this file) - Update relevant sections:
   - Architecture changes → Update architecture sections
   - New features → Update feature descriptions
   - New conventions → Update Key Conventions section
   - API changes → Update relevant API sections

2. **Memory Banks** (`.memory-banks/` directory):
   - **architecture.md** - Update for architectural changes (new services, components, data flow changes)
   - **conventions.md** - Update for new coding standards, patterns, or best practices
   - **features.md** - Update for new features, feature changes, or workflow updates

3. **README.md** - Update if user-facing changes (setup instructions, new features, deployment changes)

**When to Update**:
- Adding new agents or workflows
- Adding new API endpoints
- Changing database schema or structure
- Adding new UI pages or components
- Changing configuration or setup process
- Adding new dependencies or technologies
- Modifying existing features significantly

**Commit Message Format**:
- Include what was changed AND which documentation was updated
- Example: `feat: Add multi-agent download feature\n\nUpdated CLAUDE.md and .memory-banks/features.md with multi-agent download documentation`

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

## Server Management Policy

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

1. **Agents API** (`app/modules/agents/`)
   - **Individual config files**: Each agent has its own config file in `configs/` directory
   - **Dynamic registry loader**: `load_agent_registry()` discovers and loads all agent configs automatically
   - **Centralized instructions**: All agent instructions in `instructions.py`
   - **Unified endpoints**: Single API for all agents (`/api/v1/agents/{agent_id}/invoke`)
   - **Generic service**: `agents_service.py` handles any agent by agent_id
   - **Sample inputs with metadata**: Each sample has optional `category` and `tags` for organization
   - **Prompt tracking**: All invocations store optional `prompt_category` and `prompt_tags` fields
   - Eight agents: persona_distribution, persona_generator, transcript_parser, c2_message_generation, c1_message_generation, simulation_prompt_validator, transcript_based_simulation_parser, simulation_prompt
   - Each agent operates independently and returns results immediately

2. **Workflows API** (`app/modules/workflows/`)
   - Workflows orchestrate multiple agents with custom logic
   - Configuration registry in `config.py`
   - Workflow listing endpoints (`/api/v1/workflows/list`)
   - Example: conversation_simulation workflow (C1 service rep + C2 customer agents interact)

**Infrastructure Services (Singletons):**
- **AzureAIService** - Client factory only. Creates agents with `create_agent(name, instructions, model)`. No business logic.
- **CosmosDBService** - Generic DB operations. Uses conversation_id from Azure AI as document ID. Supports local emulator and cloud. Includes `query_cached_response()` for response caching.

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

**Modular Architecture with Nested Routes:**
- Agent pages use nested routes (`/agents/[agentId]/`, `/agents/[agentId]/batch`, `/agents/[agentId]/history`)
- Agent info loaded once in layout, shared via React Context (`AgentContext`)
- Reusable components extracted for maintainability:
  - `AgentResultModal` - View result details with JSON/Plain Text toggle
  - `AgentResultCard` - Inline result display
  - `AgentInstructionsCard` - Collapsible instructions display
  - `BatchProcessingSection` - Complete batch processing UI
  - `AgentHistoryTable` - Full-featured history table with sorting, filtering, bulk operations
  - `AgentTabs` - Tab-like navigation using Next.js Link
- Workflow pages (e.g., `/workflows/conversation_simulation`) have custom implementations
- URL-based navigation with browser back/forward support

**Global Timezone Support:**
- Context provider: `TimezoneProvider` in layout.tsx
- Hook: `useTimezone()` returns `{ timezone, formatTimestamp, formatTime }`
- Supported: UTC, IST (default: IST)
- Persisted to localStorage

**Key Files:**
- `app/agents/[agentId]/` - Nested route structure for agent pages
  - `layout.tsx` - Loads agent info, provides context
  - `page.tsx` - Generate page
  - `batch/page.tsx` - Batch processing page
  - `history/page.tsx` - History page
- `components/agents/` - Reusable agent components organized by feature
- `lib/api-client.ts` - Type-safe API client
- `lib/types.ts` - Shared TypeScript types
- `lib/timezone-context.tsx` - Global timezone management

## Workflow Pattern (Multi-Agent Orchestration)

**Shared Conversation Workflow:**
Workflows orchestrate multiple agents that communicate through a shared conversation:
1. Single conversation created at start
2. Conversation reused across all agent invocations for context continuity
3. Agents operate sequentially by adding messages and creating responses
4. Example pattern: C1 (service rep) → C2 (customer) → check completion → repeat

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

## Agent Configuration Architecture

### Individual Config Files

Each agent has its own configuration file in `backend/app/modules/agents/configs/`:
- Clear separation of concerns
- Easy to manage large sample prompt sets for evaluation
- Each config file exports an `AGENT_CONFIG` variable
- Config files: `persona_distribution_config.py`, `persona_generator_config.py`, `transcript_parser_config.py`, `c2_message_generation_config.py`, `c1_message_generation_config.py`, `simulation_prompt_validator_config.py`, `transcript_based_simulation_parser_config.py`, `simulation_prompt_config.py`

**Example config structure:**
```python
from ..config import AgentConfig
from ..instructions import AGENT_INSTRUCTIONS

AGENT_CONFIG = AgentConfig(
    agent_id="agent_id",
    agent_name="AgentName",
    display_name="Display Name",
    description="...",
    instructions=AGENT_INSTRUCTIONS,
    container_name="single_turn_conversations",
    scenario_name="ScenarioName",
    input_field="prompt",
    input_label="Prompt",
    input_placeholder="...",
    sample_inputs=[
        {
            "label": "Sample 1",
            "value": "...",
            "category": "Valid",
            "tags": ["tag1", "tag2"]
        }
    ]
)
```

### Registry System

- **Dynamic discovery** via `load_agent_registry()` function in `config.py`
- Automatically loads all `*_config.py` files from configs/ directory
- Uses Python's `pkgutil.iter_modules()` to discover config modules
- Each config module must export an `AGENT_CONFIG` variable
- Maintains backward compatibility - rest of codebase uses `AGENT_REGISTRY` dictionary
- Logs successful loading of each agent config

### Sample Inputs Enhancement

Sample inputs now include metadata for better organization and eval tracking:
- **`label`**: Display name for the sample (required)
- **`value`**: The actual prompt text (required)
- **`category`** (optional): Categorization like "Valid", "Invalid", "Edge Case", "Complex"
- **`tags`** (optional): List of tags for organization (e.g., `["billing", "technical"]`, `["positive-sentiment"]`)

**UI Display:**
- Category shown as blue Tag component
- Tags shown as green Tag components
- Displayed above the prompt value in sample inputs modal
- Helps users quickly identify prompt types

### Prompt Metadata Tracking

All agent invocations can store optional metadata:
- **`prompt_category`**: Category from sample input or user input
- **`prompt_tags`**: Tags from sample input or user input (stored as array)

**Storage and Display:**
- Stored in Cosmos DB alongside prompt and response
- Displayed in history table as columns (visible by default)
- Users can hide/show columns via settings dropdown (⚙️)
- Included in eval format downloads (tags concatenated with comma)

**User Workflow:**
1. User selects a sample input → category and tags auto-populate
2. User can manually enter category and tags (optional fields)
3. Fields sent to API during agent invocation
4. Stored in database for tracking and filtering
5. Available in history table and downloads

### Benefits

- **Scalability**: Each agent config can grow independently without bloating central file
- **Maintainability**: Easy to find and update specific agent configurations
- **Organization**: Large prompt sets (for evals) don't clutter codebase
- **Traceability**: Category and tags enable better prompt organization and analysis
- **Flexibility**: Registry loader automatically discovers new agents

## Response Caching

**Purpose**: Optimize token usage and improve performance for repeated evaluations by caching agent responses.

### How It Works

1. **Cache Check**: Before generating a response, the system queries the database for an existing response matching:
   - Exact prompt text (case-sensitive, whitespace-sensitive)
   - Agent name
   - Agent version (instruction hash)

2. **Cache Hit**: If a match is found, return the existing response immediately:
   - Response text from cached document
   - Original tokens_used and timing metrics
   - `from_cache=true` in API response
   - **No Azure AI API call** = 0 tokens used

3. **Cache Miss**: If no match found, generate normally:
   - Create conversation and get agent response
   - Save to database with all metrics
   - `from_cache=false` in API response

4. **Automatic Invalidation**: Cache is automatically invalidated when:
   - Agent instructions change (new version hash generated)
   - Different agent name used
   - Prompt text is different

### Implementation Details

**Backend Method** (`CosmosDBService.query_cached_response()`):
```python
async def query_cached_response(
    container_name: str,
    prompt: str,
    agent_name: str,
    agent_version: str
) -> Optional[Dict[str, Any]]:
    # Query Cosmos DB for exact match
    # Returns most recent matching document or None
```

**Service Layer** (`UnifiedAgentsService.invoke_agent()`):
- Creates agent to get current version
- Queries cache before generation
- Returns cached result if found (with `from_cache=True`)
- Generates new response if not found (with `from_cache=False`)
- Graceful error handling (cache failures don't block generation)

**API Response**:
- `from_cache` field in `AgentInvokeResponse` indicates source
- Frontend displays cache indicator badges
- `from_cache` is a **runtime property only** (not stored in database)

### UI Indicators

**Generate Page**:
- "From Cache" badge (cyan with database icon) for cached responses
- "Newly Generated" badge (green with lightning icon) for new generations

**Batch Processing**:
- "Source" column in results table showing cache status
- "Load All Sample Prompts" button for persona_distribution agent (50 prompts)
- First run: generates all (~100k-300k tokens)
- Second run: retrieves all from cache (0 tokens, 10-30x faster)

**History Table**:
- Optional "Source" column (hidden by default)
- Shows "Cache", "New", or "Unknown" (for historical records)
- Enable via settings dropdown (⚙️)

### Benefits

- **Token Savings**: 100% savings for repeated prompts (0 tokens on cache hits)
- **Performance**: 10-30x faster (~100-200ms vs 1-3s for generation)
- **Cost Reduction**: Significant savings for evaluation runs
- **Consistency**: Same prompt always returns same response (for given agent version)
- **Evaluation-Friendly**: Re-run test suites without token cost

### Sample Prompts: Persona Distribution Agent

The persona_distribution agent includes 50 curated sample prompts for evaluation:
- **35 Valid**: Various domains (telecom, banking, healthcare, retail, insurance, SaaS, travel, utility, mortgage, etc.)
- **10 Invalid**: Transcript-based scenarios (not supported by agent)
- **5 Irrelevant**: Off-topic requests

Each sample includes `category` and `tags` for organization and filtering.

**Workflow**:
1. Click "Load All Sample Prompts (50)" in batch processing
2. First run: Generate all 50 responses
3. Second run: Retrieve all 50 from cache (instant, 0 tokens)

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

## Download Features (Eval Format)

### Single-Agent Download

**Purpose**: Download conversations from a single agent in eval format.

**API Endpoint**: `POST /api/v1/agents/{agent_id}/download`
- Request body: Array of document IDs to download
- Response: JSON file with conversations in eval format
- Filename: `{agent_id}_evals.json`

### Multi-Agent Download

**Purpose**: Download conversations from multiple agents with version filtering in a single eval-formatted file.

**API Endpoints**:
- `GET /api/v1/agents/versions` - List all agent+version combinations with conversation counts
- `POST /api/v1/agents/download-multi` - Download selected agent+version combinations

**Multi-Agent Download Request**:
```json
{
  "selections": [
    {"agent_id": "persona_generator", "version": "v12345678"},
    {"agent_id": "transcript_parser", "version": "vabcdef01"}
  ]
}
```

**Response**: Single JSON file with flat list of conversations from all selected agent+version combinations
- Filename: `multi_agent_evals_{timestamp}.json`

**Frontend Integration**:
- Dedicated page at `/agents/download` for multi-agent selection
- Table showing all agent versions with conversation counts
- Checkbox selection for specific agent+version combinations
- Real-time count of selected versions and total conversations
- Download button triggers browser download

**Key Features**:
- Version-specific filtering (only conversations from selected versions)
- Flat list format (all conversations together, compatible with eval framework)
- No hard data size limits (typical: 1,000 conversations ≈ 2-5 MB)
- Implementation specific to eval format (not generalized for future formats)

**Download Format**:
```json
{
  "conversations": [
    {
      "Id": "document-uuid",
      "instructions": "Full agent instruction set",
      "prompt": "User's input prompt",
      "agent_prompt": "[SYSTEM]\n{instructions}\n\n[USER]\n{prompt}",
      "agent_response": "Agent's generated response",
      "scenario_name": "AgentName"
    }
  ]
}
```

**Field Descriptions**:
- `Id`: Document ID from Cosmos DB (UUID)
- `instructions`: Complete agent instruction set used for generation
- `prompt`: Original user input prompt
- `agent_prompt`: Literal template string `"[SYSTEM]\n{{instructions}}\n\n[USER]\n{{prompt}}"`
  - This is a fixed template string that the eval framework will process
  - The eval framework substitutes `{{instructions}}` and `{{prompt}}` with values from sibling fields
  - Do NOT format this string - always use the literal template
- `agent_response`: Agent's generated response text
- `scenario_name`: Agent's scenario identifier (from agent config, defaults to agent_name)

**Agent Configuration**:
Each agent in `AGENT_REGISTRY` includes a `scenario_name` field for eval downloads:
- `persona_distribution` → `PersonaDistributionGeneratorAgent`
- `persona_generator` → `PersonaGeneratorAgent`
- `transcript_parser` → `TranscriptParserAgent`
- `c2_message_generation` → `C2MessageGeneratorAgent`
- `c1_message_generation` → `C1MessageGeneratorAgent`

**Frontend Integration**:
- AgentHistoryTable component includes download functionality
- Users select conversations from history table and click "Download"
- Downloaded file named: `{agent_id}_evals.json`

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

**New Agent:**
1. Add instructions to `backend/app/modules/agents/instructions.py`
2. Register in `AGENT_REGISTRY` in `backend/app/modules/agents/config.py`
3. Add container constant to `cosmos_db_service.py`
4. Update frontend navigation in `PageLayout.tsx`
5. Frontend will automatically work via unified agents API
6. Agents operate independently and return results immediately

**New Workflow:**
1. Create directory: `backend/app/modules/workflows/{workflow_name}/`
2. Add agent instructions to `modules/agents/instructions.py` (if new agents needed)
3. Create `agents.py` (agent factories), `models.py` (schemas), `{workflow}_service.py` (orchestration), `routes.py`
4. Register router in `main.py`
5. Add container constant to `cosmos_db_service.py`
6. Register in `modules/workflows/config.py`
7. Create frontend page in `app/workflows/{workflow_id}/page.tsx` with custom UI
8. Update frontend navigation
9. Workflows orchestrate multiple agents with custom logic and conversation management

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

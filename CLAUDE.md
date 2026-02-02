# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mount Doom is a fullstack AI agent simulation platform for multi-agent conversations using Azure AI Projects and Cosmos DB. The system enables persona generation, conversation simulation, and transcript parsing.

**Key Technologies:**
- Backend: FastAPI (Python 3.9+), Azure AI Projects, Azure Cosmos DB
- Frontend: Next.js 15, TypeScript, Ant Design
- Authentication: Azure DefaultAzureCredential (automatic token refresh)

**Note on Documentation Consolidation:**
- All documentation has been consolidated into this single CLAUDE.md file
- The `.memory-banks/` directory is deprecated and no longer maintained
- This file now contains all architecture, features, and conventions documentation
- For comprehensive project context, refer to the sections below

## Documentation Update Policy

**CRITICAL: Always update documentation before committing code changes.**

Before creating any git commit, you MUST update the following documentation files to reflect your changes:

1. **CLAUDE.md** (this file) - Update relevant sections:
   - Architecture changes → Update architecture sections
   - New features → Update feature descriptions in Features section
   - New conventions → Update Development Conventions section
   - API changes → Update relevant API sections

2. **README.md** - Update if user-facing changes (setup instructions, new features, deployment changes)

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
- Example: `feat: Add multi-agent download feature\n\nUpdated CLAUDE.md with multi-agent download documentation in Features and Architecture sections`

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

## Architecture

### Backend Architecture (Clean Architecture with Vertical Slices)

#### Structure
```
backend/app/
├── core/                 # Configuration and settings
├── models/               # Shared/Common models
│   ├── shared.py         # Common API and DB schemas
│   └── single_agent.py   # Shared schemas for agent operations (note: naming kept for backend compat)
├── infrastructure/       # Infrastructure services
│   ├── ai/
│   │   └── azure_ai_service.py # Client initialization
│   └── db/              # Database services
│       └── cosmos_db_service.py
├── modules/             # Feature modules (Vertical Slices)
│   ├── agents/          # Unified agents API
│   │   ├── __init__.py
│   │   ├── config.py    # Agent configuration registry
│   │   ├── instructions.py  # All agent instructions (centralized)
│   │   ├── models.py    # API schemas for agents
│   │   ├── routes.py    # Unified agents endpoints
│   │   └── agents_service.py  # Generic agent invocation service
│   └── workflows/       # Workflows module
│       ├── __init__.py
│       ├── config.py    # Workflow configuration registry
│       ├── models.py    # API schemas for workflows
│       ├── routes.py    # Workflow listing endpoints
│       └── conversation_simulation/  # Workflow with multiple agents
│           ├── __init__.py
│           ├── agents.py    # C1 and C2 agent factories
│           ├── conversation_simulation_service.py  # Orchestration logic
│           ├── models.py    # API schemas
│           └── routes.py    # Simulation endpoints
└── main.py               # FastAPI application
```

#### Unified Agents Module (modules/agents/)
A centralized module that provides a unified API for all agent operations:

**Centralized Instructions (instructions.py)**
All agent instructions are consolidated in a single file:
- `PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS`
- `PERSONA_GENERATOR_AGENT_INSTRUCTIONS`
- `TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS`
- `C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS`
- `C1_AGENT_INSTRUCTIONS`

**Agent Configuration Registry (config.py)**
- **Individual config files**: Each agent has its own config file in `configs/` directory
- **Dynamic registry loader**: `load_agent_registry()` discovers and loads configs from `configs/*.py` files
- Each config file exports an `AGENT_CONFIG` variable with complete agent configuration
- Maintains `AGENT_REGISTRY` dictionary populated by dynamic loader
- Each `AgentConfig` contains: agent_id, agent_name, display_name, description, instructions, container_name, scenario_name, input_field, input_label, input_placeholder, sample_inputs
- Sample inputs include optional `category` and `tags` fields for organization and eval tracking
- `scenario_name`: Used for eval downloads, defaults to agent_name if not specified
- Instructions imported from centralized `instructions.py` by individual config files
- Provides helper functions: `get_agent_config()`, `get_all_agents()`, `list_agent_ids()`
- Eight agents: persona_distribution, persona_generator, transcript_parser, c2_message_generation, c1_message_generation, simulation_prompt_validator, transcript_based_simulation_parser, simulation_prompt

**Unified Agents Service (agents_service.py)**
- Generic service that can invoke any agent by agent_id
- Uses agent config to determine instructions and container
- Handles conversation creation, response extraction, JSON parsing
- **Response caching**: Checks database for cached responses before generation (exact match on prompt + agent + version)
- **Internal persistence**: `invoke_agent()` method handles timing, metrics, and database persistence internally
- **Returns Result models**: Service methods return `*Result` models (e.g., `AgentInvokeResult`) for internal use
- **Saves results to database**: Calls `CosmosDBService.save_document()` internally when `persist=True`

**Unified Agents Routes (routes.py)**
- `GET /api/v1/agents/list` - List all available agents with configurations
- `GET /api/v1/agents/{agent_id}` - Get specific agent details including instructions
- `POST /api/v1/agents/{agent_id}/invoke` - Invoke agent with input
- `GET /api/v1/agents/{agent_id}/browse` - Browse agent history
- `POST /api/v1/agents/{agent_id}/delete` - Delete agent records
- `POST /api/v1/agents/{agent_id}/download` - Download agent records in eval format
- `GET /api/v1/agents/versions` - List all agent+version combinations with counts
- `POST /api/v1/agents/download-multi` - Download multiple agent+version combinations

#### Workflows Module (modules/workflows/)
A module for workflow configurations that orchestrate multiple agents:

**Workflow Configuration Registry (config.py)**
- Maintains `WORKFLOW_REGISTRY` dictionary with workflow configurations
- Each `WorkflowConfig` contains: workflow_id, display_name, description, agents list, route_prefix
- Each `WorkflowAgentConfig` contains: agent_id, agent_name, display_name, role, instructions
- Currently contains: conversation_simulation workflow with C1 and C2 agents

**Workflow Routes (routes.py)**
- `GET /api/v1/workflows/list` - List all available workflows with agent details
- `GET /api/v1/workflows/{workflow_id}` - Get specific workflow details including agent instructions

#### Key Principles
- **Separation of Concerns**: Each service handles one feature's business logic
- **Layered Architecture**: Clear separation between routes (API layer) and services (business logic layer)
- **Dependency Injection**: Routes depend on services, not directly on Azure AI
- **Single Responsibility**: Each service class has one reason to change
- **Clean Architecture Layers**: Inward dependencies only
- **Lazy Initialization**: Clients are initialized on first access to speed up dev mode restarts

#### Service Architecture

**AzureAIService**
- **Responsibility**: Client initialization and agent/client factory
- **Lazy Initialization**: Clients are initialized on first access, not on module import
- Only contains:
  - `client` property: Returns AIProjectClient instance (lazy initialization)
  - `openai_client` property: Returns OpenAI client instance (lazy initialization)
  - `create_agent()` method: Creates agents with given name, instructions, and model
  - `_initialize_client()` private method: Initializes clients when first accessed
- Does NOT contain:
  - Business logic for any use case
  - Generic methods that wrap Azure API calls
  - Caching of use case-specific agents
  - Prompt building or workflow orchestration
- **Token Management**: Uses DefaultAzureCredential which automatically handles token refresh

**Feature Services**
- **UnifiedAgentsService** (`modules/agents/agents_service.py`): Handles all agent operations using agent configurations from the registry
- **ConversationSimulationService**: Workflow orchestration for multi-turn conversations (C1 service rep/C2 customer). Uses dedicated module in `modules/workflows/conversation_simulation/`
- Services contain:
  - Agent configuration (name, instructions, model deployment)
  - Workflow logic specific to the feature
  - Conversation management
  - Token and timing tracking
  - Data transformation and formatting
  - **Database persistence logic** (document structure, ID generation, saving)

**CosmosDBService**
- **Infrastructure service for Cosmos DB - Singleton pattern**
- **Lazy Initialization**: Client is initialized on first access, not on module import
- **Local Emulator Support**: Supports both Azure Cloud Cosmos DB and local Cosmos DB Emulator
  - Cloud mode: Uses DefaultAzureCredential for authentication
  - Emulator mode: Uses emulator key (no Azure authentication required)
  - Configured via `COSMOS_DB_USE_EMULATOR` environment variable
- Responsibilities:
  - Client initialization and management (lazy)
  - Database reference management
  - Generic container operations
  - Container name constants
- Methods:
  - `client` property: Returns CosmosClient instance (lazy initialization)
  - `database` property: Returns database client (lazy initialization)
  - `ensure_container()` - Ensure a container exists, create if needed
  - `save_document()` - Generic method to save any document to a container
  - `browse_container()` - Browse container with pagination and ordering
    - Supports custom ordering by field (default: timestamp DESC)
    - **Supports filtering by agent_name** - Optional parameter to filter results
    - Returns paginated results with total count and page info
  - `query_cached_response()` - Query for cached agent responses
    - Exact match on prompt + agent_name + agent_version
    - Returns most recent matching document or None
    - Graceful error handling (returns None on errors)
  - `get_agent_version_summary()` - Returns all unique agent+version combinations with counts
  - `query_by_agent_and_version()` - Returns conversations for specific agent+version
- Does NOT contain:
  - Feature-specific business logic
  - Document structure definitions
  - Feature-specific save methods

#### Routes

**Unified Agents API (Primary API for Agents)**
- `/api/v1/agents/*` - Unified agents API
  - GET `/list` - List all agents with configurations and instructions
  - GET `/versions` - List all agent+version combinations with counts
  - POST `/download-multi` - Download multiple agent+version combinations
  - GET `/{agent_id}` - Get specific agent details
  - POST `/{agent_id}/invoke` - Invoke agent with input
  - GET `/{agent_id}/browse` - Browse agent history
  - POST `/{agent_id}/delete` - Delete agent records
  - POST `/{agent_id}/download` - Download agent records in standardized eval format

**Workflows API**
- `/api/v1/workflows/*` - Workflow configurations
  - GET `/list` - List all workflows with agent details
  - GET `/{workflow_id}` - Get specific workflow details

**Conversation Simulation (Multi-Turn Workflow)**
- `/api/v1/conversation-simulation/*` - Delegates to ConversationSimulationService
  - POST `/simulate` - Simulate conversation between C1 and C2 agents
  - GET `/browse` - Browse past simulations with pagination
  - POST `/delete` - Delete selected records
  - POST `/download` - Download selected records as JSON

Routes only:
1. Extract request parameters
2. Call appropriate service method (which returns `*Result` models)
3. Transform Result to Response model for API response
4. Return formatted `*Response` to client

**Note**: Persistence logic is handled internally by service methods, not by routes.

#### Data Flow

**Generation/Processing Flow (with Response Caching)**
1. User interacts with frontend UI (Generate tab)
2. Frontend calls API client methods
3. API client sends HTTP requests to backend
4. **Backend Route Handler**:
   - Validates request parameters
   - Calls appropriate service method
5. **Service Layer** (with caching):
   - Creates agent to get current version
   - **Checks cache**: Queries CosmosDBService for existing response (prompt + agent + version)
   - **Cache hit**: Returns cached response immediately with `from_cache=true` (skip steps 6-7)
   - **Cache miss**: Proceeds with generation
   - Orchestrates business logic
   - Uses AzureAIService to create agents/clients
   - Manages conversation flow
   - Tracks metrics (tokens, timing)
   - Defines document structure for persistence
   - Calls CosmosDBService.save_document() to persist data
6. **AzureAIService** (only on cache miss):
   - Creates agents or gets clients
   - Communicates with Azure AI API
7. **CosmosDBService**:
   - For cache check: Queries for matching response with `query_cached_response()`
   - For cache miss: Provides generic infrastructure for Cosmos DB operations
   - Ensures containers exist
   - Saves documents with generic save_document() method
8. Backend returns response to frontend (with `from_cache` field)
9. Frontend displays results with cache indicator badge in Generate tab
10. Frontend reloads history to show new result (if newly generated)

**Browse/History Flow**
1. User switches to History tab
2. Frontend calls browse API methods with pagination parameters
3. **Backend Route Handler**: Calls CosmosDBService.browse_container()
4. **CosmosDBService**: Queries Cosmos DB with ordering, applies pagination, returns items with pagination metadata
5. Backend returns paginated response
6. Frontend displays results in Table component
7. User can navigate pages using pagination controls

### Frontend Architecture

#### Structure
```
frontend/
├── app/                        # Next.js App Router pages
│   ├── agents/                 # Nested routes for agents
│   │   ├── download/           # Multi-agent download page
│   │   │   └── page.tsx
│   │   └── [agentId]/          # Dynamic route for any agent
│   │       ├── layout.tsx      # Agent layout (loads info, provides context)
│   │       ├── page.tsx        # Generate page (default)
│   │       ├── batch/
│   │       │   └── page.tsx    # Batch processing page
│   │       └── history/
│   │           └── page.tsx    # History page
│   └── workflows/              # Workflow pages
│       └── conversation_simulation/
│           └── page.tsx
├── components/                 # React components
│   ├── PageLayout.tsx          # Reusable page layout with navigation
│   └── agents/                 # Modular agent components
│       ├── shared/
│       │   ├── AgentContext.tsx    # React Context for agent info
│       │   └── AgentTabs.tsx       # Tab navigation
│       ├── result/
│       │   ├── AgentResultModal.tsx # Modal for viewing results
│       │   └── AgentResultCard.tsx  # Inline result display
│       ├── instructions/
│       │   └── AgentInstructionsCard.tsx # Collapsible instructions
│       ├── batch/
│       │   └── BatchProcessingSection.tsx # Complete batch UI
│       └── history/
│           └── AgentHistoryTable.tsx # Full-featured history table
└── lib/                        # Utilities and API client
    ├── api-client.ts           # Backend API client (includes agents and workflows APIs)
    ├── types.ts                # Shared TypeScript types
    └── timezone-context.tsx    # Global timezone context (UTC/IST)
```

#### Key Principles
- **Modular component architecture**: Reusable components extracted from monolithic pages
- **Nested routes with layouts**: Agent info loaded once in layout, shared via React Context
- **URL-based navigation**: Each tab is a separate route with browser back/forward support
- **Global timezone support**: User can toggle between UTC and IST (default: IST)
- **Dynamic routing**: Agents pages use dynamic [agentId] routing
- **Instructions display**: All agent pages show the agent's instruction set
- Component reusability across features
- Type safety with TypeScript
- Responsive design with Ant Design
- Accessible UI with Ant Design components

#### Navigation Structure
The navigation sidebar organizes pages into two main sections:
- **Agents** - Individual agents that operate independently
  - Persona Distribution Generator
  - Persona Generator
  - Transcript Parser
  - C2 Message Generator
  - Downloads (multi-agent download page)
- **Workflows** - Multi-agent orchestration with custom logic
  - Conversation Simulation

#### Agent Pages Architecture

**Nested Routes Structure**
Agent pages use Next.js nested routes:
- `/agents/[agentId]` - Generate page (default)
- `/agents/[agentId]/batch` - Batch processing page
- `/agents/[agentId]/history` - History page
- `/agents/download` - Multi-agent download page

**Layout Component**
The `layout.tsx` file:
- Loads agent info once via API on mount
- Provides agent info to all child pages via `AgentContext`
- Renders tab navigation via `AgentTabs` component
- Handles loading and error states

**Reusable Components**
- **AgentContext** - React Context for sharing agent info
- **AgentTabs** - Tab-like navigation using Next.js Link
- **AgentResultModal** - Result viewing modal with JSON/Plain Text toggle
- **AgentResultCard** - Inline result display
- **AgentInstructionsCard** - Collapsible instructions display
- **BatchProcessingSection** - Complete batch processing UI with progress tracking
- **AgentHistoryTable** - Full-featured history table with sorting, filtering, bulk operations, column visibility controls

#### Workflow Pages
Workflows that orchestrate multiple agents have custom implementations:
- Each workflow has unique UI requirements and orchestration logic
- No shared template - each page implements its own three-tab structure
- Tab structure: Simulate, Batch Processing, History
- Custom conversation rendering and history columns
- Expandable rows in history table for viewing multi-turn conversation details
- Workflows manage stateful interactions between multiple agents

#### Timezone Context
Global timezone management via React Context:
- Provider: `TimezoneProvider` wraps the app in layout.tsx
- Hook: `useTimezone()` returns `{ timezone, setTimezone, formatTimestamp, formatTime }`
- Supported timezones: UTC, IST (Asia/Kolkata)
- Default: IST
- Persisted to localStorage

#### Routing
Agent pages use URL-based navigation:
- `/agents/persona_generator` - Persona Generator (Generate tab)
- `/agents/persona_generator/batch` - Batch Processing tab
- `/agents/persona_generator/history` - History tab
- `/agents/download` - Multi-agent download page
- Browser back/forward navigation works
- URLs are shareable

### Authentication
- Uses Azure DefaultAzureCredential
- Supports multiple auth methods (CLI, Managed Identity, etc.)
- **Automatic token refresh** - DefaultAzureCredential handles token refresh automatically
- No manual token management required
- For local Cosmos DB emulator, no Azure authentication needed (uses emulator key)

### Error Handling
- Backend: HTTP exceptions with appropriate status codes
- Frontend: Error state display with user-friendly messages
- Logging: Structured logging with structlog

### Performance Tracking
- Token usage tracked for all AI interactions
- Timing metrics for all requests
- Per-message metrics in conversations
- All metrics visible in UI

### Azure AI References
For more details on Azure AI Agent Service and Workflow:
- [Sample Workflow Multi-Agent](https://raw.githubusercontent.com/Azure/azure-sdk-for-python/refs/tags/azure-ai-projects_2.0.0b3/sdk/ai/azure-ai-projects/samples/agents/sample_workflow_multi_agent.py)
- [Workflow Concepts](https://raw.githubusercontent.com/MicrosoftDocs/azure-ai-docs/refs/heads/main/articles/ai-foundry/default/agents/concepts/workflow.md)
- [Azure AI Projects SDK README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/README.md)
- [Azure AI Documentation](https://github.com/MicrosoftDocs/azure-ai-docs/tree/main/articles/ai-foundry/default/agents)
- [AIProjectClient Documentation](https://learn.microsoft.com/en-us/python/api/azure-ai-projects/azure.ai.projects.aio.aiprojectclient?view=azure-python-preview)
- [Code Samples](https://github.com/Azure/azure-sdk-for-python/tree/azure-ai-projects_2.0.0b3/sdk/ai/azure-ai-projects/samples/agents)

## Features

### Feature 1: Persona Distribution Generator

**Purpose**: Generate persona distributions from simulation prompts using specialized AI agents. Outputs structured JSON with conversation counts, intents, sentiments, and proportions.

**Workflow**:
1. User enters a simulation prompt describing the distribution requirements
2. Backend sends prompt to PersonaDistributionGeneratorAgent via Azure AI Projects
3. PersonaDistributionGeneratorAgent generates distribution response (parser-based instruction)
4. Backend parses JSON output and stores both raw and parsed versions
5. Response stored in Cosmos DB `persona_distribution` container with complete agent details
6. Frontend displays persona distribution with metrics and parsed output

**Agent**:
- PersonaDistributionGeneratorAgent (fixed agent name)
- Instructions defined in `app/modules/agents/instructions.py`
- Instruction set includes a small set of sample prompts/expected JSON shapes for grounding
- Automatic versioning based on instruction hash
- Model: gpt-4 (default from settings)

**Output Format**:
```json
{
  "ConvCount": <integer>,
  "intents": [{"intent": "<string>", "percentage": <number>, "subject": "<string>"}],
  "Sentiments": [{"sentiment": "<string>", "percentage": <number>}],
  "Proportions": [{"intent": "<string>", "count": <integer>}],
  "IsTranscriptBasedSimulation": <boolean>,
  "CallerPhoneNumber": "<string>",
  "RecipientPhoneNumber": "<string>"
}
```

**Metrics Tracked**:
- Tokens used
- Time taken
- Start/end timestamps
- Agent details (name, version, instructions, model)
- Parsed JSON output (if parsing successful)

### Feature 2: Persona Generator

**Purpose**: Generate exact customer personas with specific intents, sentiments, subjects, and metadata. Outputs a list of detailed personas for conversation simulations.

**Workflow**:
1. User enters a prompt describing what personas to generate
2. Backend sends prompt to PersonaGeneratorAgent via Azure AI Projects
3. PersonaGeneratorAgent generates exact personas with metadata
4. Backend parses JSON output and stores both raw and parsed versions
5. Response stored in Cosmos DB `persona_generator` container with complete agent details
6. Frontend displays personas with metrics and parsed output

**Agent**:
- PersonaGeneratorAgent (fixed agent name)
- Instructions defined in `app/modules/agents/instructions.py`
- Instruction set includes sample prompts and minified JSON examples
- Automatic versioning based on instruction hash
- Model: gpt-4 (default from settings)

**Output Format**:
```json
{
  "CustomerPersonas": [
    {
      "CustomerIntent": "<string>",
      "CustomerSentiment": "<string>",
      "ConversationSubject": "<string>",
      "CustomerMetadata": {
        "key1": "value1",
        "key2": "value2"
      }
    }
  ]
}
```

### Feature 3: Transcript Parser

**Purpose**: Parse customer-representative transcripts to extract intent, subject, and sentiment.

**Workflow**:
1. User pastes or enters a transcript from a customer-representative conversation
2. Backend sends transcript to TranscriptParserAgent via Azure AI Projects
3. TranscriptParserAgent analyzes the conversation and extracts intent, subject, and sentiment
4. Backend parses JSON output and stores both raw and parsed versions
5. Response stored in Cosmos DB `transcript_parser` container with complete agent details
6. Frontend displays parsed result with extracted metadata

**Agent**:
- TranscriptParserAgent (fixed agent name)
- Instructions defined in `app/modules/agents/instructions.py`
- Instruction set focuses on analyzing customer-representative conversations
- Automatic versioning based on instruction hash
- Model: gpt-4 (default from settings)

**Output Format**:
```json
{
  "intent": "<string>",
  "subject": "<string>",
  "sentiment": "<string>"
}
```

### Feature 4: C2 Message Generation

**Purpose**: Generate C2 (customer) messages for use in conversation simulations or standalone.

**Workflow**:
1. User provides a prompt with conversation context
2. Backend sends prompt to C2MessageGeneratorAgent via unified agents service
3. Agent generates a customer message based on the context
4. **Response stored in Cosmos DB** `c2_message_generation` container with full metrics
5. Frontend displays the generated message

**Agent**:
- C2MessageGeneratorAgent (fixed agent name)
- Instructions defined in `app/modules/agents/instructions.py`
- Model: gpt-4 (default from settings)
- **Accessed via**: Unified agents API (`/api/v1/agents/c2_message_generation/invoke`)

**Metrics Tracked**:
- Tokens used (for both standalone and simulation use)
- Time taken
- Conversation ID from Azure AI
- Start/end timestamps

### Feature 5: Conversation Simulation

**Purpose**: Simulate multi-turn conversations with distinct C1/C2 logic using Python control flow.

**Participants**:
- **C1MessageGeneratorAgent**: Customer Service Representative
- **C2MessageGeneratorAgent**: Customer (uses c2_message_generation module)

**Workflow**:
1. User provides customer configuration (Intent, Sentiment, Subject)
2. Max turns is hardcoded to 15 in backend
3. Simulation starts:
   - **Empty conversation created** (no initial customer message)
   - **C1 checks for empty conversation** and greets the customer on first turn
   - Loop:
     - **C1 Turn**: C1MessageGeneratorAgent generates response to conversation history
     - **C1 Termination Check**: If C1 says "end this call now" or "transfer...", loop ends
     - **C2 Turn**:
       - Backend constructs prompt with conversation properties and messages
       - **C2 via unified agents service**: Uses `invoke_agent('c2_message_generation', prompt, persist=True)`
       - **C2 conversation persisted**: Tokens, conversation_id, and full metrics saved to database
       - C2 response is added to the conversation history
     - Repeat until 15 turns or completion
4. Full conversation stored in Cosmos DB `conversation_simulation` container
5. Frontend displays conversation history with tokens for both C1 and C2 messages

**Agents**:
- Instructions defined in `app/modules/agents/instructions.py`
- **C1 Instructions**: Standard CSR instructions, explicitly instructed to greet customer when conversation is empty
- **C2 Instructions**: Customer instructions, explicitly aware of properties via structured prompt input

**Key Features**:
- **C1 greeting on empty conversation**: C1 checks if conversation is empty and greets customer
- C1 is unaware of conversation properties
- **C2 receives context via structured prompt**: Properties and messages included
- **C2 via unified agents service**: Uses `invoke_agent()` with `persist=True`
- **C2 metrics tracked**: tokens_used and conversation_id for every C2 message
- **Two database containers**:
  - `conversation_simulation` - Full multi-turn conversations
  - `c2_message_generation` - Individual C2 message generations

### Feature 6: Unified Agents API

**Purpose**: Provides a unified consolidated API for all agent operations, eliminating the need for separate endpoints per agent.

**Key Features**:
- List all available agents with their configurations and instructions
- Invoke any agent by agent_id with a generic input
- Browse, delete, and download agent history records
- Agent instructions are exposed to the frontend for display
- Sample inputs with category and tags for better organization
- Optional prompt metadata tracking (category and tags)
- **Response caching**: Automatic caching of responses based on prompt + agent + version

**Agent Registry**:
Eight agents supported:
- `persona_distribution` - Persona Distribution Generator Agent
- `persona_generator` - Persona Generator Agent
- `transcript_parser` - Transcript Parser Agent
- `c2_message_generation` - C2 Message Generator Agent
- `c1_message_generation` - C1 Message Generator Agent
- `simulation_prompt_validator` - Simulation Prompt Validator Agent
- `transcript_based_simulation_parser` - Transcript Based Simulation Parser Agent
- `simulation_prompt` - Simulation Prompt Agent

**Sample Inputs Enhancement**:
Each agent's sample inputs include metadata:
- `label`: Display name for the sample
- `value`: The actual prompt text
- `category` (optional): Categorization like "Valid", "Invalid", "Edge Case"
- `tags` (optional): List of tags (e.g., `["billing", "technical"]`)

**UI Display**:
- Category shown as blue Tag component
- Tags shown as green Tag components
- When user selects sample, category and tags auto-populate in form
- User can manually enter or edit category and tags (optional fields)

**Prompt Metadata Tracking**:
- All invocations can include optional `prompt_category` and `prompt_tags`
- Stored in database with conversation
- Displayed in history table (visible columns by default)
- Users can hide/show columns via column settings (⚙️)
- Included in eval downloads (tags concatenated with comma)

**API Endpoints**:
- GET `/api/v1/agents/list` - List all agents
- GET `/api/v1/agents/{agent_id}` - Get agent details
- POST `/api/v1/agents/{agent_id}/invoke` - Invoke agent
- GET `/api/v1/agents/{agent_id}/browse` - Browse history
- POST `/api/v1/agents/{agent_id}/delete` - Delete records
- POST `/api/v1/agents/{agent_id}/download` - Download records in eval format
- GET `/api/v1/agents/versions` - List all agent+version combinations
- POST `/api/v1/agents/download-multi` - Download multiple agent+version combinations

### Feature 7: Response Caching

**Purpose**: Optimize token usage and improve performance by caching agent responses based on prompt, agent name, and agent version.

**How It Works**:
1. When an agent is invoked, the system first checks if an identical response already exists in the database
2. Cache lookup is based on exact match: `prompt + agent_name + agent_version`
3. **Cache hit**: Returns existing response immediately with `from_cache=true` (saves tokens and time)
4. **Cache miss**: Generates new response normally with `from_cache=false` and saves to database
5. Cache is automatically invalidated when agent instructions change (new version hash)

**Cache Key Components**:
- **Prompt**: Exact text match (case-sensitive, whitespace-sensitive)
- **Agent name**: Ensures different agents cache separately
- **Agent version**: Version hash from instruction set, ensures cache invalidation on instruction changes

**Benefits**:
- **Token savings**: 100% savings for repeated prompts (cache hits use 0 Azure AI tokens)
- **Performance**: 10-30x faster response times for cache hits (~100-200ms vs 1-3 seconds)
- **Cost reduction**: Significant cost savings for evaluation runs with repeated prompts
- **Consistency**: Identical prompts always return the same response (for given agent version)

**UI Indicators**:
- **Generate page**: Badge showing "From Cache" (cyan) or "Newly Generated" (green)
- **Batch processing**: Source column showing cache status for each item
- **History table**: Optional "Source" column (hidden by default)

**Sample Prompts Integration**:
The persona_distribution agent includes 50 sample prompts for evaluation:
- **35 Valid prompts**: Various domains (telecom, banking, healthcare, retail, insurance, etc.)
- **10 Invalid prompts**: Transcript-based scenarios not supported by the agent
- **5 Irrelevant prompts**: Off-topic requests unrelated to persona distribution
- Each sample includes `category` and `tags` for organization
- One-click "Load All Sample Prompts" button in batch processing UI
- First batch run generates all responses (~100k-300k tokens)
- Second batch run retrieves all from cache (0 tokens, 10-30x faster)

### Feature 8: Multi-Agent Download

**Purpose**: Download conversations from multiple agents with version filtering in a single eval-formatted file.

**Workflow**:
1. User navigates to `/agents/download` page
2. Frontend fetches all available agent+version combinations with conversation counts
3. User selects specific agent+version combinations via checkboxes
4. User clicks "Download Selected" button
5. Backend queries Cosmos DB for conversations matching each agent+version pair
6. Backend combines all conversations into flat list with eval format
7. Browser downloads single JSON file with all selected conversations

**Backend Implementation**:
- **GET `/api/v1/agents/versions`**: Lists all unique agent+version combinations with conversation counts
- **POST `/api/v1/agents/download-multi`**: Downloads selected conversations
  - Validates all agent_ids exist in AGENT_REGISTRY
  - For each selection, queries conversations by agent_name and agent_version
  - Transforms to eval format (same as single-agent download)
  - Returns single JSON file with flat list of all conversations
  - Filename: `multi_agent_evals_{timestamp}.json`

**Frontend Implementation**:
- Dedicated page at `/agents/download`
- Table showing agent versions with checkboxes
- Columns: Agent, Scenario Name, Version, Conversations
- Alert showing selection summary (versions count, total conversations)
- Download button (disabled when nothing selected)
- Row selection with checkboxes
- Real-time count of selected versions and total conversations

**Key Features**:
- Version-specific filtering (only conversations matching selected version)
- Flat list format (all conversations together)
- Compatible with eval framework
- No hard data size limits (typical: 1,000 conversations ≈ 2-5 MB)

### Feature 9: Workflows API

**Purpose**: Provides configuration and metadata for workflows that orchestrate multiple agents.

**Key Features**:
- List all available workflows with their agent configurations
- Get workflow details including all agent instructions
- Workflow execution routes remain in their respective modules

**Workflow Registry**:
The workflow configuration is centralized in `backend/app/modules/workflows/config.py`:
- `conversation_simulation` - Multi-turn conversation between C1 and C2 agents

**API Endpoints**:
- GET `/api/v1/workflows/list` - List all workflows
- GET `/api/v1/workflows/{workflow_id}` - Get workflow details with agent instructions

### Common Features Across All Features

**Request Features**:
- Non-streaming by default (streaming planned for future)
- Model is hardcoded in backend (GPT-4)
- Prompt input (varies by feature)

**Response Features**:
- Token usage tracking
- Timing metrics (milliseconds)
- Start and end timestamps (using `datetime.now(timezone.utc)`)
- Full response text or conversation history
- Copy-to-clipboard JSON export
- Conversation ID tracking

**Storage**:
- All results saved to Cosmos DB
- Document IDs use conversation_id from Azure AI
- Separate containers per feature
- JSON parsing for persona agents (parsed_output field)
- Complete request/response data
- Timestamps for analytics

**UI Features**:
- Clean, intuitive interface with Ant Design components
- Tab-based navigation (Generate/Batch/History)
- Real-time loading states with spinners
- Error handling with Alert components
- Toast notifications for success/error
- Metrics visualization
- Paginated history browsing
- Responsive design
- Table view for browsing past results with expandable rows
- Proper accessibility with ARIA labels
- **Agent instructions display**: All agent pages show the agent's instruction set (collapsible)
- **Workflow instructions display**: Workflow pages show all agent instructions in collapsible panels
- **Dynamic navigation**: Sidebar with "Agents" and "Workflows" sections

**History Table Enhancements**:
- **Column visibility controls**: Settings dropdown (⚙️) to show/hide columns
- **Document ID column**: Hidden by default, shows Cosmos DB document ID (copyable)
- **Conversation ID column**: Hidden by default, shows Azure AI conversation ID (copyable)
- **Fixed column widths**: 250px for timestamp, 250px for input/response to prevent horizontal scroll
- **Tooltips on hover**: View full text for long content
- **Ellipsis for overflow**: Prevents text breaking table layout
- **Consistent across all agent pages**: AgentHistoryTable component used by all agents

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

## Development Conventions

### Backend Conventions (Python/FastAPI)

#### Code Style
- Follow PEP 8 style guide
- Use type hints for all function parameters and returns
- Use async/await for I/O operations
- Use Pydantic for data validation
- **IMPORTANT**: Use `datetime.now(timezone.utc)` instead of deprecated `datetime.utcnow()`

#### Python Virtual Environment Usage
**CRITICAL: Always use the virtual environment (`backend/.venv/`) for all backend operations**

When running Python commands, pip operations, or testing imports:
- **Always** use the venv Python directly: `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux/Mac)
- **Never** use bare `python` or `pip` commands - they may use the global Python installation
- **Install dependencies**: `.venv/Scripts/python.exe -m pip install -r requirements.txt`
- **Test imports**: `.venv/Scripts/python.exe -c "import module"`
- **Run server**: `.venv/Scripts/python.exe -m uvicorn app.main:app --reload`
- Use forward slashes `/` in paths for bash compatibility

#### Naming Conventions
- Classes: PascalCase (e.g., `AzureAIService`)
- Functions/Methods: snake_case (e.g., `get_agent_response`)
- Constants: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
- Private methods: prefix with underscore (e.g., `_initialize_client`)

#### Model Naming Pattern (Result vs Response)
**Service Layer Models** - Use `*Result` suffix:
- Returned by service methods for internal use
- Contains all data needed by routes
- Example: `AgentInvokeResult`, `ConversationSimulationResult`

**API Layer Models** - Use `*Response` suffix:
- Returned by API endpoints to clients
- Public-facing schema
- Example: `AgentInvokeResponse`, `ConversationSimulationResponse`

**Pattern**:
```python
# Service layer
class AgentInvokeResult(BaseModel):
    response_text: str
    tokens_used: Optional[int] = None
    from_cache: bool = False  # Runtime property
    # ... other fields

# API layer
class AgentInvokeResponse(BaseModel):
    response_text: str
    tokens_used: Optional[int] = None
    from_cache: bool = False  # Passed through from Result
    # ... same fields as Result

# Route transforms Result → Response
@router.post("/invoke")
async def invoke_agent(...) -> AgentInvokeResponse:
    result = await service.invoke_agent(...)
    return AgentInvokeResponse(**result.model_dump())  # Includes from_cache
```

**Important**: The `from_cache` field is a **runtime property** of API responses only:
- Indicates whether THIS specific API call was served from cache
- Should be included in Result and Response models
- Should NOT be stored in database documents

#### File Organization
- **Full Vertical Slices**: Each module in `app/modules/` contains all code for a feature:
  - `routes.py`: API endpoints (transform Result → Response)
  - `models.py`: API schemas (Result models for service layer, Response models for API layer)
  - `*_service.py`: Business logic and persistence
  - `agents.py`: Agent creation logic
  - `instructions.py`: Agent instructions
- **Unified Agents Module** (`app/modules/agents/`):
  - `config.py`: Central registry of all agent configurations
  - `routes.py`: Unified API endpoints for all agents
  - `agents_service.py`: Generic agent invocation service
  - `models.py`: API schemas for agent operations
  - `configs/`: Individual config files for each agent
- **Workflows Module** (`app/modules/workflows/`):
  - `config.py`: Central registry of workflow configurations
  - `routes.py`: Workflow listing and details endpoints
  - `models.py`: API schemas for workflow operations
- **Shared Resources**:
  - `app/models/shared.py`: Common models (BaseResponse, AgentDetails, etc.)
  - `app/infrastructure/`: Shared infrastructure (DB, AI)
- **Infrastructure Services** (in `app/infrastructure/`):
  - `AzureAIService`: Client initialization and agent factory only
  - `CosmosDBService`: Database persistence
- Services are singletons
- Configuration in core/config.py
- Agent configurations are in individual files in `modules/agents/configs/` directory
- Registry loader in `modules/agents/config.py` discovers and loads all configs
- Workflow configuration is centralized in `modules/workflows/config.py`

#### Adding New Agents

To add a new agent, create a new config file in `app/modules/agents/configs/`:

**File naming**: `{agent_name}_config.py` (must end with `_config`)

**Structure**:
```python
"""Configuration for {Agent Name} Agent."""

from ..config import AgentConfig
from ..instructions import {AGENT}_INSTRUCTIONS

AGENT_CONFIG = AgentConfig(
    agent_id="agent_id",  # Unique ID (lowercase, underscores)
    agent_name="AgentName",  # Azure AI agent name
    display_name="Display Name",  # UI display name
    description="...",  # Brief description
    instructions={AGENT}_INSTRUCTIONS,  # From instructions.py
    container_name="single_turn_conversations",  # Cosmos DB container
    scenario_name="ScenarioName",  # For eval downloads
    input_field="prompt",  # DB field name
    input_label="Prompt",  # UI label
    input_placeholder="...",  # UI placeholder
    sample_inputs=[
        {
            "label": "Sample 1",
            "value": "...",
            "category": "Valid",  # Optional: "Valid", "Invalid", "Edge Case", etc.
            "tags": ["tag1", "tag2"]  # Optional: list of tags
        }
    ]
)
```

**Sample Input Guidelines**:
- Add category to help users understand prompt type
- Use tags for organization (e.g., `["billing", "technical"]`, `["positive-sentiment"]`)
- Categories: "Valid", "Invalid", "Edge Case", "Complex", "Simple"
- Tags: domain-specific keywords for filtering and analysis
- Large eval prompt sets are encouraged (config files are designed to scale)

**Registry Auto-Discovery**:
- No manual registration needed
- `load_agent_registry()` automatically discovers `*_config.py` files
- Agent appears in API endpoints immediately after adding config file
- Logs show successful loading on server start

#### Response Caching Pattern

**Purpose**: Optimize token usage and performance by caching agent responses.

**Implementation Pattern**:
```python
async def invoke_agent(self, agent_id: str, input_text: str, ...):
    # 1. Create agent to get version
    agent = azure_ai_service.create_agent(name, instructions)
    current_version = agent.agent_version_object.version

    # 2. Check cache
    cached_doc = await cosmos_db_service.query_cached_response(
        container_name=container,
        prompt=input_text,
        agent_name=agent_name,
        agent_version=current_version
    )

    # 3. Return cached response if found
    if cached_doc:
        return AgentInvokeResult(
            response_text=cached_doc.get("response"),
            tokens_used=cached_doc.get("tokens_used"),
            # ... reconstruct from cached_doc
            from_cache=True  # ✅ Cache hit
        )

    # 4. Generate new response on cache miss
    # ... normal generation flow ...

    # 5. Return with from_cache=False
    return AgentInvokeResult(
        response_text=response_text,
        # ... other fields
        from_cache=False  # ✅ Newly generated
    )
```

**Cache Key Strategy**:
- **Exact match** on: `prompt + agent_name + agent_version`
- Case-sensitive and whitespace-sensitive matching
- Agent version ensures cache invalidation when instructions change
- Different agents cache separately (same prompt, different agent = different cache entries)

**Best Practices**:
1. **Check cache before generation**: Avoids unnecessary Azure AI API calls
2. **Graceful error handling**: Cache query errors should not block generation
3. **Log cache hits/misses**: Use `logger.info()` for cache hits, `logger.debug()` for details
4. **Don't persist `from_cache`**: It's a runtime property, not a document property
5. **Return cached metrics**: Include original tokens_used and time_taken_ms from cached document

**Error Handling**:
```python
try:
    cached_doc = await cosmos_db_service.query_cached_response(...)
except Exception as e:
    logger.warning("Cache query failed, proceeding with generation", error=str(e))
    cached_doc = None  # Graceful fallback
```

**Database Query**:
```python
async def query_cached_response(...) -> Optional[Dict[str, Any]]:
    query = """
        SELECT TOP 1 * FROM c
        WHERE c.prompt = @prompt
        AND c.agent_name = @agent_name
        AND c.agent_version = @agent_version
        ORDER BY c.timestamp DESC
    """
    # Returns most recent match or None
```

#### Configuration (.env)
- Backend settings are loaded from `backend/.env` via `app/core/config.py` using an absolute path, so starting the server from the repo root (or other folders) still picks up the correct environment.

#### Error Handling
- Use HTTPException for API errors
- Include descriptive error messages
- Log errors with structlog
- Always include `exc_info=True` in error logs for stack traces

#### Logging (Verbose Mode for Local Development)
**Configuration**:
- **Centralized Configuration**: Logging logic encapsulated in `app/core/logging.py`
- Uses `structlog` with `ConsoleRenderer(colors=True)` for human-readable console output
- Configured in `main.py` via `setup_logging()` **BEFORE** importing routes
- Routes imported after logging configuration to ensure services use configured logging
- Log level controlled by `settings.api_debug` (DEBUG when True, INFO when False)
- All logs use structured logging with key-value pairs for better filtering
- **Dual Output**: Logs are written to both console (colored) and file (plain text)
- **File Logging**:
  - Location: `logs/mount_doom.log` (configurable via `settings.log_dir` and `settings.log_file`)
  - Rotation: Automatic rotation at 10MB (configurable via `settings.log_max_bytes`)
  - Backup: Keeps 5 backup files (configurable via `settings.log_backup_count`)
  - Format: ISO 8601 Timestamp with structured fields
  - Encoding: UTF-8
- **External Library Logging**:
  - Azure SDK logs (`azure`, `azure.core`, `azure.ai`, `azure.ai.projects`) suppressed to WARNING level
  - OpenAI client logs (`openai`) suppressed to WARNING level
  - HTTP client logs (`httpx`, `httpcore`, `urllib3`) suppressed to WARNING level
  - Uvicorn loggers configured to propagate to root logger
  - Python warnings captured and sent through logging system at WARNING level

**Logging Levels and Usage**:
- `logger.info()`: Key operations, milestones, and important state changes
  - Service initialization
  - Request start/end with key parameters
  - Major workflow steps
  - Database operations
  - Final results

- `logger.debug()`: Detailed operational information
  - Agent cache hits/misses
  - Document IDs and container names
  - Response text extraction steps
  - Token usage extraction attempts
  - Message previews and lengths

- `logger.error()`: Errors and exceptions
  - Always include `error=str(e)` parameter
  - Always include `exc_info=True` for stack traces
  - Log at service level and route level

**What to Log**:
1. Service initialization (client initialization, connection strings)
2. Agent operations (agent creation, cache hits/misses, version info)
3. Conversation simulation (stream events, workflow actions, messages, token usage)
4. API requests (key parameters, prompt lengths, model/agent names)
5. Responses (text length and preview, token usage, time taken)
6. Database operations (container checks, document creation, save confirmations)

**Structured Logging Best Practices**:
- Use key-value pairs: `logger.info("Message", key1=value1, key2=value2)`
- Use consistent key names across services
- Include units in key names: `time_ms`, `prompt_length`, `tokens_used`
- Use section separators for major operations: `logger.info("="*60)`
- Preview long text: `text[:150] + "..." if len(text) > 150 else text`
- Round floats for readability: `round(time_ms, 2)`

**Example Logging Pattern**:
```python
logger.info("="*60)
logger.info("Starting operation", param1=value1, param2=value2)
logger.debug("Detailed step", detail1=value1)
logger.info("Operation completed", result=value, time_ms=round(ms, 2))
logger.info("="*60)
```

### Frontend Conventions (TypeScript/Next.js)

#### Code Style
- Use TypeScript for all files
- Use 'use client' directive for client components
- Server components by default
- Proper error boundaries

#### Modular Component Pattern
Agent pages use a modular architecture with nested routes and reusable components.

**Agent Pages Structure**
Agent pages use Next.js nested routes with a shared layout:

**Layout** (`/agents/[agentId]/layout.tsx`):
- Loads agent info once via `apiClient.getAgent(agentId)`
- Provides agent info to children via `AgentContext`
- Renders `AgentTabs` navigation
- Handles loading and error states

**Generate Page** (`/agents/[agentId]/page.tsx`):
```typescript
'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { useAgentContext } from '@/components/agents/shared/AgentContext'
import AgentInstructionsCard from '@/components/agents/instructions/AgentInstructionsCard'
import AgentResultCard from '@/components/agents/result/AgentResultCard'
import { apiClient } from '@/lib/api-client'

export default function AgentGeneratePage() {
  const params = useParams()
  const agentId = params.agentId as string
  const { agentInfo } = useAgentContext()

  // State and handlers...

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <AgentInstructionsCard instructions={agentInfo.instructions} />
      {/* Form and input fields */}
      {result && <AgentResultCard result={result} />}
    </Space>
  )
}
```

**Reusable Components**:
- **AgentContext** - Share agent info across pages
- **AgentInstructionsCard** - Collapsible instructions display
- **AgentResultCard** - Inline result display with JSON/Plain Text toggle
- **AgentResultModal** - Modal for viewing result details
- **BatchProcessingSection** - Complete batch processing UI
- **AgentHistoryTable** - Full-featured history table with auto-load
- **AgentTabs** - Tab-like navigation

**Workflow Pages Pattern**
For workflows that orchestrate multiple agents, implement custom pages with:
- Three tabs: Simulate, Batch Processing, History
- All state management within the page component
- Custom rendering for conversation display
- Custom history columns specific to workflow needs

#### Timezone Handling
- Always use `useTimezone()` hook to access `formatTimestamp()` and `formatTime()` functions
- Never use raw `toLocaleString()` or `toISOString()` for user-facing timestamps
- Timezone state is global and persisted to localStorage
- Default timezone is IST (Asia/Kolkata)

#### Naming Conventions
- Components: PascalCase (e.g., `ResultDisplay`)
- Files: kebab-case (e.g., `api-client.ts`)
- Functions: camelCase (e.g., `handleSubmit`)
- Constants: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)

#### Component Structure
- Props interfaces defined inline or separately
- State management with useState
- Side effects with useEffect
- Form handling with controlled components
- Tab-based navigation for generate/history views

#### Styling
- Ant Design components with default styling
- Inline styles for custom layouts
- Responsive design with Ant Design grid system
- Proper accessibility with ARIA labels and semantic HTML

#### UI Components (Ant Design)
Standard components used across pages:
- `Button` - Primary actions (with loading states)
- `Card` - Content containers
- `Tabs` - Generate/History navigation
- `Table` - Display history with pagination
- `Input` - Form inputs (Input, TextArea)
- `Space` - Layout spacing
- `Typography` - Text elements (Title, Paragraph, Text)
- `Alert` - Error and info messages
- `message` - Toast notifications
- `Tag` - Status and label indicators

#### Page Structure Pattern
All feature pages follow this structure:
1. **Header**: Title and description (via PageLayout component)
2. **Tabs**: Generate/Validate/Simulate tab, Batch Processing tab, and History tab
3. **Generate/Validate/Simulate Tab**: Configuration form, Submit button, Result display
4. **Batch Processing Tab**: JSON input, configurable delay, progress display, results table
5. **History Tab**: Table with past results, pagination controls

#### Batch Processing Pattern
When adding batch support to a page:

**State Management**:
```typescript
const [batchItems, setBatchItems] = useState<BatchItem[]>([])
const [batchLoading, setBatchLoading] = useState(false)
const [batchProgress, setBatchProgress] = useState(0)
const [currentBatchIndex, setCurrentBatchIndex] = useState(-1)
const [batchJsonInput, setBatchJsonInput] = useState('')
const [stopBatchRequested, setStopBatchRequested] = useState(false)
const [batchDelay, setBatchDelay] = useState(5)
```

**BatchItem Interface**:
- For agents: `{ key, prompt, status, result?, error? }`
- For workflows: `{ key, customerIntent, customerSentiment, conversationSubject, status, result?, error? }`

**Core Functions**:
1. `loadBatchItemsFromText()` - Parse JSON (array or object with items array)
2. `runBatchProcessing()` - Main loop with delays and stop handling
3. `handleStopBatch()` - Set stop flag to gracefully exit

**UI Components**:
- TextArea for JSON input
- Select component for delay selection (5-60 seconds)
- Buttons: "Load Items", "Start Batch", "Stop Batch"
- Progress bar with current item indicator
- Table with Status column and expandable rows

### API Design

#### Request/Response Format
- All requests: JSON body
- All responses: JSON with standard structure
- Include metadata (tokens, timing) in all responses
- Use Pydantic models for validation

#### Endpoint Structure
- RESTful design
- Versioned API (`/api/v1/`)
- Grouped by use case
- GET for retrieval, POST for actions

#### Standard Endpoints Per Use Case
Each use case follows this pattern:
- POST `/{use-case}/generate|validate|simulate` - Create new result
- GET `/{use-case}/browse` - List past results with pagination

#### Browse Endpoint Pattern
All browse endpoints support:
- `page` (default: 1) - Page number
- `page_size` (default: 10, max: 100) - Items per page
- `order_by` (default: "timestamp") - Field to sort by
- `order_direction` (default: "DESC") - Sort direction (ASC|DESC)

Response includes:
- `items` - Array of results
- `total_count` - Total number of items
- `page` - Current page number
- `page_size` - Items per page
- `total_pages` - Total number of pages
- `has_next` - Boolean indicating if next page exists
- `has_previous` - Boolean indicating if previous page exists

**IMPORTANT - Field Name Mapping**:
Browse endpoints return raw Cosmos DB documents, NOT formatted API response schemas.
Frontend history tables must use Cosmos DB field names:
- Use `timestamp` (NOT `start_time`)
- Use `response` (NOT `response_text`)
- Use `prompt` (same in both)
- Use `tokens_used` (same in both)
- Use `time_taken_ms` (same in both)

### Database (Cosmos DB)

#### CosmosDBService - Infrastructure Only
The CosmosDBService is a singleton infrastructure service that:
- Manages Cosmos DB client and database references
- Provides container name constants for all features
- Offers generic operations (ensure_container, save_document, browse_container)
- Does NOT contain feature-specific business logic or document structures

#### Feature Service Persistence
Each feature service handles its own database persistence:
- Defines document structure specific to the feature
- Uses conversation_id from Azure AI as document ID
- Creates documents with all required fields
- Calls `cosmos_db_service.save_document()` for actual persistence

Example pattern:
```python
async def save_to_database(self, ...params, conversation_id: str):
    # Define document structure (business logic)
    document = {
        "id": conversation_id,
        "prompt": prompt,
        "response": response,
        "parsed_output": parsed_output,  # For persona agents
        # ... other fields specific to this feature
    }

    # Use generic infrastructure method
    await cosmos_db_service.save_document(
        container_name=cosmos_db_service.CONTAINER_NAME,
        document=document
    )
```

#### Container Strategy
- One container per feature
- Partition key: `/id`
- Auto-create containers if missing
- Store complete request/response data

#### Document Structure
- Document ID: conversation_id from Azure AI (ensures uniqueness)
- Include timestamp
- Include all metrics
- Include complete agent details (name, version, instructions, model, timestamp)
- Include parsed_output for JSON-based agents
- Use ISO format for dates
- Structure defined by feature services, not CosmosDBService

### Azure Integration

#### Azure AI Projects SDK Documentation
**Important References** - Read these before making changes to Azure AI integration:
- [AIProjectClient Class Documentation](https://learn.microsoft.com/en-us/python/api/azure-ai-projects/azure.ai.projects.aio.aiprojectclient?view=azure-python-preview)
- [OpenAIClient Class Documentation](https://learn.microsoft.com/en-us/python/api/azure-ai-projects/azure.ai.projects.aio.openaiclient?view=azure-python-preview)
- [Azure AI Projects Agents Code Samples](https://github.com/Azure/azure-sdk-for-python/tree/azure-ai-projects_2.0.0b3/sdk/ai/azure-ai-projects/samples/agents)

#### AzureAIService - Client Factory Only
The AzureAIService is now a **singleton client factory** with minimal responsibility:
- `client` property: Returns initialized AIProjectClient
- `openai_client` property: Returns OpenAI client (conversation API)
- `create_agent(name, instructions, model)`: Creates and returns Agent NamedTuple

**Does NOT contain**:
- Business logic for any use case
- Generic methods like `get_agent_response()` or `get_model_response()`
- Use case-specific workflows
- Agent caching strategies
- Prompt building or formatting

#### Service-Specific Agent Configuration
Each feature service contains:
- Fixed `agent_name` and `instructions` for that feature
- Agent creation logic by calling `azure_ai_service.create_agent()`
- Workflow-specific logic (conversation management, agent orchestration)
- Metrics tracking and data transformation

#### Agent Instructions Storage
- All agent instructions are stored as Python string constants in `backend/app/modules/agents/instructions.py`
- Instructions are centralized in a single file for easy management
- Each instruction is a constant: `{AGENT_TYPE}_INSTRUCTIONS`
- Services and agent configs import the instruction constants directly

#### Agent Usage Pattern
```python
# In your service class:
from app.modules.agents.instructions import PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS

class PersonaDistributionService:
    AGENT_NAME = "PersonaDistributionGeneratorAgent"
    INSTRUCTIONS = PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS

async def your_method(self, prompt: str):
    # Create agent using AzureAIService
    agent = azure_ai_service.create_agent(
        agent_name=self.AGENT_NAME,
        instructions=self.INSTRUCTIONS
    )

    # Use agent to process prompt
    conversation = azure_ai_service.openai_client.conversations.create(
        items=[{"type": "message", "role": "user", "content": prompt}]
    )

    response = azure_ai_service.openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent": {"name": agent.agent_version_object.name, "type": "agent_reference"}},
        input=""
    )
```

#### Conversation Management
- Use conversations (not threads) for stateful interactions
- Create conversations: `openai_client.conversations.create(items=[...])`
- Add messages: `openai_client.conversations.items.create(conversation_id, items=[...])`
- Create responses: `openai_client.responses.create(conversation=conversation_id, extra_body={...})`
- Each conversation maintains full context across all interactions
- Reuse conversation_id across multiple agent invocations for workflows

#### Workflow Pattern (ConversationSimulationService)
For conversation simulation with multiple agents:
- Single conversation per simulation maintained across all turns
- All agents (C1, C2) operate on same conversation for context continuity
- Each agent invocation:
  1. Adds message to shared conversation
  2. Creates response using agent
  3. Returns tokens and response text
- Workflow continues until completion status or max_turns reached

#### Automatic Versioning
- Generate version hash from instruction set: `hashlib.sha256(instructions.encode()).hexdigest()[:8]`
- Format as version string: `f"v{instructions_hash}"`
- Used for tracking agent versions in metrics and database

### Environment Management

#### Backend
- Use .env file for configuration
- Provide .env.example template
- Never commit secrets
- Use Azure KeyVault for production secrets

#### Environment Variables for Services
**Cosmos DB Configuration**:
- `COSMOS_DB_ENDPOINT` - Cosmos DB endpoint URL (cloud or emulator)
- `COSMOS_DB_DATABASE_NAME` - Database name
- `COSMOS_DB_USE_EMULATOR` - Set to `true` for local emulator, `false` for cloud
- `COSMOS_DB_KEY` - Emulator key (only needed for local emulator)

**Cloud Configuration** (production):
```env
COSMOS_DB_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOS_DB_DATABASE_NAME=mount_doom_db
COSMOS_DB_USE_EMULATOR=false
# No COSMOS_DB_KEY needed - uses DefaultAzureCredential
```

**Local Emulator Configuration** (development):
```env
COSMOS_DB_ENDPOINT=https://localhost:8081
COSMOS_DB_DATABASE_NAME=mount_doom_db
COSMOS_DB_USE_EMULATOR=true
COSMOS_DB_KEY=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==
```

#### Frontend
- Use NEXT_PUBLIC_ prefix for public variables
- Provide .env.local.example template
- Keep API URL configurable
- Never expose backend secrets

### Git Workflow

#### Branches
- main: production-ready code
- feature/: new features
- fix/: bug fixes
- docs/: documentation updates

#### Commits
- Clear, descriptive messages
- Follow conventional commits
- One logical change per commit
- Reference issues when applicable

### Performance Considerations

#### Backend
- Use async/await for I/O
- **Lazy initialization** - Services initialize clients only on first use
  - Prevents unnecessary connections during dev mode restarts
  - Improves startup time in development
  - First request may be slightly slower due to initialization
- Implement connection pooling
- Cache expensive operations
- Monitor token usage

#### Frontend
- Lazy load components
- Optimize images
- Minimize bundle size
- Use Next.js optimization features

### Documentation

#### Documentation Files Policy
**IMPORTANT**: Documentation should ONLY exist in the following locations:
- `README.md` files (root, backend, frontend)
- `CLAUDE.md` (this file) - Comprehensive project documentation
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
- All relevant information should be in README files or CLAUDE.md
- Planning and notes should be done in PR descriptions or issues, not committed files

#### Code Documentation
- Docstrings for all public functions
- Type hints serve as documentation
- Comments only when necessary
- Self-documenting code preferred

#### API Documentation
- Automatic OpenAPI/Swagger docs
- Include request/response examples
- Document error responses
- Keep docs up to date

### Response Metrics to Track
All API responses should include:
- `response_text` - The generated text
- `tokens_used` - Token count from Azure AI
- `time_taken_ms` - Calculated with `time.time() * 1000`
- `start_time` - ISO timestamp (`datetime.now(timezone.utc)`)
- `end_time` - ISO timestamp
- `agent_details` - Complete agent information

### Local Tooling Conventions

#### CXA Evals Runner
- `cxa_evals/` is a repo-root folder for running CXA AI Evals locally
- The CLI executable `Microsoft.CXA.AIEvals.Cli.exe` is manually downloaded and must not be committed
- The `output/` directory under `cxa_evals/` must not be committed (results are gitignored)
- Evals now run for `SimulationAgent` at once - no need for separate per-agent runs
- The `scenario_name` field in input files distinguishes between different agent types
- Config files: `default_config.json` (default metrics) and `cutom_config.json` (custom rules)
- Input files are stored in `cxa_evals/input/` directory

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
- Only maintain README files and CLAUDE.md
- Do NOT create summary/status/checklist markdown files (they clutter the repo)
- Planning and notes go in PR descriptions or issues, not committed files

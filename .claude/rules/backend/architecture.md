---
paths:
  - "backend/**/*.py"
---

# Backend Architecture

## Clean Architecture with Vertical Slices

### Structure
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

## Unified Agents Module (modules/agents/)

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

## Workflows Module (modules/workflows/)

A module for workflow configurations that orchestrate multiple agents:

**Workflow Configuration Registry (config.py)**
- Maintains `WORKFLOW_REGISTRY` dictionary with workflow configurations
- Each `WorkflowConfig` contains: workflow_id, display_name, description, agents list, route_prefix
- Each `WorkflowAgentConfig` contains: agent_id, agent_name, display_name, role, instructions
- Currently contains: conversation_simulation workflow with C1 and C2 agents

**Workflow Routes (routes.py)**
- `GET /api/v1/workflows/list` - List all available workflows with agent details
- `GET /api/v1/workflows/{workflow_id}` - Get specific workflow details including agent instructions

## Key Principles

- **Separation of Concerns**: Each service handles one feature's business logic
- **Layered Architecture**: Clear separation between routes (API layer) and services (business logic layer)
- **Dependency Injection**: Routes depend on services, not directly on Azure AI
- **Single Responsibility**: Each service class has one reason to change
- **Clean Architecture Layers**: Inward dependencies only
- **Lazy Initialization**: Clients are initialized on first access to speed up dev mode restarts

## Service Architecture

### AzureAIService

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

### Feature Services

- **UnifiedAgentsService** (`modules/agents/agents_service.py`): Handles all agent operations using agent configurations from the registry
- **ConversationSimulationService**: Workflow orchestration for multi-turn conversations (C1 service rep/C2 customer). Uses dedicated module in `modules/workflows/conversation_simulation/`
- Services contain:
  - Agent configuration (name, instructions, model deployment)
  - Workflow logic specific to the feature
  - Conversation management
  - Token and timing tracking
  - Data transformation and formatting
  - **Database persistence logic** (document structure, ID generation, saving)

### CosmosDBService

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

## Routes

### Unified Agents API (Primary API for Agents)
- `/api/v1/agents/*` - Unified agents API
  - GET `/list` - List all agents with configurations and instructions
  - GET `/versions` - List all agent+version combinations with counts
  - POST `/download-multi` - Download multiple agent+version combinations
  - GET `/{agent_id}` - Get specific agent details
  - POST `/{agent_id}/invoke` - Invoke agent with input
  - GET `/{agent_id}/browse` - Browse agent history
  - POST `/{agent_id}/delete` - Delete agent records
  - POST `/{agent_id}/download` - Download agent records in standardized eval format

### Workflows API
- `/api/v1/workflows/*` - Workflow configurations
  - GET `/list` - List all workflows with agent details
  - GET `/{workflow_id}` - Get specific workflow details

### Conversation Simulation (Multi-Turn Workflow)
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

## Data Flow

### Generation/Processing Flow (with Response Caching)
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

### Browse/History Flow
1. User switches to History tab
2. Frontend calls browse API methods with pagination parameters
3. **Backend Route Handler**: Calls CosmosDBService.browse_container()
4. **CosmosDBService**: Queries Cosmos DB with ordering, applies pagination, returns items with pagination metadata
5. Backend returns paginated response
6. Frontend displays results in Table component
7. User can navigate pages using pagination controls

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

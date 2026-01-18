# Mount Doom - Project Architecture

## Overview

### Updated Agent Behavior Guidelines
- C2Agent: Added behavior guidelines to restrict responses to simulation prompts only.
- Persona Distribution Generator Agent: Added behavior guidelines to restrict responses to simulation prompts only.

Mount Doom is a fullstack AI agent simulation platform with FastAPI backend and Next.js frontend.

## Backend Architecture (Clean Architecture)

### Structure
```
backend/app/
├── core/                 # Configuration and settings
├── models/               # Shared/Common models
│   ├── shared.py         # Common API and DB schemas
│   └── single_agent.py   # Shared schemas for single-agent operations
├── infrastructure/       # Infrastructure services
│   ├── ai/
│   │   └── azure_ai_service.py # Client initialization
│   └── db/              # Database services
│       └── cosmos_db_service.py
├── modules/             # Feature modules (Vertical Slices)
│   ├── shared/          # Reserved for future shared utilities
│   │   └── __init__.py
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
│       └── conversation_simulation/  # Multi-agent workflow
│           ├── __init__.py
│           ├── agents.py    # C1 and C2 agent factories
│           ├── conversation_simulation_service.py  # Orchestration logic
│           ├── models.py    # API schemas
│           └── routes.py    # Simulation endpoints
└── main.py               # FastAPI application
```

### Unified Agents Module (modules/agents/)
A centralized module that provides a single API for all single-agent operations:

#### Centralized Instructions (instructions.py)
All agent instructions are consolidated in a single file:
- `PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS`
- `PERSONA_GENERATOR_AGENT_INSTRUCTIONS`
- `TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS`
- `C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS`
- `C1_AGENT_INSTRUCTIONS`

#### Agent Configuration Registry (config.py)
- Maintains `AGENT_REGISTRY` dictionary with all agent configurations
- Each `AgentConfig` contains: agent_id, agent_name, display_name, description, instructions, container_name, input_field, input_label, input_placeholder
- Imports instructions from centralized `instructions.py`
- Provides helper functions: `get_agent_config()`, `get_all_agents()`, `list_agent_ids()`

#### Unified Agents Service (agents_service.py)
- Generic service that can invoke any agent by agent_id
- Uses agent config to determine instructions and container
- Handles conversation creation, response extraction, JSON parsing
- Saves results to the appropriate Cosmos DB container

#### Unified Agents Routes (routes.py)
- `GET /api/v1/agents/list` - List all available agents with configurations
- `GET /api/v1/agents/{agent_id}` - Get specific agent details including instructions
- `POST /api/v1/agents/{agent_id}/invoke` - Invoke agent with input
- `GET /api/v1/agents/{agent_id}/browse` - Browse agent history
- `POST /api/v1/agents/{agent_id}/delete` - Delete agent records
- `POST /api/v1/agents/{agent_id}/download` - Download agent records

### Workflows Module (modules/workflows/)
A module for multi-agent workflow configurations:

#### Workflow Configuration Registry (config.py)
- Maintains `WORKFLOW_REGISTRY` dictionary with workflow configurations
- Each `WorkflowConfig` contains: workflow_id, display_name, description, agents list, route_prefix
- Each `WorkflowAgentConfig` contains: agent_id, agent_name, display_name, role, instructions
- Currently contains: conversation_simulation workflow with C1 and C2 agents

#### Workflow Routes (routes.py)
- `GET /api/v1/workflows/list` - List all available workflows with agent details
- `GET /api/v1/workflows/{workflow_id}` - Get specific workflow details including agent instructions

### Key Principles
- **Separation of Concerns**: Each service handles one feature's business logic
- **Layered Architecture**: Clear separation between routes (API layer) and services (business logic layer)
- **Dependency Injection**: Routes depend on services, not directly on Azure AI
- **Single Responsibility**: Each service class has one reason to change
- **Clean Architecture Layers**: Inward dependencies only

### Service Architecture

#### AzureAIService
**Responsibility**: Client initialization and agent/client factory


**Lazy Initialization**: Clients are initialized on first access, not on module import.
This prevents unnecessary connections during dev mode restarts.

Only contains:
- `client` property: Returns AIProjectClient instance (lazy initialization)
- `openai_client` property: Returns OpenAI client instance (lazy initialization)
- `create_agent()` method: Creates agents with given name, instructions, and model
- `_initialize_client()` private method: Initializes clients when first accessed

Does NOT contain:
- Business logic for any use case
- Generic methods that wrap Azure API calls
- Caching of use case-specific agents
- Prompt building or workflow orchestration

**Token Management**: Uses DefaultAzureCredential which automatically handles token refresh.
No manual token management required.

### Azure AI References
For more details on Azure AI Agent Service and Workflow:
- [Sample Workflow Multi-Agent](https://raw.githubusercontent.com/Azure/azure-sdk-for-python/refs/tags/azure-ai-projects_2.0.0b2/sdk/ai/azure-ai-projects/samples/agents/sample_workflow_multi_agent.py)
- [Workflow Concepts](https://raw.githubusercontent.com/MicrosoftDocs/azure-ai-docs/refs/heads/main/articles/ai-foundry/default/agents/concepts/workflow.md)
- [Azure AI Projects SDK README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/README.md)
- [Azure AI Documentation](https://github.com/MicrosoftDocs/azure-ai-docs/tree/main/articles/ai-foundry/default/agents)

#### Feature Services
- **UnifiedAgentsService** (`modules/agents/agents_service.py`): Handles all single-agent operations. Uses agent configurations from the registry.
- **ConversationSimulationService**: Multi-agent conversation orchestration (C1/C2). Still uses dedicated module in `modules/conversation_simulation/`.

Services contain:
- Agent configuration (name, instructions, model deployment)
- Workflow logic specific to the feature
- Conversation management
- Token and timing tracking
- Data transformation and formatting
- **Database persistence logic** (document structure, ID generation, saving)

#### CosmosDBService
**Infrastructure service for Cosmos DB - Singleton pattern**

**Lazy Initialization**: Client is initialized on first access, not on module import.
This prevents unnecessary connections during dev mode restarts.

**Local Emulator Support**: Supports both Azure Cloud Cosmos DB and local Cosmos DB Emulator:
- Cloud mode: Uses DefaultAzureCredential for authentication
- Emulator mode: Uses emulator key (no Azure authentication required)
- Configured via `COSMOS_DB_USE_EMULATOR` environment variable

Responsibilities:
- Client initialization and management (lazy)
- Database reference management  
- Generic container operations
- Container name constants

Methods:
- `client` property: Returns CosmosClient instance (lazy initialization)
- `database` property: Returns database client (lazy initialization)
- `ensure_container()` - Ensure a container exists, create if needed
- `save_document()` - Generic method to save any document to a container
- `browse_container()` - Browse container with pagination and ordering
  - Supports custom ordering by field (default: timestamp DESC)
  - Returns paginated results with total count and page info
  - Used by all browse endpoints

Does NOT contain:
- Feature-specific business logic
- Document structure definitions
- Feature-specific save methods

### Routes

#### Unified Agents API (Primary API for Single Agents)
- `/api/v1/agents/*` - Unified agents API
  - GET `/list` - List all agents with configurations and instructions
  - GET `/{agent_id}` - Get specific agent details
  - POST `/{agent_id}/invoke` - Invoke agent with input
  - GET `/{agent_id}/browse` - Browse agent history
  - POST `/{agent_id}/delete` - Delete agent records
  - POST `/{agent_id}/download` - Download agent records

#### Workflows API
- `/api/v1/workflows/*` - Workflow configurations
  - GET `/list` - List all workflows with agent details
  - GET `/{workflow_id}` - Get specific workflow details

#### Conversation Simulation (Multi-Agent Workflow)
- `/api/v1/conversation-simulation/*` - Delegates to ConversationSimulationService
  - POST `/simulate` - Simulate conversation between C1 and C2 agents
  - GET `/browse` - Browse past simulations with pagination
  - POST `/delete` - Delete selected records
  - POST `/download` - Download selected records as JSON

Routes only:
1. Extract request parameters
2. Call appropriate service method
3. Save results via service's save_to_database() method
4. Return formatted response

## Frontend Architecture

### Structure
```
frontend/
├── app/                        # Next.js App Router pages
│   ├── agents/                 # Dynamic agents pages
│   │   └── [agentId]/          # Dynamic route for any agent
│   │       └── page.tsx
│   ├── workflows/              # Workflow pages
│   │   └── conversation_simulation/
│   │       └── page.tsx
│   ├── c2-message-generation/  # C2 message generation page
│   ├── conversation-simulation/ # Conversation simulation page
│   ├── persona-distribution/   # Persona distribution page
│   ├── persona-generator/      # Persona generator page
│   └── transcript-parser/      # Transcript parser page
├── components/                 # React components
│   ├── PageLayout.tsx          # Reusable page layout with navigation
│   ├── SingleAgentTemplate.tsx # Template for single-agent pages
│   └── MultiAgentTemplate.tsx  # Template for multi-agent workflows
└── lib/                        # Utilities and API client
    ├── api-client.ts           # Backend API client (includes agents and workflows APIs)
    ├── types.ts                # Shared TypeScript types
    └── timezone-context.tsx    # Global timezone context (UTC/IST)
```

### Key Principles
- **Template-based UI**: Single-agent and multi-agent pages use reusable templates
- **Global timezone support**: User can toggle between UTC and IST (default: IST)
- **Dynamic routing**: Agents pages use dynamic [agentId] routing
- **Instructions display**: All agent pages show the agent's instruction set
- Component reusability
- Type safety with TypeScript
- Responsive design with Ant Design
- Accessible UI with Ant Design components
- Tab-based interface for generate, batch, and history views

### Navigation Structure
The navigation sidebar organizes pages into two main sections:
- **Agents** - Individual agents for single-agent operations
  - Persona Distribution Generator
  - Persona Generator
  - Transcript Parser
  - C2 Message Generator
- **Workflows** - Multi-agent workflows
  - Conversation Simulation

### Templates

#### SingleAgentTemplate
Reusable template for single-agent features with three tabs:
- **Generate Tab**: Form for creating single requests with sample inputs
- **Batch Tab**: Process multiple inputs with configurable delay
- **History Tab**: Paginated view of past results with filter, sort, download, multi-select, delete

Configuration via `SingleAgentConfig`:
- `title`, `description`, `pageKey`
- `inputLabel`, `inputPlaceholder`, `inputFieldName`
- `sampleInputs` - Example prompts/inputs
- API functions: `generateFn`, `browseFn`, `deleteFn`, `downloadFn`
- Optional: `historyColumns`, `renderParsedOutput`

Pages using SingleAgentTemplate:
- Persona Distribution
- Persona Generator
- Transcript Parser
- C2 Message Generation

#### MultiAgentTemplate
Reusable template for multi-agent features with three tabs:
- **Simulate Tab**: Form with configurable input fields and sample configurations
- **Batch Tab**: Process multiple configurations in batch
- **History Tab**: Paginated view with expandable rows showing conversation history

Configuration via `MultiAgentConfig`:
- `title`, `description`, `pageKey`
- `inputFields` - Dynamic input field configuration
- `sampleConfigs` - Example configurations
- API functions: `simulateFn`, `browseFn`, `deleteFn`, `downloadFn`
- Optional: `historyColumns`, `renderConversation`

Pages using MultiAgentTemplate:
- Conversation Simulation

### Timezone Context
Global timezone management via React Context:
- Provider: `TimezoneProvider` wraps the app in layout.tsx
- Hook: `useTimezone()` returns `{ timezone, setTimezone, formatTimestamp, formatTime }`
- Supported timezones: UTC, IST (Asia/Kolkata)
- Default: IST
- Persisted to localStorage

### Pages
Each feature has a dedicated page that configures and renders the appropriate template:
- `/c2-message-generation` - SingleAgentTemplate with C2 message generation config
- `/persona-distribution` - SingleAgentTemplate with persona distribution config
- `/persona-generator` - SingleAgentTemplate with persona generator config
- `/transcript-parser` - SingleAgentTemplate with transcript parser config
- `/conversation-simulation` - MultiAgentTemplate with conversation simulation config

## Data Flow

### Generation/Processing Flow
1. User interacts with frontend UI (Generate tab)
2. Frontend calls API client methods
3. API client sends HTTP requests to backend
4. **Backend Route Handler**:
   - Validates request parameters
   - Calls appropriate service method
5. **Service Layer**:
   - Orchestrates business logic
   - Uses AzureAIService to create agents/clients
   - Manages conversation flow
   - Tracks metrics (tokens, timing)
   - Defines document structure for persistence
   - Calls CosmosDBService.save_document() to persist data
6. **AzureAIService**:
   - Creates agents or gets clients
   - Communicates with Azure AI API
7. **CosmosDBService**:
   - Provides generic infrastructure for Cosmos DB operations
   - Ensures containers exist
   - Saves documents with generic save_document() method
8. Backend returns response to frontend
9. Frontend displays results with metrics in Generate tab
10. Frontend reloads history to show new result

### Browse/History Flow
1. User switches to History tab
2. Frontend calls browse API methods with pagination parameters
3. **Backend Route Handler**:
   - Calls CosmosDBService.browse_container()
4. **CosmosDBService**:
   - Queries Cosmos DB with ordering
   - Applies pagination (page, page_size)
   - Returns items with pagination metadata
5. Backend returns paginated response
6. Frontend displays results in Table component
7. User can navigate pages using pagination controls

## Authentication
- Uses Azure DefaultAzureCredential
- Supports multiple auth methods (CLI, Managed Identity, etc.)
- **Automatic token refresh** - DefaultAzureCredential handles token refresh automatically
- No manual token management required
- For local Cosmos DB emulator, no Azure authentication needed (uses emulator key)

## Error Handling
- Backend: HTTP exceptions with appropriate status codes
- Frontend: Error state display with user-friendly messages
- Logging: Structured logging with structlog

## Performance Tracking
- Token usage tracked for all AI interactions
- Timing metrics for all requests
- Per-message metrics in conversations
- All metrics visible in UI

## Multi-Agent Workflow (Conversation Simulation)

### Architecture
The conversation simulation uses a shared conversation multi-agent workflow where:
1. Single conversation is created at the start
2. Conversation is reused across all agent invocations for context continuity
3. Agents operate sequentially by adding messages and creating responses
4. Each agent turn builds upon the complete conversation history

### Conversation Simulation Architecture
The C2 (customer) message generation is delegated to a separate module:
- **C1 Agent**: Managed by `conversation_simulation` module
- **C2 Agent**: Managed by `c2_message_generation` module
- The `conversation_simulation_service` imports and uses `c2_message_generation_service.generate_message_stateless()` for C2 responses
- This allows C2 message generation to be used independently (standalone API) or as part of conversation simulation

### Agent Naming Convention
- `C1_MESSAGE_GENERATOR_AGENT_NAME = "C1MessageGeneratorAgent"` - Service representative
- `C2_MESSAGE_GENERATOR_AGENT_NAME = "C2MessageGeneratorAgent"` - Customer

### Agent Class Structure
```python
class Agent(NamedTuple):
    instructions: str  # Agent's system instructions
    model_deployment_name: str  # Model to use (e.g., "gpt-4")
    agent_version_object: AgentVersionObject  # From create_version() - contains agent_id
```

### Conversation API Pattern
Instead of threads, we use conversations:
```python
# Create conversation with initial message
conversation = openai_client.conversations.create(
    items=[{"type": "message", "role": "user", "content": prompt}]
)

# Add more messages to conversation
openai_client.conversations.items.create(
    conversation_id=conversation.id,
    items=[{"type": "message", "role": "user", "content": message}]
)

# Create response with agent
response = openai_client.responses.create(
    conversation=conversation.id,
    extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
    input=""
)
```

### Workflow Pattern
For each conversation turn:
1. **C1 Agent** (service representative): Generates response based on conversation context
2. **C2 Agent** (customer): Generates customer response
3. If completed or max turns reached: End conversation

### ConversationSimulationService Methods
- `simulate_conversation()`: Main orchestration method that runs full conversation
  - Creates both agents
  - Manages shared conversation lifecycle
  - Runs conversation turns until completion or max_turns
  - Returns complete results with all metrics

- `_invoke_c1_agent()`: Helper to invoke C1 agent on shared conversation
- `_invoke_c2_agent()`: Helper to invoke C2 agent on shared conversation

### Benefits
- Shared context across all turns and agents
- More natural conversation flow
- Business logic encapsulated in service layer
- Routes remain clean and simple
- All agents see complete conversation history
- Simplified message management
- Easy to test and modify workflows

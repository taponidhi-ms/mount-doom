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
│   └── shared.py         # Common API and DB schemas
├── infrastructure/       # Infrastructure services
│   ├── ai/
│   │   └── azure_ai_service.py # Client initialization
│   └── db/              # Database services
│       └── cosmos_db_service.py
├── modules/             # Feature modules (Vertical Slices)
│   ├── c2_message_generation/
│   │   ├── c2_message_generation_service.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── agents.py
│   │   └── instructions.py
│   ├── conversation_simulation/
│   │   ├── conversation_simulation_service.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── agents.py    # Only C1 agent (uses c2_message_generation module for C2)
│   │   └── instructions.py # Only C1 agent instructions
│   ├── persona_distribution/
│   │   ├── persona_distribution_service.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── agents.py
│   │   └── instructions.py
│   ├── persona_generator/
│   │   ├── persona_generator_service.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── agents.py
│   │   └── instructions.py
│   ├── transcript_parser/
│   │   ├── transcript_parser_service.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── agents.py
│   │   └── instructions.py
└── main.py               # FastAPI application
```

### Key Principles
- **Separation of Concerns**: Each service handles one use case's business logic
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

#### Use Case Services
Each service handles complete business logic for its use case:
- **C2MessageGenerationService**: Generates C2 (customer) messages. Uses `create_c2_message_generator_agent()`. Provides both stateful (`generate_message()`) and stateless (`generate_message_stateless()`) generation methods.
- **PersonaDistributionService**: Generates persona distributions. Uses `create_persona_distribution_agent()`.
- **PersonaGeneratorService**: Generates exact personas. Uses `create_persona_generator_agent()`.
- **TranscriptParserService**: Parses customer-representative transcripts. Uses `create_transcript_parser_agent()`.
- **ConversationSimulationService**: Multi-agent conversation orchestration (C1/C2). Uses `create_c1_agent()` and delegates C2 message generation to `C2MessageGenerationService`.

Services contain:
- Agent configuration (name, instructions, model deployment)
- Workflow logic specific to the use case
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

### Routes (One per use case)
- `/api/v1/c2-message-generation/*` - Delegates to C2MessageGenerationService
  - POST `/generate` - Generate C2 (customer) message
  - GET `/browse` - Browse past C2 message generations with pagination
  - POST `/delete` - Delete selected records
  - POST `/download` - Download selected records as JSON
- `/api/v1/persona-distribution/*` - Delegates to PersonaDistributionService
  - POST `/generate` - Generate persona distribution
  - GET `/browse` - Browse past persona distribution generations with pagination
- `/api/v1/persona-generator/*` - Delegates to PersonaGeneratorService
  - POST `/generate` - Generate exact personas
  - GET `/browse` - Browse past persona generations with pagination
- `/api/v1/conversation-simulation/*` - Delegates to ConversationSimulationService
  - POST `/simulate` - Simulate conversation
  - GET `/browse` - Browse past simulations with pagination

Routes only:
1. Extract request parameters
2. Call appropriate service method
3. Save results via service's save_to_database() method
4. Return formatted response

## Frontend Architecture

### Structure
```
frontend/
├── app/             # Next.js App Router pages
│   ├── persona-distribution/
│   ├── transcript-parser/
│   └── conversation-simulation/
├── components/      # React components
│   └── PageLayout.tsx  # Reusable page layout component
└── lib/            # Utilities and API client
```

### Key Principles
- Component reusability
- Type safety with TypeScript
- Responsive design with Ant Design
- Accessible UI with Ant Design components
- Tab-based interface for generate and history views

### Pages
Each use case has a dedicated page with two tabs:
- **Generate/Validate/Simulate Tab**: Form for creating new requests
- **History Tab**: Paginated view of past results

Pages:
- `/c2-message-generation` - Generate and view C2 (customer) messages
- `/persona-distribution` - Generate and view persona distributions
- `/transcript-parser` - Parse customer–representative transcripts and view parsed results
- `/conversation-simulation` - Simulate and view conversations
  - Special feature: Simple form with customer intent, sentiment, and subject

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

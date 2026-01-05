# Mount Doom - Development Conventions

## Backend Conventions (Python/FastAPI)

### Code Style
- Follow PEP 8 style guide
- Use type hints for all function parameters and returns
- Use async/await for I/O operations
- Use Pydantic for data validation

### Naming Conventions
- Classes: PascalCase (e.g., `AzureAIService`)
- Functions/Methods: snake_case (e.g., `get_agent_response`)
- Constants: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
- Private methods: prefix with underscore (e.g., `_initialize_client`)

### File Organization
- One route per use case (calls service)
- **One service per use case** with business logic:
  - `PersonaDistributionService`: Persona distribution generation workflow
  - `GeneralPromptService`: Direct model response workflow
  - `PromptValidatorService`: Prompt validation workflow
  - `ConversationSimulationService`: Multi-agent conversation workflow
  - `AzureAIService`: Client initialization and agent factory only
  - `CosmosDBService`: Database persistence
- Services are singletons
- Models in schemas.py
- Configuration in core/config.py
- Agent configuration constants in instruction_sets/

### Error Handling
- Use HTTPException for API errors
- Include descriptive error messages
- Log errors with structlog
- Always include `exc_info=True` in error logs for stack traces

### Logging (Verbose Mode for Local Development)
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
  - Format: ISO 8601 Timestamp (`YYYY-MM-DDTHH:MM:SS.mmmmmmZ`) with structured fields
  - Encoding: UTF-8
- **External Library Logging**:
  - Azure SDK logs (`azure`, `azure.core`, `azure.ai`, `azure.ai.projects`) suppressed to WARNING level
  - OpenAI client logs (`openai`) suppressed to WARNING level
  - HTTP client logs (`httpx`, `httpcore`, `urllib3`) suppressed to WARNING level to prevent verbose connection/request details
  - Uvicorn loggers configured to propagate to root logger for consistent formatting
  - Python warnings captured and sent through logging system at WARNING level

**Logging Levels and Usage**:
- `logger.info()`: Key operations, milestones, and important state changes
  - Service initialization (Azure AI, Cosmos DB)
  - Request start/end with key parameters
  - Major workflow steps (agent creation, conversation turns)
  - Database operations (container creation, document saves)
  - Final results (tokens used, time taken, status)
  
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

1. **Service Initialization**:
   - Client initialization start/completion
   - Connection strings (truncated for security)
   - Database/container names

2. **Agent Operations**:
   - Agent creation requests (name, instructions length)
   - Cache hit/miss status
   - Agent version and model information
   - Created timestamps

3. **Conversation Simulation** (Most Verbose):
   - Every stream event with event count and type
   - Workflow action changes (C1, C2 turns)
   - Each message received (actor, length, preview, tokens)
   - Token usage per message
   - Final conversation status determination

4. **API Requests**:
   - Request received with key parameters
   - Prompt lengths (not full prompts)
   - Model/agent names
   - Customer intent, sentiment, subject (for conversations)

5. **Responses**:
   - Response text length and preview (first 100-150 chars)
   - Token usage
   - Time taken in milliseconds
   - Conversation status

6. **Database Operations**:
   - Container existence checks
   - Container creation
   - Document creation with IDs
   - Save success confirmations

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

## Frontend Conventions (TypeScript/Next.js)

### Code Style
- Use TypeScript for all files
- Use 'use client' directive for client components
- Server components by default
- Proper error boundaries

### Naming Conventions
- Components: PascalCase (e.g., `ResultDisplay`)
- Files: kebab-case (e.g., `api-client.ts`)
- Functions: camelCase (e.g., `handleSubmit`)
- Constants: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)

### Component Structure
- Props interfaces defined inline or separately
- State management with useState
- Side effects with useEffect
- Form handling with controlled components
- Tab-based navigation for generate/history views

### Styling
- Ant Design components with default styling
- Inline styles for custom layouts
- Responsive design with Ant Design grid system
- Proper accessibility with ARIA labels and semantic HTML

### UI Components (Ant Design)
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

### Page Structure Pattern
All use case pages follow this structure:
1. **Header**: Title and description (via PageLayout component)
2. **Tabs**: Generate/Validate/Simulate tab and History tab
3. **Generate/Validate/Simulate Tab**:
   - Configuration form (Ant Design Card)
   - Submit button with loading state
   - Result display (if available)
4. **History Tab**:
   - Ant Design Table with past results
   - Pagination controls (built into Table)
   - Loading and error states

## API Design

### Request/Response Format
- All requests: JSON body
- All responses: JSON with standard structure
- Include metadata (tokens, timing) in all responses
- Use Pydantic models for validation

### Endpoint Structure
- RESTful design
- Versioned API (`/api/v1/`)
- Grouped by use case
- GET for retrieval, POST for actions

### Standard Endpoints Per Use Case
Each use case follows this pattern:
- POST `/{use-case}/generate|validate|simulate` - Create new result
- GET `/{use-case}/browse` - List past results with pagination

### Browse Endpoint Pattern
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

Example table column configuration:
```typescript
const columns = [
  {
    title: 'Timestamp',
    dataIndex: 'timestamp',  // ✅ Cosmos DB field name
    render: (text: string) => new Date(text).toLocaleString(),
  },
  {
    title: 'Response Preview',
    dataIndex: 'response',  // ✅ Cosmos DB field name
    render: (text: string) => text?.substring(0, 100) + '...',
  },
]
```

## Database (Cosmos DB)

### CosmosDBService - Infrastructure Only
The CosmosDBService is a singleton infrastructure service that:
- Manages Cosmos DB client and database references
- Provides container name constants for all use cases
- Offers generic operations (ensure_container, save_document, browse_container)
- Does NOT contain feature-specific business logic or document structures

### Feature Service Persistence
Each feature service handles its own database persistence:
- Defines document structure specific to the use case
- Uses conversation_id from Azure AI as document ID
- Creates documents with all required fields
- Calls `cosmos_db_service.save_document()` for actual persistence

Example pattern:
```python
async def save_to_database(self, ...params, conversation_id: str):
    # Define document structure (business logic)
    # Use conversation_id from Azure AI as the document ID
    document = {
        "id": conversation_id,
        "prompt": prompt,
        "response": response,
        "parsed_output": parsed_output,  # For persona agents
        # ... other fields specific to this use case
    }
    
    # Use generic infrastructure method
    await cosmos_db_service.save_document(
        container_name=cosmos_db_service.CONTAINER_NAME,
        document=document
    )
```

### Container Strategy
- One container per use case
- Partition key: `/id`
- Auto-create containers if missing
- Store complete request/response data
- Containers: persona_distribution, persona_generator, general_prompt, prompt_validator, conversation_simulation, persona_distribution_evals

### Document Structure
- Document ID: conversation_id from Azure AI (ensures uniqueness)
- Include timestamp
- Include all metrics
- Include complete agent details (name, version, instructions, model, timestamp)
- Include parsed_output for JSON-based agents (persona distribution, persona generator)
- Use ISO format for dates
- Structure defined by feature services, not CosmosDBService

## Azure Integration

### Azure AI Projects SDK Documentation
**Important References** - Read these before making changes to Azure AI integration:
- [AIProjectClient Class Documentation](https://learn.microsoft.com/en-us/python/api/azure-ai-projects/azure.ai.projects.aio.aiprojectclient?view=azure-python-preview)
- [OpenAIClient Class Documentation](https://learn.microsoft.com/en-us/python/api/azure-ai-projects/azure.ai.projects.aio.openaiclient?view=azure-python-preview)
- [Azure AI Projects Agents Code Samples](https://github.com/Azure/azure-sdk-for-python/tree/azure-ai-projects_2.0.0b2/sdk/ai/azure-ai-projects/samples/agents)

### AzureAIService - Client Factory Only
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

### Service-Specific Agent Configuration
Each use case service (PersonaDistributionService, PromptValidatorService, etc.) contains:
- Fixed `agent_name` and `instructions` (imported from instruction_sets module) for that use case
- Agent creation logic by calling `azure_ai_service.create_agent()` with instruction string
- Workflow-specific logic (conversation management, multi-agent orchestration, etc.)
- Metrics tracking and data transformation

### Agent Instructions Storage
- All agent instructions are stored as Python string constants in `backend/app/instruction_sets/`
- File naming convention: `{agent_type}.py` (e.g., `persona_distribution.py`)
- Each module exports a constant: `{AGENT_TYPE}_INSTRUCTIONS` (e.g., `PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS`)
- Services import the instruction constants directly from the instruction_sets modules
- Two agent creation methods available:
  - `create_agent(agent_name, instructions)` - Direct text with imported instructions (preferred)
  - `create_agent_from_file(agent_name, instructions_path)` - Loads from text file (legacy support)

### Agent Usage Pattern
```python
# In your service class:
from app.instruction_sets.persona_distribution import PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS

class PersonaDistributionService:
    PERSONA_DISTRIBUTION_AGENT_NAME = "PersonaDistributionGeneratorAgent"
    PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS = PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS

async def your_method(self, prompt: str):
    # Create agent using AzureAIService with instruction string
    agent = azure_ai_service.create_agent(
        agent_name=self.PERSONA_DISTRIBUTION_AGENT_NAME,
        instructions=self.PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS
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

### Conversation Management
- Use conversations (not threads) for stateful interactions
- Create conversations: `openai_client.conversations.create(items=[...])`
- Add messages: `openai_client.conversations.items.create(conversation_id, items=[...])`
- Create responses: `openai_client.responses.create(conversation=conversation_id, extra_body={...})`
- Each conversation maintains full context across all interactions
- Reuse conversation_id across multiple agent invocations for multi-agent workflows

### Multi-Agent Workflow (ConversationSimulationService)
For conversation simulation with multiple agents:
- Single conversation per simulation maintained across all turns
- All agents (C1, C2) operate on same conversation for context continuity
- Each agent invocation:
  1. Adds message to shared conversation
  2. Creates response using agent
  3. Returns tokens and response text
- Workflow continues until completion status or max_turns reached

### Automatic Versioning
- Generate version hash from instruction set: `hashlib.sha256(instructions.encode()).hexdigest()[:8]`
- Format as version string: `f"v{instructions_hash}"`
- Used for tracking agent versions in metrics and database

## Testing Strategy (Future)

### Backend Testing
- Unit tests for services
- Integration tests for routes
- Mock Azure services
- Test error handling

### Frontend Testing
- Component tests with React Testing Library
- Integration tests for pages
- Mock API client
- Test user interactions

## Documentation

### Documentation Files Policy
**IMPORTANT**: Documentation should ONLY exist in the following locations:
- `README.md` files (root, backend, frontend)
- `.memory-banks/` directory files (architecture.md, conventions.md, use-cases.md, etc.)
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
- All relevant information should be in README files or memory banks
- Planning and notes should be done in PR descriptions or issues, not committed files

### Code Documentation
- Docstrings for all public functions
- Type hints serve as documentation
- Comments only when necessary
- Self-documenting code preferred

### API Documentation
- Automatic OpenAPI/Swagger docs
- Include request/response examples
- Document error responses
- Keep docs up to date

## Environment Management

### Backend
- Use .env file for configuration
- Provide .env.example template
- Never commit secrets
- Use Azure KeyVault for production secrets

### Environment Variables for Services
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

### Frontend
- Use NEXT_PUBLIC_ prefix for public variables
- Provide .env.local.example template
- Keep API URL configurable
- Never expose backend secrets

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

## Performance Considerations

### Backend
- Use async/await for I/O
- **Lazy initialization** - Services initialize clients only on first use
  - Prevents unnecessary connections during dev mode restarts
  - Improves startup time in development
  - First request may be slightly slower due to initialization
- Implement connection pooling
- Cache expensive operations (e.g., agent caching in AzureAIService)
- Monitor token usage

### Frontend
- Lazy load components
- Optimize images
- Minimize bundle size
- Use Next.js optimization features

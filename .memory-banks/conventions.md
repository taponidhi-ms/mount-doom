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
  - `PersonaGenerationService`: Persona generation workflow
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

### Styling
- Tailwind CSS utility classes
- CSS variables for theming
- shadcn/ui components for consistency
- Responsive design with mobile-first approach

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

## Database (Cosmos DB)

### Container Strategy
- One container per use case
- Partition key: `/id`
- Auto-create containers if missing
- Store complete request/response data

### Document Structure
- Include timestamp
- Include all metrics
- Include complete agent details (name, version, instructions, model, timestamp)
- Use ISO format for dates

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
Each use case service (PersonaGenerationService, PromptValidatorService, etc.) contains:
- Fixed `agent_name`, `instructions`, `model_deployment` for that use case
- Agent creation logic by calling `azure_ai_service.create_agent()`
- Workflow-specific logic (conversation management, multi-agent orchestration, etc.)
- Metrics tracking and data transformation

### Agent Usage Pattern
```python
# In your service class:
def __init__(self):
    self.agent_name = PERSONA_AGENT_NAME
    self.instructions = PERSONA_AGENT_INSTRUCTIONS
    self.model_deployment = "gpt-4"

async def your_method(self, prompt: str):
    # Create agent using AzureAIService factory
    agent = azure_ai_service.create_agent(
        agent_name=self.agent_name,
        instructions=self.instructions,
        model_deployment_name=self.model_deployment
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
- All agents (C1, C2, Orchestrator) operate on same conversation for context continuity
- Each agent invocation:
  1. Adds message to shared conversation
  2. Creates response using agent
  3. Returns tokens and response text
- Orchestrator checks completion status after each agent turn
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
- Implement connection pooling
- Cache expensive operations
- Monitor token usage

### Frontend
- Lazy load components
- Optimize images
- Minimize bundle size
- Use Next.js optimization features

# GitHub Copilot Instructions for Mount Doom

## IMPORTANT: Memory Banks Protocol

### Before Making Any Changes
**REQUIRED**: Always read the memory banks in the `.memory-banks/` directory before making any changes to the codebase. The memory banks contain critical project context:

1. **Read First**: Always read these files before starting any work:
   - `.memory-banks/architecture.md` - Project architecture and structure
   - `.memory-banks/conventions.md` - Development conventions and patterns
   - `.memory-banks/use-cases.md` - Detailed use case descriptions

2. **Why This Matters**: Memory banks contain:
   - Architectural decisions and patterns
   - Coding conventions and best practices
   - Use case workflows and requirements
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

3. **Use Case Changes** → Update `.memory-banks/use-cases.md`
   - New use cases or features
   - Changes to existing workflows
   - New metrics or tracking requirements
   - Updates to agent/model configurations

### Memory Bank Update Process
1. Make your code changes
2. Identify which memory bank files are affected
3. Update the relevant memory bank files to reflect the changes
4. Ensure consistency between code and documentation
5. Include memory bank updates in your PR

**Remember**: Memory banks are living documentation that must stay synchronized with the codebase. Failing to update them makes future work harder and can lead to inconsistencies.

---

## Project Overview
Mount Doom is a fullstack AI agent simulation platform built with FastAPI (backend) and Next.js (frontend). It enables multi-agent conversation simulations using Azure AI Projects and stores results in Cosmos DB.

## Key Technologies
- **Backend**: Python 3.9+, FastAPI, Azure AI Projects, Azure Cosmos DB
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, shadcn/ui
- **Authentication**: Azure DefaultAzureCredential
- **Architecture**: Clean architecture with separation of concerns

## Code Style Guidelines

### Backend (Python)
- Follow PEP 8 style guide
- Use type hints for all functions
- Use async/await for I/O operations
- Use Pydantic for validation
- Use structlog for logging
- Error handling with HTTPException

### Frontend (TypeScript)
- Use TypeScript for all files
- Client components need 'use client' directive
- Use Tailwind CSS for styling
- Follow React hooks best practices
- Proper error handling and loading states

## Project Structure

### Backend
```
backend/app/
├── api/routes/      # One route per use case
├── core/            # Configuration
├── models/          # Pydantic schemas
├── services/        # Business logic (Azure AI, Cosmos DB)
└── main.py         # FastAPI app
```

### Frontend
```
frontend/
├── app/             # Next.js pages (one per use case)
├── components/      # Reusable React components
└── lib/            # API client and utilities
```

## Important Patterns

### Backend Service Pattern
- Services are singletons
- Use dependency injection
- Separate Azure AI and Cosmos DB concerns
- Return tuples: (response, tokens) for AI calls

### Frontend API Pattern
- Centralized API client in `lib/api-client.ts`
- Type-safe requests/responses
- Error handling at component level
- Show loading states during API calls

## Use Cases (4 Total)

1. **Persona Generation**: Generate personas using specialized agents
2. **General Prompt**: Direct model access for general prompts
3. **Prompt Validator**: Validate simulation prompts
4. **Conversation Simulation**: Multi-turn conversations between C1 (service rep) and C2 (customer) agents

## Azure Integration

### Agent Usage
- Import from `azure.ai.projects`
- Use AIProjectClient with connection string
- DefaultAzureCredential for auth
- Track token usage from responses

### Cosmos DB
- One container per use case
- Auto-create containers if missing
- Store complete request/response data
- Include all metrics and timestamps

## Common Tasks

### Adding New Use Case
1. Create route in `backend/app/api/routes/`
2. Add schema in `backend/app/models/schemas.py`
3. Add Cosmos DB method in `backend/app/services/cosmos_db_service.py`
4. Create page in `frontend/app/[use-case]/page.tsx`
5. Add API methods in `frontend/lib/api-client.ts`

### Metrics to Track
- Tokens used (from Azure AI response)
- Time taken (calculated with time.time())
- Start timestamp (datetime.utcnow())
- End timestamp (datetime.utcnow())

### Response Format
All API responses should include:
```python
{
    "response_text": str,
    "tokens_used": Optional[int],
    "time_taken_ms": float,
    "start_time": datetime,
    "end_time": datetime,
    # ... use case specific fields
}
```

## Environment Configuration

### Backend (.env)
- AZURE_AI_PROJECT_CONNECTION_STRING
- COSMOS_DB_ENDPOINT
- COSMOS_DB_DATABASE_NAME
- Agent and model IDs

### Frontend (.env.local)
- NEXT_PUBLIC_API_URL

## Best Practices

1. **Separation of Concerns**: Keep routes, services, and models separate
2. **Type Safety**: Use Pydantic (backend) and TypeScript (frontend)
3. **Error Handling**: Graceful degradation with user-friendly messages
4. **Logging**: Use structlog for structured backend logging
5. **Documentation**: Self-documenting code with type hints
6. **Reusability**: Shared components and utilities
7. **Accessibility**: ARIA labels, semantic HTML, keyboard navigation
8. **Performance**: Async operations, proper loading states

## Testing Considerations
- Mock Azure services for unit tests
- Test error handling paths
- Validate API contracts
- Test UI interactions

## Security
- Never commit secrets
- Use environment variables
- Validate all inputs with Pydantic
- Proper CORS configuration
- Use Azure DefaultAzureCredential

## When Suggesting Code

- **FIRST**: Read all memory bank files in `.memory-banks/` directory
- Match existing patterns and conventions
- Include proper type hints/types
- Add appropriate error handling
- Consider performance implications
- Keep changes minimal and focused
- Update related documentation
- **ALWAYS**: Update memory banks if your changes affect architecture, conventions, or use cases
- Follow clean architecture principles

## Helpful Context

- **Conversation Simulation**: C1 always starts, orchestrator checks after each message
- **General Prompt**: Uses model directly, not agent
- **All responses**: Stored in Cosmos DB automatically
- **UI Pattern**: Each use case has dedicated page with similar layout
- **Result Display**: Shared component for showing responses and metrics

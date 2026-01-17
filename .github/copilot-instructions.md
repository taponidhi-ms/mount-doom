# GitHub Copilot Instructions for Mount Doom

## IMPORTANT: Memory Banks Protocol

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
5. Include memory bank updates in your PR

**Remember**: Memory banks are living documentation that must stay synchronized with the codebase. Failing to update them makes future work harder and can lead to inconsistencies.

---

## Project Overview
Mount Doom is a fullstack AI agent simulation platform built with FastAPI (backend) and Next.js (frontend). It enables multi-agent conversation simulations using Azure AI Projects and stores results in Cosmos DB.

## Key Technologies
- **Backend**: Python 3.9+, FastAPI, Azure AI Projects, Azure Cosmos DB
- **Frontend**: Next.js 15, TypeScript, Ant Design (antd)
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
- Agent instructions stored in `backend/app/modules/[module]/instructions.py`
- **IMPORTANT**: Use `datetime.now(timezone.utc)` instead of deprecated `datetime.utcnow()`

### Frontend (TypeScript)
- Use TypeScript for all files
- Client components need 'use client' directive
- Use Ant Design components for UI
- Follow React hooks best practices
- Proper error handling and loading states with Ant Design Alert and message components

## Project Structure

### Backend
```
backend/app/
├── core/            # Configuration
├── infrastructure/  # Infrastructure services (DB, AI)
├── modules/         # Feature modules (Vertical Slices)
│   ├── shared/      # Shared base classes (BaseSingleAgentService, route_helpers)
│   ├── [feature]/   # e.g., conversation_simulation/
│   │   ├── routes.py       # API Endpoints
│   │   ├── models.py       # Schemas
│   │   ├── *_service.py    # Business Logic
│   │   ├── agents.py       # Agent Factory
│   │   └── instructions.py # Agent Prompts
│   └── ...
├── models/          # Shared Pydantic schemas
└── main.py         # FastAPI app
```

### Frontend
```
frontend/
├── app/             # Next.js pages (one per feature)
├── components/      # Reusable React components (PageLayout, SingleAgentTemplate, MultiAgentTemplate)
└── lib/            # API client and utilities
```

## Important Patterns

### Backend Service Pattern
- Services are singletons
- Use dependency injection
- Separate Azure AI and Cosmos DB concerns
- Agent instructions stored in `modules/[module]/instructions.py`
- Use `create_agent()` with instructions from module
- Services located in `modules/[module]/[name]_service.py`
- Single-agent services extend `BaseSingleAgentService` for consistency

### Frontend API Pattern
- Centralized API client in `lib/api-client.ts`
- Type-safe requests/responses
- Error handling at component level with Ant Design Alert and message
- Show loading states during API calls with Button loading prop
- No model selection (hardcoded in backend)

## Features (5 Total)

1. **Persona Distribution**: Generate persona distributions from simulation prompts
2. **Persona Generator**: Generate exact customer personas with metadata
3. **Transcript Parser**: Parse customer-representative transcripts to extract intent, subject, sentiment
4. **C2 Message Generation**: Generate C2 (customer) messages
5. **Conversation Simulation**: Multi-turn conversations (max 15 turns) between C1 (service rep) and C2 (customer) agents

## Azure Integration

### Agent Usage
- Import from `azure.ai.projects`
- Use AIProjectClient with connection string
- DefaultAzureCredential for auth
- Track token usage from responses

### Cosmos DB
- One container per feature
- Auto-create containers if missing
- Store complete request/response data
- Include all metrics and timestamps

## Common Tasks

### Adding a New Single-Agent Feature
Single-agent features use one agent to process a prompt and return a response.

1. **Create module directory**: `backend/app/modules/[feature_name]/`

2. **Create `instructions.py`** with agent prompts:
   ```python
   AGENT_NAME = "FeatureNameAgent"
   AGENT_INSTRUCTIONS = """Your agent instructions here..."""
   ```

3. **Create `agents.py`** with agent factory:
   ```python
   from app.infrastructure.ai.azure_ai_service import azure_ai_service
   from .instructions import AGENT_NAME, AGENT_INSTRUCTIONS
   
   def create_feature_agent():
       return azure_ai_service.create_agent(
           name=AGENT_NAME,
           instructions=AGENT_INSTRUCTIONS
       )
   ```

4. **Create `models.py`** for API schemas:
   ```python
   from pydantic import BaseModel
   from app.models.shared import BaseRequest, BaseResponse
   
   class FeatureRequest(BaseRequest):
       prompt: str
   
   class FeatureResponse(BaseResponse):
       parsed_output: Optional[Dict[str, Any]] = None
   ```

5. **Create `[feature_name]_service.py`** for business logic (or extend `BaseSingleAgentService`)

6. **Create `routes.py`** for API endpoints:
   - Use `browse_records`, `delete_records`, `download_records_as_conversations` from `app.modules.shared.route_helpers`

7. **Register router** in `backend/app/main.py`

8. **Add container constant** in `backend/app/infrastructure/db/cosmos_db_service.py`

9. **Create frontend page** in `frontend/app/[feature-name]/page.tsx` using `SingleAgentTemplate`

10. **Add API methods** in `frontend/lib/api-client.ts`

### Adding a New Multi-Agent Feature
Multi-agent features orchestrate multiple agents in a conversation loop.

1. **Create module directory**: `backend/app/modules/[feature_name]/`

2. **Create `instructions.py`** with prompts for each agent

3. **Create `agents.py`** with factory functions for each agent

4. **Create `models.py`** with conversation-specific schemas (messages, history, etc.)

5. **Create `[feature_name]_service.py`** with orchestration logic:
   - Implement conversation loop
   - Handle termination conditions
   - Track per-message and total metrics

6. **Create `routes.py`** for API endpoints

7. **Register router** in `backend/app/main.py`

8. **Add container constant** in `backend/app/infrastructure/db/cosmos_db_service.py`

9. **Create frontend page** in `frontend/app/[feature-name]/page.tsx` using `MultiAgentTemplate`

10. **Add API methods** in `frontend/lib/api-client.ts`

### Metrics to Track
- Tokens used (from Azure AI response)
- Time taken (calculated with `time.time()`)
- Start timestamp: `datetime.now(timezone.utc)`
- End timestamp: `datetime.now(timezone.utc)`

### Response Format
All API responses should include:
```python
{
    "response_text": str,
    "tokens_used": Optional[int],
    "time_taken_ms": float,
    "start_time": datetime,
    "end_time": datetime,
    # ... feature-specific fields
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
9. **Datetime**: Always use `datetime.now(timezone.utc)` for timezone-aware UTC timestamps

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
- **ALWAYS**: Update memory banks if your changes affect architecture, conventions, or features
- Follow clean architecture principles

### Feature Change Validation
When making changes to any feature, **ALWAYS validate compatibility between backend and frontend**:

1. **API Contract Validation**:
   - Verify request schemas match between `backend/app/modules/[feature]/models.py` and `frontend/lib/api-client.ts`
   - Verify response schemas match between backend Pydantic models and frontend TypeScript types
   - Check that field names, types, and optional/required status are consistent

2. **Endpoint Validation**:
   - Confirm route paths in `backend/app/modules/[feature]/routes.py` match API calls in `frontend/lib/api-client.ts`
   - Verify HTTP methods (GET, POST, etc.) are consistent
   - Check query parameters and request body structures

3. **Type Alignment Checklist**:
   - Backend Pydantic `BaseModel` ↔ Frontend TypeScript `interface`
   - Backend `Optional[X]` ↔ Frontend `X | null` or `X?`
   - Backend `datetime` ↔ Frontend `string` (ISO format)
   - Backend `List[X]` ↔ Frontend `X[]`
   - Backend `Dict[str, Any]` ↔ Frontend `Record<string, any>`

4. **Test After Changes**:
   - Run the backend server and verify endpoints respond correctly
   - Test frontend API calls to ensure no type mismatches or 422 errors
   - Check browser console for any parsing or type errors

## Helpful Context

- **Conversation Simulation**: C1 always starts, orchestrator checks after each message
- **All responses**: Stored in Cosmos DB automatically
- **UI Pattern**: Each feature has dedicated page with similar layout
- **Result Display**: Shared template components for showing responses and metrics

## Notes Directory Policy

The repository includes a root-level `notes/` directory intended for personal notes and ad-hoc artifacts. To protect privacy and avoid contaminating project context:

1. Do not read, parse, or reference files in `notes/` for memory bank ingestion or any Copilot/AI-assisted workflows.
2. Do not import or depend on `notes/` contents from application code or tests.
3. Treat `notes/` as non-source documentation that is tracked by Git but excluded from architectural, convention, or feature documentation.

This policy ensures that only `.memory-banks/` governs project context while allowing collaborators to keep tracked personal notes.

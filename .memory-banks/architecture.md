# Mount Doom - Project Architecture

## Overview
Mount Doom is a fullstack AI agent simulation platform with FastAPI backend and Next.js frontend.

## Backend Architecture (Clean Architecture)

### Structure
```
backend/app/
├── api/routes/      # REST API endpoints
├── core/            # Configuration and settings
├── models/          # Pydantic schemas
├── services/        # Business logic and external integrations
└── main.py         # FastAPI application
```

### Key Principles
- Separation of concerns
- Dependency injection
- Single responsibility
- Clean architecture layers

### Services
- **AzureAIService**: Manages Azure AI Projects client, agent interactions, and model responses
- **CosmosDBService**: Handles Cosmos DB operations, container management, and data persistence

### Routes (One per use case)
- `/api/v1/persona-generation/*` - Persona generation endpoints
- `/api/v1/general-prompt/*` - General prompt endpoints
- `/api/v1/prompt-validator/*` - Prompt validation endpoints
- `/api/v1/conversation-simulation/*` - Conversation simulation endpoints

## Frontend Architecture

### Structure
```
frontend/
├── app/             # Next.js App Router pages
├── components/      # React components
└── lib/            # Utilities and API client
```

### Key Principles
- Component reusability
- Type safety with TypeScript
- Responsive design
- Accessible UI

### Pages
Each use case has a dedicated page:
- `/persona-generation`
- `/general-prompt`
- `/prompt-validator`
- `/conversation-simulation`

## Data Flow

1. User interacts with frontend UI
2. Frontend calls API client methods
3. API client sends HTTP requests to backend
4. Backend routes handle requests
5. Services process business logic and call Azure AI
6. Responses are stored in Cosmos DB
7. Results are returned to frontend
8. Frontend displays results with metrics

## Authentication
- Uses Azure DefaultAzureCredential
- Supports multiple auth methods (CLI, Managed Identity, etc.)
- No manual token management required

## Error Handling
- Backend: HTTP exceptions with appropriate status codes
- Frontend: Error state display with user-friendly messages
- Logging: Structured logging with structlog

## Performance Tracking
- Token usage tracked for all AI interactions
- Timing metrics for all requests
- Per-message metrics in conversations
- All metrics visible in UI

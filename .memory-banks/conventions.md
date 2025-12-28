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
- One route per use case
- Services are singletons
- Models in schemas.py
- Configuration in core/config.py

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
- Include agent/model IDs
- Use ISO format for dates

## Azure Integration

### Azure AI Projects SDK Documentation
**Important References** - Read these before making changes to Azure AI integration:
- [AIProjectClient Class Documentation](https://learn.microsoft.com/en-us/python/api/azure-ai-projects/azure.ai.projects.aio.aiprojectclient?view=azure-python-preview)
- [OpenAIClient Class Documentation](https://learn.microsoft.com/en-us/python/api/azure-ai-projects/azure.ai.projects.aio.openaiclient?view=azure-python-preview)
- [Azure AI Projects Agents Code Samples](https://github.com/Azure/azure-sdk-for-python/tree/azure-ai-projects_2.0.0b2/sdk/ai/azure-ai-projects/samples/agents)

### Agent Usage
- Use AIProjectClient from azure-ai-projects
- DefaultAzureCredential for authentication
- Agent IDs configured in environment variables
- Separate agents for different use cases
- Create agents using `client.agents.create_agent()` with PromptAgentDefinition
- Manage conversation threads for stateful interactions
- Use `create_and_process_run()` for automatic polling

### Model Usage
- Direct model access for general prompts
- Use inference API for chat completions
- Track token usage
- Include timing metrics

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

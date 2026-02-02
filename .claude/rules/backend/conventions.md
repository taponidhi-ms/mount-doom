---
paths:
  - "backend/**/*.py"
---

# Backend Development Conventions (Python/FastAPI)

## Code Style

- Follow PEP 8 style guide
- Use type hints for all function parameters and returns
- Use async/await for I/O operations
- Use Pydantic for data validation
- **IMPORTANT**: Use `datetime.now(timezone.utc)` instead of deprecated `datetime.utcnow()`

## Python Virtual Environment Usage

**CRITICAL: Always use the virtual environment (`backend/.venv/`) for all backend operations**

When running Python commands, pip operations, or testing imports:
- **Always** use the venv Python directly: `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux/Mac)
- **Never** use bare `python` or `pip` commands - they may use the global Python installation
- **Install dependencies**: `.venv/Scripts/python.exe -m pip install -r requirements.txt`
- **Test imports**: `.venv/Scripts/python.exe -c "import module"`
- **Run server**: `.venv/Scripts/python.exe -m uvicorn app.main:app --reload`
- Use forward slashes `/` in paths for bash compatibility

## Naming Conventions

- Classes: PascalCase (e.g., `AzureAIService`)
- Functions/Methods: snake_case (e.g., `get_agent_response`)
- Constants: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
- Private methods: prefix with underscore (e.g., `_initialize_client`)

## Model Naming Pattern (Result vs Response)

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

## File Organization

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

## Adding New Agents

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

**Shared Sample Inputs**:
- Use `shared_sample_inputs.py` to avoid duplication across multiple agents
- Import and reuse sample input lists when agents share similar evaluation criteria
- Example: `SIMULATION_SAMPLE_INPUTS` is shared by persona_distribution, simulation_prompt, and persona_generator agents
- Pattern: `from .shared_sample_inputs import SIMULATION_SAMPLE_INPUTS`
- Each agent can still define custom sample inputs if needed by using a list literal

**Registry Auto-Discovery**:
- No manual registration needed
- `load_agent_registry()` automatically discovers `*_config.py` files
- Agent appears in API endpoints immediately after adding config file
- Logs show successful loading on server start

## Configuration (.env)

- Backend settings are loaded from `backend/.env` via `app/core/config.py` using an absolute path, so starting the server from the repo root (or other folders) still picks up the correct environment.

## Error Handling

- Use HTTPException for API errors
- Include descriptive error messages
- Log errors with structlog
- Always include `exc_info=True` in error logs for stack traces

## Response Metrics to Track

All API responses should include:
- `response_text` - The generated text
- `tokens_used` - Token count from Azure AI
- `time_taken_ms` - Calculated with `time.time() * 1000`
- `start_time` - ISO timestamp (`datetime.now(timezone.utc)`)
- `end_time` - ISO timestamp
- `agent_details` - Complete agent information

## Performance Considerations

- Use async/await for I/O
- **Lazy initialization** - Services initialize clients only on first use
  - Prevents unnecessary connections during dev mode restarts
  - Improves startup time in development
  - First request may be slightly slower due to initialization
- Implement connection pooling
- Cache expensive operations
- Monitor token usage

# Mount Doom - Development Conventions

## Backend Conventions (Python/FastAPI)

### Updated Agent Behavior Guidelines
- Ensure all agents adhere to the new behavior guidelines regarding input processing and response restrictions.


### Code Style
- Follow PEP 8 style guide
- Use type hints for all function parameters and returns
- Use async/await for I/O operations
- Use Pydantic for data validation
- **IMPORTANT**: Use `datetime.now(timezone.utc)` instead of deprecated `datetime.utcnow()`

### Python Virtual Environment Usage
**CRITICAL: Always use the virtual environment (`backend/.venv/`) for all backend operations**

When running Python commands, pip operations, or testing imports:
- **Always** use the venv Python directly: `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux/Mac)
- **Never** use bare `python` or `pip` commands - they may use the global Python installation
- **Install dependencies**: `.venv/Scripts/python.exe -m pip install -r requirements.txt`
- **Test imports**: `.venv/Scripts/python.exe -c "import module"`
- **Run server**: `.venv/Scripts/python.exe -m uvicorn app.main:app --reload`
- Use forward slashes `/` in paths for bash compatibility

### Naming Conventions
- Classes: PascalCase (e.g., `AzureAIService`)
- Functions/Methods: snake_case (e.g., `get_agent_response`)
- Constants: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
- Private methods: prefix with underscore (e.g., `_initialize_client`)

### Model Naming Pattern (Result vs Response)
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
    # ... other fields

# API layer
class AgentInvokeResponse(BaseModel):
    response_text: str
    tokens_used: Optional[int] = None
    # ... same fields as Result

# Route transforms Result → Response
@router.post("/invoke")
async def invoke_agent(...) -> AgentInvokeResponse:
    result = await service.invoke_agent(...)
    return AgentInvokeResponse(**result.model_dump())
```

### File Organization
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

### Adding New Agents

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

**Registry Auto-Discovery**:
- No manual registration needed
- `load_agent_registry()` automatically discovers `*_config.py` files
- Agent appears in API endpoints immediately after adding config file
- Logs show successful loading on server start

### Configuration (.env)
- Backend settings are loaded from `backend/.env` via `app/core/config.py` using an absolute path, so starting the server from the repo root (or other folders) still picks up the correct environment.

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

### Modular Component Pattern
Agent pages use a modular architecture with nested routes and reusable components:

#### Agent Pages Structure
Agent pages use Next.js nested routes with a shared layout:

**Layout** (`/agents/[agentId]/layout.tsx`):
- Loads agent info once via `apiClient.getAgent(agentId)`
- Provides agent info to children via `AgentContext`
- Renders `AgentTabs` navigation
- Handles loading and error states

**Generate Page** (`/agents/[agentId]/page.tsx`):
```typescript
'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { useAgentContext } from '@/components/agents/shared/AgentContext'
import AgentInstructionsCard from '@/components/agents/instructions/AgentInstructionsCard'
import AgentResultCard from '@/components/agents/result/AgentResultCard'
import { apiClient } from '@/lib/api-client'

export default function AgentGeneratePage() {
  const params = useParams()
  const agentId = params.agentId as string
  const { agentInfo } = useAgentContext()

  // State and handlers...

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <AgentInstructionsCard instructions={agentInfo.instructions} />
      {/* Form and input fields */}
      {result && <AgentResultCard result={result} />}
    </Space>
  )
}
```

**Batch Page** (`/agents/[agentId]/batch/page.tsx`):
```typescript
'use client'

import { useParams } from 'next/navigation'
import { useAgentContext } from '@/components/agents/shared/AgentContext'
import BatchProcessingSection from '@/components/agents/batch/BatchProcessingSection'

export default function AgentBatchPage() {
  const params = useParams()
  const agentId = params.agentId as string
  const { agentInfo } = useAgentContext()

  return (
    <BatchProcessingSection
      agentId={agentId}
      inputLabel={agentInfo.input_label}
      inputField={agentInfo.input_field}
    />
  )
}
```

**History Page** (`/agents/[agentId]/history/page.tsx`):
```typescript
'use client'

import { useParams } from 'next/navigation'
import { useAgentContext } from '@/components/agents/shared/AgentContext'
import AgentHistoryTable from '@/components/agents/history/AgentHistoryTable'

export default function AgentHistoryPage() {
  const params = useParams()
  const agentId = params.agentId as string
  const { agentInfo } = useAgentContext()

  return (
    <AgentHistoryTable
      agentId={agentId}
      inputLabel={agentInfo.input_label}
      inputField={agentInfo.input_field}
    />
  )
}
```

#### Reusable Components
**AgentContext** - Share agent info across pages:
```typescript
import { useAgentContext } from '@/components/agents/shared/AgentContext'
const { agentInfo, loadingAgent, agentError } = useAgentContext()
```

**Component imports**:
- `AgentInstructionsCard` - Collapsible instructions display
- `AgentResultCard` - Inline result display with JSON/Plain Text toggle
- `AgentResultModal` - Modal for viewing result details
- `BatchProcessingSection` - Complete batch processing UI
- `AgentHistoryTable` - Full-featured history table with auto-load
- `AgentTabs` - Tab-like navigation

#### Workflow Pages Pattern
For workflows that orchestrate multiple agents (e.g., Conversation Simulation), implement custom pages with:

**Structure:**
- Three tabs: Simulate, Batch Processing, History
- All state management within the page component
- Custom rendering for conversation display
- Custom history columns specific to workflow needs

**Key Components:**
```typescript
'use client'

import { useState, useCallback, useEffect } from 'react'
import { Tabs, Card, Table, ... } from 'antd'
import PageLayout from '@/components/PageLayout'
import { apiClient } from '@/lib/api-client'
import { useTimezone } from '@/lib/timezone-context'

export default function WorkflowPage() {
  const { formatTimestamp, formatTime } = useTimezone()

  // State for simulate, batch, and history tabs
  // Custom handlers for each workflow's specific needs
  // Custom rendering functions

  const tabItems = [
    { key: 'simulate', label: 'Simulate', children: <SimulateTab /> },
    { key: 'batch', label: 'Batch Processing', children: <BatchTab /> },
    { key: 'history', label: 'History', children: <HistoryTab /> },
  ]

  return (
    <PageLayout title="..." description="...">
      <Tabs defaultActiveKey="simulate" items={tabItems} />
    </PageLayout>
  )
}
```

**Rationale**: Workflows have unique requirements, so custom implementations provide more flexibility than a shared template.

### Timezone Handling
- Always use `useTimezone()` hook to access `formatTimestamp()` and `formatTime()` functions
- Never use raw `toLocaleString()` or `toISOString()` for user-facing timestamps
- Timezone state is global and persisted to localStorage
- Default timezone is IST (Asia/Kolkata)

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

## Local Tooling Conventions

### CXA Evals Runner
- `cxa_evals/` is a repo-root folder for running CXA AI Evals locally.
- The CLI executable `Microsoft.CXA.AIEvals.Cli.exe` is manually downloaded and must not be committed.
- The `output/` directory under `cxa_evals/` must not be committed (results are gitignored).
- Evals now run for `SimulationAgent` at once - no need for separate per-agent runs.
- The `scenario_name` field in input files distinguishes between different agent types.
- Config files: `default_config.json` (default metrics) and `cutom_config.json` (custom rules).
- Input files are stored in `cxa_evals/input/` directory.

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
All feature pages follow this structure:
1. **Header**: Title and description (via PageLayout component)
2. **Tabs**: Generate/Validate/Simulate tab, Batch Processing tab, and History tab
3. **Generate/Validate/Simulate Tab**:
   - Configuration form (Ant Design Card)
   - Submit button with loading state
   - Result display (if available)
4. **Batch Processing Tab**:
   - JSON input for batch items (prompts or configurations)
   - Configurable delay between items (Select component with 5-60 second options)
   - Load and Start buttons
   - Progress display (current item count + Progress bar)
   - Table showing loaded items with status (pending/running/completed/failed)
   - Expandable rows showing detailed results
5. **History Tab**:
   - Ant Design Table with past results
   - Pagination controls (built into Table)
   - Loading and error states

### Batch Processing Pattern (Conversation Simulation & Persona Distribution)
When adding batch support to a page:

**State Management**:
```typescript
const [batchItems, setBatchItems] = useState<BatchItem[]>([])
const [batchLoading, setBatchLoading] = useState(false)
const [batchProgress, setBatchProgress] = useState(0)
const [currentBatchIndex, setCurrentBatchIndex] = useState(-1)
const [batchJsonInput, setBatchJsonInput] = useState('')
const [stopBatchRequested, setStopBatchRequested] = useState(false)
const [batchDelay, setBatchDelay] = useState(5)
```

**BatchItem Interface**:
- For conversation simulation: `{ key, customerIntent, customerSentiment, conversationSubject, status, result?, error? }`
- For persona distribution: `{ key, prompt, status, result?, error? }`

**Core Functions**:
1. `loadBatchItemsFromText()` - Parse JSON (array or object with items array)
2. `runBatchDistributions()` / `runBatchSimulation()` - Main loop with delays and stop handling
3. `handleStopBatch()` - Set stop flag to gracefully exit

**UI Components**:
- TextArea for JSON input
- Select component for delay selection (5-60 seconds, 5-second increments)
- Buttons: "Load Items", "Start Batch", "Stop Batch" (shows during processing)
- Progress bar with current item indicator
- Table with columns: Item description, Status (tag), Result
- Expandable rows showing detailed response data

**Common Pattern**:
```tsx
const loadBatchItemsFromText = () => {
  // Parse JSON (array or { prompts/personas/configurations: [...] })
  // Validate items (filter empty ones)
  // Create BatchItem[] with unique keys and 'pending' status
  // Set to state and message.success()
}

const runBatchDistributions = async () => {
  // Loop through items
  // Set status to 'running'
  // Call API method with item data
  // Set status to 'completed'/'failed'
  // Add delay between items (except last)
  // Check stopBatchRequested flag for graceful exit
}
```

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
- Provides container name constants for all features
- Offers generic operations (ensure_container, save_document, browse_container)
- Does NOT contain feature-specific business logic or document structures

### Feature Service Persistence
Each feature service handles its own database persistence:
- Defines document structure specific to the feature
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
        # ... other fields specific to this feature
    }
    
    # Use generic infrastructure method
    await cosmos_db_service.save_document(
        container_name=cosmos_db_service.CONTAINER_NAME,
        document=document
    )
```

### Container Strategy
- One container per feature
- Partition key: `/id`
- Auto-create containers if missing
- Store complete request/response data
- Containers: persona_distribution, persona_generator, conversation_simulation, transcript_parser, c2_message_generation

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
- [Azure AI Projects Agents Code Samples](https://github.com/Azure/azure-sdk-for-python/tree/azure-ai-projects_2.0.0b3/sdk/ai/azure-ai-projects/samples/agents)

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
Each feature service (PersonaDistributionService, TranscriptParserService, etc.) contains:
- Fixed `agent_name` and `instructions` (imported from instruction_sets module) for that feature
- Agent creation logic by calling `azure_ai_service.create_agent()` with instruction string
- Workflow-specific logic (conversation management, agent orchestration, etc.)
- Metrics tracking and data transformation

### Agent Instructions Storage
- All agent instructions are stored as Python string constants in `backend/app/modules/agents/instructions.py`
- Instructions are centralized in a single file for easy management
- Each instruction is a constant: `{AGENT_TYPE}_INSTRUCTIONS` (e.g., `PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS`)
- Services and agent configs import the instruction constants directly from the instructions module
- Agent creation method: `create_agent(agent_name, instructions, model)` - Creates agent with given instructions string

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
- Reuse conversation_id across multiple agent invocations for workflows

### Workflow Pattern (ConversationSimulationService)
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
- `.memory-banks/` directory files (architecture.md, conventions.md, features.md, etc.)
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

# Mount Doom Backend API

FastAPI backend for multi-agent conversation simulation and prompt generation using Azure AI Projects and Cosmos DB.

## Architecture

The backend follows clean architecture principles with clear separation of concerns:

```
backend/
├── app/
│   ├── core/                # Core configuration and logging
│   ├── infrastructure/      # Shared infrastructure services
│   │   ├── ai/             # Azure AI service
│   │   └── db/             # Cosmos DB service
│   ├── models/              # Shared models
│   │   ├── shared.py        # Common API and DB schemas
│   │   └── single_agent.py  # Shared schemas for single-agent operations
│   ├── modules/             # Feature modules (Vertical Slices)
│   │   ├── agents/          # Unified agents API
│   │   │   ├── config.py   # Agent configuration registry
│   │   │   ├── instructions.py  # Centralized agent instructions
│   │   │   ├── models.py   # API schemas
│   │   │   ├── routes.py   # Unified agents endpoints
│   │   │   └── agents_service.py  # Generic agent invocation
│   │   ├── workflows/       # Workflows module
│   │   │   ├── config.py   # Workflow configuration registry
│   │   │   ├── models.py   # API schemas
│   │   │   ├── routes.py   # Workflow listing endpoints
│   │   │   └── conversation_simulation/  # Multi-agent workflow
│   │   ├── persona_distribution/
│   │   ├── persona_generator/
│   │   ├── transcript_parser/
│   │   └── shared/
│   └── main.py             # FastAPI application entry point
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## Unified Agent Architecture

The application uses a **unified agent architecture** with centralized configuration and instructions:

### Unified Agents Module (`app/modules/agents/`)
A centralized module providing a single API for all single-agent operations:

**Centralized Instructions** (`instructions.py`):
- All agent instructions consolidated in one file
- Instructions: `PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS`, `PERSONA_GENERATOR_AGENT_INSTRUCTIONS`, `TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS`, `D365_TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS`, `C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS`

**Agent Configuration Registry** (`config.py`):
- Dynamically loads agent configurations from individual `configs/*_config.py` files
- Each config file exports an `AGENT_CONFIG` with: agent_id, agent_name, display_name, description, instructions, container_name, sample_inputs
- Provides helper functions: `get_agent_config()`, `get_all_agents()`, `list_agent_ids()`
- **Shared Sample Inputs** (`configs/shared_sample_inputs.py`): Reusable sample prompt sets across multiple agents
  - `SIMULATION_SAMPLE_INPUTS` (50 prompts) - Used by persona_distribution, simulation_prompt, and persona_generator agents
  - Avoids duplication and ensures consistency in evaluation datasets

**Unified Agents Service** (`agents_service.py`):
- Generic service that can invoke any agent by agent_id
- Handles conversation creation, response extraction, JSON parsing
- Saves results to the appropriate Cosmos DB container

**Current Registered Agents**:
- **PersonaDistributionGeneratorAgent** - Generates persona distributions from simulation prompts
- **PersonaGeneratorAgent** - Generates customer personas
- **TranscriptParserAgent** - Parses transcripts to extract intent, subject, sentiment
- **D365TranscriptParserAgent** - Parses Dynamics 365 HTML transcripts into conversation format (agent/customer roles)
- **C2MessageGeneratorAgent** - Generates customer messages for simulations

### Agent Versioning
- Agent versions are automatically generated based on instruction set changes
- Version identifier: SHA256 hash of instructions (first 8 characters)
- When instructions change, a new version is automatically created
- All agent details (name, version, instructions, model) are saved to Cosmos DB

## Features

### Single Agents (via Unified Agents API)

1. **Persona Distribution** - Generate persona distributions from simulation prompts with structured JSON output
2. **Persona Generation** - Generate exact customer personas from natural language descriptions
3. **Transcript Parser** - Parse customer-representative transcripts to extract intent, subject, and sentiment
4. **D365 Transcript Parser** - Parse HTML transcripts from Dynamics 365 Customer Service Workspace into conversation format
5. **C2 Message Generation** - Generate customer messages for use in conversation simulations

### Multi-Agent Workflows

6. **Conversation Simulation** - Multi-turn conversation between C1 (service rep) and C2 (customer) agents

### Key Capabilities

- Fixed agent names with automatic versioning based on instruction changes
- Model selection (GPT-4, GPT-3.5 Turbo) instead of agent selection
- Instruction sets stored in separate, easily modifiable files
- Token usage tracking for all requests
- Timing metrics for performance monitoring
- Cosmos DB integration with complete agent details persistence
- CORS enabled for frontend integration
- Structured logging with JSON output

## Setup

### Prerequisites

- Python 3.9 or higher
- Azure AI Projects subscription
- Azure Cosmos DB account (or local Cosmos DB Emulator for testing)
- Azure credentials configured

### Installation

1. Create and activate a virtual environment:
```bash
cd backend
python -m venv .venv

# Activate virtual environment:
# Linux/Mac:
source .venv/bin/activate

# Windows PowerShell (requires execution policy):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser  # One-time setup
.\.venv\Scripts\Activate.ps1

# Windows CMD:
.\.venv\Scripts\activate.bat

# Windows Git Bash:
source .venv/Scripts/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

### Configuration

Edit `.env` file with your Azure configuration:

```env
# Azure AI Projects
AZURE_AI_PROJECT_CONNECTION_STRING=your_connection_string

# Cosmos DB - Cloud Instance
COSMOS_DB_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOS_DB_DATABASE_NAME=mount_doom_db
COSMOS_DB_USE_EMULATOR=false

# Cosmos DB - Local Emulator (for testing)
# COSMOS_DB_ENDPOINT=https://localhost:8081
# COSMOS_DB_DATABASE_NAME=mount_doom_db
# COSMOS_DB_USE_EMULATOR=true
# COSMOS_DB_KEY=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==

# Default model deployment (optional - can be overridden per request)
default_model_deployment=gpt-4.1
```

**Note:** Agent configurations (IDs, names, instructions) are defined in code (`modules/agents/config.py`), not in environment variables. The unified agents API provides access to all registered agents.

### Using Local Cosmos DB Emulator

For local development and testing, you can use the Cosmos DB Emulator instead of an Azure Cosmos DB instance:

1. **Install Cosmos DB Emulator**:
   - Windows: Download from [Microsoft Cosmos DB Emulator](https://aka.ms/cosmosdb-emulator)
   - Linux/macOS: Use Docker container:
     ```bash
     docker pull mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator
     docker run -p 8081:8081 -p 10251:10251 -p 10252:10252 -p 10253:10253 -p 10254:10254 \
       --name=cosmos-emulator \
       -e AZURE_COSMOS_EMULATOR_PARTITION_COUNT=10 \
       -e AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE=true \
       mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator
     ```

2. **Configure Environment Variables**:
   Set `COSMOS_DB_USE_EMULATOR=true` in your `.env` file:
   ```env
   COSMOS_DB_ENDPOINT=https://localhost:8081
   COSMOS_DB_DATABASE_NAME=mount_doom_db
   COSMOS_DB_USE_EMULATOR=true
   COSMOS_DB_KEY=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==
   ```
   
   The default emulator key is provided above. You can use a custom key if you configured the emulator with one.

3. **Benefits of Local Emulator**:
   - No Azure subscription required for Cosmos DB testing
   - No authentication needed (uses emulator key)
   - Faster development iteration
   - No cloud costs for local testing
   - Same API and functionality as cloud Cosmos DB

### Lazy Initialization

The backend now uses **lazy initialization** for Azure AI and Cosmos DB clients:

- **What it means**: Clients are initialized only when first used, not on module import
- **Benefits**:
  - Faster dev mode restarts when code changes
  - No unnecessary connections during startup
  - Better development experience with hot reload
- **When initialization happens**: On first API request that needs the service
- **Note**: First request may be slightly slower due to initialization overhead

## Running the API

### Development Mode

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or using the main module:
```bash
cd backend
python app/main.py
```

### Production Mode

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs (Swagger): http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc

## API Endpoints

### Unified Agents API

- `GET /api/v1/agents/list` - List all available agents with configurations
- `GET /api/v1/agents/{agent_id}` - Get specific agent details including instructions
- `POST /api/v1/agents/{agent_id}/invoke` - Invoke agent with input
- `GET /api/v1/agents/{agent_id}/browse` - Browse agent history with pagination
- `POST /api/v1/agents/{agent_id}/delete` - Delete agent records
- `POST /api/v1/agents/{agent_id}/download` - Download agent records as JSON
- `GET /api/v1/agents/versions` - List all agent+version combinations with conversation counts
- `POST /api/v1/agents/download-multi` - Download from multiple agents with optional conversation limits

**Available agent_ids**: `persona_distribution`, `persona_generator`, `transcript_parser`, `c2_message_generation`

**Multi-Agent Download**:
The `/download-multi` endpoint accepts a list of agent+version selections with optional limits:
```json
{
  "selections": [
    {
      "agent_id": "persona_distribution",
      "version": "v12abc345",
      "limit": 10  // Optional: download only 10 conversations
    },
    {
      "agent_id": "c2_message_generation",
      "version": "v98xyz789"
      // No limit: downloads all conversations
    }
  ]
}
```

This enables creating smaller eval subsets for testing strategies before full evaluations.

### Workflows API

- `GET /api/v1/workflows/list` - List all available workflows with agent details
- `GET /api/v1/workflows/{workflow_id}` - Get specific workflow details including agent instructions

### Conversation Simulation (Multi-Agent Workflow)

- `POST /api/v1/conversation-simulation/simulate` - Simulate conversation using C1 and C2 agents
- `GET /api/v1/conversation-simulation/browse` - Browse past simulations with pagination
- `POST /api/v1/conversation-simulation/delete` - Delete selected records
- `POST /api/v1/conversation-simulation/download` - Download selected records as JSON

### Health Check

- `GET /health` - Check API health status

## Request Examples

### Invoke Agent (Unified API)

```bash
curl -X POST "http://localhost:8000/api/v1/agents/persona_generator/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Create a persona for a tech-savvy millennial",
    "model_deployment_name": "gpt-4"
  }'
```

Response includes agent details:
```json
{
  "response_text": "...",
  "tokens_used": 150,
  "time_taken_ms": 1250.5,
  "start_time": "2025-01-15T10:30:00Z",
  "end_time": "2025-01-15T10:30:01Z",
  "agent_details": {
    "agent_name": "PersonaGeneratorAgent",
    "agent_version": "vab12cd34",
    "instructions": "You are a specialized persona generation agent...",
    "model": "gpt-4",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### List All Agents

```bash
curl -X GET "http://localhost:8000/api/v1/agents/list"
```

### Simulate Conversation

```bash
curl -X POST "http://localhost:8000/api/v1/conversation-simulation/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_properties": {
      "CustomerIntent": "Technical Support",
      "CustomerSentiment": "Frustrated",
      "ConversationSubject": "Product Issue"
    },
    "model_deployment_name": "gpt-4",
    "max_turns": 10
  }'
```

Response includes details for both C1 (service rep) and C2 (customer) agents.

## Authentication

The backend uses `DefaultAzureCredential` for Azure authentication, which supports:
- Environment variables
- Managed Identity
- Azure CLI authentication (`az login`)
- Visual Studio Code authentication
- Interactive browser authentication
- And more...

### Token Refresh

**Important**: `DefaultAzureCredential` automatically handles token refresh for you:

- Tokens are refreshed automatically before expiration
- No manual intervention required (no need to run `az account get-access-token`)
- If using Azure CLI authentication, ensure you're logged in with `az login`
- The service maintains the credential and refreshes it as needed

**If you experience authentication issues after extended periods**:
1. Try re-running `az login` to refresh your Azure CLI authentication
2. Check that your Azure subscription is active
3. Verify your credentials have the necessary permissions

The automatic token refresh should prevent the need for manual token management in most cases.

## Data Storage

All use case results are automatically stored in Cosmos DB in separate containers with complete agent details:

### Containers
- `persona_distribution` - Persona distribution generation results
- `persona_generator` - Persona generation results
- `transcript_parser` - Transcript parsing results
- `c2_message_generation` - C2 message generation results
- `conversation_simulation` - Conversation simulation results with C1 and C2 agent details

### Stored Information
Each record includes:
- Document ID: `conversation_id` from Azure AI (ensures uniqueness)
- Request data (prompt/input, model, parameters)
- Response data (text, tokens used, timing)
- Agent details:
  - Agent name (e.g., "PersonaGeneratorAgent", "C1MessageGeneratorAgent")
  - Agent version (hash of instructions)
  - Complete instruction set
  - Model used
  - Timestamp
- For JSON-based agents: `parsed_output` field with structured data

Containers are created automatically if they don't exist.

## Development

### Code Style

The project follows Python best practices:
- PEP 8 style guide
- Type hints for better IDE support
- Pydantic models for data validation
- Clean architecture with separation of concerns

### Adding New Features

#### Adding a New Single Agent

1. Add instructions to `backend/app/modules/agents/instructions.py`:
   ```python
   MY_NEW_AGENT_INSTRUCTIONS = """
   Your agent instructions here...
   """
   ```

2. Register in `backend/app/modules/agents/config.py`:
   ```python
   "my_agent": AgentConfig(
       agent_id="my_agent",
       agent_name="MyAgentName",
       display_name="My Agent",
       description="Agent description",
       instructions=MY_NEW_AGENT_INSTRUCTIONS,
       container_name="my_agent",
       input_field="prompt",
       input_label="Prompt",
       input_placeholder="Enter your prompt...",
   )
   ```

3. Add container constant to `cosmos_db_service.py`:
   ```python
   CONTAINER_MY_AGENT = "my_agent"
   ```

4. Frontend will automatically work via unified agents API at `/api/v1/agents/my_agent/invoke`

#### Adding a New Multi-Agent Workflow

1. Create directory: `backend/app/modules/workflows/{workflow_name}/`
2. Add agent instructions to `modules/agents/instructions.py`
3. Create workflow files: `agents.py`, `models.py`, `{workflow}_service.py`, `routes.py`
4. Register router in `main.py`
5. Register in `modules/workflows/config.py`
6. Create frontend page in `app/workflows/{workflow_id}/page.tsx`

## Troubleshooting

### Common Issues

1. **Azure Authentication Fails**
   - Ensure Azure credentials are configured
   - Try `az login` if using Azure CLI
   - Check connection string format

2. **Cosmos DB Connection Issues**
   - Verify endpoint URL is correct
   - Check firewall rules in Azure Portal
   - Ensure credentials have proper permissions

3. **Agent/Model Not Found**
   - Models are selected via the API (gpt-4, gpt-4.1, etc.)
   - Agent IDs are defined in `modules/agents/config.py` in AGENT_REGISTRY
   - Check that the model deployment exists in your Azure AI project
   - Verify agent_id exists: GET `/api/v1/agents/list`

4. **Instruction Set Changes Not Reflected**
   - Modify instruction files in `app/modules/agents/instructions.py`
   - Restart the server to load new instructions
   - New agent version will be automatically created based on instruction hash

## License

Copyright (c) 2025. All rights reserved.

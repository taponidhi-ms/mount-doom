# Mount Doom Backend API

FastAPI backend for multi-agent conversation simulation and prompt generation using Azure AI Projects and Cosmos DB.

## Architecture

The backend follows clean architecture principles with clear separation of concerns:

```
backend/
├── app/
│   ├── api/
│   │   └── routes/          # API endpoints for each use case
│   ├── core/                # Core configuration
│   ├── instruction_sets/    # Agent instruction sets (fixed per agent)
│   ├── models/              # Pydantic models and schemas
│   ├── services/            # Business logic and external service integrations
│   └── main.py             # FastAPI application entry point
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## Agent Architecture

This application uses a **fixed agent architecture** where each use case has predefined agents with fixed names and instruction sets:

### Agent Names (Fixed)
- **PersonaAgent** - Generates personas from simulation prompts
- **PromptValidatorAgent** - Validates simulation prompts for quality
- **C1Agent** - Customer service representative in conversations
- **C2Agent** - Customer in conversations
- **OrchestratorAgent** - Determines conversation completion status

### Agent Versioning
- Agent versions are automatically generated based on instruction set changes
- Version identifier: SHA256 hash of instructions (first 8 characters)
- When instructions change, a new version is automatically created
- All agent details (name, version, instructions, model) are saved to Cosmos DB

### Instruction Sets
All agent instructions are defined in the `app/instruction_sets/` module:
- Each agent has its own file (e.g., `c1_agent.py`, `persona_agent.py`)
- Instructions are constant strings that define agent behavior
- Modifying instructions in these files automatically creates new agent versions

## Features

### Use Cases

1. **Persona Generation** - Generate personas using PersonaAgent with your choice of model
2. **General Prompt** - Get responses for any general prompt using LLM models directly (no agent)
3. **Prompt Validator** - Validate simulation prompts using PromptValidatorAgent
4. **Conversation Simulation** - Multi-turn conversation between C1Agent (service rep) and C2Agent (customer)

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
- Azure Cosmos DB account
- Azure credentials configured

### Installation

1. Create and activate a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Azure credentials and agent/model IDs
```

### Configuration

Edit `.env` file with your Azure configuration:

```env
# Azure AI Projects
AZURE_AI_PROJECT_CONNECTION_STRING=your_connection_string

# Cosmos DB
COSMOS_DB_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOS_DB_DATABASE_NAME=mount_doom_db

# Model IDs (for direct model access in general prompt)
GENERAL_MODEL_1=gpt-4
GENERAL_MODEL_2=gpt-35-turbo
```

**Note:** Agent IDs are no longer required in configuration. Each use case uses fixed agent names defined in the `instruction_sets` module.

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

### Persona Generation

- `GET /api/v1/persona-generation/models` - Get available models
- `POST /api/v1/persona-generation/generate` - Generate persona using PersonaAgent

### General Prompt

- `GET /api/v1/general-prompt/models` - Get available models
- `POST /api/v1/general-prompt/generate` - Generate response (direct model access, no agent)

### Prompt Validator

- `GET /api/v1/prompt-validator/models` - Get available models
- `POST /api/v1/prompt-validator/validate` - Validate prompt using PromptValidatorAgent

### Conversation Simulation

- `GET /api/v1/conversation-simulation/models` - Get available models
- `POST /api/v1/conversation-simulation/simulate` - Simulate conversation using C1Agent, C2Agent, and OrchestratorAgent

### Health Check

- `GET /health` - Check API health status

## Request Examples

### Generate Persona

```bash
curl -X POST "http://localhost:8000/api/v1/persona-generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a persona for a tech-savvy millennial",
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
    "agent_name": "PersonaAgent",
    "agent_version": "vab12cd34",
    "instructions": "You are a specialized persona generation agent...",
    "model": "gpt-4",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
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

Response includes details for all three agents (C1Agent, C2Agent, OrchestratorAgent).

## Authentication

The backend uses `DefaultAzureCredential` for Azure authentication, which supports:
- Environment variables
- Managed Identity
- Azure CLI authentication
- Visual Studio Code authentication
- And more...

Ensure your Azure credentials are configured properly before running the application.

## Data Storage

All use case results are automatically stored in Cosmos DB in separate containers with complete agent details:

### Containers
- `persona_generation` - Persona generation results with PersonaAgent details
- `general_prompt` - General prompt results (model-only, no agent)
- `prompt_validator` - Validation results with PromptValidatorAgent details
- `conversation_simulation` - Conversation results with C1Agent, C2Agent, and OrchestratorAgent details

### Stored Information
Each record includes:
- Request data (prompt, model, parameters)
- Response data (text, tokens used, timing)
- Agent details:
  - Agent name (e.g., "PersonaAgent", "C1Agent")
  - Agent version (hash of instructions)
  - Complete instruction set
  - Model used
  - Timestamp

Containers are created automatically if they don't exist.

## Development

### Code Style

The project follows Python best practices:
- PEP 8 style guide
- Type hints for better IDE support
- Pydantic models for data validation
- Clean architecture with separation of concerns

### Adding New Use Cases

1. Create instruction set in `app/instruction_sets/`:
   - Define agent name constant (e.g., `MY_AGENT_NAME = "MyAgent"`)
   - Define instructions constant (e.g., `MY_AGENT_INSTRUCTIONS = "..."`)
   - Export in `__init__.py`

2. Create request/response schemas in `app/models/schemas.py`:
   - Inherit from `BaseRequest` and `BaseResponse`
   - Include model parameter (default "gpt-4")
   - Response automatically includes `agent_details`

3. Add route file in `app/api/routes/`:
   - Import instruction set constants
   - Call `azure_ai_service.get_agent_response()` with agent name and instructions
   - Save to Cosmos DB with agent details

4. Include the router in `app/main.py`

5. Add Cosmos DB save method in `app/services/cosmos_db_service.py`

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
   - Models are now selected via the API (gpt-4, gpt-35-turbo)
   - Agent names are fixed and defined in instruction_sets module
   - Check that the model exists in your Azure AI deployment

4. **Instruction Set Changes Not Reflected**
   - Modify instruction files in `app/instruction_sets/`
   - Restart the server to load new instructions
   - New agent version will be automatically created

## License

Copyright (c) 2025. All rights reserved.

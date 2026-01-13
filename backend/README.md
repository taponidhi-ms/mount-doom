# Mount Doom Backend API

FastAPI backend for multi-agent conversation simulation and prompt generation using Azure AI Projects and Cosmos DB.

## Architecture

The backend follows clean architecture principles with clear separation of concerns:

```
backend/
├── app/
│   ├── core/                # Core configuration
│   ├── infrastructure/      # Shared infrastructure services
│   ├── models/              # Shared models
│   ├── modules/             # Feature modules (Vertical Slices)
│   │   ├── conversation_simulation/
│   │   ├── general_prompt/
│   │   ├── persona_distribution/
│   │   ├── persona_generator/
│   │   ├── prompt_validator/
│   │   ├── transcript_parser/
│   │   └── system/
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

### Agent Versioning
- Agent versions are automatically generated based on instruction set changes
- Version identifier: SHA256 hash of instructions (first 8 characters)
- When instructions change, a new version is automatically created
- All agent details (name, version, instructions, model) are saved to Cosmos DB

### Instruction Sets
All agent instructions are defined in the `app/modules/*/instructions.py` files:
- Each module has its own instruction definitions (e.g., `modules/conversation_simulation/instructions.py`)
- Instructions are constant strings that define agent behavior
- Modifying instructions in these files automatically creates new agent versions

## Features

### Use Cases

1. **Persona Distribution** - Generate persona distributions from simulation prompts
2. **Persona Generation** - Generate exact customer personas from natural language descriptions
3. **General Prompt** - Get responses for any general prompt using LLM models directly (no agent)
4. **Prompt Validator** - Validate simulation prompts using PromptValidatorAgent
5. **Transcript Parser** - Parse customer-representative transcripts to extract intent, subject, and sentiment
6. **Conversation Simulation** - Multi-turn conversation between C1Agent (service rep) and C2Agent (customer)

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

# Cosmos DB - Cloud Instance
COSMOS_DB_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOS_DB_DATABASE_NAME=mount_doom_db
COSMOS_DB_USE_EMULATOR=false

# Cosmos DB - Local Emulator (for testing)
# COSMOS_DB_ENDPOINT=https://localhost:8081
# COSMOS_DB_DATABASE_NAME=mount_doom_db
# COSMOS_DB_USE_EMULATOR=true
# COSMOS_DB_KEY=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==

# Model IDs (for direct model access in general prompt)
GENERAL_MODEL_1=gpt-4
GENERAL_MODEL_2=gpt-35-turbo
```

**Note:** Agent IDs are no longer required in configuration. Each use case uses fixed agent names defined in the `instruction_sets` module.

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
- `POST /api/v1/conversation-simulation/simulate` - Simulate conversation using C1Agent and C2Agent

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

Response includes details for both agents (C1Agent and C2Agent).

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
- `persona_generation` - Persona generation results with PersonaAgent details
- `general_prompt` - General prompt results (model-only, no agent)
- `prompt_validator` - Validation results with PromptValidatorAgent details
- `conversation_simulation` - Conversation results with C1Agent and C2Agent details

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

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
│   ├── models/              # Pydantic models and schemas
│   ├── services/            # Business logic and external service integrations
│   └── main.py             # FastAPI application entry point
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## Features

### Use Cases

1. **Persona Generation** - Generate personas from simulation prompts using specialized agents
2. **General Prompt** - Get responses for any general prompt using LLM models directly
3. **Prompt Validator** - Validate simulation prompts
4. **Conversation Simulation** - Complex multi-agent conversation between customer service rep and customer

### Key Capabilities

- Multiple agent support for each use case
- Direct model access (non-agent) for general prompts
- Token usage tracking for all requests
- Timing metrics for performance monitoring
- Cosmos DB integration for data persistence
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

# Agent IDs
PERSONA_GENERATION_AGENT_1=agent_id_1
PERSONA_GENERATION_AGENT_2=agent_id_2
PROMPT_VALIDATOR_AGENT=validator_agent_id
CONVERSATION_C1_AGENT=c1_agent_id
CONVERSATION_C2_AGENT=c2_agent_id
CONVERSATION_ORCHESTRATOR_AGENT=orchestrator_agent_id

# Model IDs
GENERAL_MODEL_1=gpt-4
GENERAL_MODEL_2=gpt-35-turbo
```

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

- `GET /api/v1/persona-generation/agents` - Get available agents
- `POST /api/v1/persona-generation/generate` - Generate persona

### General Prompt

- `GET /api/v1/general-prompt/models` - Get available models
- `POST /api/v1/general-prompt/generate` - Generate response

### Prompt Validator

- `GET /api/v1/prompt-validator/agents` - Get available agents
- `POST /api/v1/prompt-validator/validate` - Validate prompt

### Conversation Simulation

- `GET /api/v1/conversation-simulation/agents` - Get available agents
- `POST /api/v1/conversation-simulation/simulate` - Simulate conversation

### Health Check

- `GET /health` - Check API health status

## Request Examples

### Generate Persona

```bash
curl -X POST "http://localhost:8000/api/v1/persona-generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "your_agent_id",
    "prompt": "Create a persona for a tech-savvy millennial",
    "stream": false
  }'
```

### Simulate Conversation

```bash
curl -X POST "http://localhost:8000/api/v1/conversation-simulation/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "c1_agent_id": "c1_agent_id",
    "c2_agent_id": "c2_agent_id",
    "conversation_properties": {
      "CustomerIntent": "Technical Support",
      "CustomerSentiment": "Frustrated",
      "ConversationSubject": "Product Issue"
    },
    "max_turns": 10,
    "stream": false
  }'
```

## Authentication

The backend uses `DefaultAzureCredential` for Azure authentication, which supports:
- Environment variables
- Managed Identity
- Azure CLI authentication
- Visual Studio Code authentication
- And more...

Ensure your Azure credentials are configured properly before running the application.

## Data Storage

All use case results are automatically stored in Cosmos DB in separate containers:
- `persona_generation` - Persona generation results
- `general_prompt` - General prompt results
- `prompt_validator` - Validation results
- `conversation_simulation` - Conversation simulation results

Containers are created automatically if they don't exist.

## Development

### Code Style

The project follows Python best practices:
- PEP 8 style guide
- Type hints for better IDE support
- Pydantic models for data validation
- Clean architecture with separation of concerns

### Adding New Use Cases

1. Create a new schema in `app/models/schemas.py`
2. Add a new route file in `app/api/routes/`
3. Include the router in `app/main.py`
4. Add a new container method in `app/services/cosmos_db_service.py`

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
   - Verify agent/model IDs in `.env` file
   - Check Azure AI Projects for available agents
   - Ensure agents are deployed and accessible

## License

Copyright (c) 2025. All rights reserved.

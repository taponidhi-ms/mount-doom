---
paths:
  - "backend/**/*.py"
---

# Azure AI Integration Patterns

## Azure AI Projects SDK Documentation

**Important References** - Read these before making changes to Azure AI integration:
- [AIProjectClient Class Documentation](https://learn.microsoft.com/en-us/python/api/azure-ai-projects/azure.ai.projects.aio.aiprojectclient?view=azure-python-preview)
- [OpenAIClient Class Documentation](https://learn.microsoft.com/en-us/python/api/azure-ai-projects/azure.ai.projects.aio.openaiclient?view=azure-python-preview)
- [Azure AI Projects Agents Code Samples](https://github.com/Azure/azure-sdk-for-python/tree/azure-ai-projects_2.0.0b3/sdk/ai/azure-ai-projects/samples/agents)

Additional References:
- [Sample Workflow Multi-Agent](https://raw.githubusercontent.com/Azure/azure-sdk-for-python/refs/tags/azure-ai-projects_2.0.0b3/sdk/ai/azure-ai-projects/samples/agents/sample_workflow_multi_agent.py)
- [Workflow Concepts](https://raw.githubusercontent.com/MicrosoftDocs/azure-ai-docs/refs/heads/main/articles/ai-foundry/default/agents/concepts/workflow.md)
- [Azure AI Projects SDK README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/README.md)
- [Azure AI Documentation](https://github.com/MicrosoftDocs/azure-ai-docs/tree/main/articles/ai-foundry/default/agents)

## AzureAIService - Client Factory Only

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

## Service-Specific Agent Configuration

Each feature service contains:
- Fixed `agent_name` and `instructions` for that feature
- Agent creation logic by calling `azure_ai_service.create_agent()`
- Workflow-specific logic (conversation management, agent orchestration)
- Metrics tracking and data transformation

## Agent Instructions Storage

- All agent instructions are stored as Python string constants in `backend/app/modules/agents/instructions.py`
- Instructions are centralized in a single file for easy management
- Each instruction is a constant: `{AGENT_TYPE}_INSTRUCTIONS`
- Services and agent configs import the instruction constants directly

## Agent Usage Pattern

```python
# In your service class:
from app.modules.agents.instructions import PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS

class PersonaDistributionService:
    AGENT_NAME = "PersonaDistributionGeneratorAgent"
    INSTRUCTIONS = PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS

async def your_method(self, prompt: str):
    # Create agent using AzureAIService
    agent = azure_ai_service.create_agent(
        agent_name=self.AGENT_NAME,
        instructions=self.INSTRUCTIONS
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

## Conversation Management

- Use conversations (not threads) for stateful interactions
- Create conversations: `openai_client.conversations.create(items=[...])`
- Add messages: `openai_client.conversations.items.create(conversation_id, items=[...])`
- Create responses: `openai_client.responses.create(conversation=conversation_id, extra_body={...})`
- Each conversation maintains full context across all interactions
- Reuse conversation_id across multiple agent invocations for workflows

## Workflow Pattern (ConversationSimulationService)

For conversation simulation with multiple agents:
- Single conversation per simulation maintained across all turns
- All agents (C1, C2) operate on same conversation for context continuity
- Each agent invocation:
  1. Adds message to shared conversation
  2. Creates response using agent
  3. Returns tokens and response text
- Workflow continues until completion status or max_turns reached

## Automatic Versioning

- Generate version hash from instruction set: `hashlib.sha256(instructions.encode()).hexdigest()[:8]`
- Format as version string: `f"v{instructions_hash}"`
- Used for tracking agent versions in metrics and database

## Authentication

- Uses Azure DefaultAzureCredential
- Supports multiple auth methods (CLI, Managed Identity, etc.)
- **Automatic token refresh** - DefaultAzureCredential handles token refresh automatically
- No manual token management required
- For local Cosmos DB emulator, no Azure authentication needed (uses emulator key)
- Use `az login` for local development

## Error Handling

- Backend: HTTP exceptions with appropriate status codes
- Frontend: Error state display with user-friendly messages
- Logging: Structured logging with structlog

## Performance Tracking

- Token usage tracked for all AI interactions
- Timing metrics for all requests
- Per-message metrics in conversations
- All metrics visible in UI

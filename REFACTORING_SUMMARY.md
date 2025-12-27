# Agent Architecture Refactoring - Summary

## Overview
This document summarizes the changes made to refactor the Mount Doom application from a dynamic agent selection model to a fixed agent architecture with instruction-based versioning.

## Problem Statement Requirements

### Original Requirements
1. Don't allow passing agent_id in APIs - fix agent names for each use case
2. Remove agent_id passing from UI - allow passing model instead
3. Implement instruction-based agent versioning (similar to Azure AI Foundry pattern)
4. Store instruction sets in separate files for easy modification
5. Save complete agent details (name, version, instructions, model, timestamp) to Cosmos DB

## Changes Implemented

### 1. Backend - Instruction Sets Module (`backend/app/instruction_sets/`)

Created a new module with dedicated files for each agent:

#### Files Created:
- `__init__.py` - Module exports
- `c1_agent.py` - Customer service representative agent
- `c2_agent.py` - Customer agent  
- `orchestrator_agent.py` - Conversation completion orchestrator
- `persona_agent.py` - Persona generation agent
- `prompt_validator_agent.py` - Prompt validation agent

#### Agent Names (Fixed):
- **C1Agent** - "C1Agent"
- **C2Agent** - "C2Agent"
- **OrchestratorAgent** - "OrchestratorAgent"
- **PersonaAgent** - "PersonaAgent"
- **PromptValidatorAgent** - "PromptValidatorAgent"

Each file defines:
- Agent name constant (e.g., `C1_AGENT_NAME`)
- Agent instructions constant (e.g., `C1_AGENT_INSTRUCTIONS`)

### 2. Backend - Schema Updates (`backend/app/models/schemas.py`)

#### New Classes:
- `AgentDetails` - Contains agent metadata (name, version, instructions, model, timestamp)

#### Modified Request Schemas:
- **PersonaGenerationRequest**: 
  - Removed: `agent_id`
  - Added: `model` (default "gpt-4")
  
- **PromptValidatorRequest**:
  - Removed: `agent_id`
  - Added: `model` (default "gpt-4")
  
- **ConversationSimulationRequest**:
  - Removed: `c1_agent_id`, `c2_agent_id`
  - Added: `model` (default "gpt-4")

#### Modified Response Schemas:
- **BaseResponse**: Added `agent_details: AgentDetails`
- **ConversationMessage**: Changed `agent_id` to `agent_name` and `agent_version`
- **ConversationSimulationResponse**: 
  - Removed: `c1_agent_id`, `c2_agent_id`
  - Added: `c1_agent_details`, `c2_agent_details`, `orchestrator_agent_details`

### 3. Backend - Azure AI Service (`backend/app/services/azure_ai_service.py`)

#### Key Changes:
- Removed dependency on `PromptAgentDefinition` (not available in current SDK)
- Implemented instruction-based approach using OpenAI client with system messages
- Added automatic version generation using SHA256 hash of instructions

#### New Method Signature:
```python
async def get_agent_response(
    agent_name: str,        # Fixed agent name
    instructions: str,      # Instruction set
    prompt: str,           # User prompt
    model: str,            # Model to use (gpt-4, gpt-35-turbo)
    stream: bool = False
) -> tuple[str, Optional[int], str, datetime]:
    # Returns: (response_text, tokens_used, agent_version, timestamp)
```

#### Version Generation:
```python
instructions_hash = hashlib.sha256(instructions.encode()).hexdigest()[:8]
agent_version = f"v{instructions_hash}"
```

### 4. Backend - Cosmos DB Service (`backend/app/services/cosmos_db_service.py`)

#### Updated Methods:
All save methods now accept and store complete agent details:
- `save_persona_generation()` - Added agent details parameters
- `save_prompt_validator()` - Added agent details parameters
- `save_conversation_simulation()` - Added agent details for all three agents

#### Document Structure:
```json
{
  "id": "...",
  "prompt": "...",
  "response": "...",
  "tokens_used": 150,
  "time_taken_ms": 1250.5,
  "agent_details": {
    "agent_name": "PersonaAgent",
    "agent_version": "vab12cd34",
    "instructions": "You are a specialized...",
    "model": "gpt-4",
    "timestamp": "2025-01-15T10:30:00Z"
  },
  "timestamp": "2025-01-15T10:30:01Z"
}
```

### 5. Backend - API Routes

#### Updated Routes:
- `persona_generation.py`:
  - Changed `/agents` to `/models`
  - Uses `PERSONA_AGENT_NAME` and `PERSONA_AGENT_INSTRUCTIONS`
  - Returns model list instead of agent list
  
- `prompt_validator.py`:
  - Changed `/agents` to `/models`
  - Uses `PROMPT_VALIDATOR_AGENT_NAME` and `PROMPT_VALIDATOR_AGENT_INSTRUCTIONS`
  - Returns model list instead of agent list
  
- `conversation_simulation.py`:
  - Changed `/agents` to `/models`
  - Uses all three agent constants (C1, C2, Orchestrator)
  - Single model parameter for all agents
  - Returns complete agent details for all three agents

### 6. Frontend - API Client (`frontend/lib/api-client.ts`)

#### New File Created:
Type-safe API client with updated interfaces matching backend changes.

#### Key Types:
```typescript
interface AgentDetails {
  agent_name: string;
  agent_version?: string;
  instructions: string;
  model: string;
  timestamp: string;
}

interface BaseResponse {
  response_text: string;
  tokens_used?: number;
  time_taken_ms: number;
  start_time: string;
  end_time: string;
  agent_details: AgentDetails;
}
```

#### API Methods:
- `getPersonaModels()` - Get available models
- `generatePersona(prompt, model)` - Generate persona
- `getPromptValidatorModels()` - Get available models
- `validatePrompt(prompt, model)` - Validate prompt
- `getConversationModels()` - Get available models
- `simulateConversation(properties, model, maxTurns)` - Simulate conversation
- `getGeneralModels()` - Get available models (general prompt)
- `generateGeneralResponse(modelId, prompt)` - Generate response

### 7. Frontend - UI Updates

#### Updated Pages:
- `persona-generation/page.tsx`:
  - Model selection dropdown (replaces agent selection)
  - Calls `getPersonaModels()` and `generatePersona()`
  
- `prompt-validator/page.tsx`:
  - Model selection dropdown (replaces agent selection)
  - Calls `getPromptValidatorModels()` and `validatePrompt()`
  
- `conversation-simulation/page.tsx`:
  - Single model selection (replaces C1/C2 agent selection)
  - Simplified form with model dropdown
  - Calls `getConversationModels()` and `simulateConversation()`
  
- `general-prompt/page.tsx`:
  - Fixed to use correct API methods

#### Also Created:
- `lib/utils.ts` - Utility functions for UI components (cn function)

### 8. Configuration Changes

#### Environment Variables:
**Removed** from `.env`:
```env
# No longer needed
PERSONA_GENERATION_AGENT_1
PERSONA_GENERATION_AGENT_2
PROMPT_VALIDATOR_AGENT
CONVERSATION_C1_AGENT
CONVERSATION_C2_AGENT
CONVERSATION_ORCHESTRATOR_AGENT
```

**Still Required**:
```env
AZURE_AI_PROJECT_CONNECTION_STRING
COSMOS_DB_ENDPOINT
COSMOS_DB_DATABASE_NAME
GENERAL_MODEL_1=gpt-4
GENERAL_MODEL_2=gpt-35-turbo
```

### 9. Documentation Updates

#### Backend README:
- Added "Agent Architecture" section explaining fixed agents and versioning
- Updated configuration examples (removed agent IDs)
- Updated API endpoint documentation (changed /agents to /models)
- Updated request examples with new schema
- Added agent details to example responses
- Updated troubleshooting section

## Benefits of New Architecture

### 1. Simplified Configuration
- No need to manage agent IDs in environment variables
- Models are the only variable configuration

### 2. Easier Maintenance
- Instructions in separate, well-organized files
- Easy to modify agent behavior without touching code logic
- Clear separation between agent definition and usage

### 3. Automatic Versioning
- Version automatically generated from instruction hash
- Track when agent behavior changes
- Full traceability of agent configurations used

### 4. Better Data Tracking
- Complete agent context saved with every request
- Can recreate exact conditions of any historical request
- Better debugging and analytics capabilities

### 5. Improved User Experience
- Simpler UI with model selection instead of agent selection
- More intuitive - users care about model quality, not agent IDs
- Consistent experience across all use cases

### 6. Consistency
- Fixed agent names across system
- Predictable behavior
- Easier to reason about system architecture

## Migration Path

For existing deployments:

1. **Backend Migration**:
   - Update code to latest version
   - No agent configuration needed in `.env`
   - Existing Cosmos DB containers will have new structure for new records
   - Old records remain accessible (different schema)

2. **Frontend Migration**:
   - Deploy updated frontend
   - Users will see model selection instead of agent selection
   - Existing functionality preserved

3. **Data Migration** (optional):
   - Old records can be left as-is
   - Or migrate to new schema with agent_details structure

## Testing Checklist

- [x] Python syntax validation
- [x] TypeScript compilation
- [x] Next.js build
- [ ] Runtime testing with Azure credentials
- [ ] Integration testing
- [ ] End-to-end testing

## Files Modified

### Backend:
- `app/models/schemas.py` - Updated request/response schemas
- `app/services/azure_ai_service.py` - New agent response method
- `app/services/cosmos_db_service.py` - Updated save methods
- `app/api/routes/persona_generation.py` - Updated to use instruction sets
- `app/api/routes/prompt_validator.py` - Updated to use instruction sets
- `app/api/routes/conversation_simulation.py` - Updated to use instruction sets
- `README.md` - Documentation updates

### Backend - New Files:
- `app/instruction_sets/__init__.py`
- `app/instruction_sets/c1_agent.py`
- `app/instruction_sets/c2_agent.py`
- `app/instruction_sets/orchestrator_agent.py`
- `app/instruction_sets/persona_agent.py`
- `app/instruction_sets/prompt_validator_agent.py`

### Frontend:
- `app/persona-generation/page.tsx` - Model selection UI
- `app/prompt-validator/page.tsx` - Model selection UI
- `app/conversation-simulation/page.tsx` - Model selection UI
- `app/general-prompt/page.tsx` - Fixed API calls

### Frontend - New Files:
- `lib/api-client.ts` - Type-safe API client
- `lib/utils.ts` - UI utility functions

### Configuration:
- `.gitignore` - Updated to allow frontend/lib

## Conclusion

This refactoring successfully implements all requirements from the problem statement:
- ✅ Agent IDs removed from APIs and UI
- ✅ Fixed agent names for each use case
- ✅ Model selection enabled
- ✅ Instruction sets in separate files
- ✅ Automatic versioning based on instructions
- ✅ Complete agent details saved to Cosmos DB
- ✅ Documentation updated

The new architecture provides better maintainability, traceability, and user experience while simplifying the overall system design.

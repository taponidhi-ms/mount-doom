# Mount Doom - Use Cases

## Use Case 1: Persona Generation

**Purpose**: Generate detailed personas from simulation prompts using specialized AI agents.

**Workflow**:
1. User selects a model (GPT-4 or GPT-3.5 Turbo)
2. User enters a simulation prompt describing the persona requirements
3. Backend sends prompt to PersonaAgent via Azure AI Projects
4. PersonaAgent generates detailed persona response
5. Response stored in Cosmos DB `persona_generation` container with complete agent details
6. Frontend displays persona with metrics

**Agent**: 
- PersonaAgent (fixed agent name)
- Instructions defined in `PersonaGenerationService`
- Automatic versioning based on instruction hash
- Model: gpt-4 (default from settings)

**Metrics Tracked**:
- Tokens used
- Time taken
- Start/end timestamps
- Agent details (name, version, instructions, model)

**Browse API**:
- GET `/api/v1/persona-generation/browse`
- Supports pagination and ordering
- Returns list of past persona generations

---

## Use Case 2: General Prompt

**Purpose**: Get responses for any general prompt using LLM models directly (without agent).

**Workflow**:
1. User enters any general prompt
2. Backend calls model directly using inference API (default: gpt-4)
3. Model generates response
4. Response stored in Cosmos DB `general_prompt` container
5. Frontend displays response with metrics

**Models**:
- Uses default model from settings (gpt-4)
- Direct model access (not agent-based) for faster responses

**Key Difference**: Uses model directly, not agent, for faster responses.

**Browse API**:
- GET `/api/v1/general-prompt/browse`
- Supports pagination and ordering
- Returns list of past general prompts

---

## Use Case 3: Prompt Validator

**Purpose**: Validate simulation prompts to ensure quality and effectiveness.

**Workflow**:
1. User selects a model (GPT-4 or GPT-3.5 Turbo)
2. User enters simulation prompt to validate
3. Backend sends prompt to PromptValidatorAgent
4. PromptValidatorAgent analyzes prompt and provides feedback
5. Response stored in Cosmos DB `prompt_validator` container with complete agent details
6. Frontend displays validation results

**Agent**:
- PromptValidatorAgent (fixed agent name)
- Instructions defined in `PromptValidatorService`
- Automatic versioning based on instruction hash
- Model: gpt-4 (default from settings)

**Validation Aspects**:
- Clarity and specificity
- Completeness
- Potential improvements
- Quality assessment

**Browse API**:
- GET `/api/v1/prompt-validator/browse`
- Supports pagination and ordering
- Returns list of past validations

---

## Use Case 4: Conversation Simulation

**Purpose**: Simulate multi-turn conversations between customer service representative and customer.

**Participants**:
- **C1Agent**: Customer Service Representative (fixed agent name)
- **C2Agent**: Customer (fixed agent name)
- **OrchestratorAgent**: Determines conversation completion (fixed agent name)

**Workflow**:
1. User selects a model (GPT-4 or GPT-3.5 Turbo) - used for all three agents
2. User configures conversation in one of two ways:
   - **Option A**: Select existing persona from persona generation container
   - **Option B**: Manually input customer properties:
     - Customer Intent (e.g., "Technical Support")
     - Customer Sentiment (e.g., "Frustrated")
     - Conversation Subject (e.g., "Product Issue")
3. User sets max turns (1-20)
4. Simulation starts:
   - C1Agent speaks first (as service rep)
   - OrchestratorAgent checks if conversation is complete
   - C2Agent responds (as customer)
   - OrchestratorAgent checks again
   - Repeat until complete or max turns reached
5. Full conversation stored in Cosmos DB `conversation_simulation` container with details for all three agents
6. Frontend displays conversation history with metrics

**Agents**:
- All three agents use fixed names and instructions defined in service classes
- Automatic versioning for each agent based on their instruction hash
- Model: gpt-4 (default from settings)

**C1 Agent Prompt Template**:
```
Generate a next message as an Agent for the following ongoing conversation:
ConversationProperties: {json}
messages: {history}
```

**C2 Agent Prompt Template**:
```
Generate a next message as a customer for the following ongoing conversation:
ConversationProperties: {json}
messages: {history}
```

**Orchestrator Response**:
```json
{
  "ConversationStatus": "Ongoing" | "Completed"
}
```

**Metrics Tracked**:
- Per-message tokens and timing
- Total tokens used
- Total time taken
- Conversation status
- Number of turns completed

**Key Features**:
- Turn-by-turn simulation
- Intelligent completion detection
- Full conversation history
- Detailed per-message metrics
- Maximum 20 turns for safety
- Persona selection or manual input

**Browse API**:
- GET `/api/v1/conversation-simulation/browse`
- Supports pagination and ordering
- Returns list of past simulations

---

## Common Features Across All Use Cases

### Request Features
- Non-streaming by default (streaming planned for future)
- Model: gpt-4 (default from settings)
- Prompt input (varies by use case)

### Response Features
- Token usage tracking
- Timing metrics (milliseconds)
- Start and end timestamps
- Full response text or conversation history
- Copy-to-clipboard JSON export

### Storage
- All results saved to Cosmos DB
- Separate containers per use case
- Complete request/response data
- Timestamps for analytics

### UI Features
- Clean, intuitive interface with shadcn/ui components
- Tab-based navigation (Generate/History)
- Real-time loading states
- Error handling and display
- Metrics visualization
- Paginated history browsing
- Responsive design
- Table view for browsing past results

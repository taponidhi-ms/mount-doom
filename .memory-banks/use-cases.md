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
- Instructions defined in `instruction_sets/persona_agent.py`
- Automatic versioning based on instruction hash
- Model selection by user (gpt-4 or gpt-35-turbo)

**Metrics Tracked**:
- Tokens used
- Time taken
- Start/end timestamps
- Agent details (name, version, instructions, model)

---

## Use Case 2: General Prompt

**Purpose**: Get responses for any general prompt using LLM models directly (without agent).

**Workflow**:
1. User selects a model (GPT-4 or GPT-3.5 Turbo)
2. User enters any general prompt
3. Backend calls model directly using inference API
4. Model generates response
5. Response stored in Cosmos DB `general_prompt` container
6. Frontend displays response with metrics

**Models**:
- GPT-4: Advanced model for complex tasks
- GPT-3.5 Turbo: Fast model for general tasks

**Key Difference**: Uses model directly, not agent, for faster responses.

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
- Instructions defined in `instruction_sets/prompt_validator_agent.py`
- Automatic versioning based on instruction hash
- Model selection by user (gpt-4 or gpt-35-turbo)

**Validation Aspects**:
- Clarity and specificity
- Completeness
- Potential improvements
- Quality assessment

---

## Use Case 4: Conversation Simulation

**Purpose**: Simulate multi-turn conversations between customer service representative and customer.

**Participants**:
- **C1Agent**: Customer Service Representative (fixed agent name)
- **C2Agent**: Customer (fixed agent name)
- **OrchestratorAgent**: Determines conversation completion (fixed agent name)

**Workflow**:
1. User selects a model (GPT-4 or GPT-3.5 Turbo) - used for all three agents
2. User configures conversation properties:
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
- All three agents use fixed names and instructions from `instruction_sets/` module
- Automatic versioning for each agent based on their instruction hash
- Single model selection applies to all agents

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

---

## Common Features Across All Use Cases

### Request Features
- Non-streaming by default (streaming planned for future)
- Agent/model selection
- Prompt input

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
- Clean, intuitive interface
- Real-time loading states
- Error handling and display
- Metrics visualization
- JSON export functionality
- Responsive design

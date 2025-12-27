# Mount Doom - Use Cases

## Use Case 1: Persona Generation

**Purpose**: Generate detailed personas from simulation prompts using specialized AI agents.

**Workflow**:
1. User selects an agent from available persona generation agents
2. User enters a simulation prompt describing the persona requirements
3. Backend sends prompt to selected agent via Azure AI Projects
4. Agent generates detailed persona response
5. Response stored in Cosmos DB `persona_generation` container
6. Frontend displays persona with metrics

**Agents**: 
- Multiple agents available
- Each optimized for different persona types
- Agent IDs configured in environment

**Metrics Tracked**:
- Tokens used
- Time taken
- Start/end timestamps

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
1. User selects validator agent
2. User enters simulation prompt to validate
3. Backend sends prompt to validator agent
4. Agent analyzes prompt and provides feedback
5. Response stored in Cosmos DB `prompt_validator` container
6. Frontend displays validation results

**Validation Aspects**:
- Clarity and specificity
- Completeness
- Potential improvements
- Quality assessment

---

## Use Case 4: Conversation Simulation

**Purpose**: Simulate multi-turn conversations between customer service representative and customer.

**Participants**:
- **C1 Agent**: Customer Service Representative
- **C2 Agent**: Customer
- **Orchestrator Agent**: Determines conversation completion

**Workflow**:
1. User selects C1 and C2 agents
2. User configures conversation properties:
   - Customer Intent (e.g., "Technical Support")
   - Customer Sentiment (e.g., "Frustrated")
   - Conversation Subject (e.g., "Product Issue")
3. User sets max turns (1-20)
4. Simulation starts:
   - C1 Agent speaks first (as service rep)
   - Orchestrator checks if conversation is complete
   - C2 Agent responds (as customer)
   - Orchestrator checks again
   - Repeat until complete or max turns reached
5. Full conversation stored in Cosmos DB `conversation_simulation` container
6. Frontend displays conversation history with metrics

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

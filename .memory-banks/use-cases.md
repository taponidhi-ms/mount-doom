# Mount Doom - Use Cases

## Use Case 1: Persona Distribution Generator

**Purpose**: Generate persona distributions from simulation prompts using specialized AI agents. Outputs structured JSON with conversation counts, intents, sentiments, and proportions.

**Workflow**:
1. User enters a simulation prompt describing the distribution requirements
2. Backend sends prompt to PersonaDistributionGeneratorAgent via Azure AI Projects
3. PersonaDistributionGeneratorAgent generates distribution response (parser-based instruction)
4. Backend parses JSON output and stores both raw and parsed versions
5. Response stored in Cosmos DB `persona_distribution` container with complete agent details
6. Frontend displays persona distribution with metrics and parsed output

**Agent**: 
- PersonaDistributionGeneratorAgent (fixed agent name)
- Instructions defined in `app/instruction_sets/persona_distribution.py`
- Automatic versioning based on instruction hash
- Model: gpt-4 (default from settings)

**Output Format**:
```json
{
  "ConvCount": <integer>,
  "intents": [{"intent": "<string>", "percentage": <number>, "subject": "<string>"}],
  "Sentiments": [{"sentiment": "<string>", "percentage": <number>}],
  "Proportions": [{"intent": "<string>", "count": <integer>}],
  "IsTranscriptBasedSimulation": <boolean>,
  "CallerPhoneNumber": "<string>",
  "RecipientPhoneNumber": "<string>"
}
```

**Metrics Tracked**:
- Tokens used
- Time taken
- Start/end timestamps
- Agent details (name, version, instructions, model)
- Parsed JSON output (if parsing successful)

**Database Schema**:
- Document ID: conversation_id from Azure AI
- Fields: prompt, response, parsed_output, tokens_used, time_taken_ms, agent_details, timestamp

**Browse API**:
- GET `/api/v1/persona-distribution/browse`
- Supports pagination and ordering
- Returns list of past persona distribution generations

---

## Use Case 2: Persona Generator

**Purpose**: Generate exact customer personas with specific intents, sentiments, subjects, and metadata. Outputs a list of detailed personas for conversation simulations.

**Workflow**:
1. User enters a prompt describing what personas to generate (e.g., "Generate 5 personas for technical support")
2. Backend sends prompt to PersonaGeneratorAgent via Azure AI Projects
3. PersonaGeneratorAgent generates exact personas with metadata
4. Backend parses JSON output and stores both raw and parsed versions
5. Response stored in Cosmos DB `persona_generator` container with complete agent details
6. Frontend displays personas with metrics and parsed output

**Agent**: 
- PersonaGeneratorAgent (fixed agent name)
- Instructions defined in `app/instruction_sets/persona_generator.py`
- Automatic versioning based on instruction hash
- Model: gpt-4 (default from settings)

**Output Format**:
```json
{
  "CustomerPersonas": [
    {
      "CustomerIntent": "<string>",
      "CustomerSentiment": "<string>",
      "ConversationSubject": "<string>",
      "CustomerMetadata": {
        "key1": "value1",
        "key2": "value2"
      }
    }
  ]
}
```

**Metrics Tracked**:
- Tokens used
- Time taken
- Start/end timestamps
- Agent details (name, version, instructions, model)
- Parsed JSON output (if parsing successful)

**Database Schema**:
- Document ID: conversation_id from Azure AI
- Fields: prompt, response, parsed_output, tokens_used, time_taken_ms, agent_details, timestamp

**Browse API**:
- GET `/api/v1/persona-generator/browse`
- Supports pagination and ordering
- Returns list of past persona generations

---

## Use Case 3: General Prompt

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
1. User enters simulation prompt to validate
2. Backend sends prompt to PromptValidatorAgent
3. PromptValidatorAgent analyzes prompt and provides feedback
4. Response stored in Cosmos DB `prompt_validator` container with complete agent details
5. Frontend displays validation results

**Agent**:
- PromptValidatorAgent (fixed agent name)
- Instructions defined in `app/instruction_sets/prompt_validator.py`
- Automatic versioning based on instruction hash
- Model: gpt-4 (default from settings)

**Validation Aspects**:
- Clarity and specificity
- Completeness
- Potential improvements
- Quality assessment

**Database Schema**:
- Document ID: conversation_id from Azure AI
- Fields: prompt, response, tokens_used, time_taken_ms, agent_details, timestamp

**Browse API**:
- GET `/api/v1/prompt-validator/browse`
- Supports pagination and ordering
- Returns list of past validations

---

## Use Case 5: Conversation Simulation

**Purpose**: Simulate multi-turn conversations between customer service representative and customer.

**Participants**:
- **C1Agent**: Customer Service Representative (fixed agent name)
- **C2Agent**: Customer (fixed agent name)
- **OrchestratorAgent**: Determines conversation completion (fixed agent name)

**Workflow**:
1. User provides customer configuration directly:
   - Customer Intent (e.g., "Technical Support")
   - Customer Sentiment (e.g., "Frustrated")
   - Conversation Subject (e.g., "Product Issue")
2. Max turns is hardcoded to 20 in backend
3. Simulation starts:
   - C1Agent speaks first (as service rep)
   - OrchestratorAgent checks if conversation is complete
   - C2Agent responds (as customer)
   - OrchestratorAgent checks again
   - Repeat until complete or max turns (20) reached
4. Full conversation stored in Cosmos DB `conversation_simulation` container with details for all three agents
5. Frontend displays conversation history with metrics

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
- Conversation ID from Azure AI

**Database Schema**:
- Document ID: conversation_id from Azure AI
- Fields: conversation_properties, conversation_history, conversation_status, total_tokens_used, total_time_taken_ms, c1_agent_details, c2_agent_details, orchestrator_agent_details, timestamp

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
- Model is hardcoded in backend (GPT-4)
- Prompt input (varies by use case)

### Response Features
- Token usage tracking
- Timing metrics (milliseconds)
- Start and end timestamps
- Full response text or conversation history
- Copy-to-clipboard JSON export
- Conversation ID tracking

### Storage
- All results saved to Cosmos DB
- Document IDs use conversation_id from Azure AI
- Separate containers per use case
- JSON parsing for persona agents (parsed_output field)
- Separate containers per use case
- Complete request/response data
- Timestamps for analytics

### UI Features
- Clean, intuitive interface with Ant Design components
- Tab-based navigation (Generate/History)
- Real-time loading states with spinners
- Error handling with Alert components
- Toast notifications for success/error
- Metrics visualization
- Paginated history browsing
- Responsive design
- Table view for browsing past results with expandable rows
- Proper accessibility with ARIA labels

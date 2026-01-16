# Mount Doom - Use Cases

## Use Case 1: Persona Distribution Generator

### Updated Agent Behavior Guidelines
- All agents involved in use cases must follow the newly defined behavior guidelines to ensure appropriate handling of prompts.


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
- Instructions defined in `app/modules/persona_distribution/instructions.py`
- Instruction set includes a small set of sample prompts/expected JSON shapes for grounding (examples are not meant to be echoed)
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

**Evals Preparation**:
- POST `/api/v1/persona-distribution/prepare-evals` - Prepare CXA AI Evals from selected runs
- GET `/api/v1/persona-distribution/evals/latest` - Get latest prepared evals
- Combines multiple persona distribution runs into standardized evals format
- Generates predefined evaluation rules (no LLM usage)
- Stores results in `persona_distribution_evals` container
- Frontend: "Prepare for Evals" tab with multi-select table and a single zip download
- Output: a zip named by `evals_id` containing `cxa_evals_config.json` and `cxa_evals_input_data.json`

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
- Instructions defined in `app/modules/persona_generator/instructions.py`
- Instruction set includes sample prompts and minified JSON examples aligned with the "no newline characters" output rule
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

## Use Case 3: Transcript Parser

**Purpose**: Parse customer-representative transcripts to extract intent, subject, and sentiment.

**Workflow**:
1. User pastes or enters a transcript from a customer-representative conversation
2. Backend sends transcript to TranscriptParserAgent via Azure AI Projects
3. TranscriptParserAgent analyzes the conversation and extracts:
   - Intent: What the customer wants
   - Subject: Main topic or issue
   - Sentiment: Emotional tone (calm, curious, angry, unkind, etc.)
4. Backend parses JSON output and stores both raw and parsed versions
5. Response stored in Cosmos DB `transcript_parser` container with complete agent details
6. Frontend displays parsed result with extracted metadata

**Agent**:
- TranscriptParserAgent (fixed agent name)
- Instructions defined in `app/modules/transcript_parser/instructions.py`
- Instruction set focuses on analyzing customer-representative conversations
- Automatic versioning based on instruction hash
- Model: gpt-4 (default from settings)

**Output Format**:
```json
{
  "intent": "<string>",
  "subject": "<string>",
  "sentiment": "<string>"
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
- Fields: transcript, response, parsed_output, tokens_used, time_taken_ms, agent_details, timestamp

**Browse API**:
- GET `/api/v1/transcript-parser/browse`
- Supports pagination and ordering
- Returns list of past transcript parsing records

**Sample Transcripts**:
- Phone upgrade inquiries
- Device troubleshooting calls
- Return/refund requests
- Account management conversations

---

## Use Case 4: Conversation Simulation

**Purpose**: Simulate multi-turn conversations between customer service representative and customer.

**Participants**:
- **C1Agent**: Customer Service Representative (fixed agent name)
- **C2Agent**: Customer (fixed agent name)

**Workflow**:
1. User provides customer configuration:
   - **Single Simulation**: Manually enter Customer Intent, Customer Sentiment, and Conversation Subject.
   - **Batch Simulation**: Upload a JSON file containing a list of personas (CustomerIntent, CustomerSentiment, ConversationSubject).
2. Max turns is hardcoded to 20 in backend
3. Simulation starts (sequentially for batch):
   - C1Agent speaks first (as service rep)
  - Check for termination phrase after C1 ("transfer this call to my supervisor" or "end this call now")
  - C2Agent responds (as customer) using injected customer properties
   - Repeat until complete or max turns (20) reached
4. Full conversation stored in Cosmos DB `conversation_simulation` container with details for agents
5. Frontend displays conversation history with metrics

**Agents**:
- Agents use fixed names and instructions defined in `app/modules/conversation_simulation/instructions.py`
- Automatic versioning for each agent based on their instruction hash
- Model: gpt-4 (default from settings)
- C1/C2 instruction sets include sample next-message prompt shapes to ground responses to the expected input format

**C1 Agent Prompt Template**:
```
Generate a next message as an Agent for the following ongoing conversation:
messages: {history}
```

**C2 Agent Prompt Template**:
```
Generate a next message as a customer for the following ongoing conversation:
CustomerContext: {json}
RepresentativeLastMessage: {text}
```

**Completion Logic**:
- Conversation ends if C1 says "i will transfer this call to my supervisor now"
- Conversation ends if C1 says "I will end this call now."
- Conversation ends if max turns (20) reached

**Metrics Tracked**:
- Per-message tokens and timing
- Total tokens used
- Total time taken
- Conversation status
- Number of turns completed
- Conversation ID from Azure AI

**Database Schema**:
- Document ID: conversation_id from Azure AI
- Fields: conversation_properties, conversation_history, conversation_status, total_tokens_used, total_time_taken_ms, c1_agent_details, c2_agent_details, timestamp

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

**Evals Preparation**:
- POST `/api/v1/conversation-simulation/evals/prepare` - Prepare CXA AI Evals from selected runs
- GET `/api/v1/conversation-simulation/evals/latest` - Get latest prepared evals
- Combines simulation runs into evals format
- Target agent: C2Agent (evaluated as Assistant) against C1Agent (User messages)
- Stores results in `conversation_simulation_evals` container
- Frontend: "Prepare for Evals" tab
- Output: zip download with config and data

---

## Use Case 5: Conversation Simulation V2

**Purpose**: Simulate multi-turn conversations v2 with distinct C1/C2 logic using Python control flow (Manual Logic).

**Participants**:
- **C1MessageGeneratorAgent**: Customer Service Representative (new agent name)
- **C2MessageGeneratorAgent**: Customer (new agent name)

**Workflow**:
1. User provides customer configuration (Manual entry of Intent, Sentiment, Subject).
2. Max turns is hardcoded to 10 in backend (v2 constraint).
3. Simulation starts:
   - System initiates conversation with "Hello" from customer perspective to trigger C1.
   - Loop:
     - **C1 Turn**: C1MessageGeneratorAgent generates response to conversation history.
     - **C1 Termination Check**: If C1 says "end this call now" or "transfer...", loop ends.
     - **C2 Turn**: 
       - Backend constructs JSON transcript of conversation + properties.
       - C2MessageGeneratorAgent generates response using this transcript as input.
       - C2 response is added to the conversation history.
     - Repeat until 10 turns.
4. Full conversation stored in Cosmos DB `conversation_simulation_v2` container.
5. Frontend displays conversation history.

**Agents**:
- Instructions defined in `app/modules/conversation_simulation_v2/instructions.py`
- **C1 Instructions**: Standard CSR instructions, unaware of hidden conversation properties.
- **C2 Instructions**: Customer instructions, explicitly aware of properties via JSON input. Includes instruction to "Use the Properties section..." and respond naturally.

**Differences from V1**:
- Uses `C1MessageGeneratorAgent` and `C2MessageGeneratorAgent` instead of generic C1/C2.
- C1 is unaware of conversation properties (properties removed from C1 context).
- C2 receives context via "Ongoing transcript" JSON input string instead of implicit context.
- Orchestration is done via explicit Python loop + individual Agent API calls, rather than Azure AI Workflow YAML.
- Data stored in `conversation_simulation_v2` container.

**Browse API**:
- GET `/api/v1/conversation-simulation-v2/browse`
- Delete/Download endpoints also available.

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

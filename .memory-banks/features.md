# Mount Doom - Features

## Feature 1: Persona Distribution Generator

### Updated Agent Behavior Guidelines
- All agents involved in features must follow the newly defined behavior guidelines to ensure appropriate handling of prompts.


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

---

## Feature 2: Persona Generator

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

## Feature 3: Transcript Parser

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

## Feature 4: C2 Message Generation

**Purpose**: Generate C2 (customer) messages for use in conversation simulations or standalone.

**Workflow**:
1. User provides a prompt with conversation context
2. Backend sends prompt to C2MessageGeneratorAgent via unified agents service
3. Agent generates a customer message based on the context
4. **Response stored in Cosmos DB** `c2_message_generation` container with full metrics
5. Frontend displays the generated message

**Agent**:
- C2MessageGeneratorAgent (fixed agent name)
- Instructions defined in `app/modules/agents/instructions.py`
- Model: gpt-4 (default from settings)
- **Accessed via**: Unified agents API (`/api/v1/agents/c2_message_generation/invoke`)

**Database Schema**:
- Document ID: conversation_id from Azure AI
- Fields: prompt, response, tokens_used, time_taken_ms, agent_details, timestamp, conversation_id

**Metrics Tracked**:
- Tokens used (for both standalone and simulation use)
- Time taken
- Conversation ID from Azure AI
- Start/end timestamps

---

## Feature 5: Conversation Simulation

**Purpose**: Simulate multi-turn conversations with distinct C1/C2 logic using Python control flow.

**Participants**:
- **C1MessageGeneratorAgent**: Customer Service Representative (agent name)
- **C2MessageGeneratorAgent**: Customer (agent name, uses c2_message_generation module)

**Workflow**:
1. User provides customer configuration (Manual entry of Intent, Sentiment, Subject).
2. Max turns is hardcoded to 15 in backend.
3. Simulation starts:
   - **Empty conversation created** (no initial customer message)
   - **C1 checks for empty conversation** and greets the customer on first turn
   - Loop:
     - **C1 Turn**: C1MessageGeneratorAgent generates response to conversation history.
     - **C1 Termination Check**: If C1 says "end this call now" or "transfer...", loop ends.
     - **C2 Turn**:
       - Backend constructs prompt: "Generate a next message as a customer for the following ongoing conversation where ConversationProperties: {...} Messages: [...]"
       - **C2 via unified agents service**: Uses `invoke_agent('c2_message_generation', prompt, persist=True)`
       - **C2 conversation persisted**: Tokens, conversation_id, and full metrics saved to database
       - C2 response is added to the conversation history.
     - Repeat until 15 turns or completion.
4. Full conversation stored in Cosmos DB `conversation_simulation` container.
5. Frontend displays conversation history with tokens for both C1 and C2 messages.

**Agents**:
- Instructions defined in `app/modules/agents/instructions.py`
- **C1 Instructions**:
  - Standard CSR instructions, unaware of hidden conversation properties
  - **Greeting behavior**: Explicitly instructed to greet customer when conversation is empty
  - Example: "Hi there, how can I help you today?"
- **C2 Instructions**: Customer instructions, explicitly aware of properties via structured prompt input.

**Key Features**:
- **C1 greeting on empty conversation**: C1 checks if conversation is empty and greets customer
- C1 is unaware of conversation properties (properties removed from C1 context).
- **C2 receives context via structured prompt**: "Generate a next message as a customer for the following ongoing conversation where ConversationProperties: {...} Messages: [...]"
- **C2 via unified agents service**: Uses `invoke_agent()` with `persist=True` for database storage
- **C2 metrics tracked**: tokens_used and conversation_id for every C2 message
- Orchestration is done via explicit Python loop + individual Agent API calls.
- **Two database containers**:
  - `conversation_simulation` - Full multi-turn conversations
  - `c2_message_generation` - Individual C2 message generations

**Browse API**:
- GET `/api/v1/conversation-simulation/browse`
- Delete/Download endpoints also available.

---

## Unified Agents API

**Purpose**: Provides a single consolidated API for all single-agent operations, replacing the need for separate endpoints per agent.

**Key Features**:
- List all available agents with their configurations and instructions
- Invoke any agent by agent_id with a generic input
- Browse, delete, and download agent history records
- Agent instructions are exposed to the frontend for display

**Agent Registry**:
The agent configuration is centralized in `backend/app/modules/agents/config.py`:
- `persona_distribution` - Persona Distribution Generator Agent
- `persona_generator` - Persona Generator Agent
- `transcript_parser` - Transcript Parser Agent
- `c2_message_generation` - C2 Message Generator Agent

**API Endpoints**:
- GET `/api/v1/agents/list` - List all agents
- GET `/api/v1/agents/{agent_id}` - Get agent details
- POST `/api/v1/agents/{agent_id}/invoke` - Invoke agent
- GET `/api/v1/agents/{agent_id}/browse` - Browse history
- POST `/api/v1/agents/{agent_id}/delete` - Delete records
- POST `/api/v1/agents/{agent_id}/download` - Download records

---

## Workflows API

**Purpose**: Provides configuration and metadata for multi-agent workflows.

**Key Features**:
- List all available workflows with their agent configurations
- Get workflow details including all agent instructions
- Workflow execution routes remain in their respective modules

**Workflow Registry**:
The workflow configuration is centralized in `backend/app/modules/workflows/config.py`:
- `conversation_simulation` - Multi-turn conversation between C1 and C2 agents

**API Endpoints**:
- GET `/api/v1/workflows/list` - List all workflows
- GET `/api/v1/workflows/{workflow_id}` - Get workflow details with agent instructions

---

## Common Features Across All Features

### Request Features
- Non-streaming by default (streaming planned for future)
- Model is hardcoded in backend (GPT-4)
- Prompt input (varies by feature)

### Response Features
- Token usage tracking
- Timing metrics (milliseconds)
- Start and end timestamps (using `datetime.now(timezone.utc)`)
- Full response text or conversation history
- Copy-to-clipboard JSON export
- Conversation ID tracking

### Storage
- All results saved to Cosmos DB
- Document IDs use conversation_id from Azure AI
- Separate containers per feature
- JSON parsing for persona agents (parsed_output field)
- Complete request/response data
- Timestamps for analytics

### UI Features
- Clean, intuitive interface with Ant Design components
- Tab-based navigation (Generate/Batch/History)
- Real-time loading states with spinners
- Error handling with Alert components
- Toast notifications for success/error
- Metrics visualization
- Paginated history browsing
- Responsive design
- Table view for browsing past results with expandable rows
- Proper accessibility with ARIA labels
- **Agent instructions display**: All agent pages show the agent's instruction set (collapsible)
- **Workflow instructions display**: Workflow pages show all agent instructions in collapsible panels
- **Dynamic navigation**: Sidebar with "Agents" and "Workflows" sections

### History Table Enhancements
- **Column visibility controls**: Settings dropdown (⚙️) to show/hide columns
- **Document ID column**: Hidden by default, shows Cosmos DB document ID (copyable)
- **Conversation ID column**: Hidden by default, shows Azure AI conversation ID (copyable)
- **Fixed column widths**: 200-300px to prevent horizontal scroll
- **Tooltips on hover**: View full text for long content
- **Ellipsis for overflow**: Prevents text breaking table layout
- **Consistent across all pages**: SingleAgentTemplate and custom agent pages

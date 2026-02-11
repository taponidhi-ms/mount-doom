# Features Documentation

Mount Doom supports 9 main features across agents and workflows (with 9 specialized agents in the Unified Agents API).

## Feature 1: Persona Distribution Generator

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
- Instructions defined in `app/modules/agents/instructions.py`
- Instruction set includes a small set of sample prompts/expected JSON shapes for grounding
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

## Feature 2: Persona Generator

**Purpose**: Generate exact customer personas with specific intents, sentiments, subjects, and metadata. Outputs a list of detailed personas for conversation simulations.

**Workflow**:
1. User enters a prompt describing what personas to generate
2. Backend sends prompt to PersonaGeneratorAgent via Azure AI Projects
3. PersonaGeneratorAgent generates exact personas with metadata
4. Backend parses JSON output and stores both raw and parsed versions
5. Response stored in Cosmos DB `persona_generator` container with complete agent details
6. Frontend displays personas with metrics and parsed output

**Agent**:
- PersonaGeneratorAgent (fixed agent name)
- Instructions defined in `app/modules/agents/instructions.py`
- Instruction set includes sample prompts and minified JSON examples
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

## Feature 3: Transcript Parser

**Purpose**: Parse customer-representative transcripts to extract intent, subject, and sentiment.

**Workflow**:
1. User pastes or enters a transcript from a customer-representative conversation
2. Backend sends transcript to TranscriptParserAgent via Azure AI Projects
3. TranscriptParserAgent analyzes the conversation and extracts intent, subject, and sentiment
4. Backend parses JSON output and stores both raw and parsed versions
5. Response stored in Cosmos DB `transcript_parser` container with complete agent details
6. Frontend displays parsed result with extracted metadata

**Agent**:
- TranscriptParserAgent (fixed agent name)
- Instructions defined in `app/modules/agents/instructions.py`
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

**Metrics Tracked**:
- Tokens used (for both standalone and simulation use)
- Time taken
- Conversation ID from Azure AI
- Start/end timestamps

## Feature 5: Conversation Simulation

**Purpose**: Simulate multi-turn conversations with distinct C1/C2 logic using Python control flow.

**Documentation**: See [Synthetic Data Generation & Evaluation Strategy](../presentations/synthetic-data-generation.md) for a leadership-friendly overview of the workflow and evaluation approach.

**Participants**:
- **C1MessageGeneratorAgent**: Customer Service Representative
- **C2MessageGeneratorAgent**: Customer (uses c2_message_generation module)

**Workflow**:
1. User provides customer configuration (Intent, Sentiment, Subject)
2. Max turns is hardcoded to 15 in backend
3. Simulation starts:
   - **Empty conversation created** (no initial customer message)
   - **C1 checks for empty conversation** and greets the customer on first turn
   - Loop:
     - **C1 Turn**: C1MessageGeneratorAgent generates response to conversation history
     - **C1 Termination Check**: If C1 says "end this call now" or "transfer...", loop ends
     - **C2 Turn**:
       - Backend constructs prompt with conversation properties and messages
       - **C2 via unified agents service**: Uses `invoke_agent('c2_message_generation', prompt, persist=True)`
       - **C2 conversation persisted**: Tokens, conversation_id, and full metrics saved to database
       - C2 response is added to the conversation history
     - Repeat until 15 turns or completion
4. Full conversation stored in Cosmos DB `conversation_simulation` container
5. Frontend displays conversation history with tokens for both C1 and C2 messages

**Agents**:
- Instructions defined in `app/modules/agents/instructions.py`
- **C1 Instructions**: Standard CSR instructions, explicitly instructed to greet customer when conversation is empty
- **C2 Instructions**: Customer instructions, explicitly aware of properties via structured prompt input

**Key Features**:
- **C1 greeting on empty conversation**: C1 checks if conversation is empty and greets customer
- C1 is unaware of conversation properties
- **C2 receives context via structured prompt**: Properties and messages included
- **C2 via unified agents service**: Uses `invoke_agent()` with `persist=True`
- **C2 metrics tracked**: tokens_used and conversation_id for every C2 message
- **Two database containers**:
  - `conversation_simulation` - Full multi-turn conversations
  - `c2_message_generation` - Individual C2 message generations

## Feature 6: Unified Agents API

**Purpose**: Provides a unified consolidated API for all agent operations, eliminating the need for separate endpoints per agent.

**Key Features**:
- List all available agents with their configurations and instructions
- Invoke any agent by agent_id with a generic input
- Browse, delete, and download agent history records
- Agent instructions are exposed to the frontend for display
- Sample inputs with category and tags for better organization
- Optional prompt metadata tracking (category and tags)
- **Response caching**: Automatic caching of responses based on prompt + agent + version

**Agent Registry**:
Nine agents supported:
- `persona_distribution` - Persona Distribution Generator Agent
- `persona_generator` - Persona Generator Agent
- `transcript_parser` - Transcript Parser Agent
- `c2_message_generation` - C2 Message Generator Agent
- `c1_message_generation` - C1 Message Generator Agent
- `simulation_prompt_validator` - Simulation Prompt Validator Agent
- `transcript_based_simulation_parser` - Transcript Based Simulation Parser Agent
- `simulation_prompt` - Simulation Prompt Agent
- `d365_transcript_parser` - D365 Transcript Parser Agent

**Sample Inputs Enhancement**:
Each agent's sample inputs include metadata:
- `label`: Display name for the sample
- `value`: The actual prompt text
- `category` (optional): Categorization like "Valid", "Invalid", "Edge Case"
- `tags` (optional): List of tags (e.g., `["billing", "technical"]`)

**UI Display**:
- Category shown as blue Tag component
- Tags shown as green Tag components
- When user selects sample, category and tags auto-populate in form
- User can manually enter or edit category and tags (optional fields)

**Prompt Metadata Tracking**:
- All invocations can include optional `prompt_category` and `prompt_tags`
- Stored in database with conversation
- Displayed in history table (visible columns by default)
- Users can hide/show columns via column settings (⚙️)
- Included in eval downloads (tags concatenated with comma)

**API Endpoints**:
- GET `/api/v1/agents/list` - List all agents
- GET `/api/v1/agents/{agent_id}` - Get agent details
- POST `/api/v1/agents/{agent_id}/invoke` - Invoke agent
- GET `/api/v1/agents/{agent_id}/browse` - Browse history
- POST `/api/v1/agents/{agent_id}/delete` - Delete records
- POST `/api/v1/agents/{agent_id}/download` - Download records in eval format
- GET `/api/v1/agents/versions` - List all agent+version combinations
- POST `/api/v1/agents/download-multi` - Download multiple agent+version combinations

## Feature 7: Response Caching

**Purpose**: Optimize token usage and improve performance by caching agent responses based on prompt, agent name, and agent version.

**How It Works**:
1. When an agent is invoked, the system first checks if an identical response already exists in the database
2. Cache lookup is based on exact match: `prompt + agent_name + agent_version`
3. **Cache hit**: Returns existing response immediately with `from_cache=true` (saves tokens and time)
4. **Cache miss**: Generates new response normally with `from_cache=false` and saves to database
5. Cache is automatically invalidated when agent instructions change (new version hash)

**Cache Key Components**:
- **Prompt**: Exact text match (case-sensitive, whitespace-sensitive)
- **Agent name**: Ensures different agents cache separately
- **Agent version**: Version hash from instruction set, ensures cache invalidation on instruction changes

**Benefits**:
- **Token savings**: 100% savings for repeated prompts (cache hits use 0 Azure AI tokens)
- **Performance**: 10-30x faster response times for cache hits (~100-200ms vs 1-3 seconds)
- **Cost reduction**: Significant cost savings for evaluation runs with repeated prompts
- **Consistency**: Identical prompts always return the same response (for given agent version)

**UI Indicators**:
- **Generate page**: Badge showing "From Cache" (cyan) or "Newly Generated" (green)
- **Batch processing**: Source column showing cache status for each item
- **History table**: Optional "Source" column (hidden by default)

**Sample Prompts Integration**:
The persona_distribution agent includes 50 sample prompts for evaluation:
- **35 Valid prompts**: Various domains (telecom, banking, healthcare, retail, insurance, etc.)
- **10 Invalid prompts**: Transcript-based scenarios not supported by the agent
- **5 Irrelevant prompts**: Off-topic requests unrelated to persona distribution
- Each sample includes `category` and `tags` for organization
- One-click "Load All Sample Prompts" button in batch processing UI
- First batch run generates all responses (~100k-300k tokens)
- Second batch run retrieves all from cache (0 tokens, 10-30x faster)

## Feature 8: Multi-Agent Download

**Purpose**: Download conversations from multiple agents with version filtering in a single eval-formatted file.

**Workflow**:
1. User navigates to `/agents/download` page
2. Frontend fetches all available agent+version combinations with conversation counts
3. User selects specific agent+version combinations via checkboxes
4. User clicks "Download Selected" button
5. Backend queries Cosmos DB for conversations matching each agent+version pair
6. Backend combines all conversations into flat list with eval format
7. Browser downloads single JSON file with all selected conversations

**Backend Implementation**:
- **GET `/api/v1/agents/versions`**: Lists all unique agent+version combinations with conversation counts
- **POST `/api/v1/agents/download-multi`**: Downloads selected conversations
  - Validates all agent_ids exist in AGENT_REGISTRY
  - For each selection, queries conversations by agent_name and agent_version
  - Transforms to eval format (same as single-agent download)
  - Returns single JSON file with flat list of all conversations
  - Filename: `multi_agent_evals_{timestamp}.json`

**Frontend Implementation**:
- Dedicated page at `/agents/download`
- Table showing agent versions with checkboxes
- Columns: Agent, Scenario Name, Version, Total, Limit
- **Limit column**: Optional InputNumber to specify conversation count per agent+version
- Alert showing selection summary (versions count, total conversations respecting limits)
- Download button (disabled when nothing selected)
- Row selection with checkboxes
- Real-time count of selected versions and total conversations

**Key Features**:
- Version-specific filtering (only conversations matching selected version)
- **Conversation count limits**: Users can specify how many conversations to download per selection
- **Flexible subsets**: Create smaller eval samples (e.g., 10 of Agent A, 5 of Agent B)
- Flat list format (all conversations together)
- Compatible with eval framework
- No hard data size limits (typical: 1,000 conversations ≈ 2-5 MB)

**Download Format**:
```json
{
  "conversations": [
    {
      "Id": "document-uuid",
      "instructions": "Full agent instruction set",
      "prompt": "User's input prompt",
      "agent_prompt": "[SYSTEM]\n{instructions}\n\n[USER]\n{prompt}",
      "agent_response": "Agent's generated response",
      "scenario_name": "AgentName"
    }
  ]
}
```

## Feature 9: Workflows API

**Purpose**: Provides configuration and metadata for workflows that orchestrate multiple agents.

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
- **Batch processing View button**: View detailed results for completed batch items in a modal
  - Shows full input and response with JSON/Plain Text toggle
  - Displays metrics (tokens, time, cache status)
  - Consistent with history table result viewing experience

### History Table Enhancements
- **Column visibility controls**: Settings dropdown (⚙️) to show/hide columns
- **Document ID column**: Hidden by default, shows Cosmos DB document ID (copyable)
- **Conversation ID column**: Hidden by default, shows Azure AI conversation ID (copyable)
- **Fixed column widths**: 250px for timestamp, 250px for input/response to prevent horizontal scroll
- **Tooltips on hover**: View full text for long content
- **Ellipsis for overflow**: Prevents text breaking table layout
- **Consistent across all agent pages**: AgentHistoryTable component used by all agents

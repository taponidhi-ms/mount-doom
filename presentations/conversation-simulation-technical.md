# Conversation Simulation - Technical Documentation

## Table of Contents

- [System Architecture](#system-architecture)
- [Workflow Overview](#workflow-overview)
- [Agent Configurations](#agent-configurations)
  - [C1 Agent (Customer Service Representative)](#c1-agent-customer-service-representative)
  - [C2 Agent (Customer)](#c2-agent-customer)
  - [Persona Generator Agent](#persona-generator-agent)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Implementation Details](#implementation-details)
  - [Core Service Methods](#core-service-methods)
  - [Response Caching](#response-caching)
  - [Token Tracking](#token-tracking)
- [Evaluation Framework](#evaluation-framework)
  - [Configuration Files](#configuration-files)
  - [Running Evaluations](#running-evaluations)
- [Development Guide](#development-guide)
  - [Setup](#setup)
  - [Testing](#testing)
  - [Adding New Features](#adding-new-features)

---

## System Architecture

### Technology Stack

**Backend:**
- Python 3.9+ with FastAPI
- Azure AI Projects SDK (`azure-ai-projects`)
- Azure Cosmos DB for persistence
- DefaultAzureCredential for authentication

**Frontend:**
- Next.js 15 with TypeScript
- Ant Design (antd) UI components
- React 19

### Architecture Pattern

**Clean Architecture with Vertical Slices:**

```
backend/app/
├── core/                    # Configuration (settings, logging)
├── infrastructure/          # Infrastructure services
│   ├── ai/                  # Azure AI client initialization
│   │   └── azure_ai_service.py
│   └── db/                  # Cosmos DB client
│       └── cosmos_db_service.py
├── modules/                 # Feature modules (Vertical Slices)
│   ├── agents/              # Unified agents API
│   │   ├── config.py        # Agent registry
│   │   ├── instructions.py  # Centralized instructions
│   │   ├── agents_service.py
│   │   └── routes.py
│   └── workflows/           # Multi-agent workflows
│       ├── config.py        # Workflow registry
│       └── conversation_simulation/
│           ├── agents.py    # C1/C2 agent factories
│           ├── conversation_simulation_service.py
│           └── routes.py
└── main.py
```

### Key Services

1. **AzureAIService** (Singleton)
   - Initializes AIProjectClient and OpenAI client (lazy loading)
   - Factory for creating agents: `create_agent(name, instructions, model)`
   - Does NOT contain business logic

2. **CosmosDBService** (Singleton)
   - Manages Cosmos DB connections (lazy loading)
   - Generic CRUD operations: `save_document()`, `browse_container()`, `query_cached_response()`
   - Container management: `ensure_container()`
   - Does NOT contain feature-specific document structures

3. **UnifiedAgentsService**
   - Generic agent invocation service
   - Handles response caching
   - Database persistence with timing and metrics
   - Used by C2 agent in conversation simulation

4. **ConversationSimulationService**
   - Orchestrates multi-turn conversations between C1 and C2
   - Manages shared conversation context
   - Tracks per-message and total metrics

---

## Workflow Overview

### High-Level Process

```
User Input (Persona) → Conversation Simulation Workflow
                       ↓
        ┌──────────────────────────────────┐
        │  Shared Conversation Context     │
        │  (Azure AI Conversation API)     │
        └──────────────────────────────────┘
                       ↓
        ┌──────────────┬──────────────────┐
        │   C1 Agent   │    C2 Agent      │
        │  (Service    │   (Customer)     │
        │   Rep)       │                  │
        └──────────────┴──────────────────┘
                       ↓
         Turn-by-Turn Conversation (Max 15 turns)
                       ↓
         Store in Cosmos DB with Full Metrics
```

### Detailed Step-by-Step Flow

1. **Initialization**
   - User provides customer persona (Intent, Sentiment, Subject)
   - Frontend sends POST request to `/api/v1/conversation-simulation/simulate`
   - Backend creates empty conversation using Azure AI Conversations API
   - `max_turns` hardcoded to 15 in backend

2. **Turn Loop** (Repeat until completion or max_turns):

   **C1 Turn:**
   - Check if conversation is empty (first turn)
   - If empty, C1 greets customer: "Hi there, how can I help you today?"
   - If not empty, C1 responds to customer's last message
   - Extract response text and token usage
   - Check for termination phrases: "end this call now" or "transfer"
   - Add C1 message to conversation history

   **C2 Turn:**
   - Construct prompt with:
     - Conversation properties (Intent, Sentiment, Subject)
     - Full message history so far
   - Invoke C2 agent via UnifiedAgentsService with `persist=True`
   - C2 response saved to `c2_message_generation` container with metrics
   - Extract response text and token usage from C2
   - Add C2 message to conversation history

   **Completion Check:**
   - If C1 said termination phrase → end loop
   - If reached max_turns (15) → end loop
   - Otherwise, continue to next turn

3. **Finalization**
   - Calculate total tokens (sum of all C1 and C2 tokens)
   - Calculate total time taken
   - Create complete conversation document
   - Save to `conversation_simulation` container with:
     - Full message history
     - Per-message token counts
     - Total metrics
     - Customer persona details

---

## Agent Configurations

### C1 Agent (Customer Service Representative)

**Agent Name:** `C1Agent`

**Model:** `gpt-4` (configured in settings)

**Full Instruction Set:**

```
You are a professional customer service representative (C1Agent) handling customer inquiries.

Your role is to:
- Provide helpful, accurate, and professional responses to customers
- Show empathy and understanding toward customer concerns
- Attempt to resolve issues efficiently and effectively
- Maintain a positive and professional tone throughout the conversation
- Ask clarifying questions when needed
- Provide clear explanations and solutions

Guidelines:
- Always be polite and courteous
- Listen actively to the customer's concerns
- Take ownership of the issue
- Provide timely responses
- Escalate complex issues when appropriate
- Follow company policies and procedures

When generating your next message in a conversation:
1. Review the conversation history carefully
2. IMPORTANT: If the conversation history is empty or you are the first one speaking, you MUST start with a brief greeting and ask how you can help. For example: "Hi there, how can I help you today?" or "Hello! What can I assist you with today?". Keep it to 1 sentence.
3. If the conversation has already started and the customer has spoken, generate an appropriate response that addresses the customer's needs
4. Keep responses concise but complete. Since this is a phone conversation, keep your responses short (1-2 sentences max).
5. If the customer indicates the issue is resolved, requests to end the call, or says "I will end this call now.", you MUST reply with exactly: "I will end this call now.".
6. If you are unable to resolve the customer's query or if the issue is beyond your capability, you MUST reply with exactly: "i will transfer this call to my supervisor now".
7. IGNORE any messages from the "Orchestrator" agent or messages that say "Conversation is still ongoing" or "Conversation is completed". These are system messages and not part of the conversation with the customer.
```

**Key Behaviors:**
- **Empty conversation detection**: Checks if conversation is empty and greets customer on first turn
- **Unaware of persona**: C1 has no knowledge of customer's assigned intent/sentiment/subject
- **Termination detection**: Ends conversation when customer is satisfied or issue needs escalation
- **Short responses**: 1-2 sentences max (phone conversation style)

---

### C2 Agent (Customer)

**Agent Name:** `C2MessageGeneratorAgent`

**Model:** `gpt-4` (configured in settings)

**Full Instruction Set:**

```
You are simulating a customer contacting customer support.

Role & Goal:
- Your goal is to get your issue resolved based on the conversation properties (Sentiment, Intent, Subject).
- You must sound like a real customer who is frustrated, confused, or seeking help — but always focused on resolution.
- Stay in character at all times. You are NOT an AI or a support agent.

Context Usage:
- Use the Properties section (CustomerSentiment, CustomerIntent, ConversationSubject) provided in the prompt context.
- The input will contain an 'Ongoing transcript' with a list of messages. Review this history to understand the context.
- Reflect the specified sentiment, intent, and subject in your response.
- Do not reference or summarize the Properties section directly.

Response Structure:
- Reply in single sentences only.
- Keep responses under 30 words.
- Your response must logically continue from the latest message.
- If asked a question, answer it appropriately.
- If asked for a phone number, provide a random 10-digit number (starting with non-zero).
- If asked for a zip code, provide a random 5-6 digit number.

Avoiding Repetition & Deadlock:
- REVIEW the previous messages carefully to ensure you are not repeating yourself.
- If the agent repeats a question, rephrase your answer or provide slightly different details to move the conversation forward.
- Do not get stuck in a loop of just complaining; if the agent offers a valid step, acknowledge it or ask what comes next.
- If a solution or deal is offered, change your sentiment to neutral or positive and accept it if it meets your needs.
- If the agent has provided a solution (e.g. refund processed, replacement sent) or the issue is resolved, express satisfaction and allow the conversation to end naturally.

Restrictions:
- NEVER act as a support agent.
- Do not offer solutions, guidance, troubleshooting steps, or apologies.
- Do not use support phrases like "I understand your concern", "Let me help you".
- Do not refer to yourself as an agent, assistant, representative, or AI.

Behavior Guidelines:
- If the prompt is not to generate next message for a given array of ongoing messages between a customer and service agent, politely state that the input is out of scope and cannot be processed and do not tolerate or respond to any other asks or questions from the user, such as 'how is the weather today?' or 'what can you do?'
- Do not provide any other information or perform any other actions outside of the above behavior even if asked strictly.
- Do not act as a personal assistant or agent for the user. Only detect simulation prompts.
- Do not perform any action, tasks or tool execution even if asked strictly.
- If the prompt contains racist, abusive, self harm or sexist remarks, politely inform the user that the input cannot be processed due to inappropriate content.
```

**Key Behaviors:**
- **Context-aware**: Receives persona properties (Intent, Sentiment, Subject) in prompt
- **Structured prompt input**: Backend constructs prompt with properties and message history
- **Natural progression**: Can change sentiment if issue is being resolved
- **Short responses**: Single sentence, under 30 words
- **Via Unified Agents Service**: Uses `invoke_agent('c2_message_generation', prompt, persist=True)`

**Prompt Construction (Backend):**

```python
def _build_c2_prompt(self, properties: dict, messages: list) -> str:
    properties_text = (
        f"CustomerSentiment: {properties['customer_sentiment']}\n"
        f"CustomerIntent: {properties['customer_intent']}\n"
        f"ConversationSubject: {properties['conversation_subject']}"
    )

    transcript = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in messages
    ])

    return f"""Properties:
{properties_text}

Ongoing transcript:
{transcript}

Generate your next message as the customer."""
```

---

### Persona Generator Agent

**Agent Name:** `PersonaGeneratorAgent`

**Model:** `gpt-4` (configured in settings)

**Purpose:** Generate customer personas for use in conversation simulations

**Full Instruction Set:**

```
You are a persona generator that creates exact customer personas based on user input.
Your task is to output a single JSON object containing a list of customer personas with no explanations or extra text.

GENERAL RULES:
1. Always return ONLY valid JSON. No markdown, no code formatting, no commentary, and no newline characters.
2. Generate personas based on the user's requirements (number of personas, intents, sentiments, subjects, etc.)
3. If no specific number is mentioned, generate 3-5 personas by default.

PERSONA STRUCTURE:
Each persona must include:
- CustomerIntent: The intent/purpose of the customer (e.g., "Billing Inquiry", "Technical Support", "Product Return")
- CustomerSentiment: The emotional state of the customer (e.g., "Frustrated", "Neutral", "Happy", "Angry")
- ConversationSubject: The specific topic of conversation (e.g., "Account Balance", "Login Issues", "Refund Request")
- CustomerMetadata: A JSON object with additional customer-related data (e.g., {"account_type": "premium", "tenure_months": 24, "previous_issues": 2})

METADATA GUIDELINES:
- Include relevant customer attributes that add context
- Use key-value pairs appropriate to the scenario
- Examples: account_type, tenure_months, previous_issues, subscription_tier, location, device_type, etc.
- Generate realistic metadata that aligns with the persona's intent and sentiment

OUTPUT FORMAT:
Return ONLY this JSON structure:
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

**Output Example:**

```json
{
  "CustomerPersonas": [
    {
      "CustomerIntent": "Technical Support",
      "CustomerSentiment": "Frustrated",
      "ConversationSubject": "Cannot log in to my account",
      "CustomerMetadata": {
        "account_type": "business",
        "tenure_months": 18,
        "previous_issues": 3
      }
    }
  ]
}
```

---

## API Endpoints

### Conversation Simulation

**POST** `/api/v1/conversation-simulation/simulate`

Simulate a multi-turn conversation between C1 and C2 agents.

**Request Body:**
```json
{
  "customer_intent": "Billing Inquiry",
  "customer_sentiment": "Frustrated",
  "conversation_subject": "Incorrect charge on bill"
}
```

**Response:**
```json
{
  "conversation_id": "conv-uuid-here",
  "messages": [
    {
      "role": "C1",
      "content": "Hi there, how can I help you today?",
      "tokens_used": 45
    },
    {
      "role": "C2",
      "content": "I was charged twice for my monthly subscription.",
      "tokens_used": 38
    }
  ],
  "total_turns": 8,
  "total_tokens_used": 856,
  "time_taken_ms": 12450,
  "start_time": "2026-02-11T10:30:00.000Z",
  "end_time": "2026-02-11T10:30:12.450Z",
  "customer_intent": "Billing Inquiry",
  "customer_sentiment": "Frustrated",
  "conversation_subject": "Incorrect charge on bill"
}
```

**GET** `/api/v1/conversation-simulation/browse`

Browse past simulations with pagination.

**Query Parameters:**
- `page` (default: 1)
- `page_size` (default: 10, max: 100)
- `order_by` (default: "timestamp")
- `order_direction` (default: "DESC")

**Response:**
```json
{
  "items": [...],
  "total_count": 156,
  "page": 1,
  "page_size": 10,
  "total_pages": 16,
  "has_next": true,
  "has_previous": false
}
```

### Unified Agents API (C2 Message Generation)

**POST** `/api/v1/agents/c2_message_generation/invoke`

Invoke the C2 agent directly (standalone, not in simulation context).

**Request Body:**
```json
{
  "input_text": "Your prompt here with context",
  "prompt_category": "Valid",
  "prompt_tags": ["billing", "technical"]
}
```

**Response:**
```json
{
  "response_text": "Generated customer message",
  "tokens_used": 42,
  "time_taken_ms": 1250,
  "conversation_id": "conv-uuid",
  "start_time": "2026-02-11T10:30:00.000Z",
  "end_time": "2026-02-11T10:30:01.250Z",
  "agent_name": "C2MessageGeneratorAgent",
  "agent_version": "v12ab34cd",
  "from_cache": false
}
```

---

## Database Schema

### Cosmos DB Containers

1. **`conversation_simulation`** - Full multi-turn conversations
2. **`c2_message_generation`** - Individual C2 message generations

### Document Structure: conversation_simulation

```json
{
  "id": "conv-uuid-from-azure-ai",
  "conversation_id": "conv-uuid-from-azure-ai",
  "messages": [
    {
      "role": "C1",
      "content": "Hi there, how can I help you today?",
      "tokens_used": 45
    },
    {
      "role": "C2",
      "content": "I need help with my billing.",
      "tokens_used": 38
    }
  ],
  "total_turns": 8,
  "total_tokens_used": 856,
  "time_taken_ms": 12450,
  "timestamp": "2026-02-11T10:30:00.000Z",
  "start_time": "2026-02-11T10:30:00.000Z",
  "end_time": "2026-02-11T10:30:12.450Z",
  "customer_intent": "Billing Inquiry",
  "customer_sentiment": "Frustrated",
  "conversation_subject": "Incorrect charge",
  "c1_agent_name": "C1Agent",
  "c1_agent_version": "v12ab34cd",
  "c1_agent_instructions": "Full C1 instruction text...",
  "c1_agent_model": "gpt-4",
  "c2_agent_name": "C2MessageGeneratorAgent",
  "c2_agent_version": "v56ef78gh",
  "c2_agent_instructions": "Full C2 instruction text...",
  "c2_agent_model": "gpt-4"
}
```

### Document Structure: c2_message_generation

```json
{
  "id": "conv-uuid-from-azure-ai",
  "conversation_id": "conv-uuid-from-azure-ai",
  "prompt": "Full constructed prompt with properties and transcript",
  "response": "Generated customer message",
  "tokens_used": 42,
  "time_taken_ms": 1250,
  "timestamp": "2026-02-11T10:30:01.000Z",
  "start_time": "2026-02-11T10:30:00.000Z",
  "end_time": "2026-02-11T10:30:01.250Z",
  "agent_name": "C2MessageGeneratorAgent",
  "agent_version": "v56ef78gh",
  "agent_instructions": "Full C2 instruction text...",
  "agent_model": "gpt-4",
  "prompt_category": "Valid",
  "prompt_tags": ["billing"]
}
```

**Note:** `from_cache` is NOT stored in database - it's a runtime property of API responses only.

---

## Implementation Details

### Core Service Methods

#### ConversationSimulationService.simulate()

Main orchestration method for multi-turn conversations.

**Key Steps:**

```python
async def simulate(
    self,
    customer_intent: str,
    customer_sentiment: str,
    conversation_subject: str,
    max_turns: int = 15
) -> ConversationSimulationResult:
    # 1. Create agents
    c1_agent = self._create_c1_agent()
    c2_agent_name = "C2MessageGeneratorAgent"

    # 2. Create empty conversation
    conversation = openai_client.conversations.create(items=[])
    conversation_id = conversation.id

    # 3. Initialize tracking
    messages = []
    total_tokens = 0
    start_time = datetime.now(timezone.utc)

    # 4. Turn loop
    for turn in range(max_turns):
        # C1 Turn
        is_first_turn = len(messages) == 0
        c1_result = await self._c1_turn(
            conversation_id,
            c1_agent,
            is_first_turn
        )
        messages.append({
            "role": "C1",
            "content": c1_result["message"],
            "tokens_used": c1_result["tokens"]
        })
        total_tokens += c1_result["tokens"]

        # Check C1 termination
        if self._should_terminate(c1_result["message"]):
            break

        # C2 Turn (via unified agents service)
        properties = {
            "customer_intent": customer_intent,
            "customer_sentiment": customer_sentiment,
            "conversation_subject": conversation_subject
        }
        c2_result = await self._c2_turn(
            conversation_id,
            properties,
            messages
        )
        messages.append({
            "role": "C2",
            "content": c2_result["message"],
            "tokens_used": c2_result["tokens"]
        })
        total_tokens += c2_result["tokens"]

    # 5. Finalize and save
    end_time = datetime.now(timezone.utc)
    time_taken_ms = (end_time - start_time).total_seconds() * 1000

    document = {
        "id": conversation_id,
        "conversation_id": conversation_id,
        "messages": messages,
        "total_turns": len(messages) // 2,
        "total_tokens_used": total_tokens,
        "time_taken_ms": round(time_taken_ms, 2),
        # ... customer properties, agent details
    }

    await cosmos_db_service.save_document(
        container_name="conversation_simulation",
        document=document
    )

    return ConversationSimulationResult(**document)
```

#### _c1_turn()

Handles C1 agent's turn in the conversation.

```python
async def _c1_turn(
    self,
    conversation_id: str,
    agent: Agent,
    is_first_turn: bool
) -> dict:
    # Create C1 response
    response = openai_client.responses.create(
        conversation=conversation_id,
        extra_body={
            "agent": {
                "name": agent.agent_version_object.name,
                "type": "agent_reference"
            }
        },
        input=""
    )

    # Extract message and tokens
    message = self._extract_response_text(response)
    tokens = self._extract_tokens(response)

    return {
        "message": message,
        "tokens": tokens
    }
```

#### _c2_turn()

Handles C2 agent's turn via UnifiedAgentsService.

```python
async def _c2_turn(
    self,
    conversation_id: str,
    properties: dict,
    messages: list
) -> dict:
    # Build C2 prompt
    prompt = self._build_c2_prompt(properties, messages)

    # Invoke C2 via unified agents service
    result = await unified_agents_service.invoke_agent(
        agent_id="c2_message_generation",
        input_text=prompt,
        persist=True  # Save to c2_message_generation container
    )

    # Add C2 message to conversation
    openai_client.conversations.items.create(
        conversation_id=conversation_id,
        items=[{
            "type": "message",
            "role": "user",
            "content": result.response_text
        }]
    )

    return {
        "message": result.response_text,
        "tokens": result.tokens_used or 0
    }
```

---

### Response Caching

**Purpose:** Optimize token usage by caching agent responses based on exact prompt match.

**Cache Key:** `prompt + agent_name + agent_version`

**Flow:**

```python
async def invoke_agent(
    self,
    agent_id: str,
    input_text: str,
    persist: bool = True
) -> AgentInvokeResult:
    # 1. Get agent config
    agent_config = get_agent_config(agent_id)

    # 2. Create agent to get current version
    agent = azure_ai_service.create_agent(
        agent_name=agent_config.agent_name,
        instructions=agent_config.instructions
    )
    current_version = agent.agent_version_object.version

    # 3. Check cache
    try:
        cached_doc = await cosmos_db_service.query_cached_response(
            container_name=agent_config.container_name,
            prompt=input_text,
            agent_name=agent_config.agent_name,
            agent_version=current_version
        )

        if cached_doc:
            logger.info("Cache hit", agent=agent_config.agent_name)
            return AgentInvokeResult(
                response_text=cached_doc.get("response"),
                tokens_used=cached_doc.get("tokens_used"),
                time_taken_ms=cached_doc.get("time_taken_ms"),
                conversation_id=cached_doc.get("conversation_id"),
                start_time=cached_doc.get("start_time"),
                end_time=cached_doc.get("end_time"),
                agent_name=agent_config.agent_name,
                agent_version=current_version,
                from_cache=True  # ✅ Cache hit
            )
    except Exception as e:
        logger.warning("Cache query failed", error=str(e))

    # 4. Cache miss - generate new response
    logger.info("Cache miss, generating new response")

    # ... normal generation flow ...

    return AgentInvokeResult(
        response_text=response_text,
        tokens_used=tokens_used,
        # ... other fields
        from_cache=False  # ✅ Newly generated
    )
```

**Cache Query (CosmosDBService):**

```python
async def query_cached_response(
    self,
    container_name: str,
    prompt: str,
    agent_name: str,
    agent_version: str
) -> Optional[Dict[str, Any]]:
    container = self.database.get_container_client(container_name)

    query = """
        SELECT TOP 1 * FROM c
        WHERE c.prompt = @prompt
        AND c.agent_name = @agent_name
        AND c.agent_version = @agent_version
        ORDER BY c.timestamp DESC
    """

    parameters = [
        {"name": "@prompt", "value": prompt},
        {"name": "@agent_name", "value": agent_name},
        {"name": "@agent_version", "value": agent_version}
    ]

    items = list(container.query_items(
        query=query,
        parameters=parameters,
        enable_cross_partition_query=True
    ))

    return items[0] if items else None
```

**Benefits:**
- **100% token savings** on cache hits (0 Azure AI API calls)
- **10-30x faster** response times (~100-200ms vs 1-3s)
- **Automatic invalidation** when agent instructions change (new version)
- **Evaluation-friendly** - re-run test suites without token cost

---

### Token Tracking

**Per-Message Tracking (Conversation Simulation):**

```python
# Extract tokens from Azure AI response
def _extract_tokens(self, response) -> int:
    try:
        if hasattr(response, 'usage') and response.usage:
            return response.usage.total_tokens
        return 0
    except Exception as e:
        logger.warning("Failed to extract tokens", error=str(e))
        return 0
```

**Total Token Tracking:**

```python
# Sum all C1 and C2 tokens
total_tokens = sum([
    msg["tokens_used"]
    for msg in messages
])
```

**Database Storage:**
- Per-message: `messages[].tokens_used`
- Per-conversation: `total_tokens_used`
- Per-C2-invocation: `tokens_used` in `c2_message_generation` container

---

## Evaluation Framework

### Configuration Files

**Location:** `cxa_evals/`

**Key Files:**
- `default_config.json` - Default metrics evaluation
- `groundedness_config.json` - Groundedness evaluation
- `custom_multiturn_config.json` - Custom criteria for conversation simulation

### Custom Multi-Turn Configuration

**File:** `cxa_evals/custom_multiturn_config.json`

**Eval Type:** `multi_turn`

**Input Fields:**
```json
{
  "variable_columns": [
    "customer_intent",
    "customer_sentiment",
    "conversation_subject"
  ]
}
```

**Custom Rules:**

```json
{
  "scenario_name": "ConversationSimulation",
  "rules": [
    {
      "rule_name": "persona_adherence",
      "rule_category": "Conversationality",
      "rule_description": "The customer should maintain consistency with their assigned persona throughout the conversation. Customer intent: {{customer_intent}}, sentiment: {{customer_sentiment}}, subject: {{conversation_subject}}. The customer's messages should align with these characteristics. As the conversation progresses, it is fine for the customer to exhibit changes in sentiment that reflect a natural response to the interaction, as long as these changes remain believable and consistent with the overall persona."
    },
    {
      "rule_name": "goal_pursuit",
      "rule_category": "Usefulness",
      "rule_description": "The customer should actively work towards achieving their goal. The customer's messages should reflect their intent to accomplish this goal. Customer intent: {{customer_intent}}, sentiment: {{customer_sentiment}}, subject: {{conversation_subject}}. The customer should not deviate from this goal or introduce unrelated objectives."
    }
  ]
}
```

**Variable Substitution:**
- `{{customer_intent}}` - Replaced with actual value from input
- `{{customer_sentiment}}` - Replaced with actual value from input
- `{{conversation_subject}}` - Replaced with actual value from input

### Running Evaluations

**Prerequisites:**
- Download `Microsoft.CXA.AIEvals.Cli.exe` (not committed to repo)
- Place in `cxa_evals/` directory

**Command:**

```bash
cd cxa_evals

# Default metrics
./Microsoft.CXA.AIEvals.Cli.exe run --config default_config.json

# Groundedness
./Microsoft.CXA.AIEvals.Cli.exe run --config groundedness_config.json

# Custom multi-turn (conversation simulation)
./Microsoft.CXA.AIEvals.Cli.exe run --config custom_multiturn_config.json
```

**Input File Format:**

For conversation simulation (`input/multiturn_c2_small.json`):

```json
{
  "conversations": [
    {
      "customer_intent": "Billing Inquiry",
      "customer_sentiment": "Frustrated",
      "conversation_subject": "Incorrect charge on bill"
    }
  ]
}
```

**Output:**
- Results stored in `cxa_evals/output/` (gitignored)
- Includes per-rule scores and overall metrics

---

## Development Guide

### Setup

**Backend:**

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (Windows Git Bash)
source .venv/Scripts/activate

# Install dependencies
.venv/Scripts/python.exe -m pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with Azure credentials

# Run server
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local (set NEXT_PUBLIC_API_URL=http://localhost:8000)

# Run dev server
npm run dev
```

### Testing

**Test Agent Instructions:**

```bash
cd backend
.venv/Scripts/python.exe -c "from app.modules.agents.instructions import C1_AGENT_INSTRUCTIONS; print(C1_AGENT_INSTRUCTIONS)"
```

**Test Database Connection:**

```bash
.venv/Scripts/python.exe -c "from app.infrastructure.db.cosmos_db_service import cosmos_db_service; import asyncio; asyncio.run(cosmos_db_service.ensure_container('test_container'))"
```

**Manual API Testing:**

```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/conversation-simulation/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "customer_intent": "Billing Inquiry",
    "customer_sentiment": "Frustrated",
    "conversation_subject": "Incorrect charge"
  }'
```

### Adding New Features

**Adding a New Agent:**

1. Add instructions to `backend/app/modules/agents/instructions.py`:
   ```python
   NEW_AGENT_INSTRUCTIONS = """Your instructions here..."""
   ```

2. Create config in `backend/app/modules/agents/configs/new_agent_config.py`:
   ```python
   from ..config import AgentConfig
   from ..instructions import NEW_AGENT_INSTRUCTIONS

   AGENT_CONFIG = AgentConfig(
       agent_id="new_agent",
       agent_name="NewAgentName",
       display_name="New Agent",
       description="Description",
       instructions=NEW_AGENT_INSTRUCTIONS,
       container_name="single_turn_conversations",
       scenario_name="NewAgent",
       input_field="prompt",
       input_label="Prompt",
       input_placeholder="Enter your prompt...",
       sample_inputs=[...]
   )
   ```

3. Agent automatically appears in API (`/api/v1/agents/list`)

**Modifying Conversation Simulation Workflow:**

1. Update agent instructions in `instructions.py` if needed
2. Modify orchestration logic in `ConversationSimulationService.simulate()`
3. Update termination conditions in `_should_terminate()`
4. Adjust `max_turns` if needed (currently hardcoded to 15)

**Adding New Eval Criteria:**

1. Create new config file in `cxa_evals/` (e.g., `custom_new_criteria.json`)
2. Define custom rules with `rule_name`, `rule_category`, `rule_description`
3. Use variable substitution with `{{variable_name}}` syntax
4. Run evals with new config

---

## Key Technical Decisions

### Why Shared Conversation?

- **Context Continuity**: C1 and C2 need full conversation history
- **Azure AI Pattern**: Conversations maintain state across multiple agent invocations
- **Simpler Code**: Single conversation ID tracked throughout workflow

### Why Two Database Containers?

1. **`conversation_simulation`**: Full multi-turn conversations (complete stories)
2. **`c2_message_generation`**: Individual C2 invocations (granular tracking)

**Benefits:**
- Track C2 performance independently
- Enable C2-specific evals
- Support standalone C2 message generation API
- Maintain conversation-level metrics separately

### Why Response Caching?

- **Token Optimization**: Eval runs with repeated prompts save 100% tokens on cache hits
- **Performance**: 10-30x faster for cache hits
- **Cost Reduction**: Significant savings for large-scale testing
- **Automatic Invalidation**: Cache invalidates when instructions change (via version hash)

### Why UnifiedAgentsService for C2?

- **Code Reuse**: Same service for standalone C2 and conversation C2
- **Consistent Metrics**: Both paths track tokens and timing identically
- **Automatic Persistence**: C2 messages saved to database when `persist=True`
- **Cache Support**: C2 benefits from response caching in both contexts

---

## Appendix: Environment Variables

**Backend (.env):**

```env
# Azure AI Projects
AZURE_AI_PROJECT_CONNECTION_STRING=your_connection_string

# Cosmos DB
COSMOS_DB_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOS_DB_DATABASE_NAME=mount_doom_db
COSMOS_DB_USE_EMULATOR=false  # true for local emulator

# Model Configuration
default_model_deployment=gpt-4

# Logging
api_debug=true  # Enable debug logging
```

**Frontend (.env.local):**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Local Cosmos DB Emulator:**

```env
COSMOS_DB_ENDPOINT=https://localhost:8081
COSMOS_DB_USE_EMULATOR=true
COSMOS_DB_KEY=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==
```

---

## Support and Resources

**Documentation:**
- [Azure AI Projects SDK](https://learn.microsoft.com/en-us/python/api/azure-ai-projects/)
- [Azure AI Code Samples](https://github.com/Azure/azure-sdk-for-python/tree/azure-ai-projects_2.0.0b3/sdk/ai/azure-ai-projects/samples/agents)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)

**Codebase Documentation:**
- `CLAUDE.md` - Project overview and policies
- `.claude/rules/` - Detailed architecture and conventions
- `backend/README.md` - Backend setup and API docs
- `frontend/README.md` - Frontend setup and component docs

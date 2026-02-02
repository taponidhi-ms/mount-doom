---
paths:
  - "backend/**/*.py"
---

# API Design Patterns

## Request/Response Format

- All requests: JSON body
- All responses: JSON with standard structure
- Include metadata (tokens, timing) in all responses
- Use Pydantic models for validation

## Endpoint Structure

- RESTful design
- Versioned API (`/api/v1/`)
- Grouped by use case
- GET for retrieval, POST for actions

## Standard Endpoints Per Use Case

Each use case follows this pattern:
- POST `/{use-case}/generate|validate|simulate` - Create new result
- GET `/{use-case}/browse` - List past results with pagination

## Browse Endpoint Pattern

All browse endpoints support:
- `page` (default: 1) - Page number
- `page_size` (default: 10, max: 100) - Items per page
- `order_by` (default: "timestamp") - Field to sort by
- `order_direction` (default: "DESC") - Sort direction (ASC|DESC)

Response includes:
- `items` - Array of results
- `total_count` - Total number of items
- `page` - Current page number
- `page_size` - Items per page
- `total_pages` - Total number of pages
- `has_next` - Boolean indicating if next page exists
- `has_previous` - Boolean indicating if previous page exists

**IMPORTANT - Field Name Mapping**:
Browse endpoints return raw Cosmos DB documents, NOT formatted API response schemas.
Frontend history tables must use Cosmos DB field names:
- Use `timestamp` (NOT `start_time`)
- Use `response` (NOT `response_text`)
- Use `prompt` (same in both)
- Use `tokens_used` (same in both)
- Use `time_taken_ms` (same in both)

## Response Caching

**Purpose**: Optimize token usage and improve performance by caching agent responses.

### How It Works

1. **Cache Check**: Before generating a response, the system queries the database for an existing response matching:
   - Exact prompt text (case-sensitive, whitespace-sensitive)
   - Agent name
   - Agent version (instruction hash)

2. **Cache Hit**: If a match is found, return the existing response immediately:
   - Response text from cached document
   - Original tokens_used and timing metrics
   - `from_cache=true` in API response
   - **No Azure AI API call** = 0 tokens used

3. **Cache Miss**: If no match found, generate normally:
   - Create conversation and get agent response
   - Save to database with all metrics
   - `from_cache=false` in API response

4. **Automatic Invalidation**: Cache is automatically invalidated when:
   - Agent instructions change (new version hash generated)
   - Different agent name used
   - Prompt text is different

### Implementation Details

**Backend Method** (`CosmosDBService.query_cached_response()`):
```python
async def query_cached_response(
    container_name: str,
    prompt: str,
    agent_name: str,
    agent_version: str
) -> Optional[Dict[str, Any]]:
    # Query Cosmos DB for exact match
    # Returns most recent matching document or None
```

**Service Layer** (`UnifiedAgentsService.invoke_agent()`):
- Creates agent to get current version
- Queries cache before generation
- Returns cached result if found (with `from_cache=True`)
- Generates new response if not found (with `from_cache=False`)
- Graceful error handling (cache failures don't block generation)

**API Response**:
- `from_cache` field in `AgentInvokeResponse` indicates source
- Frontend displays cache indicator badges
- `from_cache` is a **runtime property only** (not stored in database)

### Implementation Pattern

```python
async def invoke_agent(self, agent_id: str, input_text: str, ...):
    # 1. Create agent to get version
    agent = azure_ai_service.create_agent(name, instructions)
    current_version = agent.agent_version_object.version

    # 2. Check cache
    cached_doc = await cosmos_db_service.query_cached_response(
        container_name=container,
        prompt=input_text,
        agent_name=agent_name,
        agent_version=current_version
    )

    # 3. Return cached response if found
    if cached_doc:
        return AgentInvokeResult(
            response_text=cached_doc.get("response"),
            tokens_used=cached_doc.get("tokens_used"),
            # ... reconstruct from cached_doc
            from_cache=True  # ✅ Cache hit
        )

    # 4. Generate new response on cache miss
    # ... normal generation flow ...

    # 5. Return with from_cache=False
    return AgentInvokeResult(
        response_text=response_text,
        # ... other fields
        from_cache=False  # ✅ Newly generated
    )
```

### Cache Key Strategy

- **Exact match** on: `prompt + agent_name + agent_version`
- Case-sensitive and whitespace-sensitive matching
- Agent version ensures cache invalidation when instructions change
- Different agents cache separately (same prompt, different agent = different cache entries)

### Best Practices

1. **Check cache before generation**: Avoids unnecessary Azure AI API calls
2. **Graceful error handling**: Cache query errors should not block generation
3. **Log cache hits/misses**: Use `logger.info()` for cache hits, `logger.debug()` for details
4. **Don't persist `from_cache`**: It's a runtime property, not a document property
5. **Return cached metrics**: Include original tokens_used and time_taken_ms from cached document

### Error Handling

```python
try:
    cached_doc = await cosmos_db_service.query_cached_response(...)
except Exception as e:
    logger.warning("Cache query failed, proceeding with generation", error=str(e))
    cached_doc = None  # Graceful fallback
```

### Database Query

```python
async def query_cached_response(...) -> Optional[Dict[str, Any]]:
    query = """
        SELECT TOP 1 * FROM c
        WHERE c.prompt = @prompt
        AND c.agent_name = @agent_name
        AND c.agent_version = @agent_version
        ORDER BY c.timestamp DESC
    """
    # Returns most recent match or None
```

### Benefits

- **Token Savings**: 100% savings for repeated prompts (0 tokens on cache hits)
- **Performance**: 10-30x faster (~100-200ms vs 1-3s for generation)
- **Cost Reduction**: Significant savings for evaluation runs
- **Consistency**: Same prompt always returns same response (for given agent version)
- **Evaluation-Friendly**: Re-run test suites without token cost

# Cosmos DB Refactoring - Architecture Comparison

## Before Refactoring

```
┌─────────────────────────────────────────────────────────────────┐
│                           ROUTES                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Persona    │  │   General    │  │   Prompt     │  ...     │
│  │  Generation  │  │    Prompt    │  │  Validator   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FEATURE SERVICES                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Persona    │  │   General    │  │   Prompt     │  ...     │
│  │  Generation  │  │    Prompt    │  │  Validator   │         │
│  │   Service    │  │   Service    │  │   Service    │         │
│  │              │  │              │  │              │         │
│  │ • generate   │  │ • generate   │  │ • validate   │         │
│  │   persona    │  │   response   │  │   prompt     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────┬──────────────────┬──────────────────┬─────────────────┘
          │                  │                  │
          │ All call         │                  │
          └──────────────────┼──────────────────┘
                             ▼
          ┌────────────────────────────────────────────┐
          │         CosmosDBService                    │
          │  ❌ MIXED RESPONSIBILITIES                 │
          │                                            │
          │  Infrastructure:                           │
          │  • _initialize_client()                    │
          │  • ensure_container()                      │
          │  • browse_container()                      │
          │                                            │
          │  Business Logic: ⚠️ SHOULD NOT BE HERE    │
          │  • save_persona_generation()               │
          │  • save_general_prompt()                   │
          │  • save_prompt_validator()                 │
          │  • save_conversation_simulation()          │
          │                                            │
          │  Document Structures: ⚠️ SHOULD NOT BE HERE│
          │  • Persona document format                 │
          │  • General prompt document format          │
          │  • Validator document format               │
          │  • Conversation document format            │
          └────────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   Cosmos DB    │
                    └────────────────┘
```

**Problems:**
- ❌ CosmosDBService has feature-specific methods
- ❌ Document structures defined in infrastructure layer
- ❌ Violates Single Responsibility Principle
- ❌ Feature services don't own their persistence logic
- ❌ Hard to maintain and test

---

## After Refactoring

```
┌─────────────────────────────────────────────────────────────────┐
│                           ROUTES                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Persona    │  │   General    │  │   Prompt     │  ...     │
│  │  Generation  │  │    Prompt    │  │  Validator   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FEATURE SERVICES                           │
│  ✅ OWN COMPLETE BUSINESS LOGIC                                │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Persona    │  │   General    │  │   Prompt     │  ...     │
│  │  Generation  │  │    Prompt    │  │  Validator   │         │
│  │   Service    │  │   Service    │  │   Service    │         │
│  │              │  │              │  │              │         │
│  │ • generate   │  │ • generate   │  │ • validate   │         │
│  │   persona    │  │   response   │  │   prompt     │         │
│  │              │  │              │  │              │         │
│  │ ✅ NEW:      │  │ ✅ NEW:      │  │ ✅ NEW:      │         │
│  │ • save_to_   │  │ • save_to_   │  │ • save_to_   │         │
│  │   database() │  │   database() │  │   database() │         │
│  │              │  │              │  │              │         │
│  │ • Document   │  │ • Document   │  │ • Document   │         │
│  │   structure  │  │   structure  │  │   structure  │         │
│  │ • ID gen     │  │ • ID gen     │  │ • ID gen     │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │ All call         │                  │
          └──────────────────┼──────────────────┘
                             ▼
          ┌────────────────────────────────────────────┐
          │         CosmosDBService                    │
          │  ✅ INFRASTRUCTURE ONLY                    │
          │                                            │
          │  Generic Operations:                       │
          │  • _initialize_client()                    │
          │  • ensure_container()                      │
          │  • save_document() ⭐ NEW GENERIC METHOD   │
          │  • browse_container()                      │
          │                                            │
          │  Constants:                                │
          │  • PERSONA_GENERATION_CONTAINER            │
          │  • GENERAL_PROMPT_CONTAINER                │
          │  • PROMPT_VALIDATOR_CONTAINER              │
          │  • CONVERSATION_SIMULATION_CONTAINER       │
          │                                            │
          │  ✅ NO business logic                      │
          │  ✅ NO document structures                 │
          │  ✅ NO feature-specific methods            │
          └────────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   Cosmos DB    │
                    └────────────────┘
```

**Benefits:**
- ✅ CosmosDBService is infrastructure-only
- ✅ Each service owns its persistence logic
- ✅ Document structures where they belong
- ✅ Single Responsibility Principle
- ✅ Easy to maintain and test
- ✅ Scalable for new features

---

## Key Changes

### CosmosDBService
```diff
- async def save_persona_generation(prompt, response, ...)
- async def save_general_prompt(model_id, prompt, ...)
- async def save_prompt_validator(prompt, response, ...)
- async def save_conversation_simulation(properties, ...)

+ async def save_document(container_name, document)
```

### Feature Services (Example: PersonaGenerationService)
```diff
  async def generate_persona(prompt):
      # Business logic
      ...
      return result
+
+ async def save_to_database(prompt, response, ...):
+     # Define document structure
+     document_id = f"{datetime.utcnow().isoformat()}_{agent_name}"
+     document = {
+         "id": document_id,
+         "prompt": prompt,
+         "response": response,
+         # ... feature-specific fields
+     }
+     
+     # Use generic infrastructure
+     await cosmos_db_service.save_document(
+         container_name=cosmos_db_service.PERSONA_GENERATION_CONTAINER,
+         document=document
+     )
```

### Routes
```diff
  # Get result from service
  result = await service.generate_persona(request.prompt)
  
  # Save to database
- await cosmos_db_service.save_persona_generation(...)
+ await persona_generation_service.save_to_database(...)
```

---

## Code Statistics

| Component | Lines Before | Lines After | Change |
|-----------|-------------|-------------|---------|
| CosmosDBService | ~230 | ~120 | -110 (-48%) |
| PersonaGenerationService | ~110 | ~167 | +57 |
| GeneralPromptService | ~133 | ~177 | +44 |
| PromptValidatorService | ~110 | ~168 | +58 |
| ConversationSimulationService | ~292 | ~347 | +55 |
| Routes (4 files) | N/A | N/A | Minimal |
| Memory Banks | N/A | N/A | +62 |
| **Total** | N/A | N/A | **+153 net** |

---

## Architecture Principles

### Single Responsibility Principle ✅
- **CosmosDBService**: Manages Cosmos DB infrastructure
- **Feature Services**: Own complete business logic including persistence

### Separation of Concerns ✅
- Infrastructure layer: Generic database operations
- Business layer: Feature-specific logic and data structures

### Encapsulation ✅
- Each service controls its own data format
- Document structures co-located with business logic

### Open/Closed Principle ✅
- CosmosDBService open for use, closed for modification
- New features don't require changing infrastructure

---

## Testing Verification

✅ **Syntax**: All Python files compile without errors
✅ **Structure**: Verified correct method names and locations
✅ **Imports**: All services properly import cosmos_db_service
✅ **Routes**: All routes call service.save_to_database()
⚠️ **Runtime**: Requires Azure credentials (not tested in CI)

---

## Migration Pattern for New Features

```python
# 1. In your feature service
class NewFeatureService:
    async def save_to_database(self, ...):
        # Define document (business logic)
        document = {
            "id": f"{datetime.utcnow().isoformat()}_{id}",
            # ... your fields
        }
        
        # Use infrastructure (generic)
        await cosmos_db_service.save_document(
            container_name=cosmos_db_service.NEW_CONTAINER,
            document=document
        )

# 2. In your route
result = await new_service.do_work(...)
await new_service.save_to_database(...)  # ✅ NOT cosmos_db_service
```

**DO NOT** add new methods to CosmosDBService!

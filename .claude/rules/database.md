# Database Architecture (Cosmos DB)

## CosmosDBService - Infrastructure Only

The CosmosDBService is a singleton infrastructure service that:
- Manages Cosmos DB client and database references
- Provides container name constants for all features
- Offers generic operations (ensure_container, save_document, browse_container)
- Does NOT contain feature-specific business logic or document structures

## Feature Service Persistence

Each feature service handles its own database persistence:
- Defines document structure specific to the feature
- Uses conversation_id from Azure AI as document ID
- Creates documents with all required fields
- Calls `cosmos_db_service.save_document()` for actual persistence

Example pattern:
```python
async def save_to_database(self, ...params, conversation_id: str):
    # Define document structure (business logic)
    document = {
        "id": conversation_id,
        "prompt": prompt,
        "response": response,
        "parsed_output": parsed_output,  # For persona agents
        # ... other fields specific to this feature
    }

    # Use generic infrastructure method
    await cosmos_db_service.save_document(
        container_name=cosmos_db_service.CONTAINER_NAME,
        document=document
    )
```

## Container Strategy

- One container per feature
- Partition key: `/id`
- Auto-create containers if missing
- Store complete request/response data

## Document Structure

- Document ID: conversation_id from Azure AI (ensures uniqueness)
- Include timestamp
- Include all metrics
- Include complete agent details (name, version, instructions, model, timestamp)
- Include parsed_output for JSON-based agents
- Use ISO format for dates
- Structure defined by feature services, not CosmosDBService

## Local Development

- Supports Cosmos DB Emulator (set `COSMOS_DB_USE_EMULATOR=true`)
- No Azure authentication needed for emulator (uses emulator key)

## Environment Variables

**Cosmos DB Configuration**:
- `COSMOS_DB_ENDPOINT` - Cosmos DB endpoint URL (cloud or emulator)
- `COSMOS_DB_DATABASE_NAME` - Database name
- `COSMOS_DB_USE_EMULATOR` - Set to `true` for local emulator, `false` for cloud
- `COSMOS_DB_KEY` - Emulator key (only needed for local emulator)

**Cloud Configuration** (production):
```env
COSMOS_DB_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOS_DB_DATABASE_NAME=mount_doom_db
COSMOS_DB_USE_EMULATOR=false
# No COSMOS_DB_KEY needed - uses DefaultAzureCredential
```

**Local Emulator Configuration** (development):
```env
COSMOS_DB_ENDPOINT=https://localhost:8081
COSMOS_DB_DATABASE_NAME=mount_doom_db
COSMOS_DB_USE_EMULATOR=true
COSMOS_DB_KEY=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==
```

# Logging (Verbose Development Mode)

## Configuration

- **Centralized Configuration**: Logging logic encapsulated in `app/core/logging.py`
- Uses `structlog` with `ConsoleRenderer(colors=True)` for human-readable console output
- Configured in `main.py` via `setup_logging()` **BEFORE** importing routes
- Routes imported after logging configuration to ensure services use configured logging
- Log level controlled by `settings.api_debug` (DEBUG when True, INFO when False)
- All logs use structured logging with key-value pairs for better filtering
- **Dual Output**: Logs are written to both console (colored) and file (plain text)

## File Logging

- Location: `logs/mount_doom.log` (configurable via `settings.log_dir` and `settings.log_file`)
- Rotation: Automatic rotation at 10MB (configurable via `settings.log_max_bytes`)
- Backup: Keeps 5 backup files (configurable via `settings.log_backup_count`)
- Format: ISO 8601 Timestamp with structured fields
- Encoding: UTF-8

## External Library Logging

External library logs suppressed to WARNING:
- Azure SDK (`azure`, `azure.core`, `azure.ai`, `azure.ai.projects`)
- OpenAI client (`openai`)
- HTTP clients (`httpx`, `httpcore`, `urllib3`)
- Uvicorn loggers configured to propagate to root logger
- Python warnings captured and sent through logging system at WARNING level

## Logging Levels and Usage

### `logger.info()`: Key operations, milestones, and important state changes
- Service initialization
- Request start/end with key parameters
- Major workflow steps
- Database operations
- Final results

### `logger.debug()`: Detailed operational information
- Agent cache hits/misses
- Document IDs and container names
- Response text extraction steps
- Token usage extraction attempts
- Message previews and lengths

### `logger.error()`: Errors and exceptions
- Always include `error=str(e)` parameter
- Always include `exc_info=True` for stack traces
- Log at service level and route level

## What to Log

1. Service initialization (client initialization, connection strings)
2. Agent operations (agent creation, cache hits/misses, version info)
3. Conversation simulation (stream events, workflow actions, messages, token usage)
4. API requests (key parameters, prompt lengths, model/agent names)
5. Responses (text length and preview, token usage, time taken)
6. Database operations (container checks, document creation, save confirmations)

## Structured Logging Best Practices

- Use key-value pairs: `logger.info("Message", key1=value1, key2=value2)`
- Use consistent key names across services
- Include units in key names: `time_ms`, `prompt_length`, `tokens_used`
- Use section separators for major operations: `logger.info("="*60)`
- Preview long text: `text[:150] + "..." if len(text) > 150 else text`
- Round floats for readability: `round(time_ms, 2)`

## Example Logging Pattern

```python
logger.info("="*60)
logger.info("Starting operation", param1=value1, param2=value2)
logger.debug("Detailed step", detail1=value1)
logger.info("Operation completed", result=value, time_ms=round(ms, 2))
logger.info("="*60)
```

import logging
import logging.handlers
import sys
import warnings
from pathlib import Path
import structlog
from app.core.config import settings

def setup_logging() -> structlog.stdlib.BoundLogger:
    """
    Configure structured logging for the application.
    
    This sets up:
    1. Log directory and file
    2. Python standard logging handlers (Console & File)
    3. Structlog processors and formatters
    4. Library log level suppressions (Azure, OpenAI, etc.)
    5. Uvicorn logging integration
    6. Warnings capture
    """
    
    # Get backend root directory (parent of app)
    # app/core/logging.py -> app/core -> app -> backend
    backend_root = Path(__file__).resolve().parent.parent.parent
    
    # Ensure log directory exists
    if Path(settings.log_dir).is_absolute():
        log_dir = Path(settings.log_dir)
    else:
        log_dir = backend_root / settings.log_dir
        
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / settings.log_file

    # Determine log level
    log_level = logging.DEBUG if settings.api_debug else logging.INFO

    # ------------------------------------------------------------------
    # 1. Configure Standard Logging Handlers
    # ------------------------------------------------------------------
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(log_file_path),
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(log_level)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    # Remove existing handlers to avoid duplicates if setup is called multiple times
    root_logger.handlers = []
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # ------------------------------------------------------------------
    # 2. Configure Structlog
    # ------------------------------------------------------------------
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Create structlog formatters
    structlog_console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=True),
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
        ],
    )

    structlog_file_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
        ],
    )

    # Apply formatters to handlers
    console_handler.setFormatter(structlog_console_formatter)
    file_handler.setFormatter(structlog_file_formatter)

    # ------------------------------------------------------------------
    # 3. Suppress Noisy Libraries
    # ------------------------------------------------------------------
    
    # Azure SDK
    logging.getLogger('azure').setLevel(logging.WARNING)
    logging.getLogger('azure.core').setLevel(logging.WARNING)
    logging.getLogger('azure.ai').setLevel(logging.WARNING)
    logging.getLogger('azure.ai.projects').setLevel(logging.WARNING)
    logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
    
    # OpenAI
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('openai._base_client').setLevel(logging.WARNING)
    
    # HTTP Clients
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('httpcore.connection').setLevel(logging.WARNING)
    logging.getLogger('httpcore.http11').setLevel(logging.WARNING)

    # ------------------------------------------------------------------
    # 4. Configure Uvicorn Integration
    # ------------------------------------------------------------------
    
    # Force Uvicorn to use our logging config
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.setLevel(log_level)
        uvicorn_logger.handlers = []  # Remove default handlers
        uvicorn_logger.propagate = True  # Propagate to root logger

    # ------------------------------------------------------------------
    # 5. Capture Warnings
    # ------------------------------------------------------------------
    
    logging.captureWarnings(True)
    warnings_logger = logging.getLogger('py.warnings')
    warnings_logger.setLevel(logging.WARNING)

    # Return a logger for the caller to use immediately
    logger = structlog.get_logger()
    logger.info("Logging configured successfully", 
               log_level=logging.getLevelName(log_level),
               log_file=str(log_file_path))
               
    return logger

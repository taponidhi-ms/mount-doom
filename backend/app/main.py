from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import (
    persona_generation,
    general_prompt,
    prompt_validator,
    conversation_simulation,
    models
)
from app.core.config import settings
import structlog
import logging
import logging.handlers
import os
from pathlib import Path

# Ensure log directory exists
log_dir = Path(settings.log_dir)
log_dir.mkdir(parents=True, exist_ok=True)
log_file_path = log_dir / settings.log_file

# Configure Python's logging with both console and file handlers
log_level = logging.DEBUG if settings.api_debug else logging.INFO

# Create formatters
console_formatter = logging.Formatter("%(message)s")
file_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_handler.setFormatter(console_formatter)

# File handler with rotation
file_handler = logging.handlers.RotatingFileHandler(
    filename=str(log_file_path),
    maxBytes=settings.log_max_bytes,
    backupCount=settings.log_backup_count,
    encoding="utf-8"
)
file_handler.setLevel(log_level)
file_handler.setFormatter(file_formatter)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(log_level)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

# Configure structured logging for console output
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.dev.ConsoleRenderer(colors=True)
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()
logger.info("=" * 80)
logger.info("Mount Doom Backend Starting", 
           debug_mode=settings.api_debug,
           log_file=str(log_file_path))
logger.info("=" * 80)

# Create FastAPI application
app = FastAPI(
    title="Mount Doom - Simulation Agent API",
    description="API for multi-agent conversation simulation and prompt generation",
    version="1.0.0",
    debug=settings.api_debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
logger.info("Registering API routes...")
app.include_router(models.router, prefix="/api/v1")
logger.debug("Registered route", router="models", prefix="/api/v1")
app.include_router(persona_generation.router, prefix="/api/v1")
logger.debug("Registered route", router="persona_generation", prefix="/api/v1")
app.include_router(general_prompt.router, prefix="/api/v1")
logger.debug("Registered route", router="general_prompt", prefix="/api/v1")
app.include_router(prompt_validator.router, prefix="/api/v1")
logger.debug("Registered route", router="prompt_validator", prefix="/api/v1")
app.include_router(conversation_simulation.router, prefix="/api/v1")
logger.debug("Registered route", router="conversation_simulation", prefix="/api/v1")
logger.info("All API routes registered successfully")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Mount Doom - Simulation Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )

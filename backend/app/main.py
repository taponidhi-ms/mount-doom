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

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

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
app.include_router(models.router, prefix="/api/v1")
app.include_router(persona_generation.router, prefix="/api/v1")
app.include_router(general_prompt.router, prefix="/api/v1")
app.include_router(prompt_validator.router, prefix="/api/v1")
app.include_router(conversation_simulation.router, prefix="/api/v1")


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

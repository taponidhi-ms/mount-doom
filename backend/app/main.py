from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging

# Configure logging before anything else
logger = setup_logging()

logger.info("=" * 80)
logger.info("Mount Doom Backend Starting", 
           debug_mode=settings.api_debug)
logger.info("=" * 80)

# Import routes after logging is configured
# This ensures services initialized during import use the proper logging config
from app.api.routes import (
    persona_distribution,
    persona_generator,
    general_prompt,
    prompt_validator,
    conversation_simulation
)

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
app.include_router(persona_distribution.router, prefix="/api/v1")
logger.debug("Registered route", router="persona_distribution", prefix="/api/v1")
app.include_router(persona_generator.router, prefix="/api/v1")
logger.debug("Registered route", router="persona_generator", prefix="/api/v1")
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
    
    # Disable uvicorn's default logging and use our configured logging
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        log_config=None  # Use our logging configuration instead of uvicorn's default
    )

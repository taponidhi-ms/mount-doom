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
from app.modules.persona_distribution import routes as persona_distribution
from app.modules.persona_generator import routes as persona_generator
from app.modules.conversation_simulation import routes as conversation_simulation
from app.modules.transcript_parser import routes as transcript_parser
from app.modules.c2_message_generation import routes as c2_message_generation
from app.modules.agents import routes as agents
from app.modules.workflows import routes as workflows

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
app.include_router(conversation_simulation.router, prefix="/api/v1")
logger.debug("Registered route", router="conversation_simulation", prefix="/api/v1")
app.include_router(transcript_parser.router, prefix="/api/v1")
logger.debug("Registered route", router="transcript_parser", prefix="/api/v1")
app.include_router(c2_message_generation.router, prefix="/api/v1")
logger.debug("Registered route", router="c2_message_generation", prefix="/api/v1")
# Unified agents and workflows APIs
app.include_router(agents.router, prefix="/api/v1")
logger.debug("Registered route", router="agents", prefix="/api/v1")
app.include_router(workflows.router, prefix="/api/v1")
logger.debug("Registered route", router="workflows", prefix="/api/v1")
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

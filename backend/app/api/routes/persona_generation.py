from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    PersonaGenerationRequest,
    PersonaGenerationResponse,
    AvailableAgentsResponse,
    AgentInfo
)
from app.services.azure_ai_service import azure_ai_service
from app.services.cosmos_db_service import cosmos_db_service
from app.core.config import settings
from datetime import datetime
import time

router = APIRouter(prefix="/persona-generation", tags=["Persona Generation"])


@router.get("/agents", response_model=AvailableAgentsResponse)
async def get_available_agents():
    """Get list of available agents for persona generation use case."""
    agents = []
    
    if settings.persona_generation_agent_1:
        agents.append(AgentInfo(
            agent_id=settings.persona_generation_agent_1,
            agent_name="Persona Generation Agent 1",
            description="Primary agent for persona generation"
        ))
    
    if settings.persona_generation_agent_2:
        agents.append(AgentInfo(
            agent_id=settings.persona_generation_agent_2,
            agent_name="Persona Generation Agent 2",
            description="Secondary agent for persona generation"
        ))
    
    return AvailableAgentsResponse(agents=agents)


@router.post("/generate", response_model=PersonaGenerationResponse)
async def generate_persona(request: PersonaGenerationRequest):
    """Generate persona from simulation prompt."""
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000
    
    try:
        # Get response from agent
        response_text, tokens_used = await azure_ai_service.get_agent_response(
            agent_id=request.agent_id,
            prompt=request.prompt,
            stream=request.stream
        )
        
        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        time_taken_ms = end_ms - start_ms
        
        # Save to Cosmos DB
        await cosmos_db_service.save_persona_generation(
            agent_id=request.agent_id,
            prompt=request.prompt,
            response=response_text,
            tokens_used=tokens_used,
            time_taken_ms=time_taken_ms
        )
        
        return PersonaGenerationResponse(
            agent_id=request.agent_id,
            response_text=response_text,
            tokens_used=tokens_used,
            time_taken_ms=time_taken_ms,
            start_time=start_time,
            end_time=end_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating persona: {str(e)}")

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    PersonaGenerationRequest,
    PersonaGenerationResponse,
    AgentDetails
)
from app.services.azure_ai_service import azure_ai_service
from app.services.cosmos_db_service import cosmos_db_service
from app.core.config import settings
from app.instruction_sets import PERSONA_AGENT_NAME, PERSONA_AGENT_INSTRUCTIONS
from datetime import datetime
import time

router = APIRouter(prefix="/persona-generation", tags=["Persona Generation"])


@router.post("/generate", response_model=PersonaGenerationResponse)
async def generate_persona(request: PersonaGenerationRequest):
    """Generate persona from simulation prompt."""
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000
    
    try:
        # Get response from agent using fixed agent name and instructions
        agent_response = await azure_ai_service.get_agent_response(
            agent_name=PERSONA_AGENT_NAME,
            instructions=PERSONA_AGENT_INSTRUCTIONS,
            prompt=request.prompt,
            model_deployment_name=request.model_deployment_name
        )
        
        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        time_taken_ms = end_ms - start_ms
        
        # Save to Cosmos DB
        await cosmos_db_service.save_persona_generation(
            prompt=request.prompt,
            response=agent_response.response_text,
            tokens_used=agent_response.tokens_used,
            time_taken_ms=time_taken_ms,
            agent_name=PERSONA_AGENT_NAME,
            agent_version=agent_response.agent_version,
            agent_instructions=PERSONA_AGENT_INSTRUCTIONS,
            model=request.model_deployment_name,
            agent_timestamp=agent_response.timestamp
        )
        
        agent_details = AgentDetails(
            agent_name=PERSONA_AGENT_NAME,
            agent_version=agent_response.agent_version,
            instructions=PERSONA_AGENT_INSTRUCTIONS,
            model_deployment_name=request.model_deployment_name,
            timestamp=agent_response.timestamp
        )
        
        return PersonaGenerationResponse(
            response_text=agent_response.response_text,
            tokens_used=agent_response.tokens_used,
            time_taken_ms=time_taken_ms,
            start_time=start_time,
            end_time=end_time,
            agent_details=agent_details
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating persona: {str(e)}")

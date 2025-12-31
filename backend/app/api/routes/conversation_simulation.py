from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import (
    ConversationSimulationRequest,
    ConversationSimulationResponse,
    BrowseResponse
)
from app.services.features.conversation_simulation_service import conversation_simulation_service
from app.services.db.cosmos_db_service import cosmos_db_service
from datetime import datetime
import time
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/conversation-simulation", tags=["Conversation Simulation"])


@router.post("/simulate", response_model=ConversationSimulationResponse)
async def simulate_conversation(request: ConversationSimulationRequest):
    """
    Simulate a conversation between C1 and C2 agents using multi-agent workflow.
    
    The workflow uses a single shared conversation where:
    1. C1 agent generates a service representative response
    2. Orchestrator checks if conversation should continue
    3. C2 agent generates a customer response
    4. Orchestrator checks again if conversation should end
    This repeats until max_turns or completion status is reached.
    """
    logger.info("Received conversation simulation request",
               max_turns=request.max_turns,
               customer_intent=request.conversation_properties.customer_intent,
               customer_sentiment=request.conversation_properties.customer_sentiment,
               conversation_subject=request.conversation_properties.conversation_subject)
    
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000
    
    try:
        # Convert conversation properties to dict
        conv_props_dict = {
            "CustomerIntent": request.conversation_properties.customer_intent,
            "CustomerSentiment": request.conversation_properties.customer_sentiment,
            "ConversationSubject": request.conversation_properties.conversation_subject
        }

        # Use conversation simulation service
        simulation_result = await conversation_simulation_service.simulate_conversation(
            simulation_prompt=request.conversation_prompt,
            conversation_properties=conv_props_dict,
            max_turns=request.max_turns
        )

        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        total_time_taken_ms = end_ms - start_ms
        
        logger.info("Simulation completed, preparing for database save",
                   status=simulation_result.conversation_status,
                   messages=len(simulation_result.conversation_history),
                   total_tokens=simulation_result.total_tokens_used)

        # Save to Cosmos DB
        conversation_history_dict = [
            {
                "agent_name": msg.agent_name,
                "message": msg.message,
                "tokens_used": msg.tokens_used,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in simulation_result.conversation_history
        ]

        c1_agent_details = simulation_result.c1_agent_details
        c2_agent_details = simulation_result.c2_agent_details
        orchestrator_agent_details = simulation_result.orchestrator_agent_details

        await cosmos_db_service.save_conversation_simulation(
            conversation_properties=conv_props_dict,
            conversation_history=conversation_history_dict,
            conversation_status=simulation_result.conversation_status,
            total_tokens_used=simulation_result.total_tokens_used,
            total_time_taken_ms=total_time_taken_ms,
            c1_agent_details={
                "agent_name": c1_agent_details.agent_name,
                "agent_version": c1_agent_details.agent_version,
                "instructions": c1_agent_details.instructions,
                "model": c1_agent_details.model_deployment_name,
                "timestamp": c1_agent_details.created_at.isoformat()
            },
            c2_agent_details={
                "agent_name": c2_agent_details.agent_name,
                "agent_version": c2_agent_details.agent_version,
                "instructions": c2_agent_details.instructions,
                "model": c2_agent_details.model_deployment_name,
                "timestamp": c2_agent_details.created_at.isoformat()
            },
            orchestrator_agent_details={
                "agent_name": orchestrator_agent_details.agent_name,
                "agent_version": orchestrator_agent_details.agent_version,
                "instructions": orchestrator_agent_details.instructions,
                "model": orchestrator_agent_details.model_deployment_name,
                "timestamp": orchestrator_agent_details.created_at.isoformat()
            }
        )
        
        logger.info("Returning successful response",
                   total_time_ms=round(total_time_taken_ms, 2),
                   status=simulation_result.conversation_status)

        return ConversationSimulationResponse(
            conversation_history=simulation_result.conversation_history,
            conversation_status=simulation_result.conversation_status,
            total_tokens_used=simulation_result.total_tokens_used,
            total_time_taken_ms=total_time_taken_ms,
            start_time=start_time,
            end_time=end_time,
            c1_agent_details=c1_agent_details,
            c2_agent_details=c2_agent_details,
            orchestrator_agent_details=orchestrator_agent_details
        )

    except Exception as e:
        logger.error("Error in conversation simulation endpoint", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error simulating conversation: {str(e)}")


@router.get("/browse", response_model=BrowseResponse)
async def browse_conversation_simulations(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    order_by: str = Query(default="timestamp", description="Field to order by"),
    order_direction: str = Query(default="DESC", pattern="^(ASC|DESC)$", description="Order direction")
):
    """
    Browse conversation simulation records with pagination and ordering.
    
    Returns a list of conversation simulation records from the database.
    """
    logger.info("Browsing conversation simulations",
               page=page,
               page_size=page_size,
               order_by=order_by,
               order_direction=order_direction)
    
    try:
        result = await cosmos_db_service.browse_container(
            container_name=cosmos_db_service.CONVERSATION_SIMULATION_CONTAINER,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_direction=order_direction
        )
        
        logger.info("Returning browse results", total_count=result["total_count"])
        return result
    
    except Exception as e:
        logger.error("Error browsing conversation simulations", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error browsing conversation simulations: {str(e)}")

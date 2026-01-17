from fastapi import APIRouter, HTTPException, Query, Response
from app.models.shared import BrowseResponse
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from .models import (
    ConversationSimulationRequest,
    ConversationSimulationResponse
)
from .conversation_simulation_service import conversation_simulation_service
from datetime import datetime
import time
import json
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/conversation-simulation", tags=["Conversation Simulation"])

@router.post("/simulate", response_model=ConversationSimulationResponse)
async def simulate_conversation(request: ConversationSimulationRequest):
    """
    Simulate a conversation between C1 and C2 agents.
    """
    MAX_TURNS = 15
    logger.info("Received conversation simulation request", 
               max_turns=MAX_TURNS,
               customer_intent=request.customer_intent,
               customer_sentiment=request.customer_sentiment,
               conversation_subject=request.conversation_subject)
    
    start_ms = time.time() * 1000

    try:
        conv_props_dict = {
            "CustomerIntent": request.customer_intent,
            "CustomerSentiment": request.customer_sentiment,
            "ConversationSubject": request.conversation_subject
        }

        # Use conversation simulation service
        simulation_result = await conversation_simulation_service.simulate_conversation(
            conversation_properties=conv_props_dict,
            max_turns=MAX_TURNS
        )

        end_ms = time.time() * 1000
        total_time_taken_ms = end_ms - start_ms

        logger.info("Simulation completed, preparing for database save", 
                   status=simulation_result.conversation_status,
                   messages=len(simulation_result.conversation_history))

        c1_agent_details = simulation_result.c1_agent_details
        c2_agent_details = simulation_result.c2_agent_details

        await conversation_simulation_service.save_to_database(
            conversation_properties=conv_props_dict,
            conversation_history=simulation_result.conversation_history,
            conversation_status=simulation_result.conversation_status,
            total_time_taken_ms=total_time_taken_ms,
            c1_agent_details={
                "agent_name": c1_agent_details.agent_name,
                "agent_version": c1_agent_details.agent_version,
                "instructions": c1_agent_details.instructions,
                "model_deployment_name": c1_agent_details.model_deployment_name,
                "created_at": c1_agent_details.created_at
            },
            c2_agent_details={
                "agent_name": c2_agent_details.agent_name,
                "agent_version": c2_agent_details.agent_version,
                "instructions": c2_agent_details.instructions,
                "model_deployment_name": c2_agent_details.model_deployment_name,
                "created_at": c2_agent_details.created_at
            },
            conversation_id=simulation_result.conversation_id
        )

        return ConversationSimulationResponse(
            conversation_history=simulation_result.conversation_history,
            conversation_status=simulation_result.conversation_status,
            total_time_taken_ms=total_time_taken_ms,
            start_time=simulation_result.start_time,
            end_time=simulation_result.end_time,
            c1_agent_details=c1_agent_details,
            c2_agent_details=c2_agent_details,
            conversation_id=simulation_result.conversation_id
        )
        
    except Exception as e:
        logger.error("Error in conversation simulation", error=str(e), exc_info=True)
        raise

@router.get("/browse", response_model=BrowseResponse)
async def browse_conversation_simulations(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    order_by: str = Query(default="timestamp", description="Field to order by"),
    order_direction: str = Query(default="DESC", pattern="^(ASC|DESC)$", description="Order direction")
):
    """
    Browse conversation simulation records with pagination and ordering.
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

@router.post("/delete")
async def delete_conversation_simulations(conversation_ids: list[str]):
    """
    Delete conversation simulation records by their IDs.
    """
    logger.info("Received delete request", count=len(conversation_ids))

    if not conversation_ids:
        raise HTTPException(status_code=400, detail="No conversation IDs provided")

    try:
        container = await cosmos_db_service.ensure_container(
            cosmos_db_service.CONVERSATION_SIMULATION_CONTAINER
        )
        
        deleted_count = 0
        errors = []
        
        for conv_id in conversation_ids:
            try:
                container.delete_item(item=conv_id, partition_key=conv_id)
                deleted_count += 1
                logger.debug("Deleted conversation", conversation_id=conv_id)
            except Exception as e:
                error_msg = f"Failed to delete {conv_id}: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)
        
        logger.info("Delete operation completed", deleted=deleted_count, failed=len(errors))
        
        return {
            "deleted_count": deleted_count,
            "failed_count": len(errors),
            "errors": errors
        }
    
    except Exception as e:
        logger.error("Error deleting conversation simulations", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting conversation simulations: {str(e)}")


@router.post("/download")
async def download_conversation_simulations(conversation_ids: list[str]):
    """
    Download conversation simulation records as JSON.
    Returns conversations array with full metadata and conversation history.
    """
    logger.info("Received download request", count=len(conversation_ids))
    
    if not conversation_ids:
        raise HTTPException(status_code=400, detail="No conversation IDs provided")

    try:
        container = await cosmos_db_service.ensure_container(
            cosmos_db_service.CONVERSATION_SIMULATION_CONTAINER
        )
        
        conversations = []
        
        for conv_id in conversation_ids:
            try:
                item = container.read_item(item=conv_id, partition_key=conv_id)
                
                # Extract conversation properties
                conv_props = item.get("conversation_properties", {})
                customer_intent = conv_props.get("CustomerIntent", "")
                customer_sentiment = conv_props.get("CustomerSentiment", "")
                conversation_subject = conv_props.get("ConversationSubject", "")
                
                # Build conversation messages
                conversation_messages = []
                
                # Add conversation history
                conversation_history = item.get("conversation_history", [])
                for msg in conversation_history:
                    agent_name = msg.get("agent_name", "")
                    message_text = msg.get("message", "")
                    
                    # C1 is CSR (user), C2 is customer (assistant)
                    if "C1" in agent_name:
                        conversation_messages.append({
                            "role": "customer_service_representative",
                            "content": message_text
                        })
                    elif "C2" in agent_name:
                        conversation_messages.append({
                            "role": "customer",
                            "content": message_text
                        })
                
                conversation = {
                    "Id": item.get("id"),
                    "scenario_name": "conversation_simulation",
                    "customer_intent": customer_intent,
                    "customer_sentiment": customer_sentiment,
                    "conversation_subject": conversation_subject,
                    "conversation": conversation_messages
                }
                conversations.append(conversation)
                
            except Exception as e:
                logger.warning("Failed to retrieve conversation", conversation_id=conv_id, error=str(e))
                continue
        
        result = {"conversations": conversations}
        json_str = json.dumps(result, indent=2)
        
        logger.info("Returning download data", conversation_count=len(conversations))
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="conversation_simulations.json"'}
        )
        
    except Exception as e:
        logger.error("Error downloading conversation simulations", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error downloading: {str(e)}")

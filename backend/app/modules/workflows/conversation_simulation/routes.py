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

        # agent_details is already a dict from the service
        await conversation_simulation_service.save_to_database(
            conversation_properties=conv_props_dict,
            conversation_history=simulation_result.conversation_history,
            conversation_status=simulation_result.conversation_status,
            total_time_taken_ms=total_time_taken_ms,
            agent_details=simulation_result.agent_details,
            conversation_id=simulation_result.conversation_id
        )

        return ConversationSimulationResponse(
            conversation_history=simulation_result.conversation_history,
            conversation_status=simulation_result.conversation_status,
            total_time_taken_ms=total_time_taken_ms,
            start_time=simulation_result.start_time,
            end_time=simulation_result.end_time,
            agent_details=simulation_result.agent_details,
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
            container_name=cosmos_db_service.MULTI_TURN_CONVERSATIONS_CONTAINER,
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
    Also deletes the corresponding Azure AI conversations.
    """
    logger.info("Received delete request", count=len(conversation_ids))

    if not conversation_ids:
        raise HTTPException(status_code=400, detail="No conversation IDs provided")

    try:
        from app.modules.agents.agents_service import unified_agents_service

        container = await cosmos_db_service.ensure_container(
            cosmos_db_service.MULTI_TURN_CONVERSATIONS_CONTAINER
        )

        deleted_count = 0
        errors = []

        for conv_id in conversation_ids:
            try:
                # First, read the document to get the Azure AI conversation_id
                item = container.read_item(item=conv_id, partition_key=conv_id)
                azure_conversation_id = item.get("conversation_id")

                # Delete from Azure AI if conversation_id exists
                if azure_conversation_id:
                    try:
                        await unified_agents_service.delete_conversation(azure_conversation_id)
                        logger.debug("Deleted Azure AI conversation", conversation_id=azure_conversation_id)
                    except Exception as azure_error:
                        logger.warning("Failed to delete Azure AI conversation",
                                     conversation_id=azure_conversation_id,
                                     error=str(azure_error))
                        # Continue with Cosmos DB deletion even if Azure deletion fails

                # Delete from Cosmos DB
                container.delete_item(item=conv_id, partition_key=conv_id)
                deleted_count += 1
                logger.debug("Deleted Cosmos DB document", document_id=conv_id)
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
            cosmos_db_service.MULTI_TURN_CONVERSATIONS_CONTAINER
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

                # Add conversation history (using new structure with role and content)
                conversation_history = item.get("conversation_history", [])
                for msg in conversation_history:
                    role = msg.get("role", "")
                    content = msg.get("content", "")

                    # Map role to download format
                    if role == "agent":
                        conversation_messages.append({
                            "role": "customer_service_representative",
                            "content": content
                        })
                    elif role == "customer":
                        conversation_messages.append({
                            "role": "customer",
                            "content": content
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

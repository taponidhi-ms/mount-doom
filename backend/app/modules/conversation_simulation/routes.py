from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.modules.conversation_simulation.models import (
    ConversationSimulationRequest,
    ConversationSimulationResponse
)
from app.models.shared import (
    BrowseResponse,
    PrepareEvalsRequest,
    PrepareEvalsResponse,
    EvalsDataResponse
)
from app.core.config import settings
from .conversation_simulation_service import conversation_simulation_service
from .conversation_simulation_evals_service import conversation_simulation_evals_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from datetime import datetime
import time
import structlog
import io
import json
import zipfile

logger = structlog.get_logger()

router = APIRouter(prefix="/conversation-simulation", tags=["Conversation Simulation"])

@router.post("/simulate", response_model=ConversationSimulationResponse)
async def simulate_conversation(request: ConversationSimulationRequest):
    """
    Simulate a conversation between C1 and C2 agents using multi-agent workflow.
    The workflow uses a single shared conversation where:
    1. C1 agent generates a service representative response
    2. C2 agent generates a customer response
    This repeats until max_turns (10) or completion status is reached.
    """
    MAX_TURNS = 10  # Hardcoded max turns (5 turns each for C1 and C2)
    logger.info("Received conversation simulation request", 
               max_turns=MAX_TURNS,
               customer_intent=request.customer_intent,
               customer_sentiment=request.customer_sentiment,
               conversation_subject=request.conversation_subject)
    
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000

    try:
        # Convert request fields to dict for service
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

        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        total_time_taken_ms = end_ms - start_ms

        logger.info("Simulation completed, preparing for database save", 
                   status=simulation_result.conversation_status,
                   messages=len(simulation_result.conversation_history))

        # Save to database using service method
        conversation_history_dict = [
            {
                "agent_name": msg.agent_name,
                "message": msg.message,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in simulation_result.conversation_history
        ]

        c1_agent_details = simulation_result.c1_agent_details
        c2_agent_details = simulation_result.c2_agent_details

        await conversation_simulation_service.save_to_database(
            conversation_properties=conv_props_dict,
            conversation_history=conversation_history_dict,
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

        logger.info("Returning successful response", 
                   total_time_ms=round(total_time_taken_ms, 2),
                   status=simulation_result.conversation_status)
        
        return ConversationSimulationResponse(
            conversation_history=simulation_result.conversation_history,
            conversation_status=simulation_result.conversation_status,
            total_time_taken_ms=total_time_taken_ms,
            start_time=start_time,
            end_time=end_time,
            c1_agent_details=c1_agent_details,
            c2_agent_details=c2_agent_details,
            conversation_id=simulation_result.conversation_id
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

@router.post("/evals/prepare", response_model=PrepareEvalsResponse)
async def prepare_evals(request: PrepareEvalsRequest):
    """
    Prepare CXA AI Evals dataset from selected simulation runs.
    Accepts a list of run IDs, aggregates them into the required format,
    and returns an evals ID and configuration.
    """
    logger.info("Received evaluations preparation request", runs_count=len(request.selected_run_ids))

    try:
        result = await conversation_simulation_evals_service.prepare_evals(request.selected_run_ids)
        
        logger.info("Evals preparation completed", 
                   evals_id=result.get("evals_id"),
                   conversations_count=result.get("conversations_count"))
        
        return PrepareEvalsResponse(
            evals_id=result["evals_id"],
            timestamp=result["timestamp"],
            source_run_ids=result["source_run_ids"],
            conversations_count=result["conversations_count"],
            message=result["message"]
        )

    except ValueError as e:
        logger.warning("Validation error in evals preparation", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error preparing evals", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error preparing evals: {str(e)}")

@router.get("/evals/latest", response_model=EvalsDataResponse)
async def get_latest_evals():
    """
    Get the most recently prepared evals dataset for conversation simulation.
    Returns the latest CXA AI Evals configuration and input data.
    """
    logger.info("Fetching latest evals preparation")

    try:
        result = await conversation_simulation_evals_service.get_latest_evals()
        if not result:
            raise HTTPException(status_code=404, detail="No evals preparations found")
            
        logger.info("Returning latest evals", evals_id=result.get("id"))
        
        return EvalsDataResponse(
            evals_id=result["id"],
            timestamp=result["timestamp"],
            source_run_ids=result["source_run_ids"],
            cxa_evals_config=result["cxa_evals_config"],
            cxa_evals_input_data=result["cxa_evals_input_data"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching latest evals", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching latest evals: {str(e)}")

@router.post("/delete")
async def delete_conversation_simulations(conversation_ids: list[str]):
    """
    Delete conversation simulation records by their IDs.
    Accepts a list of conversation IDs to delete.
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

@router.get("/evals/{evals_id}/download")
async def download_evals_zip(evals_id: str):
    """Download a prepared evals bundle as a zip file."""
    logger.info("Preparing evals zip download", evals_id=evals_id)
    try:
        container = await cosmos_db_service.ensure_container(
            cosmos_db_service.CONVERSATION_SIMULATION_EVALS_CONTAINER
        )
        evals_document = container.read_item(item=evals_id, partition_key=evals_id)
        
        cxa_evals_config = evals_document.get("cxa_evals_config")
        cxa_evals_input_data = evals_document.get("cxa_evals_input_data")
        
        if cxa_evals_config is None or cxa_evals_input_data is None:
            raise HTTPException(status_code=404, detail="Evals config or input data not found")
            
        zip_buffer = io.BytesIO()
        folder_prefix = f"{evals_id}/"

        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                f"{folder_prefix}cxa_evals_config.json", 
                json.dumps(cxa_evals_config, indent=2)
            )
            zf.writestr(
                f"{folder_prefix}cxa_evals_input_data.json", 
                json.dumps(cxa_evals_input_data, indent=2)
            )

        zip_buffer.seek(0)
        headers = {"Content-Disposition": f'attachment; filename="{evals_id}.zip"'}
        logger.info("Returning evals zip", evals_id=evals_id)
        return StreamingResponse(zip_buffer, media_type="application/zip", headers=headers)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error generating evals zip", evals_id=evals_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating evals zip: {str(e)}")

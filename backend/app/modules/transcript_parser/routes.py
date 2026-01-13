from fastapi import APIRouter, HTTPException, Query
from app.modules.transcript_parser.models import (
    TranscriptParserRequest,
    TranscriptParserResponse
)
from app.models.shared import (
    BrowseResponse,
    AgentDetails
)
from app.core.config import settings
from .transcript_parser_service import transcript_parser_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from datetime import datetime
import time
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/transcript-parser", tags=["Transcript Parser"])

@router.post("/parse", response_model=TranscriptParserResponse)
async def parse_transcript(request: TranscriptParserRequest):
    """Parse a transcript to extract intent, subject, and sentiment."""
    logger.info("Received transcript parsing request", transcript_length=len(request.transcript))
    
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000

    try:
        # Get response from transcript parser service
        agent_response = await transcript_parser_service.parse_transcript(request.transcript)
        
        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        time_taken_ms = end_ms - start_ms

        logger.info("Transcript parsed, saving to database", 
                   tokens=agent_response.tokens_used,
                   time_ms=round(time_taken_ms, 2))

        # Save to database using service method
        await transcript_parser_service.save_to_database(
            transcript=request.transcript,
            response=agent_response.response_text,
            tokens_used=agent_response.tokens_used,
            time_taken_ms=time_taken_ms,
            agent_name=agent_response.agent_details.agent_name,
            agent_version=agent_response.agent_details.agent_version,
            agent_instructions=agent_response.agent_details.instructions,
            model=agent_response.agent_details.model_deployment_name,
            agent_timestamp=agent_response.agent_details.created_at,
            conversation_id=agent_response.conversation_id,
            parsed_output=agent_response.parsed_output
        )

        logger.info("Returning successful transcript parsing response")
        return TranscriptParserResponse(
            response_text=agent_response.response_text,
            tokens_used=agent_response.tokens_used,
            time_taken_ms=time_taken_ms,
            start_time=start_time,
            end_time=end_time,
            agent_details=agent_response.agent_details,
            parsed_output=agent_response.parsed_output
        )

    except Exception as e:
        logger.error("Error in transcript parsing endpoint", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error parsing transcript: {str(e)}")

@router.get("/browse", response_model=BrowseResponse)
async def browse_transcripts(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    order_by: str = Query(default="timestamp", description="Field to order by"),
    order_direction: str = Query(default="DESC", pattern="^(ASC|DESC)$", description="Order direction")
):
    """
    Browse transcript parsing records with pagination and ordering.
    Returns a list of transcript parsing records from the database.
    """
    logger.info("Browsing transcript parsing records", 
               page=page, 
               page_size=page_size, 
               order_by=order_by,
               order_direction=order_direction)

    try:
        result = await cosmos_db_service.browse_container(
            container_name=cosmos_db_service.TRANSCRIPT_PARSER_CONTAINER,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_direction=order_direction
        )

        logger.info("Returning browse results", total_count=result["total_count"])
        return result

    except Exception as e:
        logger.error("Error browsing transcript parsing records", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error browsing transcript parsing records: {str(e)}")

@router.post("/delete")
async def delete_transcripts(ids: list[str]):
    """Delete transcript parsing records by their IDs."""
    logger.info("Received delete request", count=len(ids))
    if not ids:
        raise HTTPException(status_code=400, detail="No IDs provided")

    try:
        container = await cosmos_db_service.ensure_container(
            cosmos_db_service.TRANSCRIPT_PARSER_CONTAINER
        )
        
        deleted_count = 0
        errors = []
        
        for item_id in ids:
            try:
                container.delete_item(item=item_id, partition_key=item_id)
                deleted_count += 1
            except Exception as e:
                errors.append(f"Failed to delete {item_id}: {str(e)}")
                logger.warning(f"Failed to delete {item_id}", error=str(e))
        
        logger.info("Delete operation completed", deleted=deleted_count, failed=len(errors))
        return {"deleted_count": deleted_count, "failed_count": len(errors), "errors": errors}
    
    except Exception as e:
        logger.error("Error deleting transcript parsing records", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting: {str(e)}")

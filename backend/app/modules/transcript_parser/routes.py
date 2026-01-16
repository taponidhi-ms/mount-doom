"""Routes for Transcript Parser use case."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from datetime import datetime, timezone
import time
import structlog

from app.modules.transcript_parser.models import (
    TranscriptParserRequest,
    TranscriptParserResponse
)
from app.models.shared import BrowseResponse
from .transcript_parser_service import transcript_parser_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from app.modules.shared.route_helpers import (
    browse_records,
    delete_records,
    download_records_as_conversations
)

logger = structlog.get_logger()

router = APIRouter(prefix="/transcript-parser", tags=["Transcript Parser"])


@router.post("/parse", response_model=TranscriptParserResponse)
async def parse_transcript(request: TranscriptParserRequest):
    """Parse a transcript to extract intent, subject, and sentiment."""
    logger.info("Received transcript parsing request", transcript_length=len(request.transcript))
    
    start_time = datetime.now(timezone.utc)
    start_ms = time.time() * 1000

    try:
        # Get response from transcript parser service
        agent_response = await transcript_parser_service.parse_transcript(request.transcript)
        
        end_time = datetime.now(timezone.utc)
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
    """Browse transcript parsing records with pagination and ordering."""
    return await browse_records(
        container_name=cosmos_db_service.TRANSCRIPT_PARSER_CONTAINER,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order_direction=order_direction,
        use_case_name="transcript parsing records"
    )


@router.post("/delete")
async def delete_transcripts(ids: list[str]):
    """Delete transcript parsing records by their IDs."""
    return await delete_records(
        container_name=cosmos_db_service.TRANSCRIPT_PARSER_CONTAINER,
        ids=ids,
        use_case_name="transcript parsing records"
    )


@router.post("/download")
async def download_transcripts(ids: list[str]) -> Response:
    """Download transcript parsing records as JSON."""
    return await download_records_as_conversations(
        container_name=cosmos_db_service.TRANSCRIPT_PARSER_CONTAINER,
        ids=ids,
        scenario_name="transcript_parsing",
        filename="transcript_parsing_records.json",
        use_case_name="transcript parsing records",
        input_field="transcript"
    )


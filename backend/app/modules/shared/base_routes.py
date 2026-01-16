"""
Base routes factory for single-agent operations.

This module provides factory functions to create standard CRUD routes
for single-agent use cases, reducing code duplication across modules.
"""

from datetime import datetime, timezone
import time
import json
import structlog
from typing import Callable, Awaitable, Type, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel

from app.models.shared import BrowseResponse, AgentDetails
from app.models.single_agent import SingleAgentResponse
from app.infrastructure.db.cosmos_db_service import cosmos_db_service

logger = structlog.get_logger()


def create_single_agent_routes(
    router: APIRouter,
    service: object,
    container_name: str,
    use_case_name: str,
    request_model: Type[BaseModel],
    response_model: Type[BaseModel] = SingleAgentResponse,
    generate_endpoint_name: str = "/generate",
    input_field_name: str = "prompt",
    parse_json: bool = True
):
    """
    Add standard single-agent routes to a router.
    
    This creates:
    - POST /{generate_endpoint_name}: Generate using the agent
    - GET /browse: Browse past results with pagination
    - POST /delete: Delete selected records
    - POST /download: Download selected records as JSON
    
    Args:
        router: The FastAPI router to add routes to
        service: The service instance with a generate() method
        container_name: Cosmos DB container name
        use_case_name: Human-readable name for logging
        request_model: Pydantic model for the request
        response_model: Pydantic model for the response
        generate_endpoint_name: Name of the generate endpoint
        input_field_name: Name of the input field in the request (prompt or transcript)
        parse_json: Whether to parse JSON from response
    """
    
    @router.post(generate_endpoint_name, response_model=response_model)
    async def generate(request: request_model):
        """Generate using the agent."""
        input_value = getattr(request, input_field_name)
        logger.info(f"Received {use_case_name} request", input_length=len(input_value))
        
        start_time = datetime.now(timezone.utc)
        start_ms = time.time() * 1000

        try:
            # Get response from service
            agent_response = await service.generate(input_value, parse_json=parse_json)
            
            end_time = datetime.now(timezone.utc)
            end_ms = time.time() * 1000
            time_taken_ms = end_ms - start_ms

            logger.info(f"{use_case_name} generated, saving to database", 
                       tokens=agent_response.tokens_used,
                       time_ms=round(time_taken_ms, 2))

            # Save to database
            await service.save_to_database(
                prompt=input_value,
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

            logger.info(f"Returning successful {use_case_name} response")
            return response_model(
                response_text=agent_response.response_text,
                tokens_used=agent_response.tokens_used,
                time_taken_ms=time_taken_ms,
                start_time=start_time,
                end_time=end_time,
                agent_details=agent_response.agent_details,
                parsed_output=agent_response.parsed_output if hasattr(response_model, 'parsed_output') else None
            )

        except Exception as e:
            logger.error(f"Error in {use_case_name} endpoint", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error in {use_case_name}: {str(e)}")

    @router.get("/browse", response_model=BrowseResponse)
    async def browse(
        page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
        order_by: str = Query(default="timestamp", description="Field to order by"),
        order_direction: str = Query(default="DESC", pattern="^(ASC|DESC)$", description="Order direction")
    ):
        """Browse records with pagination and ordering."""
        logger.info(f"Browsing {use_case_name}", 
                   page=page, 
                   page_size=page_size, 
                   order_by=order_by,
                   order_direction=order_direction)

        try:
            result = await cosmos_db_service.browse_container(
                container_name=container_name,
                page=page,
                page_size=page_size,
                order_by=order_by,
                order_direction=order_direction
            )

            logger.info("Returning browse results", total_count=result["total_count"])
            return result

        except Exception as e:
            logger.error(f"Error browsing {use_case_name}", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error browsing {use_case_name}: {str(e)}")

    @router.post("/delete")
    async def delete_records(ids: list[str]):
        """Delete records by their IDs."""
        logger.info(f"Received delete request for {use_case_name}", count=len(ids))
        if not ids:
            raise HTTPException(status_code=400, detail="No IDs provided")

        try:
            container = await cosmos_db_service.ensure_container(container_name)
            
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
            logger.error(f"Error deleting {use_case_name}", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error deleting: {str(e)}")

    @router.post("/download")
    async def download_records(ids: list[str]):
        """Download records as JSON."""
        logger.info(f"Received download request for {use_case_name}", count=len(ids))
        
        if not ids:
            raise HTTPException(status_code=400, detail="No IDs provided")

        try:
            container = await cosmos_db_service.ensure_container(container_name)
            
            documents = []
            for item_id in ids:
                try:
                    doc = container.read_item(item=item_id, partition_key=item_id)
                    # Clean up Cosmos DB metadata
                    doc.pop('_rid', None)
                    doc.pop('_self', None)
                    doc.pop('_etag', None)
                    doc.pop('_attachments', None)
                    doc.pop('_ts', None)
                    documents.append(doc)
                except Exception as e:
                    logger.warning(f"Failed to read document {item_id}", error=str(e))
            
            json_content = json.dumps(documents, indent=2, default=str)
            
            return Response(
                content=json_content,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={container_name}_{datetime.now(timezone.utc).isoformat()}.json"
                }
            )
        
        except Exception as e:
            logger.error(f"Error downloading {use_case_name}", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error downloading: {str(e)}")
    
    return router

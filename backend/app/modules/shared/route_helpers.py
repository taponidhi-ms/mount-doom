"""
Shared route helper functions for single-agent operations.

This module provides reusable helper functions for common route operations
like browse, delete, and download, reducing code duplication across modules.
"""

import json
import structlog
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from fastapi import HTTPException
from fastapi.responses import Response

from app.models.shared import BrowseResponse
from app.infrastructure.db.cosmos_db_service import cosmos_db_service

logger = structlog.get_logger()


async def browse_records(
    container_name: str,
    page: int,
    page_size: int,
    order_by: str,
    order_direction: str,
    use_case_name: str
) -> Dict[str, Any]:
    """
    Browse records with pagination and ordering.
    
    Args:
        container_name: Cosmos DB container name
        page: Page number (1-indexed)
        page_size: Items per page
        order_by: Field to order by
        order_direction: ASC or DESC
        use_case_name: Name for logging
    
    Returns:
        Dict with items and total_count
    """
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


async def delete_records(
    container_name: str,
    ids: List[str],
    use_case_name: str
) -> Dict[str, Any]:
    """
    Delete records by their IDs.
    
    Args:
        container_name: Cosmos DB container name
        ids: List of record IDs to delete
        use_case_name: Name for logging
    
    Returns:
        Dict with deleted_count, failed_count, and errors
    """
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


async def download_records_as_conversations(
    container_name: str,
    ids: List[str],
    scenario_name: str,
    filename: str,
    use_case_name: str,
    input_field: str = "prompt"
) -> Response:
    """
    Download records as JSON in conversation format.
    
    Args:
        container_name: Cosmos DB container name
        ids: List of record IDs to download
        scenario_name: Name for the scenario field in output
        filename: Output filename
        use_case_name: Name for logging
        input_field: Field name for user input (prompt or transcript)
    
    Returns:
        Response with JSON content
    """
    logger.info(f"Received download request for {use_case_name}", count=len(ids))
    
    if not ids:
        raise HTTPException(status_code=400, detail="No IDs provided")

    try:
        container = await cosmos_db_service.ensure_container(container_name)
        
        conversations = []
        
        for item_id in ids:
            try:
                item = container.read_item(item=item_id, partition_key=item_id)
                
                # Extract agent instructions from agent_details
                agent_details = item.get("agent_details", {})
                agent_instructions = agent_details.get("instructions", "")
                
                # Extract data from the stored item
                conversation = {
                    "Id": item.get("id"),
                    "scenario_name": scenario_name,
                    "conversation": [
                        {
                            "role": "system",
                            "content": agent_instructions
                        },
                        {
                            "role": "user",
                            "content": item.get(input_field, "")
                        },
                        {
                            "role": "assistant",
                            "content": item.get("response", "")
                        }
                    ]
                }
                conversations.append(conversation)
                
            except Exception as e:
                logger.warning("Failed to retrieve item", item_id=item_id, error=str(e))
                continue
        
        result = {"conversations": conversations}
        json_str = json.dumps(result, indent=2)
        
        logger.info("Returning download data", conversation_count=len(conversations))
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
        
    except Exception as e:
        logger.error(f"Error downloading {use_case_name}", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error downloading: {str(e)}")


async def download_records_raw(
    container_name: str,
    ids: List[str],
    filename: str,
    use_case_name: str
) -> Response:
    """
    Download records as raw JSON (without conversation format transformation).
    
    Args:
        container_name: Cosmos DB container name
        ids: List of record IDs to download
        filename: Output filename
        use_case_name: Name for logging
    
    Returns:
        Response with JSON content
    """
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
                "Content-Disposition": f'attachment; filename="{filename}_{datetime.now(timezone.utc).isoformat()}.json"'
            }
        )
    
    except Exception as e:
        logger.error(f"Error downloading {use_case_name}", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error downloading: {str(e)}")

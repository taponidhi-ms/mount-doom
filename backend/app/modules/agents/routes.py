"""
Routes for the unified Agents API.

This module provides a single consolidated API for all single-agent operations.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
import json
import structlog

from app.models.shared import BrowseResponse
from app.infrastructure.db.cosmos_db_service import cosmos_db_service

from .config import get_agent_config, get_all_agents
from .models import AgentInfo, AgentListResponse, AgentInvokeRequest, AgentInvokeResponse
from .agents_service import unified_agents_service

logger = structlog.get_logger()

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/list", response_model=AgentListResponse)
async def list_agents():
    """
    List all available agents with their configurations.
    
    Returns agent metadata including ID, name, description, and instructions.
    """
    logger.info("Listing all agents")
    
    agents_dict = get_all_agents()
    agents = [
        AgentInfo(
            agent_id=config.agent_id,
            agent_name=config.agent_name,
            display_name=config.display_name,
            description=config.description,
            instructions=config.instructions,
            input_field=config.input_field,
            input_label=config.input_label,
            input_placeholder=config.input_placeholder,
            sample_inputs=config.sample_inputs
        )
        for config in agents_dict.values()
    ]
    
    logger.info("Returning agent list", count=len(agents))
    return AgentListResponse(agents=agents)


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str):
    """
    Get details of a specific agent by ID.
    
    Returns agent metadata including instructions.
    """
    logger.info("Getting agent details", agent_id=agent_id)
    
    config = get_agent_config(agent_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    return AgentInfo(
        agent_id=config.agent_id,
        agent_name=config.agent_name,
        display_name=config.display_name,
        description=config.description,
        instructions=config.instructions,
        input_field=config.input_field,
        input_label=config.input_label,
        input_placeholder=config.input_placeholder,
        sample_inputs=config.sample_inputs
    )


@router.post("/{agent_id}/invoke", response_model=AgentInvokeResponse)
async def invoke_agent(agent_id: str, request: AgentInvokeRequest):
    """
    Invoke an agent with the given input.

    This is a unified endpoint that works for all single agents.
    The service layer handles timing, persistence, and all business logic.
    """
    logger.info("Received agent invocation request",
               agent_id=agent_id,
               input_length=len(request.input))

    config = get_agent_config(agent_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    try:
        # Invoke the agent (service handles timing and persistence)
        result = await unified_agents_service.invoke_agent(
            agent_id=agent_id,
            input_text=request.input,
            persist=True
        )

        logger.info("Agent invocation completed successfully",
                   agent_id=agent_id,
                   tokens=result.tokens_used,
                   time_ms=round(result.time_taken_ms, 2))

        # Convert service layer Result to API layer Response
        return AgentInvokeResponse(
            response_text=result.response_text,
            tokens_used=result.tokens_used,
            time_taken_ms=result.time_taken_ms,
            start_time=result.start_time,
            end_time=result.end_time,
            agent_details=result.agent_details,
            conversation_id=result.conversation_id
        )

    except Exception as e:
        logger.error("Error in agent invocation", agent_id=agent_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error invoking agent: {str(e)}")


@router.get("/{agent_id}/browse", response_model=BrowseResponse)
async def browse_agent_history(
    agent_id: str,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    order_by: str = Query(default="timestamp", description="Field to order by"),
    order_direction: str = Query(default="DESC", pattern="^(ASC|DESC)$", description="Order direction")
):
    """Browse history for a specific agent."""
    logger.info("Browsing agent history",
               agent_id=agent_id,
               page=page,
               page_size=page_size)

    config = get_agent_config(agent_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    try:
        result = await cosmos_db_service.browse_container(
            container_name=config.container_name,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_direction=order_direction,
            agent_name=config.agent_name
        )

        logger.info("Returning browse results",
                   agent_name=config.agent_name,
                   total_count=result["total_count"])
        return result

    except Exception as e:
        logger.error("Error browsing agent history", agent_id=agent_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error browsing history: {str(e)}")


@router.post("/{agent_id}/delete")
async def delete_agent_records(agent_id: str, ids: list[str]):
    """
    Delete records for a specific agent by their IDs.
    Also deletes the corresponding Azure AI conversations.
    """
    logger.info("Received delete request", agent_id=agent_id, count=len(ids))

    config = get_agent_config(agent_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    if not ids:
        raise HTTPException(status_code=400, detail="No IDs provided")

    try:
        container = await cosmos_db_service.ensure_container(config.container_name)

        deleted_count = 0
        errors = []

        for record_id in ids:
            try:
                # First, read the document to get the Azure AI conversation_id
                item = container.read_item(item=record_id, partition_key=record_id)
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
                container.delete_item(item=record_id, partition_key=record_id)
                deleted_count += 1
                logger.debug("Deleted Cosmos DB record", record_id=record_id)
            except Exception as e:
                error_msg = f"Failed to delete {record_id}: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)

        logger.info("Delete operation completed", deleted=deleted_count, failed=len(errors))

        return {
            "deleted_count": deleted_count,
            "failed_count": len(errors),
            "errors": errors
        }

    except Exception as e:
        logger.error("Error deleting records", agent_id=agent_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting records: {str(e)}")


@router.post("/{agent_id}/download")
async def download_agent_records(agent_id: str, ids: list[str]) -> Response:
    """Download records for a specific agent in eval format."""
    logger.info("Received download request", agent_id=agent_id, count=len(ids))

    config = get_agent_config(agent_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    if not ids:
        raise HTTPException(status_code=400, detail="No IDs provided")

    try:
        container = await cosmos_db_service.ensure_container(config.container_name)

        conversations = []

        for record_id in ids:
            try:
                item = container.read_item(item=record_id, partition_key=record_id)

                # Extract fields
                document_id = item.get("id", "")
                instructions = item.get("agent_instructions", "")
                prompt = item.get("prompt", "")
                response = item.get("response", "")
                scenario_name = config.scenario_name or config.agent_name

                # Build eval format record
                # agent_prompt is a literal template string - eval framework will substitute values
                record = {
                    "Id": document_id,
                    "instructions": instructions,
                    "prompt": prompt,
                    "agent_prompt": "[SYSTEM]\n{{instructions}}\n\n[USER]\n{{prompt}}",
                    "agent_response": response,
                    "scenario_name": scenario_name
                }
                conversations.append(record)

            except Exception as e:
                logger.warning("Failed to retrieve record", record_id=record_id, error=str(e))
                continue

        result = {"conversations": conversations}
        json_str = json.dumps(result, indent=2)

        logger.info("Returning download data in eval format", record_count=len(conversations))
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{agent_id}_evals.json"'}
        )

    except Exception as e:
        logger.error("Error downloading records", agent_id=agent_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error downloading: {str(e)}")

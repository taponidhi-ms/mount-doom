"""
Routes for the Workflows API.

This module provides endpoints for listing workflows and their configurations.
The actual workflow execution routes remain in their respective modules.
"""

from fastapi import APIRouter, HTTPException
import structlog

from .config import get_all_workflows, get_workflow_config
from .models import WorkflowInfo, WorkflowAgentInfo, WorkflowListResponse

logger = structlog.get_logger()

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("/list", response_model=WorkflowListResponse)
async def list_workflows():
    """
    List all available workflows with their configurations.
    
    Returns workflow metadata including agents and their instructions.
    """
    logger.info("Listing all workflows")
    
    workflows_dict = get_all_workflows()
    workflows = [
        WorkflowInfo(
            workflow_id=config.workflow_id,
            display_name=config.display_name,
            description=config.description,
            agents=[
                WorkflowAgentInfo(
                    agent_id=agent.agent_id,
                    agent_name=agent.agent_name,
                    display_name=agent.display_name,
                    role=agent.role,
                    instructions=agent.instructions
                )
                for agent in config.agents
            ],
            route_prefix=config.route_prefix
        )
        for config in workflows_dict.values()
    ]
    
    logger.info("Returning workflow list", count=len(workflows))
    return WorkflowListResponse(workflows=workflows)


@router.get("/{workflow_id}", response_model=WorkflowInfo)
async def get_workflow(workflow_id: str):
    """
    Get details of a specific workflow by ID.
    
    Returns workflow metadata including all agent instructions.
    """
    logger.info("Getting workflow details", workflow_id=workflow_id)
    
    config = get_workflow_config(workflow_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
    
    return WorkflowInfo(
        workflow_id=config.workflow_id,
        display_name=config.display_name,
        description=config.description,
        agents=[
            WorkflowAgentInfo(
                agent_id=agent.agent_id,
                agent_name=agent.agent_name,
                display_name=agent.display_name,
                role=agent.role,
                instructions=agent.instructions
            )
            for agent in config.agents
        ],
        route_prefix=config.route_prefix
    )

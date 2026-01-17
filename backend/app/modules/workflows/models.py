"""
Models for the Workflows API.
"""

from pydantic import BaseModel
from typing import List


class WorkflowAgentInfo(BaseModel):
    """Information about an agent used in a workflow."""
    agent_id: str
    agent_name: str
    display_name: str
    role: str
    instructions: str


class WorkflowInfo(BaseModel):
    """Information about a workflow."""
    workflow_id: str
    display_name: str
    description: str
    agents: List[WorkflowAgentInfo]
    route_prefix: str


class WorkflowListResponse(BaseModel):
    """Response for listing all workflows."""
    workflows: List[WorkflowInfo]

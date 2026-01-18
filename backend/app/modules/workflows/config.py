"""
Workflow Configuration Registry.

This module maintains configurations for all workflows in the system.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import instructions from centralized agents instructions module
from app.modules.agents.instructions import C1_AGENT_INSTRUCTIONS, C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS


@dataclass
class WorkflowAgentConfig:
    """Configuration for an agent used in a workflow."""
    agent_id: str
    agent_name: str
    display_name: str
    role: str  # e.g., "Customer Service Representative", "Customer"
    instructions: str


@dataclass
class WorkflowConfig:
    """Configuration for a workflow."""
    workflow_id: str
    display_name: str
    description: str
    agents: List[WorkflowAgentConfig]
    route_prefix: str  # e.g., "/conversation-simulation"


# Workflow Registry
WORKFLOW_REGISTRY: Dict[str, WorkflowConfig] = {
    "conversation_simulation": WorkflowConfig(
        workflow_id="conversation_simulation",
        display_name="Conversation Simulation",
        description="Simulate multi-turn conversations between C1 (customer service representative) and C2 (customer) agents. Configure customer intent, sentiment, and subject to generate realistic conversation flows.",
        agents=[
            WorkflowAgentConfig(
                agent_id="c1_message_generator",
                agent_name="C1MessageGeneratorAgent",
                display_name="C1 Message Generator",
                role="Customer Service Representative",
                instructions=C1_AGENT_INSTRUCTIONS,
            ),
            WorkflowAgentConfig(
                agent_id="c2_message_generator",
                agent_name="C2MessageGeneratorAgent",
                display_name="C2 Message Generator",
                role="Customer",
                instructions=C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS,
            ),
        ],
        route_prefix="/conversation-simulation",
    ),
}


def get_workflow_config(workflow_id: str) -> Optional[WorkflowConfig]:
    """Get workflow configuration by ID."""
    return WORKFLOW_REGISTRY.get(workflow_id)


def get_all_workflows() -> Dict[str, WorkflowConfig]:
    """Get all workflow configurations."""
    return WORKFLOW_REGISTRY


def list_workflow_ids() -> List[str]:
    """Get list of all workflow IDs."""
    return list(WORKFLOW_REGISTRY.keys())

"""
Instruction sets for AI agents.

This module contains the instruction sets for all agents used in the application.
Each agent has a fixed name and a constant instruction set that defines its behavior.
"""

from .c1_agent import C1_AGENT_NAME, C1_AGENT_INSTRUCTIONS
from .c2_agent import C2_AGENT_NAME, C2_AGENT_INSTRUCTIONS
from .orchestrator_agent import ORCHESTRATOR_AGENT_NAME, ORCHESTRATOR_AGENT_INSTRUCTIONS
from .persona_agent import PERSONA_AGENT_NAME, PERSONA_AGENT_INSTRUCTIONS
from .prompt_validator_agent import PROMPT_VALIDATOR_AGENT_NAME, PROMPT_VALIDATOR_AGENT_INSTRUCTIONS

__all__ = [
    "C1_AGENT_NAME",
    "C1_AGENT_INSTRUCTIONS",
    "C2_AGENT_NAME",
    "C2_AGENT_INSTRUCTIONS",
    "ORCHESTRATOR_AGENT_NAME",
    "ORCHESTRATOR_AGENT_INSTRUCTIONS",
    "PERSONA_AGENT_NAME",
    "PERSONA_AGENT_INSTRUCTIONS",
    "PROMPT_VALIDATOR_AGENT_NAME",
    "PROMPT_VALIDATOR_AGENT_INSTRUCTIONS",
]

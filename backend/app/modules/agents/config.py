"""
Agent Configuration Registry.

This module dynamically loads all agent configurations from the configs/ directory.
Each agent is defined in its own config file with name, description, instructions, and container.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import importlib
import pkgutil
from pathlib import Path
import structlog

logger = structlog.get_logger()


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    agent_id: str
    agent_name: str
    display_name: str
    description: str
    instructions: str
    container_name: str
    scenario_name: str = ""  # Scenario name for eval downloads (defaults to agent_name if not set)
    input_field: str = "prompt"  # UI field identifier (used for frontend only, DB always uses "prompt")
    input_label: str = "Prompt"  # Display label for the input field
    input_placeholder: str = "Enter your prompt..."  # Placeholder for input
    sample_inputs: List[Dict[str, Any]] = field(default_factory=list)  # Sample inputs with category and tags


def load_agent_registry() -> Dict[str, AgentConfig]:
    """
    Dynamically load all agent configurations from configs/ directory.

    Discovers and imports all *_config.py modules from the configs/ directory,
    extracting the AGENT_CONFIG variable from each to build the registry.

    Returns:
        Dictionary mapping agent_id to AgentConfig
    """
    registry = {}
    configs_dir = Path(__file__).parent / "configs"

    logger.info("Loading agent configurations from configs directory",
                configs_dir=str(configs_dir))

    # Import all config modules from configs/ directory
    try:
        for module_info in pkgutil.iter_modules([str(configs_dir)]):
            if module_info.name.endswith("_config"):
                module_path = f"app.modules.agents.configs.{module_info.name}"

                try:
                    module = importlib.import_module(module_path)

                    # Each config module should have an AGENT_CONFIG variable
                    if hasattr(module, "AGENT_CONFIG"):
                        config = module.AGENT_CONFIG
                        registry[config.agent_id] = config
                        logger.debug("Loaded agent configuration",
                                   agent_id=config.agent_id,
                                   agent_name=config.agent_name,
                                   module=module_info.name)
                    else:
                        logger.warning("Config module missing AGENT_CONFIG variable",
                                     module=module_info.name)
                except Exception as e:
                    logger.error("Failed to load agent config module",
                               module=module_info.name,
                               error=str(e),
                               exc_info=True)
    except Exception as e:
        logger.error("Failed to discover agent config modules",
                   error=str(e),
                   exc_info=True)
        raise

    logger.info("Agent registry loaded successfully",
               total_agents=len(registry),
               agent_ids=list(registry.keys()))

    return registry


# Load all agent configurations dynamically
AGENT_REGISTRY: Dict[str, AgentConfig] = load_agent_registry()


def get_agent_config(agent_id: str) -> Optional[AgentConfig]:
    """Get agent configuration by ID."""
    return AGENT_REGISTRY.get(agent_id)


def get_all_agents() -> Dict[str, AgentConfig]:
    """Get all agent configurations."""
    return AGENT_REGISTRY


def list_agent_ids() -> List[str]:
    """Get list of all agent IDs."""
    return list(AGENT_REGISTRY.keys())

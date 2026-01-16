"""Service for persona distribution generation use case using shared base."""

from typing import Callable
import structlog

from app.modules.shared.base_single_agent_service import BaseSingleAgentService
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from .agents import create_persona_distribution_agent

logger = structlog.get_logger()


class PersonaDistributionService(BaseSingleAgentService):
    """Service for generating persona distributions using the Persona Distribution Generator Agent."""

    def get_agent_creator(self) -> Callable:
        """Return the agent creation function."""
        return create_persona_distribution_agent
    
    def get_container_name(self) -> str:
        """Return the Cosmos DB container name."""
        return cosmos_db_service.PERSONA_DISTRIBUTION_CONTAINER
    
    def get_use_case_name(self) -> str:
        """Return a human-readable name for logging."""
        return "Persona Distribution"
    
    async def generate_persona_distribution(self, prompt: str):
        """
        Generate a persona distribution from the given prompt.
        
        This method wraps the base generate() method for backward compatibility.
        """
        return await self.generate(prompt, parse_json=True)


# Singleton instance
persona_distribution_service = PersonaDistributionService()

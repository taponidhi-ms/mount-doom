"""Service for conversation simulation use case."""

from datetime import datetime
import structlog
import hashlib
import json
from typing import List, Optional

from app.services.azure_ai_service import azure_ai_service
from app.models.schemas import ConversationMessage, AgentDetails
from app.instruction_sets import (
    C1_AGENT_NAME, C1_AGENT_INSTRUCTIONS,
    C2_AGENT_NAME, C2_AGENT_INSTRUCTIONS,
    ORCHESTRATOR_AGENT_NAME, ORCHESTRATOR_AGENT_INSTRUCTIONS
)

logger = structlog.get_logger()


class ConversationSimulationService:
    """Service for simulating multi-agent conversations."""

    def __init__(self):
        self.c1_agent_name = C1_AGENT_NAME
        self.c1_instructions = C1_AGENT_INSTRUCTIONS
        self.c2_agent_name = C2_AGENT_NAME
        self.c2_instructions = C2_AGENT_INSTRUCTIONS
        self.orchestrator_agent_name = ORCHESTRATOR_AGENT_NAME
        self.orchestrator_instructions = ORCHESTRATOR_AGENT_INSTRUCTIONS
        self.model_deployment = "gpt-4"

    async def simulate_conversation(
            self,
            simulation_prompt: str,
            conversation_properties: dict,
            max_turns: int
    ) -> dict:
        """
        Simulate a multi-agent conversation.
        
        Uses a shared conversation where:
        1. C1 agent (service rep) generates a response
        2. Orchestrator checks if conversation should continue
        3. C2 agent (customer) generates a response
        4. Orchestrator checks again if conversation should end
        This repeats until max_turns or completion status is reached.
        
        Args:
            simulation_prompt: Not used directly - kept for compatibility
            conversation_properties: Dict with CustomerIntent, CustomerSentiment, ConversationSubject
            max_turns: Maximum number of conversation turns
            
        Returns:
            Dictionary with:
            - conversation_history: List of ConversationMessage objects
            - conversation_status: Final status (Ongoing/Completed)
            - total_tokens_used: Total tokens across all agents
            - total_time_taken_ms: Total time for simulation
            - start_time: Simulation start time
            - end_time: Simulation end time
            - c1_agent_details: Details of C1 agent
            - c2_agent_details: Details of C2 agent
            - orchestrator_agent_details: Details of orchestrator agent
        """
        try:
            start_time = datetime.utcnow()
            logger.info("Starting conversation simulation", max_turns=max_turns)

            # Create agents
            c1_agent = azure_ai_service.create_agent(
                agent_name=self.c1_agent_name,
                instructions=self.c1_instructions,
                model_deployment_name=self.model_deployment
            )

            c2_agent = azure_ai_service.create_agent(
                agent_name=self.c2_agent_name,
                instructions=self.c2_instructions,
                model_deployment_name=self.model_deployment
            )

            orchestrator_agent = azure_ai_service.create_agent(
                agent_name=self.orchestrator_agent_name,
                instructions=self.orchestrator_instructions,
                model_deployment_name=self.model_deployment
            )

            # Generate agent version hashes
            c1_hash = hashlib.sha256(c1_agent.instructions.encode()).hexdigest()[:8]
            c2_hash = hashlib.sha256(c2_agent.instructions.encode()).hexdigest()[:8]
            orch_hash = hashlib.sha256(orchestrator_agent.instructions.encode()).hexdigest()[:8]

            c1_agent_details = AgentDetails(
                agent_name=self.c1_agent_name,
                agent_version=f"v{c1_hash}",
                instructions=self.c1_instructions,
                model_deployment_name=self.model_deployment,
                timestamp=datetime.utcnow()
            )

            c2_agent_details = AgentDetails(
                agent_name=self.c2_agent_name,
                agent_version=f"v{c2_hash}",
                instructions=self.c2_instructions,
                model_deployment_name=self.model_deployment,
                timestamp=datetime.utcnow()
            )

            orchestrator_agent_details = AgentDetails(
                agent_name=self.orchestrator_agent_name,
                agent_version=f"v{orch_hash}",
                instructions=self.orchestrator_instructions,
                model_deployment_name=self.model_deployment,
                timestamp=datetime.utcnow()
            )

            # Create shared conversation for multi-agent workflow
            shared_conversation = azure_ai_service.openai_client.conversations.create()
            shared_conversation_id = shared_conversation.id

            logger.info("Created shared conversation", conversation_id=shared_conversation_id)

            # Initialize conversation tracking
            conversation_history: List[ConversationMessage] = []
            conversation_status = "Ongoing"
            total_tokens = 0

            # Convert conversation properties for prompt formatting
            conv_props_str = json.dumps(conversation_properties, indent=2)

            # Simulate conversation turns
            for turn in range(max_turns):
                logger.info("Starting conversation turn", turn=turn + 1, max_turns=max_turns)

                # C1 Agent turn (Customer Service Representative)
                c1_turn_result = await self._invoke_c1_agent(
                    c1_agent=c1_agent,
                    shared_conversation_id=shared_conversation_id,
                    conversation_history=conversation_history,
                    conversation_properties=conv_props_str,
                    c1_agent_details=c1_agent_details
                )

                if c1_turn_result:
                    conversation_history.append(c1_turn_result['message'])
                    total_tokens += c1_turn_result.get('tokens', 0)

                # Check conversation status with orchestrator
                orch_result = await self._invoke_orchestrator_agent(
                    orchestrator_agent=orchestrator_agent,
                    shared_conversation_id=shared_conversation_id,
                    conversation_history=conversation_history,
                    conversation_properties=conv_props_str
                )

                if orch_result:
                    total_tokens += orch_result.get('tokens', 0)
                    if orch_result.get('status') == "Completed":
                        conversation_status = "Completed"
                        break

                # C2 Agent turn (Customer)
                c2_turn_result = await self._invoke_c2_agent(
                    c2_agent=c2_agent,
                    shared_conversation_id=shared_conversation_id,
                    conversation_history=conversation_history,
                    conversation_properties=conv_props_str,
                    c2_agent_details=c2_agent_details
                )

                if c2_turn_result:
                    conversation_history.append(c2_turn_result['message'])
                    total_tokens += c2_turn_result.get('tokens', 0)

                # Check conversation status again with orchestrator
                orch_result_2 = await self._invoke_orchestrator_agent(
                    orchestrator_agent=orchestrator_agent,
                    shared_conversation_id=shared_conversation_id,
                    conversation_history=conversation_history,
                    conversation_properties=conv_props_str
                )

                if orch_result_2:
                    total_tokens += orch_result_2.get('tokens', 0)
                    if orch_result_2.get('status') == "Completed":
                        conversation_status = "Completed"
                        break

            end_time = datetime.utcnow()
            total_time_ms = (end_time - start_time).total_seconds() * 1000

            logger.info("Conversation simulation completed",
                        turns=len(conversation_history),
                        status=conversation_status,
                        total_tokens=total_tokens,
                        total_time_ms=total_time_ms)

            return {
                "conversation_history": conversation_history,
                "conversation_status": conversation_status,
                "total_tokens_used": total_tokens,
                "total_time_taken_ms": total_time_ms,
                "start_time": start_time,
                "end_time": end_time,
                "c1_agent_details": c1_agent_details,
                "c2_agent_details": c2_agent_details,
                "orchestrator_agent_details": orchestrator_agent_details
            }

        except Exception as e:
            logger.error(f"Error simulating conversation: {e}", error=str(e))
            raise

    async def _invoke_c1_agent(
            self,
            c1_agent,
            shared_conversation_id: str,
            conversation_history: List[ConversationMessage],
            conversation_properties: str,
            c1_agent_details: AgentDetails
    ) -> Optional[dict]:
        """Invoke C1 agent and return message with tokens."""
        try:
            turn_start_time = datetime.utcnow()
            messages_str = json.dumps([{
                "role": msg.role,
                "message": msg.message
            } for msg in conversation_history], indent=2)

            c1_prompt = f"""Generate a next message as an Agent for the following ongoing conversation:
ConversationProperties: {conversation_properties}
messages: {messages_str}"""

            # Add user message to shared conversation
            azure_ai_service.openai_client.conversations.items.create(
                conversation_id=shared_conversation_id,
                items=[{"type": "message", "role": "user", "content": c1_prompt}]
            )

            # Create response using C1 agent
            c1_response = azure_ai_service.openai_client.responses.create(
                conversation=shared_conversation_id,
                extra_body={"agent": {"name": c1_agent.agent_version_object.name, "type": "agent_reference"}},
                input=""
            )

            response_text = c1_response.output_text
            tokens_used = 0
            if hasattr(c1_response, 'usage') and c1_response.usage:
                tokens_used = c1_response.usage.total_tokens

            turn_end_time = datetime.utcnow()
            turn_time_ms = (turn_end_time - turn_start_time).total_seconds() * 1000

            message = ConversationMessage(
                role="C1Agent",
                agent_name=self.c1_agent_name,
                agent_version=c1_agent_details.agent_version,
                message=response_text,
                tokens_used=tokens_used,
                time_taken_ms=turn_time_ms,
                timestamp=turn_end_time
            )

            logger.info("C1 agent invoked successfully",
                        conversation_id=shared_conversation_id,
                        tokens=tokens_used)

            return {"message": message, "tokens": tokens_used}

        except Exception as e:
            logger.error(f"Error invoking C1 agent: {e}", error=str(e))
            raise

    async def _invoke_c2_agent(
            self,
            c2_agent,
            shared_conversation_id: str,
            conversation_history: List[ConversationMessage],
            conversation_properties: str,
            c2_agent_details: AgentDetails
    ) -> Optional[dict]:
        """Invoke C2 agent and return message with tokens."""
        try:
            turn_start_time = datetime.utcnow()
            messages_str = json.dumps([{
                "role": msg.role,
                "message": msg.message
            } for msg in conversation_history], indent=2)

            c2_prompt = f"""Generate a next message as a customer for the following ongoing conversation:
ConversationProperties: {conversation_properties}
messages: {messages_str}"""

            # Add user message to shared conversation
            azure_ai_service.openai_client.conversations.items.create(
                conversation_id=shared_conversation_id,
                items=[{"type": "message", "role": "user", "content": c2_prompt}]
            )

            # Create response using C2 agent
            c2_response = azure_ai_service.openai_client.responses.create(
                conversation=shared_conversation_id,
                extra_body={"agent": {"name": c2_agent.agent_version_object.name, "type": "agent_reference"}},
                input=""
            )

            response_text = c2_response.output_text
            tokens_used = 0
            if hasattr(c2_response, 'usage') and c2_response.usage:
                tokens_used = c2_response.usage.total_tokens

            turn_end_time = datetime.utcnow()
            turn_time_ms = (turn_end_time - turn_start_time).total_seconds() * 1000

            message = ConversationMessage(
                role="C2Agent",
                agent_name=self.c2_agent_name,
                agent_version=c2_agent_details.agent_version,
                message=response_text,
                tokens_used=tokens_used,
                time_taken_ms=turn_time_ms,
                timestamp=turn_end_time
            )

            logger.info("C2 agent invoked successfully",
                        conversation_id=shared_conversation_id,
                        tokens=tokens_used)

            return {"message": message, "tokens": tokens_used}

        except Exception as e:
            logger.error(f"Error invoking C2 agent: {e}", error=str(e))
            raise

    async def _invoke_orchestrator_agent(
            self,
            orchestrator_agent,
            shared_conversation_id: str,
            conversation_history: List[ConversationMessage],
            conversation_properties: str
    ) -> Optional[dict]:
        """Invoke orchestrator agent to check conversation status."""
        try:
            messages_str = json.dumps([{
                "role": msg.role,
                "message": msg.message
            } for msg in conversation_history], indent=2)

            orch_prompt = f"ConversationProperties: {conversation_properties}\nmessages: {messages_str}"

            # Add user message to shared conversation
            azure_ai_service.openai_client.conversations.items.create(
                conversation_id=shared_conversation_id,
                items=[{"type": "message", "role": "user", "content": orch_prompt}]
            )

            # Create response using orchestrator agent
            orch_response = azure_ai_service.openai_client.responses.create(
                conversation=shared_conversation_id,
                extra_body={"agent": {"name": orchestrator_agent.agent_version_object.name, "type": "agent_reference"}},
                input=""
            )

            response_text = orch_response.output_text
            tokens_used = 0
            if hasattr(orch_response, 'usage') and orch_response.usage:
                tokens_used = orch_response.usage.total_tokens

            # Parse orchestrator response for status
            status = "Ongoing"
            try:
                orch_data = json.loads(response_text)
                status = orch_data.get("ConversationStatus", "Ongoing")
            except json.JSONDecodeError:
                if "Completed" in response_text:
                    status = "Completed"

            logger.info("Orchestrator agent invoked",
                        conversation_id=shared_conversation_id,
                        status=status,
                        tokens=tokens_used)

            return {"status": status, "tokens": tokens_used}

        except Exception as e:
            logger.error(f"Error invoking orchestrator agent: {e}", error=str(e))
            raise


# Singleton instance
conversation_simulation_service = ConversationSimulationService()

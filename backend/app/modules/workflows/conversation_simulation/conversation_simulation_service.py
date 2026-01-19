"""Service for conversation simulation workflow."""

from datetime import datetime, timezone
import structlog
import json
import time
import uuid
from typing import List, Optional, Dict, Any

from app.infrastructure.ai.azure_ai_service import azure_ai_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from app.models.shared import AgentDetails
from .models import ConversationMessage, ConversationSimulationResult, ConversationSimulationDocument
from .agents import (
    create_c1_agent, 
    create_c2_agent, 
    C1_MESSAGE_GENERATOR_AGENT_NAME, 
    C2_MESSAGE_GENERATOR_AGENT_NAME
)

logger = structlog.get_logger()


class ConversationSimulationService:
    """Service for simulating multi-agent conversations."""

    def __init__(self):
        pass

    async def _generate_c2_message(self, input_text: str) -> str:
        """Generate a C2 (customer) message using stateless invocation."""
        openai_client = azure_ai_service.openai_client

        # Create a fresh conversation for C2
        c2_conversation = openai_client.conversations.create(
            items=[{"type": "message", "role": "user", "content": input_text}]
        )

        # Get response from C2 agent
        c2_response = openai_client.responses.create(
            conversation=c2_conversation.id,
            extra_body={"agent": {"name": C2_MESSAGE_GENERATOR_AGENT_NAME, "type": "agent_reference"}},
            input=""
        )

        c2_text = c2_response.output_text

        # Delete C2 conversation to clean up resources
        try:
            openai_client.conversations.delete(conversation_id=c2_conversation.id)
            logger.debug("C2 conversation deleted", conversation_id=c2_conversation.id)
        except Exception as delete_error:
            logger.warning("Failed to delete C2 conversation",
                         conversation_id=c2_conversation.id,
                         error=str(delete_error))

        return c2_text

    async def simulate_conversation(
            self,
            conversation_properties: dict,
            max_turns: int
    ) -> ConversationSimulationResult:
        """
        Simulate a multi-agent conversation.
        """
        start_time = datetime.now(timezone.utc)
        start_ms = time.time() * 1000

        logger.info("="*60)
        logger.info("Starting conversation simulation", 
                   max_turns=max_turns,
                   customer_intent=conversation_properties.get('CustomerIntent'),
                   customer_sentiment=conversation_properties.get('CustomerSentiment'),
                   conversation_subject=conversation_properties.get('ConversationSubject'))
        logger.info("="*60)

        # Create C1 agent and C2 agent to get their details
        c1_agent = create_c1_agent()
        c2_agent = create_c2_agent()
        
        logger.info("Agents created", c1=C1_MESSAGE_GENERATOR_AGENT_NAME, c2=C2_MESSAGE_GENERATOR_AGENT_NAME)

        # Initialize C1 Conversation
        openai_client = azure_ai_service.openai_client
        c1_conversation = openai_client.conversations.create(
            items=[{"type": "message", "role": "user", "content": "Hello"}]
        )
        logger.info("C1 Conversation created", conversation_id=c1_conversation.id)

        conversation_history: List[ConversationMessage] = []
        conversation_status = "Ongoing"
        
        # Add initial "Hello" to history as C2 (Customer) message
        conversation_history.append(ConversationMessage(
            agent_name=C2_MESSAGE_GENERATOR_AGENT_NAME,
            message="Hello",
            timestamp=datetime.now(timezone.utc)
        ))

        turn_count = 0
        while turn_count < max_turns and conversation_status == "Ongoing":
            logger.debug(f"Turn {turn_count + 1} starting")

            # --- C1 (Agent) Turn ---
            logger.debug("Creating C1 response...")
            c1_response = openai_client.responses.create(
                conversation=c1_conversation.id,
                extra_body={"agent": {"name": C1_MESSAGE_GENERATOR_AGENT_NAME, "type": "agent_reference"}},
                input="",
            )
            c1_text = c1_response.output_text
            logger.info("C1 Response", text=c1_text)

            conversation_history.append(ConversationMessage(
                agent_name=C1_MESSAGE_GENERATOR_AGENT_NAME,
                message=c1_text,
                timestamp=datetime.now(timezone.utc)
            ))

            # Check termination by C1
            if "end this call now" in c1_text.lower() or "transfer this call to my supervisor" in c1_text.lower():
                conversation_status = "Completed"
                break

            # --- C2 (Customer) Turn ---
            # Construct C2 input
            mapped_msgs = []
            for i, msg in enumerate(conversation_history):
                role = "agent" if msg.agent_name == C1_MESSAGE_GENERATOR_AGENT_NAME else "customer"
                mapped_msgs.append({
                    role: msg.message,
                    "Id": i + 1
                })
            
            c2_payload = {
                "Properties": conversation_properties,
                "messages": mapped_msgs
            }
            c2_input_text = f"Ongoing transcript: {json.dumps(c2_payload)}"
            
            logger.debug("Creating C2 response...", input_preview=c2_input_text[:100])
            c2_text = await self._generate_c2_message(c2_input_text)
            logger.info("C2 Response", text=c2_text)

            conversation_history.append(ConversationMessage(
                agent_name=C2_MESSAGE_GENERATOR_AGENT_NAME,
                message=c2_text,
                timestamp=datetime.now(timezone.utc)
            ))

            # Add C2 generated message to C1's conversation so C1 sees it next time
            openai_client.conversations.items.create(
                conversation_id=c1_conversation.id,
                items=[{"type": "message", "role": "user", "content": c2_text}],
            )

            turn_count += 1
            if turn_count >= max_turns:
                conversation_status = "MaxTurnsReached"

        end_ms = time.time() * 1000
        total_time_taken_ms = end_ms - start_ms

        result = ConversationSimulationResult(
            conversation_history=conversation_history,
            conversation_status=conversation_status,
            total_time_taken_ms=total_time_taken_ms,
            start_time=start_time,
            end_time=datetime.now(timezone.utc),
            c1_agent_details=c1_agent.agent_details,
            c2_agent_details=c2_agent.agent_details,
            conversation_id=c1_conversation.id
        )

        # Delete C1 conversation to clean up resources
        try:
            logger.info("Deleting C1 conversation", conversation_id=c1_conversation.id)
            openai_client.conversations.delete(conversation_id=c1_conversation.id)
            logger.info("C1 conversation deleted successfully", conversation_id=c1_conversation.id)
        except Exception as delete_error:
            logger.warning("Failed to delete C1 conversation",
                         conversation_id=c1_conversation.id,
                         error=str(delete_error))

        logger.info("="*60)
        logger.info("Conversation simulation completed",
                   conversation_id=c1_conversation.id,
                   status=conversation_status,
                   total_turns=turn_count)
        logger.info("="*60)

        return result

    async def save_to_database(
            self,
            conversation_properties: dict,
            conversation_history: List[ConversationMessage],
            conversation_status: str,
            total_time_taken_ms: float,
            c1_agent_details: dict,
            c2_agent_details: dict,
            conversation_id: str
    ):
        """Save simulation result to Cosmos DB."""
        # Generate random UUID for document ID
        document_id = str(uuid.uuid4())

        # Parse agent details
        c1_agent = AgentDetails(**c1_agent_details)
        c2_agent = AgentDetails(**c2_agent_details)

        # Build document with flattened agent details
        document = {
            "id": document_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "conversation_properties": conversation_properties,
            "conversation_history": [msg.model_dump(mode='json') for msg in conversation_history],
            "conversation_status": conversation_status,
            "total_time_taken_ms": total_time_taken_ms,
            "total_tokens_used": None,
            # Flattened C1 agent details
            "c1_agent_name": c1_agent.agent_name,
            "c1_agent_version": c1_agent.agent_version,
            "c1_agent_instructions": c1_agent.instructions,
            "c1_agent_model": c1_agent.model_deployment_name,
            "c1_agent_created_at": c1_agent.created_at.isoformat() if isinstance(c1_agent.created_at, datetime) else c1_agent.created_at,
            # Flattened C2 agent details
            "c2_agent_name": c2_agent.agent_name,
            "c2_agent_version": c2_agent.agent_version,
            "c2_agent_instructions": c2_agent.instructions,
            "c2_agent_model": c2_agent.model_deployment_name,
            "c2_agent_created_at": c2_agent.created_at.isoformat() if isinstance(c2_agent.created_at, datetime) else c2_agent.created_at,
        }

        await cosmos_db_service.save_document(
            container_name=cosmos_db_service.CONVERSATION_SIMULATION_CONTAINER,
            document=document
        )
        logger.info("Saved simulation result to database",
                   document_id=document_id,
                   conversation_id=conversation_id)


conversation_simulation_service = ConversationSimulationService()

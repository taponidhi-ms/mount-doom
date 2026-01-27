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
from app.modules.agents.agents_service import unified_agents_service
from app.modules.agents.config import get_agent_config
from .models import ConversationMessage, ConversationSimulationResult, ConversationSimulationDocument
from .agents import (
    create_c2_agent,
    C1_MESSAGE_GENERATOR_AGENT_NAME,
    C2_MESSAGE_GENERATOR_AGENT_NAME
)

logger = structlog.get_logger()


class ConversationSimulationService:
    """Service for simulating multi-agent conversations."""

    def __init__(self):
        pass

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

        # Get agent configurations for metadata
        c1_config = get_agent_config("c1_message_generation")
        c2_config = get_agent_config("c2_message_generation")

        # Create persistent C1 conversation via agents_service
        # Empty initial_message creates conversation without any initial items
        # C1 will greet first when invoked on the empty conversation
        logger.info("Creating persistent C1 conversation via agents_service")
        c1_conversation_result = await unified_agents_service.create_conversation(
            agent_id="c1_message_generation",
            initial_message=""  # Empty = no initial message, C1 greets first
        )
        conversation_id = c1_conversation_result.conversation_id
        c1_agent_details = c1_conversation_result.agent_details
        c1_agent_name = c1_conversation_result.agent_name

        # Get C2 agent details (create temporarily to get details)
        c2_agent = create_c2_agent()
        c2_agent_details = c2_agent.agent_details

        logger.info("Agents configured",
                   c1_agent=c1_agent_name,
                   c2_agent=C2_MESSAGE_GENERATOR_AGENT_NAME,
                   conversation_id=conversation_id)

        # Start with empty conversation history - C1 will greet first
        conversation_history: List[ConversationMessage] = []
        conversation_status = "Ongoing"

        turn_count = 0
        while turn_count < max_turns and conversation_status == "Ongoing":
            logger.debug(f"Turn {turn_count + 1} starting")

            # --- C1 (Agent) Turn ---
            logger.debug("Creating C1 response via agents_service...")

            # On first turn (empty conversation), provide a prompt to trigger greeting
            # On subsequent turns, empty input is fine as conversation has history
            is_first_turn = len(conversation_history) == 0
            input_prompt = "Begin the conversation" if is_first_turn else ""

            c1_result = await unified_agents_service.invoke_agent_on_conversation(
                agent_id="c1_message_generation",
                conversation_id=conversation_id,
                agent_name=c1_agent_name,
                input_message=input_prompt
            )
            c1_text = c1_result.response_text
            c1_tokens = c1_result.tokens_used
            logger.info("C1 Response", text=c1_text, tokens_used=c1_tokens)

            conversation_history.append(ConversationMessage(
                role="agent",
                content=c1_text,
                tokens_used=c1_tokens,
                timestamp=datetime.now(timezone.utc),
                conversation_id=conversation_id
            ))

            # Check termination by C1
            if "end this call now" in c1_text.lower() or "transfer this call to my supervisor" in c1_text.lower():
                conversation_status = "Completed"
                break

            # --- C2 (Customer) Turn ---
            # Construct C2 input with new format
            mapped_msgs = []
            for i, msg in enumerate(conversation_history):
                # Capitalize role to match expected format (Agent/Customer)
                role_key = "Agent" if msg.role == "agent" else "Customer"
                mapped_msgs.append({
                    role_key: msg.content,
                    "Id": i + 1
                })

            # Build prompt in the required format
            conversation_props_str = json.dumps({
                "CustomerIntent": conversation_properties.get("CustomerIntent"),
                "CustomerSentiment": conversation_properties.get("CustomerSentiment"),
                "ConversationSubject": conversation_properties.get("ConversationSubject")
            })
            messages_str = json.dumps(mapped_msgs)
            c2_input_text = f"Generate a next message as a customer for the following ongoing conversation where ConversationProperties: {conversation_props_str} Messages: {messages_str}"

            logger.debug("Creating C2 response...", input_preview=c2_input_text[:100])

            # Use invoke_agent directly with persist=True to save C2 conversations
            c2_result = await unified_agents_service.invoke_agent(
                agent_id="c2_message_generation",
                input_text=c2_input_text,
                persist=True
            )

            c2_text = c2_result.response_text
            c2_tokens = c2_result.tokens_used
            c2_conversation_id = c2_result.conversation_id
            logger.info("C2 Response", text=c2_text, tokens_used=c2_tokens, conversation_id=c2_conversation_id)

            conversation_history.append(ConversationMessage(
                role="customer",
                content=c2_text,
                tokens_used=c2_tokens,
                timestamp=datetime.now(timezone.utc),
                conversation_id=c2_conversation_id  # Track C2's conversation_id
            ))

            # Add C2 message to C1's conversation via agents_service
            await unified_agents_service.add_message_to_conversation(
                conversation_id=conversation_id,
                message=c2_text,
                role="user"
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
            agent_details=c1_agent_details,  # Only C1 agent details
            conversation_id=conversation_id
        )

        # Do NOT auto-delete conversation - only delete when user explicitly deletes from Cosmos DB

        logger.info("="*60)
        logger.info("Conversation simulation completed",
                   conversation_id=conversation_id,
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
            agent_details: dict,
            conversation_id: str
    ):
        """Save simulation result to Cosmos DB."""
        # Generate random UUID for document ID
        document_id = str(uuid.uuid4())

        # Build document with flattened agent details (C1 only)
        # agent_details is already a dict with agent_name, agent_version, etc.
        created_at = agent_details.get("created_at", "")
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()

        document = {
            "id": document_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "conversation_properties": conversation_properties,
            "conversation_history": [msg.model_dump(mode='json') for msg in conversation_history],
            "conversation_status": conversation_status,
            "total_time_taken_ms": total_time_taken_ms,
            # Flattened primary agent (C1) details at root
            "agent_name": agent_details.get("agent_name"),
            "agent_version": agent_details.get("agent_version"),
            "agent_instructions": agent_details.get("instructions"),
            "agent_model": agent_details.get("model_deployment_name"),
            "agent_created_at": created_at,
        }

        await cosmos_db_service.save_document(
            container_name=cosmos_db_service.MULTI_TURN_CONVERSATIONS_CONTAINER,
            document=document
        )
        logger.info("Saved multi-turn conversation to database",
                   document_id=document_id,
                   conversation_id=conversation_id)


conversation_simulation_service = ConversationSimulationService()

"""Service for conversation simulation use case."""

from datetime import datetime
import structlog
import json
from typing import List, Optional, Dict, Any

from azure.ai.projects.models import WorkflowAgentDefinition, AgentReference, ResponseStreamEventType
from app.infrastructure.ai.azure_ai_service import azure_ai_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from app.models.shared import AgentDetails
from .models import ConversationMessage, ConversationSimulationResult, ConversationSimulationDocument
from app.core.config import settings
from .agents import create_c1_agent, create_c2_agent, C1_AGENT_NAME, C2_AGENT_NAME

logger = structlog.get_logger()


class ConversationSimulationService:
    """Service for simulating multi-agent conversations."""

    C1_AGENT_NAME = C1_AGENT_NAME
    C2_AGENT_NAME = C2_AGENT_NAME

    def __init__(self):
        pass

    async def simulate_conversation(
            self,
            simulation_prompt: str,
            conversation_properties: dict,
            max_turns: int
    ) -> ConversationSimulationResult:
        """
        Simulate a multi-agent conversation using Azure AI Agent Workflow.
        """
        start_time = datetime.utcnow()
        logger.info("="*60)
        logger.info("Starting conversation simulation", 
                   max_turns=max_turns,
                   simulation_prompt_length=len(simulation_prompt),
                   customer_intent=conversation_properties.get('CustomerIntent'),
                   customer_sentiment=conversation_properties.get('CustomerSentiment'),
                   conversation_subject=conversation_properties.get('ConversationSubject'))
        logger.info("="*60)

        # Create agents with instructions
        logger.info("Creating agents for simulation...")
        c1_agent = create_c1_agent()
        logger.debug("C1 Agent ready", agent_name=c1_agent.agent_version_object.name, version=c1_agent.agent_version_object.version)
        
        c2_agent = create_c2_agent()
        logger.debug("C2 Agent ready", agent_name=c2_agent.agent_version_object.name, version=c2_agent.agent_version_object.version)
        
        logger.info("All agents created successfully")

        # Workflow YAML
        workflow_yaml = f"""
kind: workflow
trigger:
  kind: OnConversationStart
  id: my_workflow
  actions:
    - kind: SetVariable
      id: set_initial_message
      variable: Local.LatestMessage
      value: "=UserMessage(System.LastMessageText)"

    - kind: SetVariable
      id: init_turn_count
      variable: Local.TurnCount
      value: 0

    # Start Loop - C1 Turn
    - kind: InvokeAzureAgent
      id: c1_agent_turn
      conversationId: "=System.ConversationId"
      agent:
        name: {c1_agent.agent_version_object.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.LatestMessage

    # Check C1 Termination
    - kind: ConditionGroup
      id: check_c1_termination
      conditions:
        - condition: '=!IsBlank(Find("transfer this call to my supervisor", Last(Local.LatestMessage).Text))'
          id: c1_terminates
          actions:
            - kind: EndConversation
              id: end_workflow_c1
        - condition: '=!IsBlank(Find("end this call now", Last(Local.LatestMessage).Text))'
          id: c1_ends_call
          actions:
            - kind: EndConversation
              id: end_workflow_c1_end_call
      elseActions: []

    # C2 Agent Turn
    - kind: InvokeAzureAgent
      id: c2_agent_turn
      conversationId: "=System.ConversationId"
      agent:
        name: {c2_agent.agent_version_object.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.LatestMessage

    # Increment Turn Count
    - kind: SetVariable
      id: increment_turn
      variable: Local.TurnCount
      value: "=Local.TurnCount + 1"

    # Check Max Turns
    - kind: ConditionGroup
      id: check_max_turns
      conditions:
        - condition: "=Local.TurnCount >= {max_turns}"
          id: max_turns_reached
          actions:
            - kind: EndConversation
              id: end_workflow_max_turns
      elseActions:
        - kind: GotoAction
          id: loop_back
          actionId: c1_agent_turn
"""

        # Create Workflow Agent
        logger.info("Creating workflow agent...")
        logger.debug("Workflow YAML length", yaml_length=len(workflow_yaml))
        workflow_agent = azure_ai_service.client.agents.create_version(
            agent_name="conversation-workflow",
            definition=WorkflowAgentDefinition(workflow=workflow_yaml)
        )
        logger.info("Workflow agent created", 
                   workflow_name=workflow_agent.name, 
                   workflow_version=workflow_agent.version)

        # Run Workflow
        logger.info("Creating conversation for workflow...")
        conversation = azure_ai_service.openai_client.conversations.create()
        logger.info("Conversation created", conversation_id=conversation.id)

        input_text = f"{simulation_prompt}\n\nStart the simulation."
        logger.debug("Input text prepared", input_length=len(input_text))

        logger.info("Starting workflow stream...", conversation_id=conversation.id)
        stream = azure_ai_service.openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent": AgentReference(name=workflow_agent.name).as_dict()},
            input=input_text,
            stream=True
        )
        logger.info("Stream created, processing events...")

        conversation_history: List[ConversationMessage] = []
        conversation_status = "Ongoing"
        current_actor = None

        logger.info("Processing stream events...")
        for event in stream:
            if event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED and event.item.type == "workflow_action":
                if event.item.action_id == "c1_agent_turn":
                    current_actor = self.C1_AGENT_NAME
                elif event.item.action_id == "c2_agent_turn":
                    current_actor = self.C2_AGENT_NAME
            
            elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DONE:
                if current_actor:
                    logger.info("Message received", actor=current_actor, message_preview=event.text[:100] + "...")
                    conversation_history.append(ConversationMessage(
                        agent_name=current_actor,
                        message=event.text,
                        timestamp=datetime.utcnow()
                    ))
            
            elif event.type == ResponseStreamEventType.RESPONSE_COMPLETED:
                logger.info("Stream completed")

        # Determine final status
        logger.info("Determining final conversation status...")
        if conversation_history:
            last_message = conversation_history[-1].message.lower()
            if "end this call now" in last_message or "transfer this call to my supervisor" in last_message:
                conversation_status = "Completed"
                logger.info("Conversation marked as Completed by termination phrase")
            else:
                # If max turns reached, it might also be considered completed or just stopped
                conversation_status = "Completed" if len(conversation_history) >= max_turns * 2 else "Ongoing"

        end_time = datetime.utcnow()
        total_time_ms = (end_time - start_time).total_seconds() * 1000
        
        logger.info("="*60)
        logger.info("Conversation simulation completed",
                   status=conversation_status,
                   total_messages=len(conversation_history),
                   total_time_ms=round(total_time_ms, 2))
        logger.info("="*60)

        return ConversationSimulationResult(
            conversation_history=conversation_history,
            conversation_status=conversation_status,
            total_time_taken_ms=total_time_ms,
            start_time=start_time,
            end_time=end_time,
            c1_agent_details=c1_agent.agent_details,
            c2_agent_details=c2_agent.agent_details,

            conversation_id=conversation.id
        )

    async def save_to_database(
        self,
        conversation_properties: Dict[str, Any],
        conversation_history: list,
        conversation_status: str,
        total_time_taken_ms: float,
        c1_agent_details: Dict[str, Any],
        c2_agent_details: Dict[str, Any],
        conversation_id: str
    ):
        """
        Save conversation simulation result to database.
        
        Args:
            conversation_properties: Properties of the conversation
            conversation_history: List of conversation messages
            conversation_status: Status of the conversation
            total_time_taken_ms: Total time taken in milliseconds
            c1_agent_details: Details about C1 agent
            c2_agent_details: Details about C2 agent
            conversation_id: The conversation ID from Azure AI
        """
        logger.info("Saving conversation simulation to database",
                   status=conversation_status,
                   messages=len(conversation_history),
                   time_ms=round(total_time_taken_ms, 2),
                   conversation_id=conversation_id)
        
        # Create document with structure specific to conversation simulation
        # Use conversation_id as the document ID
        document = ConversationSimulationDocument(
            id=conversation_id,
            conversation_properties=conversation_properties,
            conversation_history=conversation_history,
            conversation_status=conversation_status,
            total_time_taken_ms=total_time_taken_ms,
            c1_agent_details=AgentDetails(**c1_agent_details),
            c2_agent_details=AgentDetails(**c2_agent_details)
        )
        
        # Use generic save method from CosmosDBService
        await cosmos_db_service.save_document(
            container_name=cosmos_db_service.CONVERSATION_SIMULATION_CONTAINER,
            document=document
        )
        logger.info("Conversation simulation saved successfully", document_id=conversation_id)


conversation_simulation_service = ConversationSimulationService()

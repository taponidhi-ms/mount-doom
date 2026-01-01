"""Service for conversation simulation use case."""

from datetime import datetime
import structlog
import json
from typing import List, Optional, Dict, Any

from azure.ai.projects.models import WorkflowAgentDefinition, AgentReference, ResponseStreamEventType
from app.services.ai.azure_ai_service import azure_ai_service
from app.services.db.cosmos_db_service import cosmos_db_service
from app.models.schemas import ConversationMessage, AgentDetails, ConversationSimulationResult
from app.core.config import settings

logger = structlog.get_logger()


class ConversationSimulationService:
    """Service for simulating multi-agent conversations."""

    C1_AGENT_NAME = "C1Agent"
    C1_AGENT_INSTRUCTIONS_FILE = "c1_agent.txt"

    C2_AGENT_NAME = "C2Agent"
    C2_AGENT_INSTRUCTIONS_FILE = "c2_agent.txt"

    ORCHESTRATOR_AGENT_NAME = "OrchestratorAgent"
    ORCHESTRATOR_AGENT_INSTRUCTIONS_FILE = "orchestrator_agent.txt"

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

        # Create agents from files
        logger.info("Creating agents for simulation...")
        c1_agent = azure_ai_service.create_agent_from_file(self.C1_AGENT_NAME, self.C1_AGENT_INSTRUCTIONS_FILE)
        logger.debug("C1 Agent ready", agent_name=self.C1_AGENT_NAME, version=c1_agent.agent_version_object.version)
        
        c2_agent = azure_ai_service.create_agent_from_file(self.C2_AGENT_NAME, self.C2_AGENT_INSTRUCTIONS_FILE)
        logger.debug("C2 Agent ready", agent_name=self.C2_AGENT_NAME, version=c2_agent.agent_version_object.version)
        
        orch_agent = azure_ai_service.create_agent_from_file(self.ORCHESTRATOR_AGENT_NAME, self.ORCHESTRATOR_AGENT_INSTRUCTIONS_FILE)
        logger.debug("Orchestrator Agent ready", agent_name=self.ORCHESTRATOR_AGENT_NAME, version=orch_agent.agent_version_object.version)
        
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

    - kind: CreateConversation
      id: create_c1_conversation
      conversationId: Local.C1ConversationId
    
    - kind: CreateConversation
      id: create_c2_conversation
      conversationId: Local.C2ConversationId

    - kind: CreateConversation
      id: create_orch_conversation
      conversationId: Local.OrchConversationId

    # Start Loop - C1 Turn
    - kind: InvokeAzureAgent
      id: c1_agent_turn
      conversationId: "=Local.C1ConversationId"
      agent:
        name: {c1_agent.agent_version_object.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.LatestMessage

    # Orchestrator Check 1
    - kind: InvokeAzureAgent
      id: orch_check_1
      conversationId: "=Local.OrchConversationId"
      agent:
        name: {orch_agent.agent_version_object.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.OrchResponse

    # Check if completed
    - kind: ConditionGroup
      id: check_completion_1
      conditions:
        - condition: '=!IsBlank(Find("Completed", Last(Local.OrchResponse).Text))'
          id: is_completed_1
          actions:
            - kind: EndConversation
              id: end_workflow_1
      elseActions: []

    # C2 Agent Turn
    - kind: InvokeAzureAgent
      id: c2_agent_turn
      conversationId: "=Local.C2ConversationId"
      agent:
        name: {c2_agent.agent_version_object.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.LatestMessage

    # Orchestrator Check 2
    - kind: InvokeAzureAgent
      id: orch_check_2
      conversationId: "=Local.OrchConversationId"
      agent:
        name: {orch_agent.agent_version_object.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.OrchResponse

    # Increment Turn Count
    - kind: SetVariable
      id: increment_turn
      variable: Local.TurnCount
      value: "=Local.TurnCouC1_AGENT_NAME,
            agent_version=c1_version,
            instructions=self.C1_AGENT_INSTRUCTIONS,
            model_deployment_name=settings.default_model_deployment,
            timestamp=datetime.utcnow()
        )
        c2_agent_details = AgentDetails(
            agent_name=self.C2_AGENT_NAME,
            agent_version=c2_version,
            instructions=self.C2_AGENT_INSTRUCTIONS,
            model_deployment_name=settings.default_model_deployment,
            timestamp=datetime.utcnow()
        )
        orchestrator_agent_details = AgentDetails(
            agent_name=self.ORCHESTRATOR_AGENT_NAME,
            agent_version=orch_version,
            instructions=self.ORCHESTRATOR_AGENT_INSTRUCTIONS
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
        
        input_text = f"Simulation Context: {json.dumps(conversation_properties)}\n\nStart the simulation."
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
        total_tokens = 0
        conversation_status = "Ongoing"
        current_actor = None
        current_tokens = None
        event_count = 0

        logger.info("Processing stream events...")
        for event in stream:
            event_count += 1
            logger.debug(f"Stream event #{event_count}", event_type=str(event.type))
            
            if event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED and event.item.type == "workflow_action":
                logger.info("Workflow action added", action_id=event.item.action_id)
                if event.item.action_id == "c1_agent_turn":
                    current_actor = self.C1_AGENT_NAME
                    current_tokens = None
                    logger.info(">>> C1 Agent (Service Rep) turn started")
                elif event.item.action_id == "c2_agent_turn":
                    current_actor = self.C2_AGENT_NAME
                    current_tokens = None
                    logger.info(">>> C2 Agent (Customer) turn started")
                elif event.item.action_id in ["orch_check_1", "orch_check_2"]:
                    current_actor = self.ORCHESTRATOR_AGENT_NAME
                    current_tokens = None
                    logger.info(">>> Orchestrator checking conversation status", action_id=event.item.action_id)
            
            elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DONE:
                if current_actor:
                    message_preview = event.text[:100] + "..." if len(event.text) > 100 else event.text
                    logger.info("Message received", 
                               actor=current_actor, 
                               message_length=len(event.text),
                               message_preview=message_preview,
                               tokens=current_tokens)
                    conversation_history.append(ConversationMessage(
                        agent_name=current_actor,
                        message=event.text,
                        tokens_used=current_tokens,
                        timestamp=datetime.utcnow()
                    ))
                    logger.debug("Message added to history", history_length=len(conversation_history))
            
            elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_DONE:
                # Extract tokens for the current item
                if hasattr(event, 'item') and hasattr(event.item, 'usage') and event.item.usage:
                    current_tokens = event.item.usage.total_tokens
                    logger.debug("Token usage recorded", tokens=current_tokens, actor=current_actor)
            
            elif event.type == ResponseStreamEventType.RESPONSE_COMPLETED:
                logger.info("Stream completed")
                if hasattr(event, 'usage') and event.usage:
                    total_tokens = event.usage.total_tokens
                    logger.info("Total token usage", total_tokens=total_tokens)

        # Determine final status
        logger.info("Determining final conversation status...")
        orch_msgs = [m for m in conversation_history if m.agent_name == self.ORCHESTRATOR_AGENT_NAME]
        logger.debug("Orchestrator messages count", count=len(orch_msgs))
        if orch_msgs:
            last_orch_message = orch_msgs[-1].message
            logger.debug("Last orchestrator message", message=last_orch_message[:100])
            if "Completed" in last_orch_message:
                conversation_status = "Completed"
                logger.info("Conversation marked as Completed by orchestrator")
        
        end_time = datetime.utcnow()
        total_time_ms = (end_time - start_time).total_seconds() * 1000
        
        logger.info("="*60)
        logger.info("Conversation simulation completed",
                   status=conversation_status,
                   total_messages=len(conversation_history),
                   total_tokens=total_tokens,
                   total_time_ms=round(total_time_ms, 2),
                   events_processed=event_count)
        logger.info("="*60)

        return ConversationSimulationResult(
            conversation_history=conversation_history,
            conversation_status=conversation_status,
            total_tokens_used=total_tokens,
            total_time_taken_ms=total_time_ms,
            start_time=start_time,
            end_time=end_time,
            c1_agent_details=c1_agent.agent_details,
            c2_agent_details=c2_agent.agent_details,
            orchestrator_agent_details=orch_agent.agent_details
        )

    async def save_to_database(
        self,
        conversation_properties: Dict[str, Any],
        conversation_history: list,
        conversation_status: str,
        total_tokens_used: Optional[int],
        total_time_taken_ms: float,
        c1_agent_details: Dict[str, Any],
        c2_agent_details: Dict[str, Any],
        orchestrator_agent_details: Dict[str, Any]
    ):
        """
        Save conversation simulation result to database.
        
        Args:
            conversation_properties: Properties of the conversation
            conversation_history: List of conversation messages
            conversation_status: Status of the conversation
            total_tokens_used: Total tokens used
            total_time_taken_ms: Total time taken in milliseconds
            c1_agent_details: Details about C1 agent
            c2_agent_details: Details about C2 agent
            orchestrator_agent_details: Details about orchestrator agent
        """
        logger.info("Saving conversation simulation to database",
                   status=conversation_status,
                   messages=len(conversation_history),
                   tokens=total_tokens_used,
                   time_ms=round(total_time_taken_ms, 2))
        
        # Create document with structure specific to conversation simulation
        document_id = f"{datetime.utcnow().isoformat()}_conversation"
        document = {
            "id": document_id,
            "conversation_properties": conversation_properties,
            "conversation_history": conversation_history,
            "conversation_status": conversation_status,
            "total_tokens_used": total_tokens_used,
            "total_time_taken_ms": total_time_taken_ms,
            "c1_agent_details": c1_agent_details,
            "c2_agent_details": c2_agent_details,
            "orchestrator_agent_details": orchestrator_agent_details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Use generic save method from CosmosDBService
        await cosmos_db_service.save_document(
            container_name=cosmos_db_service.CONVERSATION_SIMULATION_CONTAINER,
            document=document
        )
        logger.info("Conversation simulation saved successfully", document_id=document_id)


conversation_simulation_service = ConversationSimulationService()

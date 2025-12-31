"""Service for conversation simulation use case."""

from datetime import datetime
import structlog
import json
from typing import List, Optional

from azure.ai.projects.models import WorkflowAgentDefinition, AgentReference, ResponseStreamEventType
from app.services.ai.azure_ai_service import azure_ai_service
from app.models.schemas import ConversationMessage, AgentDetails, ConversationSimulationResult
from app.core.config import settings

logger = structlog.get_logger()


class ConversationSimulationService:
    """Service for simulating multi-agent conversations."""

    C1_AGENT_NAME = "C1Agent"
    C1_AGENT_INSTRUCTIONS = """
        You are a professional customer service representative (C1Agent) handling customer inquiries.

        Your role is to:
        - Provide helpful, accurate, and professional responses to customers
        - Show empathy and understanding toward customer concerns
        - Attempt to resolve issues efficiently and effectively
        - Maintain a positive and professional tone throughout the conversation
        - Ask clarifying questions when needed
        - Provide clear explanations and solutions

        Guidelines:
        - Always be polite and courteous
        - Listen actively to the customer's concerns
        - Take ownership of the issue
        - Provide timely responses
        - Escalate complex issues when appropriate
        - Follow company policies and procedures

        When generating your next message in a conversation:
        1. Review the conversation history carefully
        2. Consider the customer's intent, sentiment, and the subject of conversation
        3. Generate an appropriate response that addresses the customer's needs
        4. Keep responses concise but complete
    """

    C2_AGENT_NAME = "C2Agent"
    C2_AGENT_INSTRUCTIONS = """
        You are a customer (C2Agent) interacting with a customer service representative.

        Your role is to:
        - Express your concerns, questions, or issues clearly
        - Respond naturally based on your intent and sentiment
        - Provide necessary information when asked
        - React appropriately to the service representative's responses
        - Follow a natural conversation flow
        - Express satisfaction or dissatisfaction based on the resolution

        Guidelines:
        - Stay consistent with the defined customer intent and sentiment
        - Respond authentically based on the conversation context
        - Don't resolve issues too quickly - allow for realistic back-and-forth
        - Express emotions appropriately (frustration, confusion, satisfaction, etc.)
        - Ask follow-up questions when unclear
        - Acknowledge when your issue is resolved

        When generating your next message in a conversation:
        1. Review the conversation history carefully
        2. Stay true to your defined intent, sentiment, and conversation subject
        3. Generate a natural customer response
        4. Keep responses conversational and realistic
    """

    ORCHESTRATOR_AGENT_NAME = "OrchestratorAgent"
    ORCHESTRATOR_AGENT_INSTRUCTIONS = """
        You are a conversation orchestrator agent responsible for determining conversation completion status.

        Your role is to:
        - Analyze the conversation history between a customer service representative and a customer
        - Determine if the conversation has reached a natural conclusion
        - Provide a clear status indicator

        A conversation should be marked as "Completed" when:
        - The customer's issue has been resolved
        - The customer has expressed satisfaction or acceptance
        - All questions have been answered
        - There is mutual agreement to end the conversation
        - The conversation has reached a natural stopping point

        A conversation should remain "Ongoing" when:
        - The issue is not fully resolved
        - The customer still has questions or concerns
        - Information is being gathered
        - A solution is being worked on
        - Follow-up is needed

        Response Format:
        Respond with a JSON object containing only:
        {
          "ConversationStatus": "Completed" or "Ongoing"
        }

        Important:
        - Return ONLY valid JSON
        - Use exactly "Completed" or "Ongoing" (case-sensitive)
        - Do not include any explanation or additional text
    """

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
        logger.info("Starting conversation simulation", max_turns=max_turns)

        # Create agents
        c1_agent = azure_ai_service.create_agent(self.C1_AGENT_NAME, self.C1_AGENT_INSTRUCTIONS.strip())
        c2_agent = azure_ai_service.create_agent(self.C2_AGENT_NAME, self.C2_AGENT_INSTRUCTIONS.strip())
        orch_agent = azure_ai_service.create_agent(self.ORCHESTRATOR_AGENT_NAME, self.ORCHESTRATOR_AGENT_INSTRUCTIONS.strip())

        # Get versions from agent objects
        c1_version = c1_agent.agent_version_object.version
        c2_version = c2_agent.agent_version_object.version
        orch_version = orch_agent.agent_version_object.version

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
        workflow_agent = azure_ai_service.client.agents.create_version(
            agent_name="conversation-workflow",
            definition=WorkflowAgentDefinition(workflow=workflow_yaml)
        )

        # Run Workflow
        conversation = azure_ai_service.openai_client.conversations.create()
        
        input_text = f"Simulation Context: {json.dumps(conversation_properties)}\n\nStart the simulation."

        stream = azure_ai_service.openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent": AgentReference(name=workflow_agent.name).as_dict()},
            input=input_text,
            stream=True
        )

        conversation_history: List[ConversationMessage] = []
        total_tokens = 0
        conversation_status = "Ongoing"
        current_actor = None
        current_tokens = None

        for event in stream:
            if event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED and event.item.type == "workflow_action":
                if event.item.action_id == "c1_agent_turn":
                    current_actor = self.C1_AGENT_NAME
                    current_tokens = None
                elif event.item.action_id == "c2_agent_turn":
                    current_actor = self.C2_AGENT_NAME
                    current_tokens = None
                elif event.item.action_id in ["orch_check_1", "orch_check_2"]:
                    current_actor = self.ORCHESTRATOR_AGENT_NAME
                    current_tokens = None
            
            elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DONE:
                if current_actor:
                    conversation_history.append(ConversationMessage(
                        agent_name=current_actor,
                        message=event.text,
                        tokens_used=current_tokens,
                        timestamp=datetime.utcnow()
                    ))
            
            elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_DONE:
                # Extract tokens for the current item
                if hasattr(event, 'item') and hasattr(event.item, 'usage') and event.item.usage:
                    current_tokens = event.item.usage.total_tokens
            
            elif event.type == ResponseStreamEventType.RESPONSE_COMPLETED:
                if hasattr(event, 'usage') and event.usage:
                    total_tokens = event.usage.total_tokens

        # Determine final status
        orch_msgs = [m for m in conversation_history if m.agent_name == self.ORCHESTRATOR_AGENT_NAME]
        if orch_msgs and "Completed" in orch_msgs[-1].message:
            conversation_status = "Completed"
        
        end_time = datetime.utcnow()
        total_time_ms = (end_time - start_time).total_seconds() * 1000

        # Prepare details
        c1_agent_details = AgentDetails(
            agent_name=self.C1_AGENT_NAME,
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
            instructions=self.ORCHESTRATOR_AGENT_INSTRUCTIONS,
            model_deployment_name=settings.default_model_deployment,
            timestamp=datetime.utcnow()
        )

        return ConversationSimulationResult(
            conversation_history=conversation_history,
            conversation_status=conversation_status,
            total_tokens_used=total_tokens,
            total_time_taken_ms=total_time_ms,
            start_time=start_time,
            end_time=end_time,
            c1_agent_details=c1_agent_details,
            c2_agent_details=c2_agent_details,
            orchestrator_agent_details=orchestrator_agent_details
        )


conversation_simulation_service = ConversationSimulationService()

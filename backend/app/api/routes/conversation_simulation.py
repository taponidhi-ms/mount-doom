from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    ConversationSimulationRequest,
    ConversationSimulationResponse,
    ConversationMessage,
    AgentDetails
)
from app.services.azure_ai_service import azure_ai_service
from app.services.cosmos_db_service import cosmos_db_service
from app.core.config import settings
from app.instruction_sets import (
    C1_AGENT_NAME, C1_AGENT_INSTRUCTIONS,
    C2_AGENT_NAME, C2_AGENT_INSTRUCTIONS,
    ORCHESTRATOR_AGENT_NAME, ORCHESTRATOR_AGENT_INSTRUCTIONS
)
from datetime import datetime
import time
import json

router = APIRouter(prefix="/conversation-simulation", tags=["Conversation Simulation"])


@router.post("/simulate", response_model=ConversationSimulationResponse)
async def simulate_conversation(request: ConversationSimulationRequest):
    """Simulate a conversation between C1 and C2 agents."""
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000
    
    conversation_history = []
    conversation_status = "Ongoing"
    total_tokens = 0
    
    # Store agent details for all three agents
    c1_agent_details = None
    c2_agent_details = None
    orchestrator_agent_details = None
    
    try:
        # Convert conversation properties to dict for prompt formatting
        conv_props_dict = {
            "CustomerIntent": request.conversation_properties.customer_intent,
            "CustomerSentiment": request.conversation_properties.customer_sentiment,
            "ConversationSubject": request.conversation_properties.conversation_subject
        }
        conv_props_str = json.dumps(conv_props_dict, indent=2)
        
        # Start conversation - C1Agent goes first
        for turn in range(request.max_turns):
            # C1Agent turn (Customer Service Representative)
            c1_start_ms = time.time() * 1000
            messages_str = json.dumps([{
                "role": msg.role,
                "message": msg.message
            } for msg in conversation_history], indent=2)
            
            c1_prompt = f"""Generate a next message as an Agent for the following ongoing conversation:
ConversationProperties: {conv_props_str}
messages: {messages_str}"""
            
            c1_agent_response = await azure_ai_service.get_agent_response(
                agent_name=C1_AGENT_NAME,
                instructions=C1_AGENT_INSTRUCTIONS,
                prompt=c1_prompt,
                model_deployment_name=request.model_deployment_name
            )
            
            # Store C1 agent details on first turn
            if c1_agent_details is None:
                c1_agent_details = AgentDetails(
                    agent_name=C1_AGENT_NAME,
                    agent_version=c1_agent_response.agent_version,
                    instructions=C1_AGENT_INSTRUCTIONS,
                    model_deployment_name=request.model_deployment_name,
                    timestamp=c1_agent_response.timestamp
                )
            
            c1_end_ms = time.time() * 1000
            c1_time_taken = c1_end_ms - c1_start_ms
            
            c1_message = ConversationMessage(
                role="C1Agent",
                agent_name=C1_AGENT_NAME,
                agent_version=c1_agent_response.agent_version,
                message=c1_agent_response.response_text,
                tokens_used=c1_agent_response.tokens_used,
                time_taken_ms=c1_time_taken,
                timestamp=datetime.utcnow()
            )
            conversation_history.append(c1_message)
            
            if c1_agent_response.tokens_used:
                total_tokens += c1_agent_response.tokens_used
            
            # Check conversation status with orchestrator
            messages_str = json.dumps([{
                "role": msg.role,
                "message": msg.message
            } for msg in conversation_history], indent=2)
            
            orch_agent_response = await azure_ai_service.get_agent_response(
                agent_name=ORCHESTRATOR_AGENT_NAME,
                instructions=ORCHESTRATOR_AGENT_INSTRUCTIONS,
                prompt=f"ConversationProperties: {conv_props_str}\nmessages: {messages_str}",
                model_deployment_name=request.model_deployment_name
            )
            
            # Store orchestrator agent details on first use
            if orchestrator_agent_details is None:
                orchestrator_agent_details = AgentDetails(
                    agent_name=ORCHESTRATOR_AGENT_NAME,
                    agent_version=orch_agent_response.agent_version,
                    instructions=ORCHESTRATOR_AGENT_INSTRUCTIONS,
                    model_deployment_name=request.model_deployment_name,
                    timestamp=orch_agent_response.timestamp
                )
            
            if orch_agent_response.tokens_used:
                total_tokens += orch_agent_response.tokens_used
            
            # Parse orchestrator response
            try:
                orch_data = json.loads(orch_agent_response.response_text)
                conversation_status = orch_data.get("ConversationStatus", "Ongoing")
            except json.JSONDecodeError:
                # If response is not valid JSON, check for keywords
                if "Completed" in orchestrator_response:
                    conversation_status = "Completed"
                else:
                    conversation_status = "Ongoing"
            
            if conversation_status == "Completed":
                break
            
            # C2Agent turn (Customer)
            c2_start_ms = time.time() * 1000
            messages_str = json.dumps([{
                "role": msg.role,
                "message": msg.message
            } for msg in conversation_history], indent=2)
            
            c2_prompt = f"""Generate a next message as a customer for the following ongoing conversation:
ConversationProperties: {conv_props_str}
messages: {messages_str}"""
            
            c2_agent_response = await azure_ai_service.get_agent_response(
                agent_name=C2_AGENT_NAME,
                instructions=C2_AGENT_INSTRUCTIONS,
                prompt=c2_prompt,
                model_deployment_name=request.model_deployment_name
            )
            
            # Store C2 agent details on first turn
            if c2_agent_details is None:
                c2_agent_details = AgentDetails(
                    agent_name=C2_AGENT_NAME,
                    agent_version=c2_agent_response.agent_version,
                    instructions=C2_AGENT_INSTRUCTIONS,
                    model_deployment_name=request.model_deployment_name,
                    timestamp=c2_agent_response.timestamp
                )
            
            c2_end_ms = time.time() * 1000
            c2_time_taken = c2_end_ms - c2_start_ms
            
            c2_message = ConversationMessage(
                role="C2Agent",
                agent_name=C2_AGENT_NAME,
                agent_version=c2_agent_response.agent_version,
                message=c2_agent_response.response_text,
                tokens_used=c2_agent_response.tokens_used,
                time_taken_ms=c2_time_taken,
                timestamp=datetime.utcnow()
            )
            conversation_history.append(c2_message)
            
            if c2_agent_response.tokens_used:
                total_tokens += c2_agent_response.tokens_used
            
            # Check conversation status again
            messages_str = json.dumps([{
                "role": msg.role,
                "message": msg.message
            } for msg in conversation_history], indent=2)
            
            orch_agent_response_2 = await azure_ai_service.get_agent_response(
                agent_name=ORCHESTRATOR_AGENT_NAME,
                instructions=ORCHESTRATOR_AGENT_INSTRUCTIONS,
                prompt=f"ConversationProperties: {conv_props_str}\nmessages: {messages_str}",
                model_deployment_name=request.model_deployment_name
            )
            
            if orch_agent_response_2.tokens_used:
                total_tokens += orch_agent_response_2.tokens_used
            
            # Parse orchestrator response
            try:
                orch_data = json.loads(orch_agent_response_2.response_text)
                conversation_status = orch_data.get("ConversationStatus", "Ongoing")
            except json.JSONDecodeError:
                if "Completed" in orch_agent_response_2.response_text:
                    conversation_status = "Completed"
                else:
                    conversation_status = "Ongoing"
            
            if conversation_status == "Completed":
                break
        
        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        total_time_taken_ms = end_ms - start_ms
        
        # Save to Cosmos DB
        conversation_history_dict = [
            {
                "role": msg.role,
                "agent_name": msg.agent_name,
                "agent_version": msg.agent_version,
                "message": msg.message,
                "tokens_used": msg.tokens_used,
                "time_taken_ms": msg.time_taken_ms,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in conversation_history
        ]
        
        await cosmos_db_service.save_conversation_simulation(
            conversation_properties=conv_props_dict,
            conversation_history=conversation_history_dict,
            conversation_status=conversation_status,
            total_tokens_used=total_tokens,
            total_time_taken_ms=total_time_taken_ms,
            c1_agent_details={
                "agent_name": c1_agent_details.agent_name,
                "agent_version": c1_agent_details.agent_version,
                "instructions": c1_agent_details.instructions,
                "model": c1_agent_details.model,
                "timestamp": c1_agent_details.timestamp.isoformat()
            },
            c2_agent_details={
                "agent_name": c2_agent_details.agent_name,
                "agent_version": c2_agent_details.agent_version,
                "instructions": c2_agent_details.instructions,
                "model": c2_agent_details.model,
                "timestamp": c2_agent_details.timestamp.isoformat()
            },
            orchestrator_agent_details={
                "agent_name": orchestrator_agent_details.agent_name,
                "agent_version": orchestrator_agent_details.agent_version,
                "instructions": orchestrator_agent_details.instructions,
                "model": orchestrator_agent_details.model,
                "timestamp": orchestrator_agent_details.timestamp.isoformat()
            }
        )
        
        return ConversationSimulationResponse(
            conversation_history=conversation_history,
            conversation_status=conversation_status,
            total_tokens_used=total_tokens,
            total_time_taken_ms=total_time_taken_ms,
            start_time=start_time,
            end_time=end_time,
            c1_agent_details=c1_agent_details,
            c2_agent_details=c2_agent_details,
            orchestrator_agent_details=orchestrator_agent_details
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating conversation: {str(e)}")

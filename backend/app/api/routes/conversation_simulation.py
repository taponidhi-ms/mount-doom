from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    ConversationSimulationRequest,
    ConversationSimulationResponse,
    ConversationMessage,
    AvailableAgentsResponse,
    AgentInfo
)
from app.services.azure_ai_service import azure_ai_service
from app.services.cosmos_db_service import cosmos_db_service
from app.core.config import settings
from datetime import datetime
import time
import json

router = APIRouter(prefix="/conversation-simulation", tags=["Conversation Simulation"])


@router.get("/agents", response_model=AvailableAgentsResponse)
async def get_available_agents():
    """Get list of available agents for conversation simulation use case."""
    agents = []
    
    if settings.conversation_c1_agent:
        agents.append(AgentInfo(
            agent_id=settings.conversation_c1_agent,
            agent_name="C1 Agent (Customer Service Representative)",
            description="Agent acting as customer service representative"
        ))
    
    if settings.conversation_c2_agent:
        agents.append(AgentInfo(
            agent_id=settings.conversation_c2_agent,
            agent_name="C2 Agent (Customer)",
            description="Agent acting as customer"
        ))
    
    if settings.conversation_orchestrator_agent:
        agents.append(AgentInfo(
            agent_id=settings.conversation_orchestrator_agent,
            agent_name="Conversation Orchestrator Agent",
            description="Agent for determining conversation completion status"
        ))
    
    return AvailableAgentsResponse(agents=agents)


@router.post("/simulate", response_model=ConversationSimulationResponse)
async def simulate_conversation(request: ConversationSimulationRequest):
    """Simulate a conversation between C1 and C2 agents."""
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000
    
    conversation_history = []
    conversation_status = "Ongoing"
    total_tokens = 0
    
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
            
            c1_response, c1_tokens = await azure_ai_service.get_agent_response(
                agent_id=request.c1_agent_id,
                prompt=c1_prompt,
                stream=request.stream
            )
            
            c1_end_ms = time.time() * 1000
            c1_time_taken = c1_end_ms - c1_start_ms
            
            c1_message = ConversationMessage(
                role="C1Agent",
                agent_id=request.c1_agent_id,
                message=c1_response,
                tokens_used=c1_tokens,
                time_taken_ms=c1_time_taken,
                timestamp=datetime.utcnow()
            )
            conversation_history.append(c1_message)
            
            if c1_tokens:
                total_tokens += c1_tokens
            
            # Check conversation status with orchestrator
            messages_str = json.dumps([{
                "role": msg.role,
                "message": msg.message
            } for msg in conversation_history], indent=2)
            
            orchestrator_response, orch_tokens = await azure_ai_service.get_agent_response(
                agent_id=settings.conversation_orchestrator_agent,
                prompt=f"ConversationProperties: {conv_props_str}\nmessages: {messages_str}",
                stream=False
            )
            
            if orch_tokens:
                total_tokens += orch_tokens
            
            # Parse orchestrator response
            try:
                orch_data = json.loads(orchestrator_response)
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
            
            c2_response, c2_tokens = await azure_ai_service.get_agent_response(
                agent_id=request.c2_agent_id,
                prompt=c2_prompt,
                stream=request.stream
            )
            
            c2_end_ms = time.time() * 1000
            c2_time_taken = c2_end_ms - c2_start_ms
            
            c2_message = ConversationMessage(
                role="C2Agent",
                agent_id=request.c2_agent_id,
                message=c2_response,
                tokens_used=c2_tokens,
                time_taken_ms=c2_time_taken,
                timestamp=datetime.utcnow()
            )
            conversation_history.append(c2_message)
            
            if c2_tokens:
                total_tokens += c2_tokens
            
            # Check conversation status again
            messages_str = json.dumps([{
                "role": msg.role,
                "message": msg.message
            } for msg in conversation_history], indent=2)
            
            orchestrator_response, orch_tokens = await azure_ai_service.get_agent_response(
                agent_id=settings.conversation_orchestrator_agent,
                prompt=f"ConversationProperties: {conv_props_str}\nmessages: {messages_str}",
                stream=False
            )
            
            if orch_tokens:
                total_tokens += orch_tokens
            
            # Parse orchestrator response
            try:
                orch_data = json.loads(orchestrator_response)
                conversation_status = orch_data.get("ConversationStatus", "Ongoing")
            except json.JSONDecodeError:
                if "Completed" in orchestrator_response:
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
                "agent_id": msg.agent_id,
                "message": msg.message,
                "tokens_used": msg.tokens_used,
                "time_taken_ms": msg.time_taken_ms,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in conversation_history
        ]
        
        await cosmos_db_service.save_conversation_simulation(
            c1_agent_id=request.c1_agent_id,
            c2_agent_id=request.c2_agent_id,
            conversation_properties=conv_props_dict,
            conversation_history=conversation_history_dict,
            conversation_status=conversation_status,
            total_tokens_used=total_tokens,
            total_time_taken_ms=total_time_taken_ms
        )
        
        return ConversationSimulationResponse(
            conversation_history=conversation_history,
            conversation_status=conversation_status,
            total_tokens_used=total_tokens,
            total_time_taken_ms=total_time_taken_ms,
            start_time=start_time,
            end_time=end_time,
            c1_agent_id=request.c1_agent_id,
            c2_agent_id=request.c2_agent_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating conversation: {str(e)}")

"""Service for preparing CXA AI Evals datasets from conversation simulation runs."""

from datetime import datetime
import structlog
import json
from typing import List, Dict, Any, Optional
import uuid

from app.services.db.cosmos_db_service import cosmos_db_service
from app.models.db import ConversationSimulationEvalsDocument

logger = structlog.get_logger()


class ConversationSimulationEvalsService:
    """Service for preparing evaluation datasets from conversation simulations."""
    
    def _generate_evals_config(self, evals_id: str, agent_name: str = "ttulsi_c2_customer_service_agent") -> Dict[str, Any]:
        """
        Generate the CXA evals configuration matching the required template.
        
        Args:
            evals_id: The ID of the evaluation run
            agent_name: Name of the agent being evaluated
            
        Returns:
            Dict containing the evaluation configuration
        """
        logger.info("Generating CXA evals configuration for conversation simulation", agent_name=agent_name)
        
        config = {
            "team_name": "Omnichannel",
            "agent_name": agent_name,
            "source": {
                "source_folder_path": evals_id,
                "source_file_type": "json"
            },
            "eval_config": {
                "options": [
                    "enable_logging",
                    "dev"
                ],
                "turn_mode": "multi_turn",
                "metric": "groundness", # Metric might differ but keeping groundness for now
                "lower_bound_score": 1,
                "upper_bound_score": 10,
                "score_threshold": 7
            },
            "llm_config": {
                "default_adapter": "capi",
                "adapters": {
                    "capi": {
                        "enabled": True,
                        "type": "capi",
                        "model": "gpt-xyz",
                        "prompt_parameters": {
                            "temperature": 0,
                            "top_p": 1,
                            "max_completion_tokens": 2000
                        },
                        "authorization": {
                            "endpoint": "https://capi-resourceproxy.wus-il002.gateway.test.island.powerapps.com/v0/resourceproxy/envid.360f9d1b-9200-f011-9981-000d3a32ddb4/azureopenai/llm/gpt-41-mini-2025-04-14/chatcompletions",
                            "client_id": "079f5a03-090f-4720-90b9-e03942091e6e",
                            "tenant_id": "f8cdef31-a31e-4b4a-93e4-5f571e91255a",
                            "resource_uri": "api://4309f23c-178a-4fc7-a36e-68d8fee6ca7b",
                            "key_vault_name": "crmanalyticstip",
                            "certificate_secret_name": "dynamics-cca-data-analytics-test",
                            "headers": {
                                "x-ms-source": "{\"consumptionSource\":\"Api\",\"partnerSource\":\"D365Sales.Copilot.CXAEvals\"}",
                                "x-ms-client-principal-id": "b1ee8c0b-c63a-45f8-b198-90ed3dd5b87e",
                                "x-ms-client-tenant-id": "04f02989-9a26-4c15-bf84-5ee3f23b1301"
                            },
                            "token_cache_seconds": 300
                        },
                        "timeout_seconds": 60,
                        "retries": 2
                    }
                }
            },
            "sink": {
                "type": "LocalFileWriter",
                "output_folder_path": f"{evals_id}\\output"
            },
            "reporting": {
                "enabled": False,
                "authorization": {
                    "client_id": "079f5a03-090f-4720-90b9-e03942091e6e",
                    "tenant_id": "72f988bf-86f1-41af-91ab-2d7cd011db47",
                    "resource_uri": "api://evaluation-results-api",
                    "key_vault_name": "crmanalyticstip",
                    "certificate_secret_name": "dynamics-cca-data-analytics-test",
                    "token_cache_seconds": 3600
                }
            }
        }
        
        logger.info("Evals configuration generated")
        return config

    def _create_simulation_conversation_from_run(self, run_document: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a conversation object from a conversation simulation run document.
        
        Args:
            run_document: Document from conversation_simulation container
            
        Returns:
            Conversation dictionary with system/user/assistant messages
        """
        try:
            conversation_id = run_document.get("id", "unknown")
            conversation_properties = run_document.get("conversation_properties", {})
            conversation_history = run_document.get("conversation_history", [])
            c2_agent_details = run_document.get("c2_agent_details", {})
            
            # Message 1: Instructions from C2 Agent
            instruction_set = c2_agent_details.get("instructions", "")
            
            # Message 2: Conversation Properties
            if isinstance(conversation_properties, dict):
                props_str = json.dumps(conversation_properties, ensure_ascii=False)
            else:
                props_str = str(conversation_properties)
                
            messages = [
                {
                    "role": "system",
                    "content": f"Instructions: {instruction_set}"
                },
                {
                    "role": "system",
                    "content": f"ConversationProperties: {props_str}"
                }
            ]
            
            # Message 3+: Exchanged messages
            # C1 is User, C2 is Assistant
            for msg in conversation_history:
                agent_name = msg.get("agent_name")
                message_text = msg.get("message", "")
                
                role = "user" if agent_name == "C1Agent" else "assistant"
                messages.append({
                    "role": role,
                    "content": message_text
                })
            
            conversation = {
                "Id": conversation_id,
                "scenario_name": "conversation_simulation_eval",
                "conversation": messages
            }
            
            logger.info("Created simulation conversation from run",
                       conversation_id=conversation_id,
                       messages_count=len(messages))
            
            return conversation
            
        except Exception as e:
            logger.error("Error creating simulation conversation from run",
                        run_id=run_document.get("id", "unknown"),
                        error=str(e),
                        exc_info=True)
            return None

    async def prepare_evals(self, selected_run_ids: List[str]) -> Dict[str, Any]:
        """
        Prepare CXA AI Evals dataset from selected conversation simulation runs.
        
        Args:
            selected_run_ids: List of document IDs from conversation_simulation container
            
        Returns:
            Dict containing evals preparation data
        """
        logger.info("="*60)
        logger.info("Starting simulation evals preparation", run_ids_count=len(selected_run_ids))
        
        try:
            evals_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()

            # Fetch all selected runs from Cosmos DB
            container = await cosmos_db_service.ensure_container(
                cosmos_db_service.CONVERSATION_SIMULATION_CONTAINER
            )
            
            all_conversations = []
            valid_run_ids = []
            
            for run_id in selected_run_ids:
                try:
                    logger.debug("Fetching run document", run_id=run_id)
                    run_document = container.read_item(
                        item=run_id,
                        partition_key=run_id
                    )
                    
                    # Create conversation from this run
                    conversation = self._create_simulation_conversation_from_run(run_document)
                    if conversation:
                        all_conversations.append(conversation)
                        valid_run_ids.append(run_id)
                    
                except Exception as e:
                    logger.error("Failed to fetch or process run document",
                               run_id=run_id,
                               error=str(e),
                               exc_info=True)
                    continue
            
            if not all_conversations:
                logger.warning("No valid conversations could be generated from selected runs")

            # Generate config with C2 agent name
            cxa_evals_config = self._generate_evals_config(evals_id)
            
            cxa_evals_input_data = {
                "conversations": all_conversations
            }
            
            result = {
                "evals_id": evals_id,
                "timestamp": timestamp,
                "source_run_ids": valid_run_ids,
                "cxa_evals_config": cxa_evals_config,
                "cxa_evals_input_data": cxa_evals_input_data,
                "conversations_count": len(all_conversations),
                "message": f"Successfully prepared evals with {len(all_conversations)} conversations"
            }
            
            # Save to database
            conversations_count = len(all_conversations)
            logger.info("Saving simulation evals preparation to database",
                       evals_id=evals_id,
                       source_runs=len(valid_run_ids),
                       conversations_count=conversations_count)
            
            document = ConversationSimulationEvalsDocument(
                id=evals_id,
                source_run_ids=valid_run_ids,
                cxa_evals_config=cxa_evals_config,
                cxa_evals_input_data=cxa_evals_input_data
            )
            
            await cosmos_db_service.save_document(
                container_name=cosmos_db_service.CONVERSATION_SIMULATION_EVALS_CONTAINER,
                document=document
            )
            
            logger.info("Simulation evals preparation saved successfully", evals_id=evals_id)
            
            return result

        except Exception as e:
            logger.error("Error preparing simulation evals", error=str(e), exc_info=True)
            raise

    async def get_latest_evals(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recently prepared simulation evals.
        Returns:
            Dict containing the latest evals preparation or None if none exist
        """
        logger.info("Fetching latest simulation evals preparation")
        
        try:
            result = await cosmos_db_service.browse_container(
                container_name=cosmos_db_service.CONVERSATION_SIMULATION_EVALS_CONTAINER,
                page=1,
                page_size=1,
                order_by="timestamp",
                order_direction="DESC"
            )
            
            if result["items"]:
                logger.info("Latest evals found", evals_id=result["items"][0].get("id"))
                return result["items"][0]
            else:
                logger.info("No evals preparations found")
                return None
                
        except Exception as e:
            logger.error("Error fetching latest simulation evals", error=str(e), exc_info=True)
            raise


# Singleton instance
conversation_simulation_evals_service = ConversationSimulationEvalsService()

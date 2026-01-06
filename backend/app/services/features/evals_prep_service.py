"""Service for preparing CXA AI Evals datasets from persona distribution runs."""

from datetime import datetime
import structlog
from typing import List, Dict, Any, Optional
import uuid

from app.services.db.cosmos_db_service import cosmos_db_service
from app.models.db import EvalsPrepDocument
from app.instruction_sets.persona_distribution import PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS

logger = structlog.get_logger()


class EvalsPrepService:
    """Service for preparing evaluation datasets from persona distribution generations."""

    def _generate_evals_config(self) -> Dict[str, Any]:
        """
        Generate the CXA evals configuration matching the required template.
        
        Returns:
            Dict containing the evaluation configuration
        """
        logger.info("Generating CXA evals configuration")
        
        config = {
            "team_name": "Omnichannel",
            "agent_name": "ttulsi_persona_generator_agent",
            "source": {
                "source_folder_path": ".\\tests\\resources\\input\\input_data\\input_multi_turn_example.json",
                "source_file_type": "json",
                "variable_columns": []
            },
            "eval_config": {
                "options": [
                    "enable_logging",
                    "dev"
                ],
                "turn_mode": "multi_turn",
                "metric": "groundedness",
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
                "output_folder_path": ".\\tests\\resources\\output_test\\default_multi_turn\\"
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

    def _create_conversation_from_run(self, run_document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a conversation object from a persona distribution run document.
        
        Args:
            run_document: Document from persona_distribution container
            
        Returns:
            Conversation dictionary with system/user/assistant format and groundness_fact
        """
        try:
            conversation_id = run_document.get("id", "unknown")
            prompt = run_document.get("prompt", "")
            response = run_document.get("response", "")
            groundness_fact = run_document.get("groundness_fact")
            
            conversation = {
                "Id": conversation_id,
                "scenario_name": "persona_distribution_generation",
                "conversation": [
                    {
                        "role": "system",
                        "content": PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS
                    },
                    {
                        "role": "user",
                        "content": prompt
                    },
                    {
                        "role": "assistant",
                        "content": response
                    }
                ],
                "groundness_fact": groundness_fact
            }
            
            logger.info("Created conversation from run",
                       conversation_id=conversation_id,
                       prompt_length=len(prompt),
                       response_length=len(response),
                       has_groundness_fact=groundness_fact is not None)
            
            return conversation
            
        except Exception as e:
            logger.error("Error creating conversation from run",
                        run_id=run_document.get("id", "unknown"),
                        error=str(e),
                        exc_info=True)
            return None

    async def prepare_evals(self, selected_run_ids: List[str]) -> Dict[str, Any]:
        """
        Prepare CXA AI Evals dataset from selected persona distribution runs.
        
        Args:
            selected_run_ids: List of document IDs from persona_distribution container
            
        Returns:
            Dict containing:
            - evals_id: Unique identifier for this evals preparation
            - cxa_evals_config: Evaluation configuration
            - cxa_evals_input_data: Combined conversations data
            - source_run_ids: List of source run IDs
            - timestamp: When evals were prepared
        """
        logger.info("="*60)
        logger.info("Starting evals preparation", run_ids_count=len(selected_run_ids))
        
        try:
            # Fetch all selected runs from Cosmos DB
            container = await cosmos_db_service.ensure_container(
                cosmos_db_service.PERSONA_DISTRIBUTION_CONTAINER
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
                    conversation = self._create_conversation_from_run(run_document)
                    if conversation:
                        all_conversations.append(conversation)
                        valid_run_ids.append(run_id)
                        
                        logger.info("Processed run successfully",
                                   run_id=run_id,
                                   conversation_id=conversation.get("Id"))
                    
                except Exception as e:
                    logger.error("Failed to fetch or process run document",
                               run_id=run_id,
                               error=str(e),
                               exc_info=True)
                    # Continue with other runs even if one fails
                    continue
            
            if not all_conversations:
                raise ValueError("No conversations could be created from the selected runs")
            
            # Generate evals configuration
            evals_config = self._generate_evals_config()
            
            # Create evals input data with conversations structure
            evals_input_data = {
                "conversations": all_conversations
            }
            
            # Create evals document
            evals_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()
            
            logger.info("Evals preparation completed",
                       evals_id=evals_id,
                       total_conversations=len(all_conversations),
                       source_runs=len(valid_run_ids))
            
            result = {
                "evals_id": evals_id,
                "timestamp": timestamp,
                "source_run_ids": valid_run_ids,
                "cxa_evals_config": evals_config,
                "cxa_evals_input_data": evals_input_data
            }
            
            logger.info("="*60)
            return result
            
        except Exception as e:
            logger.error("Error preparing evals", error=str(e), exc_info=True)
            raise

    async def save_to_database(
        self,
        evals_id: str,
        source_run_ids: List[str],
        cxa_evals_config: Dict[str, Any],
        cxa_evals_input_data: Dict[str, Any]
    ):
        """
        Save prepared evals to database.
        
        Args:
            evals_id: Unique identifier for this evals preparation
            source_run_ids: List of source persona distribution run IDs
            cxa_evals_config: Evaluation configuration object
            cxa_evals_input_data: Input data with conversations structure
        """
        conversations_count = len(cxa_evals_input_data.get("conversations", []))
        logger.info("Saving evals preparation to database",
                   evals_id=evals_id,
                   source_runs=len(source_run_ids),
                   conversations_count=conversations_count)
        
        document = EvalsPrepDocument(
            id=evals_id,
            source_run_ids=source_run_ids,
            cxa_evals_config=cxa_evals_config,
            cxa_evals_input_data=cxa_evals_input_data
        )
        
        await cosmos_db_service.save_document(
            container_name=cosmos_db_service.PERSONA_DISTRIBUTION_EVALS_CONTAINER,
            document=document
        )
        
        logger.info("Evals preparation saved successfully", evals_id=evals_id)

    async def get_latest_evals(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recently prepared evals.
        
        Returns:
            Dict containing the latest evals preparation or None if none exist
        """
        logger.info("Fetching latest evals preparation")
        
        try:
            result = await cosmos_db_service.browse_container(
                container_name=cosmos_db_service.PERSONA_DISTRIBUTION_EVALS_CONTAINER,
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
            logger.error("Error fetching latest evals", error=str(e), exc_info=True)
            raise


# Singleton instance
evals_prep_service = EvalsPrepService()

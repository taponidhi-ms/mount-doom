"""Service for preparing CXA AI Evals datasets from persona distribution runs."""

from datetime import datetime
import structlog
from typing import List, Dict, Any, Optional
import uuid

from app.services.db.cosmos_db_service import cosmos_db_service
from app.models.db import EvalsPrepDocument

logger = structlog.get_logger()


class EvalsPrepService:
    """Service for preparing evaluation datasets from persona distribution generations."""

    def _generate_evals_config(self) -> Dict[str, Any]:
        """
        Generate the CXA evals configuration with predefined rules.
        
        Returns:
            Dict containing the evaluation configuration
        """
        logger.info("Generating CXA evals configuration with predefined rules")
        
        config = {
            "version": "1.0",
            "eval_type": "persona_distribution",
            "description": "Evaluation of PersonaDistributionGeneratorAgent accuracy",
            "custom_rules": [
                {
                    "rule_id": "intent_distribution_accuracy",
                    "rule_name": "Intent Distribution Accuracy",
                    "rule_type": "distribution_check",
                    "description": "Verifies that the actual distribution of intents matches the expected distribution",
                    "target_field": "CustomerIntent",
                    "tolerance_percentage": 5,
                    "metric": "percentage_deviation"
                },
                {
                    "rule_id": "sentiment_distribution_accuracy",
                    "rule_name": "Sentiment Distribution Accuracy",
                    "rule_type": "distribution_check",
                    "description": "Verifies that the actual distribution of sentiments matches the expected distribution",
                    "target_field": "CustomerSentiment",
                    "tolerance_percentage": 5,
                    "metric": "percentage_deviation"
                },
                {
                    "rule_id": "subject_variation",
                    "rule_name": "Subject Variation Check",
                    "rule_type": "variety_check",
                    "description": "Ensures that conversation subjects are appropriately varied within each intent category",
                    "target_field": "ConversationSubject",
                    "min_unique_count": 2
                },
                {
                    "rule_id": "total_count_accuracy",
                    "rule_name": "Total Conversation Count Accuracy",
                    "rule_type": "count_check",
                    "description": "Verifies that the total number of conversations matches the expected count",
                    "tolerance_percentage": 2
                }
            ],
            "variable_columns": [
                "CustomerIntent",
                "CustomerSentiment",
                "ConversationSubject"
            ],
            "metrics": [
                "intent_distribution_accuracy_score",
                "sentiment_distribution_accuracy_score",
                "subject_variation_score",
                "total_count_accuracy_score"
            ]
        }
        
        logger.info("Evals configuration generated", 
                   rules_count=len(config["custom_rules"]),
                   variable_columns=config["variable_columns"])
        return config

    def _extract_personas_from_run(self, run_document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract persona data from a single persona distribution run document.
        
        Args:
            run_document: Document from persona_distribution container
            
        Returns:
            List of persona dictionaries with intent, sentiment, subject, and expected distribution
        """
        personas = []
        
        try:
            parsed_output = run_document.get("parsed_output")
            if not parsed_output:
                logger.warning("No parsed_output found in run document", 
                             run_id=run_document.get("id"))
                return personas
            
            # Extract expected distribution data
            intents = parsed_output.get("intents", [])
            sentiments = parsed_output.get("Sentiments", [])
            proportions = parsed_output.get("Proportions", [])
            conv_count = parsed_output.get("ConvCount", 0)
            
            # Create a mapping of intent to expected percentage and count
            intent_map = {}
            for intent_obj in intents:
                intent_name = intent_obj.get("intent", "")
                intent_map[intent_name] = {
                    "percentage": intent_obj.get("percentage", 0),
                    "subject": intent_obj.get("subject", ""),
                    "count": 0
                }
            
            # Update counts from proportions
            for prop in proportions:
                intent_name = prop.get("intent", "")
                if intent_name in intent_map:
                    intent_map[intent_name]["count"] = prop.get("count", 0)
            
            # Create sentiment mapping
            sentiment_map = {}
            for sentiment_obj in sentiments:
                sentiment_name = sentiment_obj.get("sentiment", "")
                sentiment_map[sentiment_name] = sentiment_obj.get("percentage", 0)
            
            # Generate persona entries based on proportions
            conversation_index = 0
            for intent_name, intent_data in intent_map.items():
                count = intent_data["count"]
                subject = intent_data["subject"]
                
                # Distribute sentiments across this intent's personas
                # For simplicity, assign sentiments proportionally
                for i in range(count):
                    conversation_index += 1
                    
                    # Select sentiment based on overall distribution
                    # Simple approach: cycle through sentiments
                    if sentiments:
                        sentiment_idx = i % len(sentiments)
                        sentiment_obj = sentiments[sentiment_idx]
                        sentiment_name = sentiment_obj.get("sentiment", "neutral") if isinstance(sentiment_obj, dict) else "neutral"
                    else:
                        sentiment_name = "neutral"
                    
                    persona = {
                        "conversation_id": f"{run_document.get('id', 'unknown')}_conv_{conversation_index}",
                        "source_run_id": run_document.get("id"),
                        "CustomerIntent": intent_name,
                        "CustomerSentiment": sentiment_name,
                        "ConversationSubject": subject,
                        "expected_distribution": {
                            "intent": intent_name,
                            "intent_percentage": intent_data["percentage"],
                            "intent_count": count,
                            "sentiment": sentiment_name,
                            "sentiment_percentage": sentiment_map.get(sentiment_name, 0),
                            "total_conversations": conv_count
                        }
                    }
                    personas.append(persona)
            
            logger.info("Extracted personas from run",
                       run_id=run_document.get("id"),
                       personas_count=len(personas))
            
        except Exception as e:
            logger.error("Error extracting personas from run",
                        run_id=run_document.get("id", "unknown"),
                        error=str(e),
                        exc_info=True)
        
        return personas

    async def prepare_evals(self, selected_run_ids: List[str]) -> Dict[str, Any]:
        """
        Prepare CXA AI Evals dataset from selected persona distribution runs.
        
        Args:
            selected_run_ids: List of document IDs from persona_distribution container
            
        Returns:
            Dict containing:
            - evals_id: Unique identifier for this evals preparation
            - cxa_evals_config: Evaluation configuration
            - cxa_evals_input_data: Combined persona data
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
            
            all_personas = []
            valid_run_ids = []
            
            for run_id in selected_run_ids:
                try:
                    logger.debug("Fetching run document", run_id=run_id)
                    run_document = container.read_item(
                        item=run_id,
                        partition_key=run_id
                    )
                    
                    # Extract personas from this run
                    personas = self._extract_personas_from_run(run_document)
                    all_personas.extend(personas)
                    valid_run_ids.append(run_id)
                    
                    logger.info("Processed run successfully",
                               run_id=run_id,
                               personas_extracted=len(personas))
                    
                except Exception as e:
                    logger.error("Failed to fetch or process run document",
                               run_id=run_id,
                               error=str(e),
                               exc_info=True)
                    # Continue with other runs even if one fails
                    continue
            
            if not all_personas:
                raise ValueError("No personas could be extracted from the selected runs")
            
            # Generate evals configuration
            evals_config = self._generate_evals_config()
            
            # Create evals document
            evals_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()
            
            logger.info("Evals preparation completed",
                       evals_id=evals_id,
                       total_personas=len(all_personas),
                       source_runs=len(valid_run_ids))
            
            result = {
                "evals_id": evals_id,
                "timestamp": timestamp,
                "source_run_ids": valid_run_ids,
                "cxa_evals_config": evals_config,
                "cxa_evals_input_data": all_personas
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
        cxa_evals_input_data: List[Dict[str, Any]]
    ):
        """
        Save prepared evals to database.
        
        Args:
            evals_id: Unique identifier for this evals preparation
            source_run_ids: List of source persona distribution run IDs
            cxa_evals_config: Evaluation configuration object
            cxa_evals_input_data: Input data array
        """
        logger.info("Saving evals preparation to database",
                   evals_id=evals_id,
                   source_runs=len(source_run_ids),
                   personas_count=len(cxa_evals_input_data))
        
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

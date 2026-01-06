# CXA AI Evals Framework

## Overview
CXA AI Evals is an internal Microsoft framework for evaluating AI model performance in customer experience scenarios. Mount Doom integrates with this framework to prepare evaluation datasets from persona distribution runs.

## Purpose
The evals feature allows users to:
1. Select multiple persona distribution generation runs from history
2. Combine them into a standardized evals input format
3. Generate a configuration file with evaluation rules
4. Download both files for use in the CXA AI Evals framework

## Evaluation Goal
The primary goal is to evaluate whether the LLM (PersonaDistributionGeneratorAgent) correctly generated the expected distribution of personas according to the prompt requirements.

## Data Structures

### Evals Input Data Format
The input data file contains a list of conversations/personas with their properties and groundness facts:
```json
[
  {
    "conversation_id": "unique-id",
    "CustomerIntent": "billing inquiry",
    "CustomerSentiment": "negative",
    "ConversationSubject": "overcharge dispute",
    "expected_distribution": {
      "intent": "billing inquiry",
      "sentiment": "negative",
      "percentage": 60
    },
    "groundness_fact": {
      "expected_conversation_count": 10,
      "expected_intents": [
        {"intent": "billing inquiry", "percentage": 60, "subject": "late fee reversal"}
      ],
      "expected_sentiments": [
        {"sentiment": "negative", "percentage": 70}
      ],
      "expected_phone_numbers": {
        "caller": "+1-206-555-0100",
        "recipient": "+1-425-555-0199"
      },
      "is_transcript_based": false,
      "explicit_constraints": ["Must have exactly 10 calls"],
      "generation_flexibility": "Sentiments can be generated if not specified"
    }
  },
  ...
]
```

### Evals Config Format
The configuration file defines evaluation rules and variable columns:
```json
{
  "version": "1.0",
  "eval_type": "multi_turn",
  "custom_rules": [
    {
      "rule_id": "intent_distribution_accuracy",
      "rule_name": "Intent Distribution Accuracy",
      "rule_type": "distribution_check",
      "target_field": "CustomerIntent",
      "tolerance": 5
    },
    {
      "rule_id": "sentiment_distribution_accuracy",
      "rule_name": "Sentiment Distribution Accuracy",
      "rule_type": "distribution_check",
      "target_field": "CustomerSentiment",
      "tolerance": 5
    }
  ],
  "variable_columns": [
    "CustomerIntent",
    "CustomerSentiment",
    "ConversationSubject"
  ]
}
```

## Predefined Rules
The following rules are used to evaluate persona distribution accuracy:

1. **Intent Distribution Accuracy**: Verifies that the actual distribution of intents matches the expected distribution within a 5% tolerance
2. **Sentiment Distribution Accuracy**: Verifies that the actual distribution of sentiments matches the expected distribution within a 5% tolerance
3. **Subject Variation**: Ensures that conversation subjects are appropriately varied within each intent category

These rules are hardcoded and do not require LLM evaluation.

## Groundness Fact Extraction

**Purpose**: Extract the expected requirements from the prompt to serve as ground truth for later evaluation by CXA Evals.

**Agent**: PersonaDistributionGroundnessFactAgent
- Specialized agent that extracts expected requirements from the prompt
- Identifies what SHOULD be in a valid output based on the prompt specifications
- Provides structured groundness fact that CXA Evals will use to evaluate actual outputs

**Extraction Focus**:
1. **Expected Values**: Conversation counts, intents, sentiments, percentages, subjects
2. **Explicit Constraints**: Specific requirements mentioned in the prompt
3. **Generation Flexibility**: What can be randomly generated vs. what must match exactly

**Groundness Fact Output**:
```json
{
  "expected_conversation_count": <integer or "unspecified">,
  "expected_intents": [
    {
      "intent": "<intent name>",
      "percentage": <number or "unspecified">,
      "subject": "<subject or 'unspecified'>"
    }
  ],
  "expected_sentiments": [
    {
      "sentiment": "<sentiment name>",
      "percentage": <number or "unspecified">
    }
  ],
  "expected_phone_numbers": {
    "caller": "<phone number or 'unspecified'>",
    "recipient": "<phone number or 'unspecified'>"
  },
  "is_transcript_based": <boolean>,
  "explicit_constraints": ["<list of constraints>"],
  "generation_flexibility": "<description of what can be generated>"
}
```

**Purpose in Evaluation**:
- The groundness fact serves as the **ground truth** reference
- CXA Evals compares the actual agent output against this groundness fact
- The evaluation framework determines how well the output matches the expected requirements
- This separation allows the extraction to happen once, and evaluation to happen later with different scoring mechanisms

**Integration with Evals**:
- Groundness fact automatically extracted for each persona distribution generation
- Stored in Cosmos DB with each result
- Included in evals preparation datasets
- Each conversation in evals input data contains its groundness_fact
- CXA Evals uses this as reference to evaluate agent output quality

## Storage
Evals preparation results are stored in a dedicated Cosmos DB container:
- Container name: `persona_distribution_evals`
- Document structure:
  - `id`: Unique identifier for the evals preparation
  - `timestamp`: When the evals were prepared
  - `source_run_ids`: List of persona distribution run IDs used
  - `cxa_evals_config`: The evaluation configuration object (not string)
  - `cxa_evals_input_data`: The input data array (not string)

## API Endpoints
- `POST /api/v1/persona-distribution/prepare-evals` - Prepare evals from selected runs
- `GET /api/v1/persona-distribution/evals/{evals_id}` - Retrieve prepared evals by ID
- `GET /api/v1/persona-distribution/evals/latest` - Get the most recently prepared evals

## UI Workflow
1. User navigates to Persona Distribution page
2. User switches to "Prepare for Evals" tab
3. User views past persona distribution runs in a table with checkboxes
4. User selects multiple runs to combine
5. User clicks "Prepare Evals" button
6. Backend combines the selected runs into evals format
7. Backend stores the prepared evals in Cosmos DB
8. UI shows success message with download buttons
9. User can download `cxa_evals_config.json` and `cxa_evals_input_data.json`

## Integration Points
- Uses existing `persona_distribution` container to fetch past runs
- Creates new `persona_distribution_evals` container for storing prepared evals
- No LLM calls during evals preparation (rule-based only)
- Downloads are direct JSON file downloads from prepared data

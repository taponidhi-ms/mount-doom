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
      "groundness_score": 9,
      "evaluation_summary": "Excellent alignment...",
      "alignment_issues": [],
      "traceability_issues": [],
      "unsupported_claims": [],
      "overall_assessment": "GROUNDED"
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

## Groundness Evaluation

**Purpose**: Measure how well the persona distribution output is anchored to the source prompt, ensuring source fidelity.

**Agent**: PersonaDistributionGroundnessFactAgent
- Specialized agent that evaluates groundedness based on the GroundnessEvaluator framework
- Measures source alignment, traceability, and absence of unsupported claims
- Provides structured evaluation with quantifiable scores

**Evaluation Criteria**:
1. **Source Alignment**: All factual statements match the prompt requirements exactly
2. **Traceability**: Each fact, percentage, or intent can be traced to the prompt
3. **No Unsupported Claims**: No speculative or inferred content beyond prompt specifications

**Groundness Fact Output**:
```json
{
  "groundness_score": <integer 1-10>,
  "evaluation_summary": "<brief summary of grounding quality>",
  "alignment_issues": ["<list of any alignment issues>"],
  "traceability_issues": ["<list of any traceability issues>"],
  "unsupported_claims": ["<list of any unsupported claims>"],
  "overall_assessment": "<GROUNDED|PARTIALLY_GROUNDED|NOT_GROUNDED>"
}
```

**Score Interpretation**:
- **10**: Perfect grounding - every element directly traceable
- **8-9**: Excellent grounding - minor discrepancies only
- **6-7**: Good grounding - some elements may be reasonably inferred
- **4-5**: Partial grounding - several elements lack clear source traceability
- **2-3**: Poor grounding - many fabricated or unsupported elements
- **1**: Not grounded - output does not reflect prompt requirements

**Integration with Evals**:
- Groundness fact automatically calculated for each persona distribution generation
- Stored in Cosmos DB with each result
- Included in evals preparation datasets
- Each conversation in evals input data contains its groundness_fact
- Enables evaluation of agent quality and prompt adherence

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

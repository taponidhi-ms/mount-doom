# CXA Evals Runner

This folder is for running CXA AI Evals locally using the CLI executable.

## Directory Structure

```
cxa_evals/
  Microsoft.CXA.AIEvals.Cli.exe  # CLI executable (download separately)
  default_config.json             # Default eval config
  cutom_config.json               # Custom eval config (note: filename is "cutom" not "custom")
  input/                          # Input data files
    multi_agent_evals_*.json
  output/                         # Eval results (git-ignored)
    output_*/
```

## Key Concepts

**Unified SimulationAgent Approach:**
- Evals now run for `SimulationAgent` (unified agent name)
- No need to run evals separately for each agent type
- The `scenario_name` field in input files distinguishes between different agent types:
  - `PersonaDistributionGeneratorAgent`
  - `PersonaGeneratorAgent`
  - `TranscriptParserAgent`
  - `C2MessageGeneratorAgent`
  - `C1MessageGeneratorAgent`
  - `conversation_simulation` (for workflow)

**Input File Format:**
Each conversation in the input file includes:
- `Id`: Unique identifier (UUID from Cosmos DB)
- `instructions`: Complete agent instruction set
- `prompt`: User's input prompt
- `agent_prompt`: Template string `"[SYSTEM]\n{{instructions}}\n\n[USER]\n{{prompt}}"`
- `agent_response`: Agent's generated response
- `scenario_name`: Agent identifier (used by eval framework)

## How to Run Evals

### 1) Download the CLI Executable

Download `Microsoft.CXA.AIEvals.Cli.exe` from the latest completed pipeline run:

https://dev.azure.com/dynamicscrm/OneCRM/_build?definitionId=29329&_a=summary&branchFilter=543757%2C543757%2C543757%2C543757

Place it directly inside `cxa_evals/` (next to this README).

### 2) Prepare Eval Data

**Input Files:**
- Place input data JSON files in the `input/` folder
- Input files are typically named `multi_agent_evals_<timestamp>.json`
- You can download these files from the Mount Doom web interface:
  - Navigate to `/agents/download` page for multi-agent downloads
  - Or use the History tab on individual agent pages for single-agent downloads

**Config Files:**
- `default_config.json` - Uses default evaluation metrics (Completeness, Conversationality, Relevance, Noise Sensitivity)
- `cutom_config.json` - Uses custom evaluation rules specific to scenarios

### 3) Execute Evals

Run from inside the `cxa_evals/` directory.

**Using Default Config:**

```powershell
.\Microsoft.CXA.AIEvals.Cli.exe .\default_config.json
```

This will:
- Use default evaluation metrics
- Process all conversations in the input file
- Scenario names determine which agent type each conversation belongs to
- Output results to `output/` directory

**Using Custom Config:**

```powershell
.\Microsoft.CXA.AIEvals.Cli.exe .\cutom_config.json
```

This will:
- Use custom evaluation rules defined for specific scenarios
- Apply scenario-specific rules based on `scenario_name` field
- Example custom rules:
  - `conversation_simulation` → persona_adherence, goal_pursuit rules
  - `persona_distribution_generation` → persona_distribution accuracy rules

### 4) View Results

Results are saved in the `output/` directory:
- Organized by run timestamp: `output/output_<timestamp>/`
- Contains detailed evaluation logs and scores
- LLM prompt-response logs saved in `llm_prompt_response_log/` subfolder

## Configuration Details

### Default Config (`default_config.json`)

Key settings:
- `agent_name`: `SimulationAgent_Dev_Default`
- `metric`: `"default"` (uses built-in metrics)
- `turn_mode`: `"single_turn"`
- `score_threshold`: `7` (out of 10)
- Default metrics: Completeness, Conversationality, Relevance, Noise Sensitivity

### Custom Config (`cutom_config.json`)

Key settings:
- `agent_name`: `SimulationAgent_Dev_Custom`
- `metric`: `"custom"` (uses custom rules)
- `custom_rules`: Scenario-specific evaluation rules
  - Rules grouped by `scenario_name`
  - Each rule has: name, category, description, scoring_hint

Example custom rules:
```json
{
  "scenario_name": "conversation_simulation",
  "rules": [
    {
      "rule_name": "persona_adherence",
      "rule_category": "Conversationality",
      "rule_description": "The customer should maintain consistency..."
    }
  ]
}
```

## Notes

- The executable (`Microsoft.CXA.AIEvals.Cli.exe`) is intentionally not tracked by git
- The `output/` directory is intentionally not tracked by git (results are gitignored)
- All conversations are evaluated in a single run (no need for separate runs per agent)
- The eval framework uses `scenario_name` to apply appropriate rules/metrics

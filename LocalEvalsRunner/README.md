# Local Evals Runner

This folder is for running CXA AI Evals locally using the CLI executable.

## Directory layout

Each agent has its own folder with `config/`, `input/`, and `output/` subdirectories:

```
LocalEvalsRunner/
  conversation_simulation_agent/
    config/
      cxa_evals_config.json
    input/
      <input_data_files>.json
    output/
      <eval_results>.json (git-ignored)
  persona_generator_agent/
    config/
      cxa_evals_config.json
    input/
      <input_data_files>.json
    output/
      <eval_results>.json (git-ignored)
```

## How to run evals

### 1) Download the CLI executable

Download `Microsoft.CXA.AIEvals.Cli.exe` from the latest completed pipeline run:

https://dev.azure.com/dynamicscrm/OneCRM/_build?definitionId=29329&_a=summary&branchFilter=543757%2C543757%2C543757%2C543757

Place it directly inside `LocalEvalsRunner/` (next to this README).

### 2) Prepare eval data

For the eval you want to run, ensure the agent folder exists with proper structure:

- Place `cxa_evals_config.json` in the agent's `config/` folder
- Place input data JSON files in the agent's `input/` folder
- The `output/` folder will be created automatically (and is git-ignored)

### 3) Execute

Run from inside the `LocalEvalsRunner/` directory.

**For Persona Generator Agent:**

```powershell
.\Microsoft.CXA.AIEvals.Cli.exe .\persona_generator_agent\config\cxa_evals_config.json
```

**For Conversation Simulation Agent:**

```powershell
.\Microsoft.CXA.AIEvals.Cli.exe .\conversation_simulation_agent\config\cxa_evals_config.json
```

## Notes

- The executable is intentionally not tracked by git.
- Any directory named `output` under `LocalEvalsRunner/` is intentionally not tracked by git.

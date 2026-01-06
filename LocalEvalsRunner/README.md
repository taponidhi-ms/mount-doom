# Local Evals Runner

This folder is for running CXA AI Evals locally using the CLI executable.

## Directory layout

Put each eval run’s files under a use-case/agent folder and eval id folder.

Example:

```
LocalEvalsRunner/
  persona_generator_agent/
    <eval_id>/
      cxa_evals_config.json
      cxa_evals_input_data.json
```

## How to run evals

### 1) Download the CLI executable

Download `Microsoft.CXA.AIEvals.Cli.exe` from the latest completed pipeline run:

https://dev.azure.com/dynamicscrm/OneCRM/_build?definitionId=29329&_a=summary&branchFilter=543757%2C543757%2C543757%2C543757

Place it directly inside `LocalEvalsRunner/` (next to this README).

### 2) Prepare eval data

For the eval you want to run, create a folder under `LocalEvalsRunner/` (see layout above) and put these files in that folder:

- `cxa_evals_config.json`
- `cxa_evals_input_data.json`

### 3) Execute

Run from inside the `LocalEvalsRunner/` directory:

```powershell
.\Microsoft.CXA.AIEvals.Cli.exe .\cxa_evals_config.json
```

## Notes

- The executable is intentionally not tracked by git.
- Any directory named `output` under `LocalEvalsRunner/` is intentionally not tracked by git.

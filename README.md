# Policy-Aware-AI-Investment-Copilot
An AI-powered workflow automation system that helps investment analysts process startup pitch decks faster while enforcing internal investment governance policies.

## Project layout
- `src/agentic_app/`: application package
- `src/agentic_app/clients/`: external API clients
- `src/agentic_app/core/`: business logic and policy checks
- `src/agentic_app/prompts/`: Claude prompt templates and renderers
- `src/agentic_app/scripts/`: runnable package entrypoints
- `tests/`: package-level tests and examples

## Run the policy agent
From the repository root:

```bash
python3 run_policy_agent.py src/agentic_app/samples/sample_policy.json src/agentic_app/samples/sample_startup.json
```

If you prefer the raw package path, use:

```bash
PYTHONPATH=src python3 -m agentic_app.scripts.run_policy_agent src/agentic_app/samples/sample_policy.json src/agentic_app/samples/sample_startup.json
```

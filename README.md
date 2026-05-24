# Policy-Aware AI Investment Diligence Copilot

## Demo
[▶ Watch the demo on YouTube](https://www.youtube.com/watch?v=bYpU06Ygixs)

## Overview
An automated deal flow pipeline that screens incoming startup pitch decks against investment policy, generates a full diligence report — market research, risk analysis, investment memo — and delivers ranked opportunities to analysts. The analyst steps in only to make the governance call. As deal volume scales, the pipeline scales with it.

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

## Extraction agent

Extract structured startup JSON from a pitch deck PDF:

```bash
python3 run_extraction_agent.py src/agentic_app/samples/sample_pitch_deck.pdf
```

This writes the extracted JSON to `src/agentic_app/samples/sample_pitch_deck.startup.json` by default. If you have a Claude API key configured, it will use Claude to improve extraction quality and otherwise fall back to a local heuristic parser.

## Full pipeline: extract and policy check

Run the complete workflow from PDF to policy validation:

```bash
python3 run_full_pipeline.py src/agentic_app/samples/sample_pitch_deck.pdf src/agentic_app/samples/sample_policy.json
```

This will:
1. Extract structured startup data from the PDF
2. Check the extracted startup against the investment policy
3. Output both `greenfleet_ai.startup.json` and `greenfleet_ai.policy_result.json`

The policy result includes a human-readable summary and an `overall_status` field (`pass` or `review`) that determines if human review is needed before proceeding to deeper diligence.

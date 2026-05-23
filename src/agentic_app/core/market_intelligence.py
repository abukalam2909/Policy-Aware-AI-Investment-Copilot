import json
from pathlib import Path

from agentic_app.clients.claude_client import call_claude, get_claude_api_key
from agentic_app.core.extractor import extract_first_json_object

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "market_intelligence_prompt.txt"


def get_market_intelligence(startup: dict) -> dict:
    """Return AI-synthesised market intelligence for the startup's sector.

    Uses Claude when an API key is available; falls back to a minimal
    placeholder so the rest of the pipeline still runs without credentials.
    """
    if not get_claude_api_key():
        return _fallback(startup)

    template = _PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.format(startup_json=json.dumps(startup, indent=2))

    try:
        resp = call_claude(prompt, max_tokens=2000)
        data = extract_first_json_object(resp.get("text", ""))
        if isinstance(data, dict) and "trends" in data:
            return data
    except Exception:
        pass

    return _fallback(startup)


def _fallback(startup: dict) -> dict:
    sector = startup.get("sector", "this sector")
    return {
        "market_size": "Unavailable (Claude API not configured)",
        "trends": [f"Growing demand for {sector} solutions"],
        "competitors": [],
        "growth_signals": ["Market data requires Claude API access"],
        "challenges": ["Market data requires Claude API access"],
        "outlook": f"Configure a Claude API key to generate market intelligence for {sector}.",
    }

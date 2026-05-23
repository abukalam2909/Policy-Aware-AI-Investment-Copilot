import json
from pathlib import Path

from agentic_app.clients.claude_client import call_claude, get_claude_api_key
from agentic_app.core.extractor import extract_first_json_object

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "memo_prompt.txt"


def generate_investment_memo(
    startup: dict,
    policy_result: dict,
    market_intel: dict,
    questions: list[dict],
) -> dict:
    """Return a structured investment memo with risk analysis.

    Falls back to a minimal placeholder when the Claude API is unavailable.
    """
    if not get_claude_api_key():
        return _fallback(startup)

    template = _PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.format(
        startup_json=json.dumps(startup, indent=2),
        policy_result_json=json.dumps(policy_result, indent=2),
        market_intel_json=json.dumps(market_intel, indent=2),
        questions_json=json.dumps(questions, indent=2),
    )

    try:
        resp = call_claude(prompt, max_tokens=3000)
        data = extract_first_json_object(resp.get("text", ""))
        if isinstance(data, dict) and "recommendation" in data:
            return data
    except Exception:
        pass

    return _fallback(startup)


def _fallback(startup: dict) -> dict:
    company = startup.get("company", "this startup")
    return {
        "thesis_fit": f"Unable to generate thesis fit — Claude API not configured. Configure an API key to analyse {company}.",
        "strengths": ["Configure Claude API key to generate analysis."],
        "weaknesses": ["Configure Claude API key to generate analysis."],
        "risk_analysis": [
            {"area": area, "level": "Medium", "description": "Configure Claude API key to generate risk analysis."}
            for area in ["Execution Risk", "Market Risk", "Competitive Risk", "Regulatory Risk", "Team Risk", "Financial Risk"]
        ],
        "missing_info": ["Configure Claude API key to generate missing information list."],
        "recommendation": {
            "action": "HOLD",
            "reason": "Cannot generate recommendation without Claude API access.",
        },
    }

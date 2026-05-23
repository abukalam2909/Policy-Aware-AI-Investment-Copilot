import json
from pathlib import Path

from agentic_app.clients.claude_client import call_claude, get_claude_api_key

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "question_prompt.txt"


def _parse_json_array(text: str) -> list | None:
    """Extract the first JSON array from a text string."""
    start = text.find("[")
    if start == -1:
        return None
    depth = 0
    for idx, char in enumerate(text[start:], start):
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start: idx + 1])
                except json.JSONDecodeError:
                    return None
    return None


def generate_diligence_questions(
    startup: dict,
    policy_result: dict,
    market_intel: dict,
) -> list[dict]:
    """Return a list of founder-specific diligence questions.

    Each item is {"category": str, "question": str}.
    Falls back to generic placeholders when the Claude API is unavailable.
    """
    if not get_claude_api_key():
        return _fallback(startup)

    template = _PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.format(
        startup_json=json.dumps(startup, indent=2),
        policy_result_json=json.dumps(policy_result, indent=2),
        market_intel_json=json.dumps(market_intel, indent=2),
    )

    try:
        resp = call_claude(prompt, max_tokens=2000)
        data = _parse_json_array(resp.get("text", ""))
        if isinstance(data, list) and data and "question" in data[0]:
            return data
    except Exception:
        pass

    return _fallback(startup)


def _fallback(startup: dict) -> list[dict]:
    company = startup.get("company", "your company")
    return [
        {
            "category": "Business Model & Revenue",
            "question": f"Walk me through {company}'s path to first $1M ARR — what does the sales motion look like?",
        },
        {
            "category": "Traction & Growth",
            "question": f"What does your current pipeline look like beyond the pilots mentioned, and what is the conversion rate to paid contracts?",
        },
        {
            "category": "Competitive Moat & Risk",
            "question": f"What stops a well-funded incumbent from replicating {company}'s core offering within 18 months?",
        },
    ]

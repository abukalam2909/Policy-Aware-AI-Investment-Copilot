import sys
import json
from pathlib import Path

from agentic_app.prompts.claude_prompts import build_policy_prompt, load_json
from agentic_app.core.policy_checker import check_policy
from agentic_app.clients import claude_client


def main():
    if len(sys.argv) != 3:
        print("Usage: python src/run_policy_agent.py <policy.json> <startup.json>")
        sys.exit(1)

    base = Path(__file__).resolve().parent.parent
    policy_path = Path(sys.argv[1])
    startup_path = Path(sys.argv[2])

    policy = load_json(policy_path)
    startup = load_json(startup_path)
    template_path = base / "prompts" / "claude_policy_prompt.txt"

    prompt = build_policy_prompt(policy, startup, template_path)

    api_key = None
    try:
        api_key = claude_client.get_claude_api_key()
    except Exception:
        api_key = None

    if not api_key:
        print("Claude API key not found; using local policy checker fallback.")
        report = check_policy(policy, startup)
        print(json.dumps(report, indent=2))
        return

    print("Calling Claude API...")
    try:
        resp = claude_client.call_claude(prompt)
        if isinstance(resp, dict) and resp.get("text"):
            print(resp.get("text"))
        else:
            print(json.dumps(resp, indent=2))
    except Exception as e:
        print("Claude call failed:", e)
        print("Falling back to local policy checker.")
        report = check_policy(policy, startup)
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

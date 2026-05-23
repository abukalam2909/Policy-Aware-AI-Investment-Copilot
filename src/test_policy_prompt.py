from pathlib import Path
from claude_prompts import build_policy_prompt, load_json

base = Path(__file__).resolve().parent
policy = load_json(base / "sample_policy.json")
startup = load_json(base / "sample_startup.json")
template = base / "claude_policy_prompt.txt"

prompt = build_policy_prompt(policy, startup, template)
print(prompt)

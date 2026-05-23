import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from agentic_app.prompts.claude_prompts import build_policy_prompt, load_json

base = Path(__file__).resolve().parent
policy = load_json(base.parent / "src" / "agentic_app" / "samples" / "sample_policy.json")
startup = load_json(base.parent / "src" / "agentic_app" / "samples" / "sample_startup.json")
template = base.parent / "src" / "agentic_app" / "prompts" / "claude_policy_prompt.txt"

prompt = build_policy_prompt(policy, startup, template)
print(prompt)

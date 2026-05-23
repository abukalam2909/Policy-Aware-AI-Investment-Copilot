import json
from pathlib import Path


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_policy_prompt(policy: dict, startup: dict, template_path: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    policy_json = json.dumps(policy, indent=2)
    startup_json = json.dumps(startup, indent=2)
    return template.format(policy_json=policy_json, startup_json=startup_json)


if __name__ == "__main__":
    print("This module provides `build_policy_prompt(policy, startup, template_path)` to render the Claude policy-check prompt.")

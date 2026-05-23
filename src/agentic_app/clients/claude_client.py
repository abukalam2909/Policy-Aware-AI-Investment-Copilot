import os
import requests
import json
from pathlib import Path


def call_claude(prompt: str, model: str = "claude-sonnet-4-6", max_tokens: int = 1000, timeout: int = 60) -> dict:
    api_key = get_claude_api_key()
    if not api_key:
        raise RuntimeError("Claude API key not found. Set CLAUDE_API_KEY or create claude_config.json with the key.")

    url = "https://api.anthropic.com/v1/messages"

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)

    if not resp.ok:
        print("Claude error response:")
        print(resp.status_code)
        print(resp.text)
        resp.raise_for_status()

    data = resp.json()

    text = ""
    if "content" in data and isinstance(data["content"], list):
        text = "".join(
            block.get("text", "")
            for block in data["content"]
            if block.get("type") == "text"
        )

    # Fallbacks: some responses return top-level text fields
    if not text:
        if isinstance(data, dict):
            text = data.get("text") or data.get("completion") or data.get("output") or ""

    return {"raw": data, "text": text}


def get_claude_api_key() -> str | None:
    """Return Claude API key from environment or local config file.

    Search order:
    1. `CLAUDE_API_KEY` environment variable
    2. `claude_config.json` in repository root (project directory)
    3. `~/.claude_config.json` in the user's home directory
    The config file should be JSON with key `CLAUDE_API_KEY` (see claude_config.example.json).
    """
    env_key = os.getenv("CLAUDE_API_KEY")
    if env_key:
        return env_key

    # Look for claude_config.json in repo root (two levels up from src) or current working dir
    possible_paths = [Path("claude_config.json"), Path.home() / ".claude_config.json"]
    for p in possible_paths:
        try:
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                # accept either key name
                return data.get("CLAUDE_API_KEY") or data.get("api_key")
        except Exception:
            continue
    return None

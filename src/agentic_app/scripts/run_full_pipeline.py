import json
import sys
from pathlib import Path

from agentic_app.clients import claude_client
from agentic_app.core.extractor import (
    build_extraction_prompt,
    extract_text_from_pdf,
    heuristic_parse_submission,
    parse_model_json,
)
from agentic_app.core.policy_checker import check_policy
from agentic_app.prompts.claude_prompts import load_json


def extract_startup_from_pdf(pdf_path: Path) -> dict:
    """Extract startup submission from PDF, using Claude if available."""
    base = Path(__file__).resolve().parent.parent
    prompt_path = base / "prompts" / "claude_extraction_prompt.txt"

    text = extract_text_from_pdf(pdf_path)
    if not text:
        raise RuntimeError(f"No text could be extracted from {pdf_path}")

    extraction_result = None
    api_key = claude_client.get_claude_api_key()
    if api_key:
        try:
            prompt = build_extraction_prompt(text, prompt_path)
            resp = claude_client.call_claude(prompt)
            if isinstance(resp, dict):
                extraction_result = parse_model_json(resp.get("text", ""))
        except Exception as exc:
            print(f"Claude extraction call failed: {exc}", file=sys.stderr)

    if extraction_result is None:
        extraction_result = heuristic_parse_submission(text)

    return extraction_result


def run_full_pipeline(pdf_path: Path, policy_path: Path, output_dir: Path | None = None) -> dict:
    """Extract startup from PDF and evaluate against policy."""
    # Extract
    startup = extract_startup_from_pdf(pdf_path)
    startup_name = startup.get("company", "Unknown Startup").replace(" ", "_").lower()
    
    if output_dir is None:
        output_dir = pdf_path.parent
    
    startup_json_path = output_dir / f"{startup_name}.startup.json"
    startup_json_path.write_text(json.dumps(startup, indent=2), encoding="utf-8")
    print(f"Extracted startup: {startup_json_path}")

    # Check policy
    policy = load_json(policy_path)
    policy_result = check_policy(policy, startup)
    
    policy_result_path = output_dir / f"{startup_name}.policy_result.json"
    policy_result_path.write_text(json.dumps(policy_result, indent=2), encoding="utf-8")
    print(f"Policy check result: {policy_result_path}")

    return {
        "startup": startup,
        "policy_result": policy_result,
        "startup_json_path": str(startup_json_path),
        "policy_result_path": str(policy_result_path),
    }


def main():
    if len(sys.argv) not in {3, 4}:
        print("Usage: python3 run_full_pipeline.py <pitchdeck.pdf> <policy.json> [output_dir]")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    policy_path = Path(sys.argv[2])
    output_dir = Path(sys.argv[3]) if len(sys.argv) == 4 else None

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        sys.exit(1)

    if not policy_path.exists():
        print(f"Policy file not found: {policy_path}")
        sys.exit(1)

    result = run_full_pipeline(pdf_path, policy_path, output_dir)
    print("\n=== PIPELINE RESULT ===")
    print(json.dumps(result["policy_result"], indent=2))


if __name__ == "__main__":
    main()

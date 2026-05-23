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


def write_json(path: Path, content: dict) -> None:
    path.write_text(json.dumps(content, indent=2), encoding="utf-8")


def main():
    if len(sys.argv) not in {2, 3}:
        print("Usage: python3 run_extraction_agent.py <pitchdeck.pdf> [output.json]")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    output_path = Path(sys.argv[2]) if len(sys.argv) == 3 else pdf_path.with_suffix(".startup.json")
    base = Path(__file__).resolve().parent.parent
    prompt_path = base / "prompts" / "claude_extraction_prompt.txt"

    print(f"Extracting text from {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("No text could be extracted from the PDF.")
        sys.exit(1)

    extraction_result = None
    api_key = claude_client.get_claude_api_key()
    if api_key:
        prompt = build_extraction_prompt(text, prompt_path)
        try:
            resp = claude_client.call_claude(prompt)
            if isinstance(resp, dict):
                extraction_result = parse_model_json(resp.get("text", ""))
        except Exception as exc:
            print("Claude extraction call failed:", exc)

    if extraction_result is None:
        print("Using local heuristic extraction fallback.")
        extraction_result = heuristic_parse_submission(text)

    write_json(output_path, extraction_result)
    print(f"Extraction complete: {output_path}")
    print(json.dumps(extraction_result, indent=2))


if __name__ == "__main__":
    main()

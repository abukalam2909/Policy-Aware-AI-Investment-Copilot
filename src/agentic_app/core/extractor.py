import json
import re
from pathlib import Path
from typing import Any
from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages).strip()


def extract_first_json_object(text: str) -> Any | None:
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    for idx, char in enumerate(text[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start: idx + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    return None
    return None


def clean_text_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def find_first_match(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        regex = re.compile(rf"(?im)^{re.escape(pattern)}\s*[:\-]\s*(.+)$", flags=re.MULTILINE)
        match = regex.search(text)
        if match:
            return match.group(1).strip()
    return None


def parse_bool(value: str | None, default: bool = False) -> bool:
    if not value:
        return default
    normalized = value.strip().lower()
    if normalized in {"yes", "true", "provided", "available", "included"}:
        return True
    if normalized in {"no", "false", "not provided", "missing", "none"}:
        return False
    return default


def heuristic_parse_submission(text: str) -> dict:
    normalized = text.replace("\r", "\n")

    company = find_first_match(normalized, ["Company", "Startup", "Company name"])
    sector = find_first_match(normalized, ["Sector", "Industry", "Vertical"])
    stage = find_first_match(normalized, ["Stage", "Funding stage", "Round"])
    country = find_first_match(normalized, ["Country", "Headquarters", "HQ"])
    funding_ask = find_first_match(normalized, ["Funding ask", "Ask", "Funding request"])
    business_model = find_first_match(normalized, ["Business model", "Model", "Revenue model"])
    claimed_traction = find_first_match(normalized, ["Traction", "Claimed traction", "Customers", "Pilot"])
    revenue_model = find_first_match(normalized, ["Revenue model", "Business model", "Pricing"])
    current_revenue = find_first_match(normalized, ["Current revenue", "Revenue", "ARR", "MRR"])
    financial_docs = find_first_match(normalized, ["Financial documents", "Financials provided", "Documents provided", "Financial information"])

    if not current_revenue:
        revenue_match = re.search(r"\$[\d,]+", normalized)
        current_revenue = revenue_match.group(0) if revenue_match else "0"

    if financial_docs is None:
        financial_docs = "yes" if re.search(r"financial documents .* provided|financials .* provided|including financials", normalized, flags=re.I) else "no"

    return {
        "company": company or "Unknown Startup",
        "sector": sector or "Unknown",
        "stage": stage or "Seed",
        "country": country or "Unknown",
        "funding_ask": funding_ask or "Unknown",
        "business_model": business_model or "Unknown",
        "claimed_traction": claimed_traction or "Not specified",
        "revenue_model": revenue_model or "Unknown",
        "current_revenue": current_revenue or "0",
        "financial_docs_provided": parse_bool(financial_docs, default=False),
    }


def build_extraction_prompt(text: str, template_path: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    return template.format(pitch_text=text)


def parse_model_json(text: str) -> dict | None:
    extracted = extract_first_json_object(text)
    if not extracted:
        return None
    if not isinstance(extracted, dict):
        return None
    return extracted

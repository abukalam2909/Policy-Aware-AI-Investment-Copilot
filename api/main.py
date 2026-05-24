"""FastAPI backend — exposes all Python AI/diligence logic as REST endpoints."""
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from agentic_app.clients.claude_client import call_claude, get_claude_api_key
from agentic_app.clients.gmail_client import send_diligence_email
from agentic_app.core.extractor import (
    build_extraction_prompt,
    extract_text_from_pdf,
    heuristic_parse_submission,
    parse_model_json,
)
from agentic_app.core.market_intelligence import get_market_intelligence
from agentic_app.core.memo_generator import generate_investment_memo
from agentic_app.core.policy_checker import check_policy
from agentic_app.core.question_generator import generate_diligence_questions
from agentic_app.core.report_generator import generate_html_report
from agentic_app.prompts.claude_prompts import load_json

SAMPLES_DIR = ROOT / "src" / "agentic_app" / "samples"
PROMPTS_DIR = ROOT / "src" / "agentic_app" / "prompts"

app = FastAPI(title="Diligence Copilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    api_key = get_claude_api_key()
    policy = load_json(SAMPLES_DIR / "sample_policy.json")
    return {
        "status": "ok",
        "claude_connected": bool(api_key),
        "policy": {
            "name": policy.get("policy_name", ""),
            "geographies": policy.get("allowed_geographies", []),
            "stages": policy.get("allowed_stages", []),
            "sectors": policy.get("allowed_sectors", []),
        },
    }


@app.post("/api/extract")
async def extract(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    api_key = get_claude_api_key()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    try:
        text = extract_text_from_pdf(tmp_path)
        startup = None
        if api_key:
            try:
                prompt = build_extraction_prompt(text, PROMPTS_DIR / "claude_extraction_prompt.txt")
                resp = call_claude(prompt, max_tokens=2000)
                startup = parse_model_json(resp.get("text", ""))
            except Exception:
                pass
        if startup is None:
            startup = heuristic_parse_submission(text)
        return {"startup": startup}
    finally:
        tmp_path.unlink(missing_ok=True)


class PolicyCheckReq(BaseModel):
    startup: dict


@app.post("/api/policy-check")
def policy_check_endpoint(req: PolicyCheckReq):
    policy = load_json(SAMPLES_DIR / "sample_policy.json")
    result = check_policy(policy, req.startup)
    return {"policy_result": result}


class MarketIntelReq(BaseModel):
    startup: dict


@app.post("/api/market-intel")
def market_intel_endpoint(req: MarketIntelReq):
    return {"market_intel": get_market_intelligence(req.startup)}


class QuestionsReq(BaseModel):
    startup: dict
    policy_result: dict
    market_intel: dict


@app.post("/api/questions")
def questions_endpoint(req: QuestionsReq):
    return {
        "questions": generate_diligence_questions(
            req.startup, req.policy_result, req.market_intel
        )
    }


class MemoReq(BaseModel):
    startup: dict
    policy_result: dict
    market_intel: dict
    questions: list


@app.post("/api/memo")
def memo_endpoint(req: MemoReq):
    return {
        "memo": generate_investment_memo(
            req.startup, req.policy_result, req.market_intel, req.questions
        )
    }


class ReportReq(BaseModel):
    startup: dict
    policy_result: dict
    market_intel: dict
    questions: list
    memo: dict
    analyst_notes: str = ""


@app.post("/api/report")
def report_endpoint(req: ReportReq):
    html = generate_html_report(
        req.startup, req.policy_result, req.market_intel,
        req.questions, req.memo, req.analyst_notes,
    )
    return {"report_html": html}


class EmailReq(BaseModel):
    to_email: str
    company: str
    report_html: str


@app.post("/api/send-email")
def send_email_endpoint(req: EmailReq):
    try:
        send_diligence_email(req.to_email, req.company, req.report_html)
        return {"status": "sent"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

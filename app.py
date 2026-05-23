import json
import sys
import tempfile
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentic_app.clients.claude_client import call_claude, get_claude_api_key
from agentic_app.core.extractor import (
    build_extraction_prompt,
    extract_text_from_pdf,
    heuristic_parse_submission,
    parse_model_json,
)
from agentic_app.core.market_intelligence import get_market_intelligence
from agentic_app.core.policy_checker import check_policy
from agentic_app.prompts.claude_prompts import load_json

SAMPLES_DIR = Path(__file__).parent / "src" / "agentic_app" / "samples"
PROMPTS_DIR = Path(__file__).parent / "src" / "agentic_app" / "prompts"

st.set_page_config(
    page_title="AI Investment Diligence Copilot",
    page_icon="📊",
    layout="wide",
)

# ── Session state ─────────────────────────────────────────────────────────────

def _init_state():
    defaults = {
        "step": 1,
        "startup": None,
        "policy_result": None,
        "human_decision": None,
        "analyst_notes": "",
        "market_intel": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

_init_state()

# ── Sidebar ───────────────────────────────────────────────────────────────────

STEP_LABELS = [
    "Upload & Extract",
    "Policy Check",
    "Human Checkpoint",
    "Market Intelligence",
    "Deeper Analysis",
]

with st.sidebar:
    st.markdown("## 📊 Diligence Copilot")
    st.markdown("---")
    st.markdown("### Workflow Progress")

    for i, label in enumerate(STEP_LABELS, start=1):
        current = st.session_state.step
        if i < current:
            st.markdown(f"✅ Step {i}: {label}")
        elif i == current:
            st.markdown(f"🔵 **Step {i}: {label}**")
        else:
            st.markdown(f"⬜ Step {i}: {label}")

    st.markdown("---")

    api_key = get_claude_api_key()
    if api_key:
        st.success("Claude API: Connected")
    else:
        st.warning("Claude API: Not configured\n(heuristic fallback active)")

    st.markdown("---")
    st.markdown("### Active Policy")
    policy_preview = load_json(SAMPLES_DIR / "sample_policy.json")
    st.caption(f"**{policy_preview.get('policy_name', 'Policy')}**")
    st.caption("Geographies: " + ", ".join(policy_preview.get("allowed_geographies", [])))
    st.caption("Stages: " + ", ".join(policy_preview.get("allowed_stages", [])))

# ── Page header ───────────────────────────────────────────────────────────────

st.markdown("# 📊 Policy-Aware AI Investment Diligence Copilot")
st.markdown(
    "*Automating first-pass startup diligence while enforcing investment governance policies*"
)
st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════════
# STEP 1 — Upload & Extract
# ════════════════════════════════════════════════════════════════════════════════

if st.session_state.step == 1:
    st.markdown("## Step 1 — Upload Pitch Deck")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        uploaded = st.file_uploader("Upload a pitch deck PDF", type=["pdf"])

        st.markdown("**— or use the built-in sample —**")
        if st.button("Load GreenFleet AI sample", use_container_width=True):
            sample_file = SAMPLES_DIR / "greenfleet_ai.startup.json"
            if not sample_file.exists():
                sample_file = SAMPLES_DIR / "sample_startup.json"
            st.session_state.startup = json.loads(sample_file.read_text(encoding="utf-8"))
            st.session_state.step = 2
            st.rerun()

        if uploaded:
            st.success(f"Uploaded: **{uploaded.name}**")
            if st.button("🤖 Extract startup data", type="primary", use_container_width=True):
                with st.spinner("AI is reading the pitch deck…"):
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                        tmp.write(uploaded.read())
                        tmp_path = Path(tmp.name)
                    try:
                        text = extract_text_from_pdf(tmp_path)
                        startup = None
                        if api_key:
                            try:
                                prompt = build_extraction_prompt(
                                    text, PROMPTS_DIR / "claude_extraction_prompt.txt"
                                )
                                resp = call_claude(prompt, max_tokens=2000)
                                startup = parse_model_json(resp.get("text", ""))
                            except Exception as exc:
                                st.warning(f"Claude extraction failed — using fallback parser. ({exc})")
                        if startup is None:
                            startup = heuristic_parse_submission(text)
                        st.session_state.startup = startup
                        st.session_state.step = 2
                        st.rerun()
                    finally:
                        tmp_path.unlink(missing_ok=True)

    with col_right:
        st.markdown("### What this system does")
        st.markdown("""
1. 🤖 AI reads the pitch deck PDF
2. 📋 Extracts structured startup fields
3. 🔍 Checks against investment governance policy
4. 🧑 **You decide** whether to proceed
5. 📊 Deep analysis, questions & report *(coming soon)*
        """)

# ════════════════════════════════════════════════════════════════════════════════
# STEP 2 — Policy Check
# ════════════════════════════════════════════════════════════════════════════════

elif st.session_state.step == 2:
    startup = st.session_state.startup
    st.markdown("## Step 2 — Extraction Results & Policy Check")

    policy = load_json(SAMPLES_DIR / "sample_policy.json")
    policy_result = check_policy(policy, startup)
    st.session_state.policy_result = policy_result

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Extracted Startup Profile")
        fields = {
            "🏢 Company": "company",
            "🌍 Country": "country",
            "📈 Stage": "stage",
            "🏭 Sector": "sector",
            "💰 Funding Ask": "funding_ask",
            "💼 Business Model": "business_model",
            "📊 Current Revenue": "current_revenue",
            "🎯 Claimed Traction": "claimed_traction",
        }
        for label, key in fields.items():
            st.markdown(f"**{label}:** {startup.get(key, '—')}")

        with st.expander("Raw JSON"):
            st.json(startup)

    with col_right:
        st.markdown("### Policy Check Results")

        overall = policy_result["overall_status"]
        if overall == "pass":
            st.success("Overall Status: **PASS**")
        else:
            st.warning("Overall Status: **REVIEW REQUIRED**")

        for check in policy_result.get("results", []):
            icon = {"pass": "✅", "caution": "⚠️", "fail": "❌"}.get(check["status"], "❓")
            label = check["check"].replace("_", " ").title()
            st.markdown(f"{icon} **{label}** — {check['reason']}")

    st.markdown("---")
    col_back, _, col_next = st.columns([1, 2, 2])
    with col_back:
        if st.button("← Back"):
            st.session_state.step = 1
            st.rerun()
    with col_next:
        if st.button("Proceed to Human Checkpoint →", type="primary", use_container_width=True):
            st.session_state.step = 3
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# STEP 3 — Human Governance Checkpoint
# ════════════════════════════════════════════════════════════════════════════════

elif st.session_state.step == 3:
    startup = st.session_state.startup
    policy_result = st.session_state.policy_result
    company = startup.get("company", "this startup")
    overall = policy_result["overall_status"]

    st.markdown("## Step 3 — Policy Governance Checkpoint")

    if overall == "pass":
        st.success(f"Policy check passed for **{company}**. Your approval is required to proceed.")
    else:
        st.warning(f"Policy check flagged items for **{company}**. Review carefully before deciding.")

    st.markdown("---")

    st.markdown(
        """
        <div style="border:2px solid #f0a500;background:#fffbea;border-radius:8px;padding:1.5rem;margin:1rem 0;">
        <h3 style="margin:0 0 0.5rem 0;">🧑 Human Decision Required</h3>
        <p>
        The AI has completed its first-pass policy evaluation.
        Before it continues with market research, diligence questions, and the investment memo,
        <strong>you must approve or reject this opportunity.</strong>
        </p>
        <p style="margin-bottom:0;">
        <em>This checkpoint exists because policy compliance is a fiduciary obligation —
        the AI cannot make this governance decision autonomously.</em>
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_summary, col_decision = st.columns(2)

    with col_summary:
        st.markdown("#### Policy Summary")
        for check in policy_result.get("results", []):
            icon = {"pass": "✅", "caution": "⚠️", "fail": "❌"}.get(check["status"], "❓")
            st.markdown(f"{icon} {check['check'].replace('_', ' ').title()}")

    with col_decision:
        st.markdown("#### Your Decision")
        notes = st.text_area(
            "Analyst notes (optional)",
            placeholder="Add reasoning for your decision…",
        )
        col_approve, col_reject = st.columns(2)
        with col_approve:
            if st.button("✅ APPROVE", type="primary", use_container_width=True):
                st.session_state.human_decision = "approved"
                st.session_state.analyst_notes = notes
                st.session_state.step = 4
                st.rerun()
        with col_reject:
            if st.button("❌ REJECT", use_container_width=True):
                st.session_state.human_decision = "rejected"
                st.session_state.analyst_notes = notes
                st.session_state.step = 99
                st.rerun()

    st.markdown("---")
    if st.button("← Back"):
        st.session_state.step = 2
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# STEP 4 — Market Intelligence
# ════════════════════════════════════════════════════════════════════════════════

elif st.session_state.step == 4:
    startup = st.session_state.startup
    company = startup.get("company", "this startup")

    st.success(f"✅ **{company}** approved for deeper diligence.")
    if st.session_state.analyst_notes:
        st.info(f"**Analyst notes:** {st.session_state.analyst_notes}")

    st.markdown("---")
    st.markdown("## Step 4 — Market Intelligence")

    if st.session_state.market_intel is None:
        with st.spinner("AI is researching the market…"):
            st.session_state.market_intel = get_market_intelligence(startup)

    intel = st.session_state.market_intel

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Market Size")
        st.info(intel.get("market_size", "—"))

        st.markdown("### Market Trends")
        for trend in intel.get("trends", []):
            st.markdown(f"- {trend}")

        st.markdown("### Growth Signals")
        for signal in intel.get("growth_signals", []):
            st.markdown(f"📈 {signal}")

    with col_right:
        st.markdown("### Key Competitors")
        for comp in intel.get("competitors", []):
            st.markdown(f"**{comp.get('name', '—')}** — {comp.get('description', '')}")

        st.markdown("### Sector Challenges")
        for challenge in intel.get("challenges", []):
            st.markdown(f"⚠️ {challenge}")

        st.markdown("### Market Outlook")
        st.markdown(intel.get("outlook", "—"))

    st.markdown("---")
    st.markdown("## Next Steps")
    st.info(
        "🚧 **Coming in upcoming feature branches:**\n\n"
        "- ❓ Founder-Specific Diligence Questions\n"
        "- 📝 Investment Memo + Risk Analysis\n"
        "- 📄 HTML Report Generation\n"
        "- 📧 Gmail + Google Drive Delivery"
    )

    col_back, col_restart = st.columns(2)
    with col_back:
        if st.button("← Back to Checkpoint"):
            st.session_state.market_intel = None
            st.session_state.step = 3
            st.rerun()
    with col_restart:
        if st.button("🔄 Start a New Analysis", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# STEP 99 — Rejected (always last; never conflicts with new workflow steps)
# ════════════════════════════════════════════════════════════════════════════════

elif st.session_state.step == 99:
    startup = st.session_state.startup
    company = startup.get("company", "this startup")

    st.error(f"❌ **{company}** rejected. The AI will not proceed with deeper diligence.")

    if st.session_state.analyst_notes:
        st.info(f"**Analyst notes:** {st.session_state.analyst_notes}")

    st.markdown("### Policy Results")
    for check in st.session_state.policy_result.get("results", []):
        icon = {"pass": "✅", "caution": "⚠️", "fail": "❌"}.get(check["status"], "❓")
        label = check["check"].replace("_", " ").title()
        st.markdown(f"{icon} **{label}** — {check['reason']}")

    if st.button("🔄 Start a New Analysis", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

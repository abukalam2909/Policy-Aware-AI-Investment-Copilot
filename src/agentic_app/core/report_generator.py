"""Generates a self-contained HTML diligence report from pipeline outputs."""

from datetime import datetime


def generate_html_report(
    startup: dict,
    policy_result: dict,
    market_intel: dict,
    questions: list[dict],
    memo: dict,
    analyst_notes: str = "",
) -> str:
    company = startup.get("company", "Unknown Startup")
    policy_name = policy_result.get("policy", "Investment Policy")
    generated_at = datetime.now().strftime("%B %d, %Y at %H:%M")
    overall = policy_result.get("overall_status", "review")
    rec = memo.get("recommendation", {})
    action = rec.get("action", "HOLD")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Diligence Report — {company}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #f4f6f9; color: #1a1a2e; line-height: 1.6; }}
  .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
             color: white; padding: 2.5rem 3rem; }}
  .header h1 {{ font-size: 0.85rem; letter-spacing: 0.15em; text-transform: uppercase;
                opacity: 0.7; margin-bottom: 0.4rem; }}
  .header h2 {{ font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; }}
  .header .meta {{ font-size: 0.85rem; opacity: 0.65; }}
  .badge {{ display: inline-block; padding: 0.2rem 0.8rem; border-radius: 20px;
            font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
            letter-spacing: 0.05em; margin-left: 1rem; vertical-align: middle; }}
  .badge-pass {{ background: #d4edda; color: #155724; }}
  .badge-review {{ background: #fff3cd; color: #856404; }}
  .badge-proceed {{ background: #d4edda; color: #155724; }}
  .badge-hold {{ background: #fff3cd; color: #856404; }}
  .badge-pass-rec {{ background: #d4edda; color: #155724; }}
  .badge-hold-rec {{ background: #fff3cd; color: #856404; }}
  .badge-passr {{ background: #f8d7da; color: #721c24; }}
  .container {{ max-width: 1100px; margin: 2rem auto; padding: 0 1.5rem; }}
  .section {{ background: white; border-radius: 10px; padding: 1.8rem 2rem;
              margin-bottom: 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
  .section h2 {{ font-size: 1.1rem; font-weight: 700; color: #0f3460;
                 border-bottom: 2px solid #e8edf4; padding-bottom: 0.6rem;
                 margin-bottom: 1.2rem; text-transform: uppercase;
                 letter-spacing: 0.05em; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
  .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }}
  .field-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
                 gap: 0.8rem; }}
  .field {{ background: #f8f9fc; border-radius: 6px; padding: 0.7rem 1rem; }}
  .field .label {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em;
                   color: #6c757d; margin-bottom: 0.2rem; }}
  .field .value {{ font-weight: 600; font-size: 0.95rem; }}
  .check-row {{ display: flex; align-items: flex-start; gap: 0.6rem;
                padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0; }}
  .check-row:last-child {{ border-bottom: none; }}
  .check-icon {{ font-size: 1rem; flex-shrink: 0; margin-top: 0.1rem; }}
  .check-label {{ font-weight: 600; font-size: 0.9rem; }}
  .check-reason {{ font-size: 0.85rem; color: #555; }}
  ul.bullets {{ padding-left: 1.2rem; }}
  ul.bullets li {{ margin-bottom: 0.4rem; font-size: 0.9rem; }}
  .strength-item {{ background: #d4edda; border-left: 4px solid #28a745;
                    border-radius: 4px; padding: 0.5rem 0.8rem; margin-bottom: 0.5rem;
                    font-size: 0.9rem; }}
  .weakness-item {{ background: #f8d7da; border-left: 4px solid #dc3545;
                    border-radius: 4px; padding: 0.5rem 0.8rem; margin-bottom: 0.5rem;
                    font-size: 0.9rem; }}
  .missing-item {{ background: #fff3cd; border-left: 4px solid #ffc107;
                   border-radius: 4px; padding: 0.5rem 0.8rem; margin-bottom: 0.5rem;
                   font-size: 0.9rem; }}
  .risk-card {{ border-radius: 8px; padding: 1rem; border: 1px solid #e0e0e0; }}
  .risk-card .risk-header {{ display: flex; justify-content: space-between;
                              align-items: center; margin-bottom: 0.4rem; }}
  .risk-card .risk-area {{ font-weight: 700; font-size: 0.9rem; }}
  .risk-level {{ font-size: 0.75rem; font-weight: 700; padding: 0.15rem 0.5rem;
                 border-radius: 10px; text-transform: uppercase; }}
  .risk-high {{ background: #f8d7da; color: #721c24; border-left: 4px solid #dc3545; }}
  .risk-medium {{ background: #fff3cd; color: #856404; border-left: 4px solid #ffc107; }}
  .risk-low {{ background: #d4edda; color: #155724; border-left: 4px solid #28a745; }}
  .risk-level-high {{ background: #f8d7da; color: #721c24; }}
  .risk-level-medium {{ background: #fff3cd; color: #856404; }}
  .risk-level-low {{ background: #d4edda; color: #155724; }}
  .risk-desc {{ font-size: 0.82rem; color: #555; }}
  .q-group {{ margin-bottom: 1.2rem; }}
  .q-category {{ font-weight: 700; font-size: 0.9rem; color: #0f3460;
                 text-transform: uppercase; letter-spacing: 0.05em;
                 margin-bottom: 0.5rem; }}
  .q-item {{ padding: 0.5rem 0; border-bottom: 1px solid #f5f5f5;
             font-size: 0.88rem; }}
  .q-num {{ font-weight: 700; color: #0f3460; margin-right: 0.4rem; }}
  .rec-box {{ border-radius: 8px; padding: 1.5rem; text-align: center; }}
  .rec-proceed {{ background: #d4edda; border: 2px solid #28a745; }}
  .rec-hold {{ background: #fff3cd; border: 2px solid #ffc107; }}
  .rec-pass {{ background: #f8d7da; border: 2px solid #dc3545; }}
  .rec-action {{ font-size: 1.8rem; font-weight: 800; margin-bottom: 0.5rem; }}
  .rec-reason {{ font-size: 0.9rem; max-width: 700px; margin: 0 auto; }}
  .notes-box {{ background: #e8f4fd; border-left: 4px solid #007bff;
                border-radius: 4px; padding: 0.8rem 1rem; font-size: 0.88rem; }}
  .outlook-box {{ background: #f0f4ff; border-radius: 6px; padding: 1rem;
                  font-size: 0.9rem; font-style: italic; }}
  .competitor {{ padding: 0.4rem 0; border-bottom: 1px solid #f0f0f0;
                 font-size: 0.88rem; }}
  .competitor:last-child {{ border-bottom: none; }}
  .competitor strong {{ color: #0f3460; }}
  footer {{ text-align: center; padding: 2rem; font-size: 0.8rem; color: #999; }}
</style>
</head>
<body>

<!-- ── HEADER ──────────────────────────────────────────────────────────────── -->
<div class="header">
  <h1>AI Investment Diligence Report</h1>
  <h2>{company}
    <span class="badge badge-{overall}">{overall.upper()}</span>
    <span class="badge badge-{action.lower()}-rec">{action}</span>
  </h2>
  <div class="meta">
    Policy: {policy_name} &nbsp;·&nbsp; Generated: {generated_at}
  </div>
</div>

<div class="container">

<!-- ── COMPANY SNAPSHOT ──────────────────────────────────────────────────── -->
<div class="section">
  <h2>Company Snapshot</h2>
  <div class="field-grid">
    {_fields(startup)}
  </div>
</div>

<!-- ── POLICY ELIGIBILITY ────────────────────────────────────────────────── -->
<div class="section">
  <h2>Policy Eligibility</h2>
  {_policy_checks(policy_result)}
  {_analyst_notes_block(analyst_notes)}
</div>

<!-- ── MARKET INTELLIGENCE ───────────────────────────────────────────────── -->
<div class="section">
  <h2>Market Intelligence</h2>
  <p style="font-size:0.9rem;color:#555;margin-bottom:1rem;">
    <strong>Market Size:</strong> {market_intel.get("market_size", "—")}
  </p>
  <div class="grid-2">
    <div>
      <p style="font-weight:700;margin-bottom:0.5rem;">Market Trends</p>
      <ul class="bullets">
        {"".join(f"<li>{t}</li>" for t in market_intel.get("trends", []))}
      </ul>
      <p style="font-weight:700;margin:1rem 0 0.5rem;">Growth Signals</p>
      <ul class="bullets">
        {"".join(f"<li>{s}</li>" for s in market_intel.get("growth_signals", []))}
      </ul>
    </div>
    <div>
      <p style="font-weight:700;margin-bottom:0.5rem;">Key Competitors</p>
      {"".join(f'<div class="competitor"><strong>{c.get("name","")}</strong> — {c.get("description","")}</div>' for c in market_intel.get("competitors", []))}
      <p style="font-weight:700;margin:1rem 0 0.5rem;">Sector Challenges</p>
      <ul class="bullets">
        {"".join(f"<li>{ch}</li>" for ch in market_intel.get("challenges", []))}
      </ul>
    </div>
  </div>
  <div class="outlook-box" style="margin-top:1rem;">
    {market_intel.get("outlook", "")}
  </div>
</div>

<!-- ── INVESTMENT THESIS FIT ─────────────────────────────────────────────── -->
<div class="section">
  <h2>Investment Thesis Fit</h2>
  <p style="font-size:0.95rem;">{memo.get("thesis_fit", "—")}</p>
</div>

<!-- ── STRENGTHS & WEAKNESSES ────────────────────────────────────────────── -->
<div class="section">
  <h2>Strengths &amp; Weaknesses</h2>
  <div class="grid-2">
    <div>
      <p style="font-weight:700;margin-bottom:0.6rem;">Strengths</p>
      {"".join(f'<div class="strength-item">✓ {s}</div>' for s in memo.get("strengths", []))}
    </div>
    <div>
      <p style="font-weight:700;margin-bottom:0.6rem;">Weaknesses &amp; Red Flags</p>
      {"".join(f'<div class="weakness-item">⚠ {w}</div>' for w in memo.get("weaknesses", []))}
    </div>
  </div>
</div>

<!-- ── RISK ANALYSIS ─────────────────────────────────────────────────────── -->
<div class="section">
  <h2>Risk Analysis</h2>
  <div class="grid-3">
    {_risk_cards(memo.get("risk_analysis", []))}
  </div>
</div>

<!-- ── DILIGENCE QUESTIONS ───────────────────────────────────────────────── -->
<div class="section">
  <h2>Founder Diligence Questions</h2>
  {_questions_html(questions)}
</div>

<!-- ── MISSING INFORMATION ───────────────────────────────────────────────── -->
<div class="section">
  <h2>Missing Information</h2>
  {"".join(f'<div class="missing-item">❓ {m}</div>' for m in memo.get("missing_info", []))}
</div>

<!-- ── RECOMMENDATION ────────────────────────────────────────────────────── -->
<div class="section">
  <h2>Recommendation</h2>
  <div class="rec-box rec-{action.lower()}">
    <div class="rec-action">{action}</div>
    <div class="rec-reason">{rec.get("reason", "")}</div>
  </div>
</div>

</div><!-- /container -->

<footer>
  Generated by Policy-Aware AI Investment Diligence Copilot &nbsp;·&nbsp;
  {generated_at} &nbsp;·&nbsp; For internal use only
</footer>

</body>
</html>"""


# ── Private helpers ───────────────────────────────────────────────────────────

def _fields(startup: dict) -> str:
    display = {
        "Company": "company",
        "Country": "country",
        "Stage": "stage",
        "Sector": "sector",
        "Funding Ask": "funding_ask",
        "Business Model": "business_model",
        "Current Revenue": "current_revenue",
        "Claimed Traction": "claimed_traction",
        "Revenue Model": "revenue_model",
    }
    parts = []
    for label, key in display.items():
        value = startup.get(key, "—") or "—"
        parts.append(
            f'<div class="field"><div class="label">{label}</div>'
            f'<div class="value">{value}</div></div>'
        )
    return "".join(parts)


def _policy_checks(policy_result: dict) -> str:
    icons = {"pass": "✅", "caution": "⚠️", "fail": "❌"}
    rows = []
    for check in policy_result.get("results", []):
        icon = icons.get(check["status"], "❓")
        label = check["check"].replace("_", " ").title()
        reason = check.get("reason", "")
        rows.append(
            f'<div class="check-row">'
            f'<span class="check-icon">{icon}</span>'
            f'<div><div class="check-label">{label}</div>'
            f'<div class="check-reason">{reason}</div></div>'
            f'</div>'
        )
    return "".join(rows)


def _analyst_notes_block(notes: str) -> str:
    if not notes or not notes.strip():
        return ""
    return (
        f'<div class="notes-box" style="margin-top:1rem;">'
        f'<strong>Analyst Notes:</strong> {notes}</div>'
    )


def _risk_cards(risks: list[dict]) -> str:
    level_class = {"High": "risk-high", "Medium": "risk-medium", "Low": "risk-low"}
    level_badge = {"High": "risk-level-high", "Medium": "risk-level-medium", "Low": "risk-level-low"}
    cards = []
    for risk in risks:
        level = risk.get("level", "Medium")
        area = risk.get("area", "—")
        desc = risk.get("description", "")
        lc = level_class.get(level, "risk-medium")
        lb = level_badge.get(level, "risk-level-medium")
        cards.append(
            f'<div class="risk-card {lc}">'
            f'<div class="risk-header">'
            f'<span class="risk-area">{area}</span>'
            f'<span class="risk-level {lb}">{level}</span>'
            f'</div>'
            f'<div class="risk-desc">{desc}</div>'
            f'</div>'
        )
    return "".join(cards)


def _questions_html(questions: list[dict]) -> str:
    categories: dict[str, list[str]] = {}
    for q in questions:
        cat = q.get("category", "General")
        categories.setdefault(cat, []).append(q["question"])

    parts = []
    for category, qs in categories.items():
        items = "".join(
            f'<div class="q-item"><span class="q-num">Q{i}.</span>{q}</div>'
            for i, q in enumerate(qs, start=1)
        )
        parts.append(
            f'<div class="q-group">'
            f'<div class="q-category">{category}</div>'
            f'{items}</div>'
        )
    return "".join(parts)

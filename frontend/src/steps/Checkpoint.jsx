import { useState } from 'react'

const STATUS_ICON = { pass: '✅', caution: '⚠️', fail: '❌' }

export default function Checkpoint({ startup, policyResult, onApprove, onReject, onBack }) {
  const [notes, setNotes] = useState('')
  const company = startup?.company || 'this startup'
  const overall = policyResult?.overall_status

  return (
    <div className="step-container">
      <div className="step-header">
        <h1>Human Governance Checkpoint</h1>
        <p>
          The AI has completed first-pass policy evaluation. As the analyst, you must
          approve or reject before deeper diligence can proceed.
        </p>
      </div>

      <div
        className={`alert ${overall === 'pass' ? 'alert-success' : 'alert-warning'}`}
        style={{ marginBottom: '1.75rem' }}
      >
        {overall === 'pass'
          ? `✓ ${company} passed all policy checks.`
          : `⚠ ${company} has flagged policy items — review carefully.`}
      </div>

      <div className="card-grid">
        {/* Policy summary */}
        <div className="card">
          <div className="card-title">Policy Summary</div>
          {policyResult?.results?.map((check, i) => (
            <div className="policy-check-row" key={i}>
              <span className="policy-check-icon">{STATUS_ICON[check.status] || '❓'}</span>
              <div>
                <div className="policy-check-name">
                  {check.check.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </div>
                <div className="policy-check-reason">{check.reason}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Decision panel */}
        <div className="decision-block">
          <div className="decision-title">Your Decision</div>

          <div className="checkpoint-company">{company}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '0.35rem', marginBottom: '1.25rem' }}>
            {startup?.sector} · {startup?.stage} · {startup?.country}
          </div>

          <div style={{ marginBottom: '0.5rem' }}>
            <label>Analyst notes (optional)</label>
            <textarea
              className="textarea"
              placeholder="Add context or reasoning for your decision…"
              value={notes}
              onChange={e => setNotes(e.target.value)}
            />
          </div>

          <div className="decision-buttons">
            <button
              className="btn btn-success btn-lg btn-full"
              onClick={() => onApprove(notes)}
            >
              ✓ APPROVE
            </button>
            <button
              className="btn btn-danger btn-lg btn-full"
              onClick={() => onReject(notes)}
            >
              ✗ REJECT
            </button>
          </div>

          <p style={{ fontSize: '10.5px', color: 'var(--text-dim)', marginTop: '1rem', textAlign: 'center' }}>
            Policy compliance is a fiduciary obligation — the AI cannot proceed without your explicit decision.
          </p>
        </div>
      </div>

      <div className="step-nav">
        <button className="btn btn-secondary" onClick={onBack}>← Back</button>
      </div>
    </div>
  )
}

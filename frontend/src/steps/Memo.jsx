import { useState, useEffect } from 'react'
import Spinner from '../components/Spinner'

const LEVEL_CLASS = { High: 'badge-fail', Medium: 'badge-caution', Low: 'badge-pass' }

export default function Memo({ startup, policyResult, marketIntel, questions, onDone, onBack }) {
  const [memo, setMemo]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState('')

  useEffect(() => {
    (async () => {
      try {
        const res  = await fetch('/api/memo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            startup,
            policy_result: policyResult,
            market_intel: marketIntel,
            questions,
          }),
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || 'Memo generation failed')
        setMemo(data.memo)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    })()
  }, [startup, policyResult, marketIntel, questions])

  if (loading) {
    return (
      <div className="step-container">
        <div className="step-header">
          <h1>Investment Memo</h1>
          <p>Synthesising all data into a structured investment memo.</p>
        </div>
        <div className="card"><Spinner label="Generating investment memo…" /></div>
      </div>
    )
  }

  const rec    = memo?.recommendation || {}
  const action = rec.action || 'HOLD'
  const recCls = { PROCEED: 'proceed', HOLD: 'hold', PASS: 'pass' }[action] || 'hold'

  return (
    <div className="step-container">
      <div className="step-header">
        <h1>Investment Memo & Risk Analysis</h1>
        <p>AI-synthesised memo for <strong style={{ color: 'var(--text)' }}>{startup?.company}</strong>.</p>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: '1.25rem' }}>{error}</div>}

      {memo && (
        <>
          {/* Thesis fit */}
          <div className="section-title">Investment Thesis Fit</div>
          <div className="thesis-block">{memo.thesis_fit}</div>

          {/* Strengths + Weaknesses */}
          <div className="card-grid" style={{ marginBottom: '1.4rem' }}>
            <div>
              <div className="section-title">Strengths</div>
              {(memo.strengths || []).map((s, i) => (
                <div className="strength-item" key={i}>
                  <span className="item-icon">✓</span> {s}
                </div>
              ))}
            </div>
            <div>
              <div className="section-title">Weaknesses & Red Flags</div>
              {(memo.weaknesses || []).map((w, i) => (
                <div className="weakness-item" key={i}>
                  <span className="item-icon">✗</span> {w}
                </div>
              ))}
            </div>
          </div>

          {/* Risk grid */}
          <div className="section-title">Risk Analysis</div>
          <div className="card-grid-3" style={{ marginBottom: '1.4rem' }}>
            {(memo.risk_analysis || []).map((risk, i) => (
              <div className="risk-card" key={i}>
                <div className="risk-header">
                  <span className="risk-area">{risk.area}</span>
                  <span className={`badge ${LEVEL_CLASS[risk.level] || 'badge-caution'}`}>
                    {risk.level}
                  </span>
                </div>
                <div className="risk-desc">{risk.description}</div>
              </div>
            ))}
          </div>

          {/* Missing info */}
          {memo.missing_info?.length > 0 && (
            <>
              <div className="section-title">Missing Information</div>
              <div style={{ marginBottom: '1.4rem' }}>
                {memo.missing_info.map((m, i) => (
                  <div className="missing-item" key={i}>⚠ {m}</div>
                ))}
              </div>
            </>
          )}

          {/* Recommendation */}
          <div className={`recommendation-block ${recCls}`}>
            <div>
              <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', opacity: 0.6, marginBottom: '0.3rem' }}>
                Recommendation
              </div>
              <div className="rec-action">{action}</div>
            </div>
            <div className="rec-reason">{rec.reason}</div>
          </div>
        </>
      )}

      <div className="step-nav">
        <button className="btn btn-secondary" onClick={onBack}>← Back</button>
        <div className="step-nav-right">
          <button
            className="btn btn-primary btn-lg"
            onClick={() => onDone(memo)}
            disabled={!memo}
          >
            Generate Report →
          </button>
        </div>
      </div>
    </div>
  )
}

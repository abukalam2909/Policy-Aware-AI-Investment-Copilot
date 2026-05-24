import { useState, useEffect } from 'react'
import Spinner from '../components/Spinner'

const FIELDS = [
  ['Company',        'company'],
  ['Country',        'country'],
  ['Stage',          'stage'],
  ['Sector',         'sector'],
  ['Funding Ask',    'funding_ask'],
  ['Business Model', 'business_model'],
  ['Current Revenue','current_revenue'],
  ['Claimed Traction','claimed_traction'],
]

const STATUS_ICON  = { pass: '✅', caution: '⚠️', fail: '❌' }
const STATUS_CLASS = { pass: 'badge-pass', caution: 'badge-caution', fail: 'badge-fail' }

export default function PolicyCheck({ startup, onDone, onBack }) {
  const [policyResult, setPolicyResult] = useState(null)
  const [loading, setLoading]           = useState(true)
  const [error, setError]               = useState('')

  useEffect(() => {
    (async () => {
      try {
        const res  = await fetch('/api/policy-check', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ startup }),
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || 'Policy check failed')
        setPolicyResult(data.policy_result)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    })()
  }, [startup])

  if (loading) {
    return (
      <div className="step-container">
        <div className="step-header">
          <h1>Policy Check</h1>
          <p>Running eligibility checks against the investment policy.</p>
        </div>
        <div className="card"><Spinner label="Running policy checks…" /></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="step-container">
        <div className="alert alert-error">{error}</div>
        <div className="step-nav">
          <button className="btn btn-secondary" onClick={onBack}>← Back</button>
        </div>
      </div>
    )
  }

  const overall = policyResult?.overall_status

  return (
    <div className="step-container">
      <div className="step-header">
        <h1>Extraction & Policy Check</h1>
        <p>AI-extracted startup profile and automated policy eligibility results.</p>
      </div>

      <div
        className={`alert ${overall === 'pass' ? 'alert-success' : 'alert-warning'}`}
        style={{ marginBottom: '1.5rem' }}
      >
        {overall === 'pass'
          ? `✓ Policy check passed for ${startup.company}. Ready for human review.`
          : `⚠ Policy flagged items for ${startup.company}. Review before proceeding.`}
      </div>

      <div className="card-grid">
        {/* Startup Profile */}
        <div className="card">
          <div className="card-title">Extracted Startup Profile</div>
          {FIELDS.map(([label, key]) => (
            <div className="field-row" key={key}>
              <span className="field-label">{label}</span>
              <span className="field-value">{startup[key] || '—'}</span>
            </div>
          ))}
        </div>

        {/* Policy Results */}
        <div className="card">
          <div className="card-title">Policy Eligibility</div>
          {policyResult?.results?.map((check, i) => (
            <div className="policy-check-row" key={i}>
              <span className="policy-check-icon">{STATUS_ICON[check.status] || '❓'}</span>
              <div>
                <div className="policy-check-name">
                  {check.check.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  &nbsp;
                  <span className={`badge ${STATUS_CLASS[check.status] || ''}`}>{check.status}</span>
                </div>
                <div className="policy-check-reason">{check.reason}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="step-nav">
        <button className="btn btn-secondary" onClick={onBack}>← Back</button>
        <div className="step-nav-right">
          <button className="btn btn-primary btn-lg" onClick={() => onDone(policyResult)}>
            Proceed to Checkpoint →
          </button>
        </div>
      </div>
    </div>
  )
}

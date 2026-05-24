import { useState, useEffect } from 'react'
import Spinner from '../components/Spinner'

const STATUS_ICON  = { pass: '✅', caution: '⚠️', fail: '❌' }
const STATUS_CLASS = { pass: 'badge-pass', caution: 'badge-caution', fail: 'badge-fail' }
const STATUS_BORDER = {
  pass:    '1px solid var(--green-border)',
  caution: '1px solid var(--amber-border)',
  fail:    '1px solid var(--red-border)',
}
const STATUS_BG = {
  pass:    'var(--green-bg)',
  caution: 'var(--amber-bg)',
  fail:    'var(--red-bg)',
}

const FIELD_ICONS = {
  country:        '🌍',
  stage:          '📈',
  sector:         '🏭',
  funding_ask:    '💰',
  current_revenue:'💵',
  business_model: '💼',
  claimed_traction:'🎯',
}

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
          <h1>Extraction & Policy Check</h1>
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
  const passCount = policyResult?.results?.filter(r => r.status === 'pass').length || 0
  const totalCount = policyResult?.results?.length || 0

  return (
    <div className="step-container">
      <div className="step-header">
        <h1>Extraction & Policy Check</h1>
        <p>AI-extracted startup profile and automated eligibility results against the active investment policy.</p>
      </div>

      <div className="card-grid">

        {/* ── Left: Startup Profile ─────────────────────────────────────── */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          {/* Company header */}
          <div style={{
            padding: '1.25rem 1.4rem 1rem',
            borderBottom: '1px solid var(--border)',
            background: 'linear-gradient(135deg, var(--surface2), var(--surface))',
          }}>
            <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              Extracted Profile
            </div>
            <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text)', letterSpacing: '-0.01em', marginBottom: '0.5rem' }}>
              {startup.company || '—'}
            </div>
            <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
              {startup.stage   && <span className="badge badge-info">{startup.stage}</span>}
              {startup.country && <span className="badge" style={{ background: 'var(--surface3)', color: 'var(--text-muted)', border: '1px solid var(--border2)' }}>{startup.country}</span>}
              {startup.sector  && <span className="badge" style={{ background: 'var(--accent-glow)', color: 'var(--accent-text)', border: '1px solid rgba(232,160,32,0.2)' }}>{startup.sector}</span>}
            </div>
          </div>

          {/* Key metrics grid */}
          <div style={{
            display: 'grid', gridTemplateColumns: '1fr 1fr',
            gap: 0, borderBottom: '1px solid var(--border)',
          }}>
            {[
              ['Funding Ask',     startup.funding_ask],
              ['Current Revenue', startup.current_revenue],
            ].map(([label, val]) => (
              <div key={label} style={{
                padding: '0.9rem 1.2rem',
                borderRight: label === 'Funding Ask' ? '1px solid var(--border)' : 'none',
              }}>
                <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>{label}</div>
                <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--accent-text)' }}>{val || '—'}</div>
              </div>
            ))}
          </div>

          {/* Long text fields */}
          {[
            ['Business Model',    startup.business_model],
            ['Claimed Traction',  startup.claimed_traction],
          ].map(([label, val]) => (
            <div key={label} style={{
              padding: '0.9rem 1.2rem',
              borderBottom: '1px solid var(--border)',
            }}>
              <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '0.3rem' }}>{label}</div>
              <div style={{ fontSize: '12.5px', color: 'var(--text)', lineHeight: 1.55 }}>{val || '—'}</div>
            </div>
          ))}

          {/* Financial docs */}
          <div style={{ padding: '0.8rem 1.2rem' }}>
            <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '0.3rem' }}>Financial Docs</div>
            <span className={`badge ${startup.financial_docs_provided ? 'badge-pass' : 'badge-caution'}`}>
              {startup.financial_docs_provided ? 'Provided' : 'Not provided'}
            </span>
          </div>
        </div>

        {/* ── Right: Policy Eligibility ────────────────────────────────── */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          {/* Header with score */}
          <div style={{
            padding: '1.25rem 1.4rem 1rem',
            borderBottom: '1px solid var(--border)',
            background: 'linear-gradient(135deg, var(--surface2), var(--surface))',
            display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
          }}>
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                Policy Eligibility
              </div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: overall === 'pass' ? 'var(--green)' : 'var(--amber)', letterSpacing: '-0.01em' }}>
                {overall === 'pass' ? 'PASSED' : 'REVIEW REQUIRED'}
              </div>
            </div>
            <div style={{
              textAlign: 'center',
              background: overall === 'pass' ? 'var(--green-bg)' : 'var(--amber-bg)',
              border: `1px solid ${overall === 'pass' ? 'var(--green-border)' : 'var(--amber-border)'}`,
              borderRadius: 'var(--radius)',
              padding: '0.5rem 0.85rem',
            }}>
              <div style={{ fontSize: '22px', fontWeight: 800, color: overall === 'pass' ? 'var(--green)' : 'var(--amber)' }}>
                {passCount}/{totalCount}
              </div>
              <div style={{ fontSize: '9.5px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>checks</div>
            </div>
          </div>

          {/* Check rows */}
          <div style={{ padding: '0.75rem 1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {policyResult?.results?.map((check, i) => (
              <div key={i} style={{
                display: 'flex', gap: '0.75rem', alignItems: 'flex-start',
                padding: '0.75rem 0.9rem',
                borderRadius: 'var(--radius-sm)',
                background: STATUS_BG[check.status] || 'var(--surface2)',
                border: STATUS_BORDER[check.status] || '1px solid var(--border)',
              }}>
                <span style={{ fontSize: '15px', marginTop: '1px', flexShrink: 0 }}>
                  {STATUS_ICON[check.status] || '❓'}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--text)' }}>
                      {check.check.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                    <span className={`badge ${STATUS_CLASS[check.status] || ''}`}>{check.status}</span>
                  </div>
                  <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                    {check.reason}
                  </div>
                </div>
              </div>
            ))}
          </div>
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

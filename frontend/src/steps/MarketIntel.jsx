import { useState, useEffect } from 'react'
import Spinner from '../components/Spinner'

export default function MarketIntel({ startup, policyResult, analystNotes, onDone, onBack }) {
  const [intel, setIntel]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState('')

  useEffect(() => {
    (async () => {
      try {
        const res  = await fetch('/api/market-intel', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ startup }),
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || 'Market intel failed')
        setIntel(data.market_intel)
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
          <h1>Market Intelligence</h1>
          <p>Researching the competitive landscape and market dynamics.</p>
        </div>
        <div className="card"><Spinner label="AI is researching the market…" /></div>
      </div>
    )
  }

  return (
    <div className="step-container">
      <div className="step-header">
        <h1>Market Intelligence</h1>
        <p>AI-synthesised market research for <strong style={{ color: 'var(--text)' }}>{startup?.company}</strong> in {startup?.sector}.</p>
      </div>

      {analystNotes && (
        <div className="alert alert-info" style={{ marginBottom: '1.4rem' }}>
          💬 Analyst notes: {analystNotes}
        </div>
      )}

      {error && <div className="alert alert-error" style={{ marginBottom: '1.4rem' }}>{error}</div>}

      {intel && (
        <>
          <div className="market-size-display">
            <div>
              <div className="market-size-label">Total Addressable Market</div>
              <div className="market-size-value">{intel.market_size}</div>
            </div>
          </div>

          <div className="card-grid" style={{ marginBottom: '1.2rem' }}>
            {/* Trends */}
            <div className="intel-card">
              <div className="intel-card-header">
                <div className="intel-card-icon">📈</div>
                <span className="intel-card-title">Market Trends</span>
              </div>
              <ul className="intel-list">
                {(intel.trends || []).map((t, i) => <li key={i}>{t}</li>)}
              </ul>
            </div>

            {/* Competitors */}
            <div className="intel-card">
              <div className="intel-card-header">
                <div className="intel-card-icon">🏢</div>
                <span className="intel-card-title">Key Competitors</span>
              </div>
              {(intel.competitors || []).map((c, i) => (
                <div className="competitor-item" key={i}>
                  <div className="competitor-name">{c.name}</div>
                  <div className="competitor-desc">{c.description}</div>
                </div>
              ))}
            </div>

            {/* Growth signals */}
            <div className="intel-card">
              <div className="intel-card-header">
                <div className="intel-card-icon">🚀</div>
                <span className="intel-card-title">Growth Signals</span>
              </div>
              <ul className="intel-list">
                {(intel.growth_signals || []).map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>

            {/* Challenges */}
            <div className="intel-card">
              <div className="intel-card-header">
                <div className="intel-card-icon">⚠️</div>
                <span className="intel-card-title">Sector Challenges</span>
              </div>
              <ul className="intel-list">
                {(intel.challenges || []).map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            </div>
          </div>

          <div className="outlook-block">
            <strong style={{ color: 'var(--blue)', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Market Outlook&nbsp;&nbsp;
            </strong>
            {intel.outlook}
          </div>
        </>
      )}

      <div className="step-nav">
        <button className="btn btn-secondary" onClick={onBack}>← Back</button>
        <div className="step-nav-right">
          <button className="btn btn-primary btn-lg" onClick={() => onDone(intel)} disabled={!intel}>
            Generate Diligence Questions →
          </button>
        </div>
      </div>
    </div>
  )
}

const STATUS_ICON = { pass: '✅', caution: '⚠️', fail: '❌' }

export default function Rejected({ startup, policyResult, analystNotes, onRestart }) {
  const company = startup?.company || 'this startup'

  return (
    <div className="step-container">
      <div className="rejected-screen">
        <div className="rejected-icon">🚫</div>
        <div className="rejected-title">{company} Rejected</div>
        <div className="rejected-sub">
          The analyst has rejected this opportunity. The AI will not proceed with deeper diligence.
        </div>

        {analystNotes && (
          <div className="alert alert-warning" style={{ width: '100%', marginBottom: '1.4rem', textAlign: 'left' }}>
            💬 Analyst notes: {analystNotes}
          </div>
        )}

        <div className="card" style={{ width: '100%', textAlign: 'left', marginBottom: '1.5rem' }}>
          <div className="card-title">Policy Results</div>
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

        <button className="btn btn-primary btn-lg" onClick={onRestart}>
          🔄 Start a New Analysis
        </button>
      </div>
    </div>
  )
}

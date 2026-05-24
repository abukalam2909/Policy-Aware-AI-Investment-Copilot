const STEPS = [
  { label: 'Upload & Extract',     sub: 'PDF pitch deck' },
  { label: 'Policy Check',         sub: 'Eligibility screening' },
  { label: 'Human Checkpoint',     sub: 'Analyst decision' },
  { label: 'Market Intelligence',  sub: 'Sector research' },
  { label: 'Diligence Questions',  sub: 'Founder-specific' },
  { label: 'Investment Memo',      sub: 'Risk & recommendation' },
  { label: 'Final Report',         sub: 'Download & deliver' },
]

export default function Sidebar({ step, health }) {
  const policy = health?.policy

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">📊</div>
          <span className="sidebar-logo-text">Diligence Copilot</span>
        </div>
        <div className="sidebar-tagline">Policy-Aware AI</div>
      </div>

      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Workflow</div>
        <div className="step-track">
          {STEPS.map((s, i) => {
            const num = i + 1
            const isCompleted = num < step
            const isActive    = num === step
            const cls = isCompleted ? 'completed' : isActive ? 'active' : ''
            return (
              <div key={num} className={`step-item ${cls}`}>
                <div className="step-circle">
                  {isCompleted ? '✓' : num}
                </div>
                <div className="step-label-wrap">
                  <div className="step-label">{s.label}</div>
                  <div className="step-sublabel">{s.sub}</div>
                </div>
              </div>
            )
          })}
        </div>
      </nav>

      <div className="sidebar-bottom">
        <div className={`status-pill ${health?.claude_connected ? 'connected' : 'offline'}`}>
          <span className="status-dot" />
          {health?.claude_connected ? 'Claude API connected' : 'Heuristic fallback'}
        </div>
        {policy && (
          <div className="policy-info">
            <div className="policy-name">{policy.name}</div>
            <div className="policy-meta">
              {policy.geographies?.join(', ')}<br />
              Stages: {policy.stages?.join(', ')}
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}

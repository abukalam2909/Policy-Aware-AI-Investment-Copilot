import { useState, useEffect } from 'react'
import Spinner from '../components/Spinner'

export default function Report({ startup, policyResult, marketIntel, questions, memo, analystNotes, onBack, onRestart }) {
  const [reportHtml, setReportHtml] = useState(null)
  const [loading, setLoading]       = useState(true)
  const [email, setEmail]           = useState('')
  const [sending, setSending]       = useState(false)
  const [toast, setToast]           = useState(null)
  const [error, setError]           = useState('')

  const company  = startup?.company || 'startup'
  const safeName = company.replace(/\s+/g, '_')

  useEffect(() => {
    (async () => {
      try {
        const res  = await fetch('/api/report', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            startup, policy_result: policyResult,
            market_intel: marketIntel, questions, memo,
            analyst_notes: analystNotes,
          }),
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || 'Report generation failed')
        setReportHtml(data.report_html)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const showToast = (msg, type) => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 4000)
  }

  const downloadReport = () => {
    const blob = new Blob([reportHtml], { type: 'text/html' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = `${safeName}_diligence_report.html`
    a.click()
    URL.revokeObjectURL(url)
  }

  const sendEmail = async () => {
    if (!email) { showToast('Enter a recipient email address.', 'error'); return }
    setSending(true)
    try {
      const res  = await fetch('/api/send-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to_email: email, company, report_html: reportHtml }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Send failed')
      showToast(`Report sent to ${email}`, 'success')
    } catch (e) {
      showToast(e.message, 'error')
    } finally {
      setSending(false)
    }
  }

  if (loading) {
    return (
      <div className="step-container">
        <div className="step-header">
          <h1>Diligence Report</h1>
          <p>Compiling the full report from all pipeline outputs.</p>
        </div>
        <div className="card"><Spinner label="Generating polished HTML report…" /></div>
      </div>
    )
  }

  return (
    <div className="step-container">
      <div className="step-header">
        <h1>Diligence Report</h1>
        <p>Your AI-generated investment diligence report for <strong style={{ color: 'var(--text)' }}>{company}</strong> is ready.</p>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: '1.25rem' }}>{error}</div>}

      {reportHtml && (
        <>
          <div className="report-actions">
            {/* Download */}
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div className="card-title">Download Report</div>
              <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                Self-contained HTML file — open in any browser.
              </p>
              <button className="btn btn-primary btn-full" onClick={downloadReport}>
                ↓ Download HTML Report
              </button>
            </div>

            {/* Email */}
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div className="card-title">Send via Gmail</div>
              <div>
                <label>Recipient email</label>
                <input
                  className="input"
                  type="email"
                  placeholder="analyst@sagard.com"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                />
              </div>
              <button
                className="btn btn-secondary btn-full"
                onClick={sendEmail}
                disabled={sending}
              >
                {sending ? 'Sending…' : '✉ Send Report'}
              </button>
            </div>
          </div>

          {/* Preview */}
          <div className="report-preview-wrap">
            <div className="report-preview-label">Report Preview</div>
            <iframe
              srcDoc={reportHtml}
              title="Diligence Report Preview"
              style={{ width: '100%', height: '640px', border: 'none', display: 'block' }}
            />
          </div>
        </>
      )}

      <div className="step-nav">
        <button className="btn btn-secondary" onClick={onBack}>← Back to Memo</button>
        <div className="step-nav-right">
          <button className="btn btn-primary" onClick={onRestart}>
            🔄 New Analysis
          </button>
        </div>
      </div>

      {toast && (
        <div className={`toast toast-${toast.type}`}>{toast.msg}</div>
      )}
    </div>
  )
}

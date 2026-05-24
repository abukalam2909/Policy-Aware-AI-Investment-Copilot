import { useState, useEffect } from 'react'
import Spinner from '../components/Spinner'

export default function Questions({ startup, policyResult, marketIntel, onDone, onBack }) {
  const [questions, setQuestions] = useState(null)
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState('')

  useEffect(() => {
    (async () => {
      try {
        const res  = await fetch('/api/questions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ startup, policy_result: policyResult, market_intel: marketIntel }),
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || 'Question generation failed')
        setQuestions(data.questions)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    })()
  }, [startup, policyResult, marketIntel])

  if (loading) {
    return (
      <div className="step-container">
        <div className="step-header">
          <h1>Diligence Questions</h1>
          <p>Generating founder-specific questions based on the startup's claims and market context.</p>
        </div>
        <div className="card"><Spinner label="Generating diligence questions…" /></div>
      </div>
    )
  }

  // Group by category
  const categories = {}
  ;(questions || []).forEach(q => {
    const cat = q.category || 'General'
    if (!categories[cat]) categories[cat] = []
    categories[cat].push(q.question)
  })

  return (
    <div className="step-container">
      <div className="step-header">
        <h1>Founder-Specific Diligence Questions</h1>
        <p>
          {questions?.length || 0} questions generated for{' '}
          <strong style={{ color: 'var(--text)' }}>{startup?.company}</strong> — grounded in their specific claims and the market context.
        </p>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: '1.25rem' }}>{error}</div>}

      {Object.entries(categories).map(([category, qs], ci) => (
        <div className="question-category" key={ci}>
          <div className="category-header">
            <div className="category-bar" />
            <span className="category-name">{category}</span>
          </div>
          {qs.map((q, qi) => (
            <div className="question-item" key={qi}>
              <span className="question-num">Q{qi + 1}</span>
              <span className="question-text">{q}</span>
            </div>
          ))}
        </div>
      ))}

      <div className="step-nav">
        <button className="btn btn-secondary" onClick={onBack}>← Back</button>
        <div className="step-nav-right">
          <button
            className="btn btn-primary btn-lg"
            onClick={() => onDone(questions)}
            disabled={!questions}
          >
            Generate Investment Memo →
          </button>
        </div>
      </div>
    </div>
  )
}

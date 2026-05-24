import { useState, useRef } from 'react'
import Spinner from '../components/Spinner'

export default function Upload({ onDone }) {
  const [file, setFile]       = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef()

  const handleFile = (f) => {
    if (!f) return
    if (!f.name.toLowerCase().endsWith('.pdf')) {
      setError('Please upload a PDF file.')
      return
    }
    setError('')
    setFile(f)
  }

  const extract = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch('/api/extract', { method: 'POST', body: form })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Extraction failed')
      onDone(data.startup)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="step-container">
        <div className="step-header">
          <h1>Upload Pitch Deck</h1>
          <p>AI is reading and extracting the startup profile from your PDF.</p>
        </div>
        <div className="card">
          <Spinner label="Claude is reading the pitch deck…" />
        </div>
      </div>
    )
  }

  return (
    <div className="step-container">
      <div className="step-header">
        <h1>Upload Pitch Deck</h1>
        <p>Drop a startup pitch deck PDF. Our AI extracts the company profile and runs an instant policy eligibility check.</p>
      </div>

      <div
        className={`dropzone ${dragging ? 'drag-over' : ''}`}
        onClick={() => inputRef.current.click()}
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => {
          e.preventDefault()
          setDragging(false)
          handleFile(e.dataTransfer.files[0])
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          style={{ display: 'none' }}
          onChange={e => handleFile(e.target.files[0])}
        />
        <div className="dropzone-icon">📄</div>
        <div className="dropzone-title">Drop your pitch deck here</div>
        <div className="dropzone-sub">or click to browse — PDF only</div>

        {file && (
          <div className="file-selected" onClick={e => e.stopPropagation()}>
            <span>✓</span> {file.name} &nbsp;·&nbsp; {(file.size / 1024).toFixed(0)} KB
          </div>
        )}
      </div>

      {error && (
        <div className="alert alert-error" style={{ marginTop: '1rem' }}>⚠ {error}</div>
      )}

      <div className="step-nav">
        <span />
        <button
          className="btn btn-primary btn-lg"
          onClick={extract}
          disabled={!file}
        >
          Extract Startup Data →
        </button>
      </div>
    </div>
  )
}

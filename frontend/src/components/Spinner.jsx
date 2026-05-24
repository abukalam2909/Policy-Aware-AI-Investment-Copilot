export default function Spinner({ label = 'Processing…' }) {
  return (
    <div className="spinner-wrap">
      <div className="spinner" />
      <span className="spinner-label">{label}</span>
    </div>
  )
}

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import CareerCard from '../components/CareerCard'
import { Spinner } from '../components/ui'

const DEFAULTS = {
  math: 5, logical_reasoning: 5, creativity: 5, communication: 5,
  programming: 5, data_interest: 5, design_interest: 5, business_interest: 5,
}

export default function Assessment() {
  const [labels, setLabels] = useState({})
  const [scores, setScores] = useState(DEFAULTS)
  const [skills, setSkills] = useState([])
  const [results, setResults] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.careers().then((d) => setLabels(d.feature_labels || {})).catch(() => {})
    api.getProfile().then((p) => setSkills(p.skills || [])).catch(() => {})
  }, [])

  async function submit(e) {
    e.preventDefault()
    setBusy(true); setError('')
    try {
      const data = await api.predict({ scores, skills })
      setResults(data.predictions)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <h1>Career Assessment 📝</h1>
      <p className="page-sub">Rate yourself honestly from 0–10 on each dimension. The ML model predicts your top-3 careers.</p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="card" style={{ marginBottom: 20 }}>
        <form onSubmit={submit}>
          {Object.keys(DEFAULTS).map((f) => (
            <div className="slider-row" key={f}>
              <label htmlFor={f}><strong>{labels[f] || f}</strong></label>
              <input id={f} type="range" min="0" max="10" step="0.5" value={scores[f]}
                onChange={(e) => setScores({ ...scores, [f]: Number(e.target.value) })} />
              <output>{scores[f]}</output>
            </div>
          ))}
          <div style={{ marginTop: 18, display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
            <button className="btn btn-primary" disabled={busy}>
              {busy ? 'Analysing…' : 'Predict my careers'}
            </button>
            <span className="muted" style={{ fontSize: 13.5 }}>
              Using {skills.length} skill(s) from your profile for calibration.
            </span>
          </div>
        </form>
      </div>

      {busy && <Spinner />}
      {results && (
        <>
          <h2>Your top-3 career matches</h2>
          <div className="grid grid-3" style={{ marginBottom: 18 }}>
            {results.map((p, i) => <CareerCard key={p.career} career={p} rank={i + 1} />)}
          </div>
          <div className="card" style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
            <strong>Next step:</strong>
            <span className="muted">See the skill gap for your #1 match and generate its roadmap.</span>
            <Link className="btn btn-primary btn-sm" to={`/app/skill-gap?career=${encodeURIComponent(results[0].career)}`}>
              Skill gap for {results[0].career}
            </Link>
            <Link className="btn btn-ghost btn-sm" to={`/app/roadmap?career=${encodeURIComponent(results[0].career)}`}>
              6-week roadmap
            </Link>
          </div>
        </>
      )}
    </>
  )
}

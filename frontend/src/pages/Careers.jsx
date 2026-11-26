import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import CareerCard from '../components/CareerCard'
import { Spinner } from '../components/ui'

export default function Careers() {
  const [careers, setCareers] = useState(null)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')

  useEffect(() => {
    api.careers().then((d) => setCareers(d.careers)).catch((e) => setError(e.message))
  }, [])

  const shown = (careers || []).filter((c) =>
    c.career.toLowerCase().includes(query.toLowerCase()) ||
    c.required_skills.some((s) => s.toLowerCase().includes(query.toLowerCase())))

  return (
    <>
      <h1>Explore Careers 🎯</h1>
      <p className="page-sub">All 8 careers the system knows — required skills, demand and indicative India fresher salaries.</p>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="form-group" style={{ maxWidth: 420 }}>
        <input className="input" placeholder="Search a career or a skill (e.g. Python)…"
          value={query} onChange={(e) => setQuery(e.target.value)} />
      </div>
      {!careers && !error && <Spinner />}
      {careers && shown.length === 0 && (
        <div className="empty"><h3>No matches</h3><p>Try a different career or skill name.</p></div>
      )}
      <div className="grid grid-3">
        {shown.map((c) => (
          <div key={c.career}>
            <CareerCard career={c} />
            <div style={{ display: 'flex', gap: 8, marginTop: 10 }}>
              <Link className="btn btn-ghost btn-sm" to={`/app/skill-gap?career=${encodeURIComponent(c.career)}`}>Skill gap</Link>
              <Link className="btn btn-ghost btn-sm" to={`/app/roadmap?career=${encodeURIComponent(c.career)}`}>Roadmap</Link>
            </div>
          </div>
        ))}
      </div>
    </>
  )
}

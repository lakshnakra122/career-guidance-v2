import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { CareerPicker, useCareerSelection } from './SkillGap'
import { MatchBar, Spinner } from '../components/ui'

export default function Roadmap() {
  const { career, setCareer, careerNames, skills } = useCareerSelection()
  const [weeks, setWeeks] = useState(6)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!career) return
    setLoading(true); setError('')
    api.roadmap({ career, skills, weeks })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [career, skills, weeks])

  return (
    <>
      <h1>Your Roadmap 🗺️</h1>
      <p className="page-sub">A week-by-week plan built from your skill gaps — foundations first, portfolio project last.</p>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        <CareerPicker career={career} setCareer={setCareer} careerNames={careerNames} />
        <div className="form-group" style={{ width: 150 }}>
          <label className="field" htmlFor="weeks">Duration (weeks)</label>
          <select id="weeks" className="select" value={weeks} onChange={(e) => setWeeks(Number(e.target.value))}>
            {[4, 6, 8, 10, 12].map((w) => <option key={w} value={w}>{w} weeks</option>)}
          </select>
        </div>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {loading && <Spinner />}
      {data && !loading && (
        <>
          <div className="card" style={{ marginBottom: 22 }}>
            <h3 style={{ marginBottom: 8 }}>{data.career} — starting point</h3>
            <MatchBar pct={data.coverage_pct} />
            <div className="chip-row" style={{ marginTop: 12 }}>
              <span className="muted" style={{ fontSize: 13.5 }}>To learn:</span>
              {data.gaps.length ? data.gaps.map((s) => <span key={s} className="pill warn">{s}</span>)
                : <span className="pill good">No gaps — advanced project plan</span>}
            </div>
          </div>
          <div className="timeline">
            {data.plan.map((w) => (
              <div className="week-node card" key={w.week}>
                <span className="pill">Week {w.week}</span>
                <h3 style={{ marginTop: 8 }}>{w.title}</h3>
                {w.focus_skills.length > 0 && (
                  <div className="chip-row">{w.focus_skills.map((s) => <span key={s} className="pill">{s}</span>)}</div>
                )}
                <ul>{w.tasks.map((t) => <li key={t}>{t}</li>)}</ul>
                {w.courses.length > 0 && (
                  <p style={{ fontSize: 14 }}>
                    📚 {w.courses.map((c, i) => (
                      <span key={c.title}>{i > 0 ? ' · ' : ''}
                        <a href={c.link} target="_blank" rel="noreferrer">{c.title} ({c.provider})</a>
                      </span>
                    ))}
                  </p>
                )}
                <p style={{ fontSize: 14, marginBottom: 0 }}><strong>✔ Checkpoint:</strong> {w.checkpoint}</p>
              </div>
            ))}
          </div>
          <Link className="btn btn-primary" to={`/app/study-plan?career=${encodeURIComponent(career)}`}>
            Turn this into a daily study plan →
          </Link>
        </>
      )}
    </>
  )
}

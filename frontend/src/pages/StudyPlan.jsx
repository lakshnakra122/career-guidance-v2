import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { CareerPicker, useCareerSelection } from './SkillGap'
import { Spinner } from '../components/ui'

export default function StudyPlan() {
  const { career, setCareer, careerNames, skills } = useCareerSelection()
  const [hours, setHours] = useState(2)
  const [days, setDays] = useState(6)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.getProfile().then((p) => { if (p.hours_per_day) setHours(p.hours_per_day) }).catch(() => {})
  }, [])

  useEffect(() => {
    if (!career) return
    setLoading(true); setError('')
    api.studyPlan({ career, skills, hours_per_day: hours, days_per_week: days, weeks: 6 })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [career, skills, hours, days])

  return (
    <>
      <h1>Study Plan Generator 📅</h1>
      <p className="page-sub">Your roadmap converted into a realistic daily routine based on the time you actually have.</p>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        <CareerPicker career={career} setCareer={setCareer} careerNames={careerNames} />
        <div className="form-group" style={{ width: 160 }}>
          <label className="field" htmlFor="hours">Hours per day</label>
          <select id="hours" className="select" value={hours} onChange={(e) => setHours(Number(e.target.value))}>
            {[1, 1.5, 2, 3, 4, 5, 6].map((h) => <option key={h} value={h}>{h} hrs/day</option>)}
          </select>
        </div>
        <div className="form-group" style={{ width: 160 }}>
          <label className="field" htmlFor="days">Days per week</label>
          <select id="days" className="select" value={days} onChange={(e) => setDays(Number(e.target.value))}>
            {[3, 4, 5, 6, 7].map((d) => <option key={d} value={d}>{d} days</option>)}
          </select>
        </div>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {loading && <Spinner />}
      {data && !loading && (
        <>
          <div className="grid grid-3" style={{ marginBottom: 18 }}>
            <div className="card center"><div className="match-ring">{data.total_hours}h</div><span className="muted">Total over {data.weeks} weeks</span></div>
            <div className="card center"><div className="match-ring">{data.hours_per_day}h</div><span className="muted">Per study day</span></div>
            <div className="card center"><div className="match-ring">{data.days_per_week} days</div><span className="muted">Per week</span></div>
          </div>

          <h2 style={{ marginBottom: 12 }}>Your daily routine</h2>
          <div className="grid grid-3" style={{ marginBottom: 22 }}>
            {data.daily_routine.map((b) => (
              <div className="card" key={b.block}>
                <h3>{b.block} · {b.minutes_per_day} min</h3>
                <div className="progress" style={{ margin: '8px 0' }}><div style={{ width: `${b.share_pct}%` }} /></div>
                <p className="muted" style={{ margin: 0 }}>{b.detail}</p>
              </div>
            ))}
          </div>

          <h2 style={{ marginBottom: 12 }}>Week-by-week schedule</h2>
          <div className="grid grid-2" style={{ marginBottom: 18 }}>
            {data.schedule.map((w) => (
              <div className="card" key={w.week}>
                <span className="pill">Week {w.week} · {w.hours_budget}h budget</span>
                <h3 style={{ marginTop: 8 }}>{w.title}</h3>
                {w.focus_skills.length > 0 && (
                  <div className="chip-row">{w.focus_skills.map((s) => <span key={s} className="pill">{s}</span>)}</div>
                )}
                <p className="muted" style={{ marginBottom: 0, fontSize: 14 }}><strong>✔</strong> {w.checkpoint}</p>
              </div>
            ))}
          </div>

          <div className="card">
            <h3>💡 Tips that make plans stick</h3>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {data.tips.map((t) => <li key={t} style={{ marginBottom: 6 }}>{t}</li>)}
            </ul>
          </div>
        </>
      )}
    </>
  )
}

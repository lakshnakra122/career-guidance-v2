import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import { EmptyState, MatchBar, Spinner } from '../components/ui'

export function useCareerSelection() {
  const [params] = useSearchParams()
  const [careerNames, setCareerNames] = useState([])
  const [career, setCareer] = useState(params.get('career') || '')
  const [skills, setSkills] = useState([])

  useEffect(() => {
    api.careers().then((d) => {
      const names = d.careers.map((c) => c.career)
      setCareerNames(names)
      setCareer((cur) => cur || names[0] || '')
    }).catch(() => {})
    api.getProfile().then((p) => {
      setSkills(p.skills || [])
      setCareer((cur) => cur || p.target_career || '')
    }).catch(() => {})
  }, [])

  return { career, setCareer, careerNames, skills, setSkills }
}

export function CareerPicker({ career, setCareer, careerNames }) {
  return (
    <div className="form-group" style={{ maxWidth: 380 }}>
      <label className="field" htmlFor="career-select">Career</label>
      <select id="career-select" className="select" value={career}
        onChange={(e) => setCareer(e.target.value)}>
        {careerNames.map((c) => <option key={c} value={c}>{c}</option>)}
      </select>
    </div>
  )
}

export default function SkillGap() {
  const { career, setCareer, careerNames, skills } = useCareerSelection()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!career) return
    setLoading(true); setError('')
    api.recommendations({ career, skills })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [career, skills])

  return (
    <>
      <h1>Skill-Gap Analysis 🧩</h1>
      <p className="page-sub">Your profile skills vs. what the career demands — and the courses that close each gap.</p>
      <CareerPicker career={career} setCareer={setCareer} careerNames={careerNames} />
      {error && <div className="alert alert-error">{error}</div>}
      {loading && <Spinner />}
      {data && !loading && (
        <>
          <div className="card" style={{ marginBottom: 18 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
              <div>
                <h3 style={{ marginBottom: 2 }}>{data.career}</h3>
                <span className="muted">{data.meta.tagline}</span>
              </div>
              <span className="pill good">₹{data.meta.salary_min_lpa}–{data.meta.salary_max_lpa} LPA · Demand: {data.meta.demand}</span>
            </div>
            <div style={{ marginTop: 16 }}><MatchBar pct={data.coverage_pct} /></div>
            <p className="muted" style={{ fontSize: 13.5 }}>
              You already cover {data.matched.length} of {data.required.length} required skills.
            </p>
            <h4 style={{ margin: '14px 0 6px' }}>✅ You have</h4>
            <div className="chip-row">
              {data.matched.length ? data.matched.map((s) => <span key={s} className="pill good">{s}</span>)
                : <span className="muted">None yet — add skills in your profile.</span>}
            </div>
            <h4 style={{ margin: '14px 0 6px' }}>🎯 To learn</h4>
            <div className="chip-row">
              {data.gaps.length ? data.gaps.map((s) => <span key={s} className="pill warn">{s}</span>)
                : <span className="pill good">No gaps — you cover everything!</span>}
            </div>
          </div>

          <h2 style={{ marginBottom: 12 }}>Recommended courses</h2>
          {data.courses.length === 0 && <EmptyState icon="🎓" title="No courses needed" hint="You already have every required skill for this career." />}
          <div className="grid grid-2" style={{ marginBottom: 18 }}>
            {data.courses.map((c) => (
              <a key={c.skill + c.title} className="card" href={c.link} target="_blank" rel="noreferrer" style={{ color: 'inherit' }}>
                <span className="pill">{c.skill}</span>
                <h3 style={{ marginTop: 10 }}>{c.title}</h3>
                <span className="muted">{c.provider} · Open course ↗</span>
              </a>
            ))}
          </div>

          <h2 style={{ marginBottom: 12 }}>Portfolio project ideas</h2>
          <div className="card" style={{ marginBottom: 18 }}>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {data.projects.map((p) => <li key={p} style={{ marginBottom: 6 }}>{p}</li>)}
            </ul>
          </div>
          <Link className="btn btn-primary" to={`/app/roadmap?career=${encodeURIComponent(career)}`}>
            Generate my roadmap →
          </Link>
        </>
      )}
    </>
  )
}

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import CareerCard from '../components/CareerCard'
import { Spinner } from '../components/ui'
import { useAuth } from '../context/AuthContext'

const FIELDS = ['math', 'logical_reasoning', 'creativity', 'communication',
  'programming', 'data_interest', 'design_interest', 'business_interest']

const HINTS = {
  math: 'Your confidence in maths & statistics',
  logical_reasoning: 'Puzzles, aptitude, problem solving',
  creativity: 'New ideas, content, innovation',
  communication: 'Speaking, writing, presenting',
  programming: 'Coding in any language',
  data_interest: 'Working with data, charts, numbers',
  design_interest: 'UI, visuals, how things look',
  business_interest: 'Business, marketing, management',
}

const PRESET_SKILLS = ['Python', 'Java', 'SQL', 'HTML/CSS', 'JavaScript', 'React',
  'Excel', 'Power BI', 'Machine Learning', 'Git', 'Communication', 'Leadership',
  'Problem Solving', 'UI/UX Design', 'Cloud Basics']

const formGrid = {
  display: 'grid', gap: 14,
  gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
}

export default function Assessment() {
  const { user } = useAuth()
  const [labels, setLabels] = useState({})
  const [careerNames, setCareerNames] = useState([])
  const [details, setDetails] = useState({
    name: '', education: '', semester: '', tenth: '', twelfth: '', cgpa: '',
  })
  const [scores, setScores] = useState(Object.fromEntries(FIELDS.map((f) => [f, 5])))
  const [skills, setSkills] = useState([])
  const [customSkill, setCustomSkill] = useState('')
  const [interest, setInterest] = useState('')
  const [results, setResults] = useState(null)
  const [submitted, setSubmitted] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.careers().then((d) => {
      setLabels(d.feature_labels || {})
      setCareerNames((d.careers || []).map((c) => c.career))
    }).catch(() => {})
    api.getProfile().then((p) => {
      setSkills(p.skills || [])
      setInterest(p.target_career || '')
      setDetails((prev) => ({
        ...prev,
        name: p.name || user?.name || '',
        education: p.education || '',
        cgpa: p.cgpa ?? '',
      }))
    }).catch(() => {
      setDetails((prev) => ({ ...prev, name: user?.name || '' }))
    })
  }, [user])

  function toggleSkill(s) {
    setSkills((prev) => (prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]))
  }

  function addCustomSkill() {
    const s = customSkill.trim()
    if (s && !skills.includes(s)) setSkills([...skills, s])
    setCustomSkill('')
  }

  async function submit(e) {
    e.preventDefault()
    setBusy(true); setError('')
    try {
      const data = await api.predict({ scores, skills })
      setResults(data.predictions)
      setSubmitted({ ...details, skills, interest })
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const setDetail = (k) => (e) => setDetails({ ...details, [k]: e.target.value })

  return (
    <>
      <h1>Student Details Form 📝</h1>
      <p className="page-sub">
        Fill your own details below — your academics, your self-ratings and your current skills.
        The KNN model compares your profile with similar students and predicts your best careers.
      </p>
      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={submit}>
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginTop: 0 }}>1 · Your details</h3>
          <div style={formGrid}>
            <div>
              <label className="field" htmlFor="d-name">Full name</label>
              <input id="d-name" className="input" value={details.name} onChange={setDetail('name')}
                placeholder="e.g. Laksh Nakra" required />
            </div>
            <div>
              <label className="field" htmlFor="d-edu">Course / Education</label>
              <input id="d-edu" className="input" value={details.education} onChange={setDetail('education')}
                placeholder="e.g. MCA (Data Science)" />
            </div>
            <div>
              <label className="field" htmlFor="d-sem">Semester</label>
              <select id="d-sem" className="select" value={details.semester} onChange={setDetail('semester')}>
                <option value="">Select</option>
                {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => <option key={s} value={s}>Semester {s}</option>)}
              </select>
            </div>
            <div>
              <label className="field" htmlFor="d-10">10th % (or CGPA)</label>
              <input id="d-10" className="input" type="number" min="0" max="100" step="0.1"
                value={details.tenth} onChange={setDetail('tenth')} placeholder="e.g. 78" />
            </div>
            <div>
              <label className="field" htmlFor="d-12">12th %</label>
              <input id="d-12" className="input" type="number" min="0" max="100" step="0.1"
                value={details.twelfth} onChange={setDetail('twelfth')} placeholder="e.g. 72" />
            </div>
            <div>
              <label className="field" htmlFor="d-cgpa">Current CGPA</label>
              <input id="d-cgpa" className="input" type="number" min="0" max="10" step="0.01"
                value={details.cgpa} onChange={setDetail('cgpa')} placeholder="e.g. 7.5" />
            </div>
          </div>
        </div>

        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginTop: 0 }}>2 · Rate yourself (0–10)</h3>
          <p className="muted" style={{ marginTop: -6 }}>Type your own number for each area — be honest, this decides your prediction.</p>
          <div style={formGrid}>
            {FIELDS.map((f) => (
              <div key={f}>
                <label className="field" htmlFor={`s-${f}`}>{labels[f] || f}</label>
                <input id={`s-${f}`} className="input" type="number" min="0" max="10" step="0.5"
                  value={scores[f]}
                  onChange={(e) => setScores({ ...scores, [f]: Math.max(0, Math.min(10, Number(e.target.value) || 0)) })} />
                <div className="muted" style={{ fontSize: 12.5, marginTop: 4 }}>{HINTS[f]}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginTop: 0 }}>3 · Your current skills</h3>
          <p className="muted" style={{ marginTop: -6 }}>Select the skills you already have — these are used for your skill-gap analysis.</p>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
            {PRESET_SKILLS.map((s) => (
              <button type="button" key={s} onClick={() => toggleSkill(s)}
                className={skills.includes(s) ? 'btn btn-primary btn-sm' : 'btn btn-ghost btn-sm'}>
                {skills.includes(s) ? '✓ ' : ''}{s}
              </button>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <input className="input" style={{ maxWidth: 260 }} placeholder="Add another skill"
              value={customSkill} onChange={(e) => setCustomSkill(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addCustomSkill() } }} />
            <button type="button" className="btn btn-ghost btn-sm" onClick={addCustomSkill}>Add skill</button>
          </div>
          {skills.length > 0 && (
            <p className="muted" style={{ marginBottom: 0 }}>Selected: {skills.join(', ')}</p>
          )}
        </div>

        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginTop: 0 }}>4 · Career you are interested in (optional)</h3>
          <div style={{ maxWidth: 340 }}>
            <label className="field" htmlFor="d-interest">Interested career</label>
            <select id="d-interest" className="select" value={interest} onChange={(e) => setInterest(e.target.value)}>
              <option value="">No preference — suggest for me</option>
              {careerNames.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div style={{ marginTop: 18 }}>
            <button className="btn btn-primary" disabled={busy}>
              {busy ? 'Analysing…' : '🔮 Predict my careers'}
            </button>
          </div>
        </div>
      </form>

      {busy && <Spinner />}
      {results && (
        <>
          <h2>Your top-3 career matches</h2>
          <div className="grid grid-3" style={{ marginBottom: 18 }}>
            {results.map((p, i) => <CareerCard key={p.career} career={p} rank={i + 1} />)}
          </div>

          {submitted && (
            <div className="card" style={{ marginBottom: 18 }}>
              <h3 style={{ marginTop: 0 }}>Details you submitted</h3>
              <p className="muted" style={{ margin: 0 }}>
                {[submitted.name, submitted.education,
                  submitted.semester ? `Semester ${submitted.semester}` : '',
                  submitted.tenth ? `10th: ${submitted.tenth}` : '',
                  submitted.twelfth ? `12th: ${submitted.twelfth}%` : '',
                  submitted.cgpa ? `CGPA: ${submitted.cgpa}` : '',
                ].filter(Boolean).join(' · ') || '—'}
                <br />
                Skills: {submitted.skills.length ? submitted.skills.join(', ') : 'none selected'}
                {submitted.interest ? <><br />Interested in: {submitted.interest}</> : null}
              </p>
            </div>
          )}

          <div className="card" style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
            <strong>Next step:</strong>
            <span className="muted">See the skill gap for your #1 match and generate its roadmap.</span>
            <Link className="btn btn-primary btn-sm" to={`/app/skill-gap?career=${encodeURIComponent(results[0].career)}`}>
              Skill gap for {results[0].career}
            </Link>
            <Link className="btn btn-ghost btn-sm" to={`/app/roadmap?career=${encodeURIComponent(results[0].career)}`}>
              6-week roadmap
            </Link>
            {interest && interest !== results[0].career && (
              <Link className="btn btn-ghost btn-sm" to={`/app/skill-gap?career=${encodeURIComponent(interest)}`}>
                What to add for {interest}
              </Link>
            )}
          </div>
        </>
      )}
    </>
  )
}

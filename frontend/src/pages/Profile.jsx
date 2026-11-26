import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { Spinner } from '../components/ui'

const ALL_SKILLS = [
  'Python', 'Java', 'JavaScript', 'HTML/CSS', 'React', 'Node.js', 'SQL', 'Git', 'Linux',
  'Machine Learning', 'Deep Learning', 'Statistics', 'Pandas', 'Data Visualization',
  'Excel', 'Figma', 'Docker', 'Kubernetes', 'Networking', 'PyTorch', 'MLOps',
  'Data Structures', 'Mathematics', 'REST APIs', 'Databases', 'Storytelling',
]

export default function Profile() {
  const { user } = useAuth()
  const [form, setForm] = useState(null)
  const [careers, setCareers] = useState([])
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api.getProfile().then(setForm).catch((e) => setError(e.message))
    api.careers().then((d) => setCareers(d.careers.map((c) => c.career))).catch(() => {})
  }, [])

  function toggleSkill(skill) {
    setSaved(false)
    setForm((f) => ({
      ...f,
      skills: f.skills.includes(skill) ? f.skills.filter((s) => s !== skill) : [...f.skills, skill],
    }))
  }

  async function submit(e) {
    e.preventDefault()
    setBusy(true); setError(''); setSaved(false)
    try {
      const data = await api.saveProfile({
        skills: form.skills, interests: form.interests || '', education: form.education || '',
        cgpa: form.cgpa === '' || form.cgpa === null ? null : Number(form.cgpa),
        target_career: form.target_career || '', hours_per_day: Number(form.hours_per_day) || 2,
      })
      setForm(data)
      setSaved(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  if (!form) return <><h1>My Profile 👤</h1>{error ? <div className="alert alert-error">{error}</div> : <Spinner />}</>

  return (
    <>
      <h1>My Profile 👤</h1>
      <p className="page-sub">
        {user?.name} · {user?.email} · role: {user?.role}. Your skills power predictions, gap analysis and your roadmap.
      </p>
      {error && <div className="alert alert-error">{error}</div>}
      {saved && <div className="alert alert-ok">✅ Profile saved — predictions, skill gap and roadmap now use these skills.</div>}
      <form onSubmit={submit}>
        <div className="card" style={{ marginBottom: 18 }}>
          <h3 style={{ marginBottom: 10 }}>Your current skills</h3>
          <p className="muted" style={{ marginTop: 0, fontSize: 14 }}>Tap to select everything you already know.</p>
          <div className="chip-row">
            {ALL_SKILLS.map((s) => (
              <button type="button" key={s}
                className={`pill ${form.skills.includes(s) ? 'good' : ''}`}
                style={{ cursor: 'pointer', border: form.skills.includes(s) ? '' : '1px solid var(--line)', fontSize: 13.5, padding: '6px 13px' }}
                onClick={() => toggleSkill(s)}>
                {form.skills.includes(s) ? '✓ ' : ''}{s}
              </button>
            ))}
          </div>
          <p className="muted" style={{ fontSize: 13.5 }}>{form.skills.length} skill(s) selected.</p>
        </div>

        <div className="card">
          <div className="grid grid-2">
            <div className="form-group">
              <label className="field" htmlFor="target">Target career</label>
              <select id="target" className="select" value={form.target_career || ''}
                onChange={(e) => { setSaved(false); setForm({ ...form, target_career: e.target.value }) }}>
                <option value="">— Decide from my assessment —</option>
                {careers.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="field" htmlFor="hours">Study hours per day</label>
              <input id="hours" className="input" type="number" min="0.5" max="12" step="0.5"
                value={form.hours_per_day ?? 2}
                onChange={(e) => { setSaved(false); setForm({ ...form, hours_per_day: e.target.value }) }} />
            </div>
            <div className="form-group">
              <label className="field" htmlFor="education">Education</label>
              <input id="education" className="input" placeholder="e.g. MCA (Data Science), UPES"
                value={form.education || ''}
                onChange={(e) => { setSaved(false); setForm({ ...form, education: e.target.value }) }} />
            </div>
            <div className="form-group">
              <label className="field" htmlFor="cgpa">CGPA (optional)</label>
              <input id="cgpa" className="input" type="number" min="0" max="10" step="0.01"
                value={form.cgpa ?? ''}
                onChange={(e) => { setSaved(false); setForm({ ...form, cgpa: e.target.value }) }} />
            </div>
          </div>
          <div className="form-group">
            <label className="field" htmlFor="interests">Interests</label>
            <textarea id="interests" className="input" rows="2" placeholder="e.g. data, dashboards, cricket analytics"
              value={form.interests || ''}
              onChange={(e) => { setSaved(false); setForm({ ...form, interests: e.target.value }) }} />
          </div>
          <button className="btn btn-primary" disabled={busy}>{busy ? 'Saving…' : 'Save profile'}</button>
        </div>
      </form>
    </>
  )
}

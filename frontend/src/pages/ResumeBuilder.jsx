import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

const grid = { display: 'grid', gap: 14, gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))' }

const emptyEdu = () => ({ degree: '', institution: '', dates: '', score: '' })
const emptyProj = () => ({ title: '', context: '', tech: '', dates: '', bullets: '' })
const emptySkill = () => ({ category: '', items: '' })

export default function ResumeBuilder() {
  const { user } = useAuth()
  const [form, setForm] = useState({
    name: '', tagline: '', email: '', phone: '', location: '',
    linkedin: '', github: '', summary: '',
  })
  const [education, setEducation] = useState([emptyEdu(), emptyEdu()])
  const [projects, setProjects] = useState([{
    title: 'AI-Powered Personalized Learning and Career Recommendation System',
    context: 'Minor Project | UPES',
    tech: 'React, FastAPI, KNN, LLM',
    dates: '',
    bullets: 'Built a KNN-based system that collects student data and predicts the best career with match percentages.\nAdded skill-gap analysis that shows what to learn to move to another career, with a 6-week roadmap and study plan.',
  }])
  const [skills, setSkills] = useState([
    { category: 'Programming Languages', items: '' },
    { category: 'Tools & Platforms', items: '' },
  ])
  const [certifications, setCertifications] = useState('')
  const [busyFmt, setBusyFmt] = useState('')
  const [error, setError] = useState('')
  const [done, setDone] = useState('')

  useEffect(() => {
    api.getProfile().then((p) => {
      setForm((f) => ({
        ...f,
        name: p.name || user?.name || '',
        email: user?.email || '',
        summary: f.summary || '',
      }))
      if (p.education) {
        setEducation([{ degree: p.education, institution: '', dates: '', score: p.cgpa ? `CGPA: ${p.cgpa}` : '' }, emptyEdu()])
      }
      if (Array.isArray(p.skills) && p.skills.length) {
        setSkills([
          { category: 'Programming Languages', items: p.skills.join(', ') },
          { category: 'Tools & Platforms', items: '' },
        ])
      }
    }).catch(() => {
      setForm((f) => ({ ...f, name: user?.name || '', email: user?.email || '' }))
    })
  }, [user])

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  function updateList(list, setList, i, k, v) {
    const next = [...list]
    next[i] = { ...next[i], [k]: v }
    setList(next)
  }

  async function download(fmt) {
    setBusyFmt(fmt); setError(''); setDone('')
    try {
      const payload = {
        format: fmt,
        ...form,
        education,
        projects: projects.map((p) => ({
          ...p,
          bullets: p.bullets.split('\n').map((b) => b.trim()).filter(Boolean),
        })),
        skills,
        certifications: certifications.split('\n').map((c) => c.trim()).filter(Boolean),
      }
      const { blob, filename } = await api.downloadResume(payload)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
      setDone(filename)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyFmt('')
    }
  }

  return (
    <>
      <h1>Resume Builder 📄</h1>
      <p className="page-sub">
        Fill your details once — download your resume in the university format as a LaTeX file,
        a PDF, or a Word (DOCX) file. In project bullets, wrap words in **double stars** to make them bold.
      </p>
      {error && <div className="alert alert-error">{error}</div>}
      {done && <div className="alert alert-ok">Downloaded: {done}</div>}

      <div className="card" style={{ marginBottom: 20 }}>
        <h3 style={{ marginTop: 0 }}>Personal details</h3>
        <div style={grid}>
          <div><label className="field">Full name *</label>
            <input className="input" value={form.name} onChange={set('name')} placeholder="e.g. Laksh Nakra" /></div>
          <div><label className="field">Tagline</label>
            <input className="input" value={form.tagline} onChange={set('tagline')} placeholder="e.g. Aspiring Data Scientist" /></div>
          <div><label className="field">Email</label>
            <input className="input" value={form.email} onChange={set('email')} placeholder="you@gmail.com" /></div>
          <div><label className="field">Phone</label>
            <input className="input" value={form.phone} onChange={set('phone')} placeholder="(+91) 98XXXXXXXX" /></div>
          <div><label className="field">Location</label>
            <input className="input" value={form.location} onChange={set('location')} placeholder="Dehradun, IN" /></div>
          <div><label className="field">LinkedIn</label>
            <input className="input" value={form.linkedin} onChange={set('linkedin')} placeholder="linkedin.com/in/yourname" /></div>
          <div><label className="field">GitHub</label>
            <input className="input" value={form.github} onChange={set('github')} placeholder="github.com/yourname" /></div>
        </div>
        <div style={{ marginTop: 14 }}>
          <label className="field">Professional summary</label>
          <textarea className="input" rows={3} value={form.summary} onChange={set('summary')}
            placeholder="2-3 lines about you — course, strengths, interests." />
        </div>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <h3 style={{ marginTop: 0 }}>Education</h3>
        {education.map((e, i) => (
          <div key={i} style={{ ...grid, marginBottom: 12 }}>
            <div><label className="field">Degree</label>
              <input className="input" value={e.degree} placeholder="MCA (Data Science)"
                onChange={(ev) => updateList(education, setEducation, i, 'degree', ev.target.value)} /></div>
            <div><label className="field">Institution</label>
              <input className="input" value={e.institution} placeholder="UPES, Dehradun"
                onChange={(ev) => updateList(education, setEducation, i, 'institution', ev.target.value)} /></div>
            <div><label className="field">Dates</label>
              <input className="input" value={e.dates} placeholder="2025 -- 2027 / Pursuing"
                onChange={(ev) => updateList(education, setEducation, i, 'dates', ev.target.value)} /></div>
            <div><label className="field">Score</label>
              <input className="input" value={e.score} placeholder="CGPA: 8.1 / 72%"
                onChange={(ev) => updateList(education, setEducation, i, 'score', ev.target.value)} /></div>
          </div>
        ))}
        <button type="button" className="btn btn-ghost btn-sm" onClick={() => setEducation([...education, emptyEdu()])}>
          + Add education
        </button>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <h3 style={{ marginTop: 0 }}>Projects</h3>
        {projects.map((p, i) => (
          <div key={i} style={{ borderTop: i ? '1px dashed var(--line)' : 'none', paddingTop: i ? 14 : 0, marginBottom: 16 }}>
            <div style={grid}>
              <div><label className="field">Project title</label>
                <input className="input" value={p.title}
                  onChange={(ev) => updateList(projects, setProjects, i, 'title', ev.target.value)} /></div>
              <div><label className="field">Context</label>
                <input className="input" value={p.context} placeholder="Minor Project | UPES"
                  onChange={(ev) => updateList(projects, setProjects, i, 'context', ev.target.value)} /></div>
              <div><label className="field">Tech stack</label>
                <input className="input" value={p.tech} placeholder="React, FastAPI, KNN"
                  onChange={(ev) => updateList(projects, setProjects, i, 'tech', ev.target.value)} /></div>
              <div><label className="field">Dates</label>
                <input className="input" value={p.dates} placeholder="Aug 2026 -- Present"
                  onChange={(ev) => updateList(projects, setProjects, i, 'dates', ev.target.value)} /></div>
            </div>
            <div style={{ marginTop: 10 }}>
              <label className="field">Bullets — one point per line</label>
              <textarea className="input" rows={3} value={p.bullets}
                onChange={(ev) => updateList(projects, setProjects, i, 'bullets', ev.target.value)} />
            </div>
          </div>
        ))}
        <button type="button" className="btn btn-ghost btn-sm" onClick={() => setProjects([...projects, emptyProj()])}>
          + Add project
        </button>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <h3 style={{ marginTop: 0 }}>Technical skills</h3>
        {skills.map((s, i) => (
          <div key={i} style={{ ...grid, marginBottom: 12 }}>
            <div><label className="field">Category</label>
              <input className="input" value={s.category} placeholder="Programming Languages"
                onChange={(ev) => updateList(skills, setSkills, i, 'category', ev.target.value)} /></div>
            <div style={{ gridColumn: 'span 2' }}><label className="field">Skills (comma separated)</label>
              <input className="input" value={s.items} placeholder="Python, Java, SQL"
                onChange={(ev) => updateList(skills, setSkills, i, 'items', ev.target.value)} /></div>
          </div>
        ))}
        <button type="button" className="btn btn-ghost btn-sm" onClick={() => setSkills([...skills, emptySkill()])}>
          + Add skill row
        </button>
        <div style={{ marginTop: 14 }}>
          <label className="field">Certifications &amp; training — one per line</label>
          <textarea className="input" rows={2} value={certifications} onChange={(e) => setCertifications(e.target.value)}
            placeholder={'Kotlin Programming -- Certified Course'} />
        </div>
      </div>

      <div className="card center">
        <h3 style={{ marginTop: 0 }}>Download your resume</h3>
        <p className="muted">University format — same layout for all three files.</p>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
          <button className="btn btn-primary" disabled={!!busyFmt} onClick={() => download('pdf')}>
            {busyFmt === 'pdf' ? 'Making…' : '⬇ PDF'}
          </button>
          <button className="btn btn-primary" disabled={!!busyFmt} onClick={() => download('docx')}>
            {busyFmt === 'docx' ? 'Making…' : '⬇ DOCX (Word)'}
          </button>
          <button className="btn btn-ghost" disabled={!!busyFmt} onClick={() => download('tex')}>
            {busyFmt === 'tex' ? 'Making…' : '⬇ LaTeX (.tex)'}
          </button>
        </div>
        <p className="muted" style={{ fontSize: 13, marginBottom: 0 }}>
          The .tex file can be compiled on Overleaf or with pdflatex for the exact university look.
        </p>
      </div>
    </>
  )
}

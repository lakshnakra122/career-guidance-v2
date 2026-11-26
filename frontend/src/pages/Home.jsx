import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { TopNav, Spinner } from '../components/ui'
import CareerCard from '../components/CareerCard'
import { useAuth } from '../context/AuthContext'

const FEATURES = [
  { icon: '🧠', title: 'KNN Career Prediction', text: 'A K-Nearest Neighbors (KNN) model compares your 8-dimension assessment with similar student profiles and ranks careers with match percentages.' },
  { icon: '🧩', title: 'Skill-Gap Analysis', text: 'See exactly which skills you already have and which are missing for your target role — with courses for every gap.' },
  { icon: '🗺️', title: '6-Week Roadmap', text: 'A week-by-week plan that sequences your missing skills, adds tasks and checkpoints, and ends with a portfolio project.' },
  { icon: '📅', title: 'Study Plan Generator', text: 'Turn the roadmap into a daily routine sized to your real available hours — learn, practice, build.' },
  { icon: '🤖', title: 'AI Mentor Chat', text: 'A real LLM mentor with multi-key failover and response caching — and a built-in knowledge base so it always answers.' },
  { icon: '💰', title: 'India Salary Outlook', text: 'Indicative fresher CTC ranges and demand trends for every career, so your choice is grounded in the market.' },
]

const TEAM = [
  { name: 'Isha', sap: '590024867' },
  { name: 'Praveen Prajapati', sap: '590025124' },
  { name: 'Laksh Nakra', sap: '590021804' },
  { name: 'Prashant Srivastava', sap: '590024511' },
]

export default function Home() {
  const { user } = useAuth()
  const [careers, setCareers] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.careers().then((d) => setCareers(d.careers)).catch((e) => setError(e.message))
  }, [])

  return (
    <>
      <TopNav />
      <section className="hero">
        <div className="container">
          <span className="pill">AI-Powered Personalized Learning &amp; Career Recommendation System</span>
          <h1 style={{ marginTop: 16 }}>Find the career that <span className="grad">fits you</span> —<br />then follow the plan to get there.</h1>
          <p className="lead">
            Fill a short student form. Our ML model predicts your top-3 careers, maps your skill gaps,
            and builds a personalised 6-week roadmap and study plan — with an AI mentor on chat whenever you are stuck.
          </p>
          <div className="hero-cta">
            <Link className="btn btn-primary" to={user ? '/app/assessment' : '/register'}>
              {user ? 'Go to Student Form' : 'Fill the Student Form'} →
            </Link>
            <Link className="btn btn-ghost" to="/careers-preview">Explore Careers</Link>
          </div>
          <div className="stat-row">
            <div className="stat"><b>8</b><span>Career paths analysed</span></div>
            <div className="stat"><b>Top 3</b><span>Matches with % scores</span></div>
            <div className="stat"><b>6 weeks</b><span>Personal roadmap</span></div>
            <div className="stat"><b>24×7</b><span>AI mentor on chat</span></div>
          </div>
        </div>
      </section>

      <section className="container" style={{ padding: '54px 20px 0' }}>
        <h2 className="center">Everything you need, in one place</h2>
        <p className="center muted" style={{ maxWidth: 560, margin: '0 auto 30px' }}>
          From “I don’t know what to do” to a week-by-week plan — in a single sitting.
        </p>
        <div className="grid grid-3">
          {FEATURES.map((f) => (
            <div className="card" key={f.title}>
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p className="muted" style={{ margin: 0 }}>{f.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="container" id="careers" style={{ padding: '54px 20px 0' }}>
        <h2 className="center">Careers you can aim for</h2>
        <p className="center muted" style={{ marginBottom: 26 }}>Required skills and indicative India fresher salaries.</p>
        {error && <div className="alert alert-error">{error}</div>}
        {!careers && !error && <Spinner />}
        {careers && (
          <div className="grid grid-3">
            {careers.slice(0, 6).map((c) => <CareerCard key={c.career} career={c} />)}
          </div>
        )}
        <div className="center" style={{ marginTop: 24 }}>
          <Link className="btn btn-ghost" to="/careers-preview">See all 8 careers →</Link>
        </div>
      </section>

      <section className="container" id="team" style={{ padding: '54px 20px 0' }}>
        <h2 className="center">Meet the Team</h2>
        <p className="center muted" style={{ maxWidth: 620, margin: '0 auto 30px' }}>
          AI-Powered Personalized Learning and Career Recommendation System — a minor project by
          MCA (Data Science) students, School of Computer Science, UPES Dehradun.
        </p>
        <div className="grid grid-3">
          {TEAM.map((m) => (
            <div className="card center" key={m.sap}>
              <div style={{
                width: 56, height: 56, borderRadius: '50%', margin: '0 auto 12px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: 'linear-gradient(135deg,#6366f1,#d946ef)', color: '#fff',
                fontSize: 22, fontWeight: 700,
              }}>{m.name.charAt(0)}</div>
              <h3 style={{ marginBottom: 4 }}>{m.name}</h3>
              <p className="muted" style={{ margin: 0 }}>SAP ID: {m.sap}</p>
              <p className="muted" style={{ margin: 0 }}>MCA – Data Science</p>
            </div>
          ))}
          <div className="card center" style={{ background: 'linear-gradient(135deg,#eef2ff,#fdf4ff)' }}>
            <div className="feature-icon">🎓</div>
            <h3 style={{ marginBottom: 4 }}>Guided by</h3>
            <p style={{ margin: 0, fontWeight: 600 }}>Dr. Alka Yadav</p>
            <p className="muted" style={{ margin: 0 }}>Assistant Professor<br />School of Computer Science</p>
          </div>
        </div>
      </section>

      <footer className="site">
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
          <span>🧭 PathFinder AI — MCA Minor Project, UPES Dehradun</span>
          <span>Team: Isha · Praveen Prajapati · Laksh Nakra · Prashant Srivastava</span>
        </div>
      </footer>
    </>
  )
}

export function CareersPreview() {
  const [careers, setCareers] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    api.careers().then((d) => setCareers(d.careers)).catch((e) => setError(e.message))
  }, [])
  return (
    <>
      <TopNav />
      <div className="container" style={{ padding: '44px 20px 0' }}>
        <h1>All career paths</h1>
        <p className="page-sub">Every career the system can recommend, with the skills it needs and fresher salary outlook in India.</p>
        {error && <div className="alert alert-error">{error}</div>}
        {!careers && !error && <Spinner />}
        {careers && (
          <div className="grid grid-3">
            {careers.map((c) => <CareerCard key={c.career} career={c} />)}
          </div>
        )}
      </div>
      <footer className="site"><div className="container">🧭 PathFinder AI</div></footer>
    </>
  )
}

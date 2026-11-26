import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { EmptyState, MatchBar, Spinner } from '../components/ui'

export default function Dashboard() {
  const { user } = useAuth()
  const [profile, setProfile] = useState(null)
  const [health, setHealth] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getProfile().then(setProfile).catch((e) => setError(e.message))
    api.health().then(setHealth).catch(() => {})
  }, [])

  const skills = profile?.skills || []
  const target = profile?.target_career

  return (
    <>
      <h1>Namaste, {user?.name?.split(' ')[0]} 👋</h1>
      <p className="page-sub">Your personalised career workspace — pick up right where you left off.</p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="grid grid-3" style={{ marginBottom: 18 }}>
        <div className="card">
          <div className="feature-icon">🎯</div>
          <h3>{target || 'No target set yet'}</h3>
          <p className="muted" style={{ margin: 0 }}>
            {target ? 'Your chosen target career. Track its skill gap below.' : 'Set a target career in your profile or from your assessment results.'}
          </p>
          <div style={{ marginTop: 12 }}>
            <Link className="btn btn-ghost btn-sm" to="/app/assessment">Fill student form</Link>
          </div>
        </div>
        <div className="card">
          <div className="feature-icon">🧩</div>
          <h3>{skills.length} skills on profile</h3>
          <div className="chip-row">
            {skills.slice(0, 8).map((s) => <span key={s} className="pill good">{s}</span>)}
            {skills.length === 0 && <span className="muted">Add your current skills to unlock gap analysis.</span>}
          </div>
          <div style={{ marginTop: 12 }}>
            <Link className="btn btn-ghost btn-sm" to="/app/profile">Edit profile</Link>
          </div>
        </div>
        <div className="card">
          <div className="feature-icon">🤖</div>
          <h3>AI Mentor {health ? (health.llm_available ? '· Live LLM' : '· Knowledge Base') : ''}</h3>
          <p className="muted" style={{ margin: 0 }}>
            {health
              ? health.llm_available
                ? `Connected to ${health.model} with ${health.keys_configured} key(s) and response caching.`
                : 'Running on the built-in knowledge base — answers still work offline.'
              : 'Checking mentor status…'}
          </p>
          <div style={{ marginTop: 12 }}>
            <Link className="btn btn-ghost btn-sm" to="/app/chat">Chat now</Link>
          </div>
        </div>
      </div>

      <h2 style={{ margin: '10px 0 14px' }}>Quick actions</h2>
      <div className="grid grid-2">
        <Link to="/app/roadmap" className="card" style={{ color: 'inherit' }}>
          <h3>🗺️ My 6-week roadmap</h3>
          <p className="muted" style={{ margin: 0 }}>Week-by-week tasks and checkpoints for {target || 'your target career'}.</p>
        </Link>
        <Link to="/app/study-plan" className="card" style={{ color: 'inherit' }}>
          <h3>📅 My study plan</h3>
          <p className="muted" style={{ margin: 0 }}>
            A daily routine sized to {profile?.hours_per_day || 2} hours/day — learn, practice, build.
          </p>
        </Link>
        <Link to="/app/skill-gap" className="card" style={{ color: 'inherit' }}>
          <h3>🧩 Skill-gap analysis</h3>
          <p className="muted" style={{ margin: 0 }}>Coverage score, missing skills and the exact courses to close them.</p>
        </Link>
        <Link to="/app/careers" className="card" style={{ color: 'inherit' }}>
          <h3>🎯 Explore all careers</h3>
          <p className="muted" style={{ margin: 0 }}>Compare required skills, demand and India fresher salaries across 8 roles.</p>
        </Link>
      </div>

      {skills.length === 0 && (
        <div style={{ marginTop: 18 }}>
          <EmptyState icon="🌱" title="Start by completing your profile"
            hint="Add your current skills — everything else (predictions, gaps, roadmap) builds on them.">
            <Link className="btn btn-primary btn-sm" to="/app/profile">Complete profile</Link>
          </EmptyState>
        </div>
      )}
    </>
  )
}

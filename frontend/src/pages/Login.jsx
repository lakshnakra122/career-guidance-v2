import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { TopNav } from '../components/ui'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setBusy(true); setError('')
    try {
      await login(email, password)
      navigate('/app')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  function fillDemo(kind) {
    if (kind === 'student') { setEmail('student@college.edu'); setPassword('student123') }
    else { setEmail('admin@college.edu'); setPassword('admin123') }
  }

  return (
    <>
      <TopNav />
      <div className="container">
        <div className="auth-wrap card">
          <h1 style={{ fontSize: 24 }}>Welcome back 👋</h1>
          <p className="muted">Log in to your dashboard, roadmap and AI mentor.</p>
          {error && <div className="alert alert-error">{error}</div>}
          <form onSubmit={submit}>
            <div className="form-group">
              <label className="field" htmlFor="email">Email</label>
              <input id="email" className="input" type="email" required value={email}
                onChange={(e) => setEmail(e.target.value)} placeholder="you@college.edu" />
            </div>
            <div className="form-group">
              <label className="field" htmlFor="password">Password</label>
              <input id="password" className="input" type="password" required value={password}
                onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
            </div>
            <button className="btn btn-primary" style={{ width: '100%' }} disabled={busy}>
              {busy ? 'Logging in…' : 'Log in'}
            </button>
          </form>
          <p className="center muted" style={{ marginTop: 16 }}>
            New here? <Link to="/register">Create an account</Link>
          </p>
          <div className="demo-box">
            <strong>Demo accounts</strong> — click to fill:
            <div style={{ marginTop: 8, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <button type="button" className="btn btn-ghost btn-sm" onClick={() => fillDemo('student')}>
                Student · <code>student@college.edu</code>
              </button>
              <button type="button" className="btn btn-ghost btn-sm" onClick={() => fillDemo('admin')}>
                Admin · <code>admin@college.edu</code>
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

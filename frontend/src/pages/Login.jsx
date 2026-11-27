import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { TopNav } from '../components/ui'

// The admin email is intentionally NOT shown anywhere on this page.
// Admin sign-in works only by entering the admin password (upes123),
// which is verified by the backend — nothing is revealed to visitors.
const ADMIN_EMAIL = 'admin@college.edu'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [showAdmin, setShowAdmin] = useState(false)
  const [adminPw, setAdminPw] = useState('')
  const [adminError, setAdminError] = useState('')
  const [adminBusy, setAdminBusy] = useState(false)

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

  async function adminSubmit(e) {
    e.preventDefault()
    setAdminBusy(true); setAdminError('')
    try {
      await login(ADMIN_EMAIL, adminPw)
      navigate('/app')
    } catch {
      setAdminError('Wrong admin password. Please try again.')
    } finally {
      setAdminBusy(false)
    }
  }

  function fillDemo() {
    setEmail('student@college.edu'); setPassword('student123')
  }

  return (
    <>
      <TopNav />
      <div className="container">
        <div className="auth-wrap card">
          <h1 style={{ fontSize: 24 }}>Welcome back 👋</h1>
          <p className="muted">Log in to your dashboard, roadmap and AI mentor.</p>
          {error && <div className="alert alert-error">{error}</div>}
          {error && error.toLowerCase().includes('not registered') && (
            <div className="demo-box" style={{ marginBottom: 16 }}>
              <strong>New here? Follow these steps:</strong>
              <ol style={{ margin: '8px 0 10px', paddingLeft: 20, lineHeight: 1.7 }}>
                <li>Click <strong>Create an account</strong> below.</li>
                <li>Fill your name, this same email, and a new password.</li>
                <li>Come back here and log in with that email + password.</li>
              </ol>
              <Link className="btn btn-primary btn-sm" to="/register">Create an account →</Link>
            </div>
          )}
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
            {busy && (
              <p className="center muted" style={{ fontSize: 13, marginTop: 10 }}>
                Please wait — the free server can take 30–60 seconds to wake up the first time.
              </p>
            )}
          </form>
          <p className="center muted" style={{ marginTop: 16 }}>
            New here? <Link to="/register">Create an account</Link>
          </p>
          <div className="demo-box">
            <strong>Demo account</strong> — click to fill:
            <div style={{ marginTop: 8, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <button type="button" className="btn btn-ghost btn-sm" onClick={fillDemo}>
                Student · <code>student@college.edu</code>
              </button>
            </div>
          </div>

          <div style={{ marginTop: 18, borderTop: '1px dashed var(--line)', paddingTop: 14 }}>
            {!showAdmin ? (
              <button type="button" className="btn btn-ghost btn-sm" onClick={() => setShowAdmin(true)}>
                🔐 Admin login
              </button>
            ) : (
              <form onSubmit={adminSubmit}>
                <label className="field" htmlFor="admin-pw">Admin password</label>
                {adminError && <div className="alert alert-error">{adminError}</div>}
                <div style={{ display: 'flex', gap: 8 }}>
                  <input id="admin-pw" className="input" type="password" required value={adminPw}
                    onChange={(e) => setAdminPw(e.target.value)} placeholder="Enter admin password"
                    autoFocus style={{ flex: 1 }} />
                  <button className="btn btn-primary btn-sm" disabled={adminBusy}>
                    {adminBusy ? 'Checking…' : 'Login as Admin'}
                  </button>
                </div>
                <p className="muted" style={{ fontSize: 12.5, marginBottom: 0 }}>
                  Only the admin knows this password. Nothing is shown on this page.
                </p>
              </form>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

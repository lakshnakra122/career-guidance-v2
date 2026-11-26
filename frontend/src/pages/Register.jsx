import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { TopNav } from '../components/ui'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setBusy(true); setError('')
    try {
      await register(name, email, password)
      navigate('/app/profile')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <TopNav />
      <div className="container">
        <div className="auth-wrap card">
          <h1 style={{ fontSize: 24 }}>Create your account 🚀</h1>
          <p className="muted">Two minutes from now you will have your top-3 career matches.</p>
          {error && <div className="alert alert-error">{error}</div>}
          <form onSubmit={submit}>
            <div className="form-group">
              <label className="field" htmlFor="name">Full name</label>
              <input id="name" className="input" required minLength={2} value={name}
                onChange={(e) => setName(e.target.value)} placeholder="Your name" />
            </div>
            <div className="form-group">
              <label className="field" htmlFor="email">Email</label>
              <input id="email" className="input" type="email" required value={email}
                onChange={(e) => setEmail(e.target.value)} placeholder="you@college.edu" />
            </div>
            <div className="form-group">
              <label className="field" htmlFor="password">Password (min 6 characters)</label>
              <input id="password" className="input" type="password" required minLength={6} value={password}
                onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
            </div>
            <button className="btn btn-primary" style={{ width: '100%' }} disabled={busy}>
              {busy ? 'Creating…' : 'Create account'}
            </button>
          </form>
          <p className="center muted" style={{ marginTop: 16 }}>
            Already registered? <Link to="/login">Log in</Link>
          </p>
        </div>
      </div>
    </>
  )
}

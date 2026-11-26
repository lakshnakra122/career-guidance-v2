import { Link, NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function Logo() {
  return (
    <span className="logo">
      <span className="logo-badge">🧭</span> PathFinder&nbsp;AI
    </span>
  )
}

export function TopNav() {
  const { user } = useAuth()
  return (
    <header className="topnav">
      <div className="container topnav-inner">
        <Link to="/" style={{ textDecoration: 'none' }}><Logo /></Link>
        <nav className="topnav-links">
          <Link className="hide-sm" to="/careers-preview">Careers</Link>
          {user ? (
            <Link className="btn btn-primary btn-sm" to="/app">Open Dashboard</Link>
          ) : (
            <>
              <Link to="/login">Log in</Link>
              <Link className="btn btn-primary btn-sm" to="/register">Get Started</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}

const SIDE_LINKS = [
  { to: '/app', label: 'Dashboard', icon: '🏠', end: true },
  { to: '/app/assessment', label: 'Assessment', icon: '📝' },
  { to: '/app/careers', label: 'Careers', icon: '🎯' },
  { to: '/app/skill-gap', label: 'Skill Gap', icon: '🧩' },
  { to: '/app/roadmap', label: 'Roadmap', icon: '🗺️' },
  { to: '/app/study-plan', label: 'Study Plan', icon: '📅' },
  { to: '/app/chat', label: 'AI Mentor Chat', icon: '🤖' },
  { to: '/app/profile', label: 'Profile', icon: '👤' },
]

export function AppLayout() {
  const { user, logout } = useAuth()
  return (
    <div className="shell">
      <aside className="sidebar">
        <Link to="/" style={{ textDecoration: 'none' }}><Logo /></Link>
        {SIDE_LINKS.map((l) => (
          <NavLink key={l.to} to={l.to} end={l.end}
            className={({ isActive }) => `side-link${isActive ? ' active' : ''}`}>
            <span>{l.icon}</span> {l.label}
          </NavLink>
        ))}
        <div className="side-user">
          <div><strong style={{ color: '#fff' }}>{user?.name}</strong></div>
          <div className="muted" style={{ color: '#9a9ec4' }}>{user?.email}</div>
          <button className="btn btn-ghost btn-sm" onClick={logout}>Log out</button>
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}

export function Spinner() {
  return <div className="spinner" role="status" aria-label="Loading" />
}

export function EmptyState({ icon = '📭', title, hint, children }) {
  return (
    <div className="empty">
      <div style={{ fontSize: 34 }}>{icon}</div>
      <h3 style={{ marginTop: 8 }}>{title}</h3>
      {hint && <p>{hint}</p>}
      {children}
    </div>
  )
}

export function MatchBar({ pct }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13.5, marginBottom: 5 }}>
        <span className="muted">Match</span><strong>{pct}%</strong>
      </div>
      <div className="progress"><div style={{ width: `${Math.min(100, pct)}%` }} /></div>
    </div>
  )
}

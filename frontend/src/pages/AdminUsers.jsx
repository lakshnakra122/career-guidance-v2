import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Spinner } from '../components/ui'
import { useAuth } from '../context/AuthContext'

function fmtDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('en-IN', {
      day: 'numeric', month: 'short', year: 'numeric',
      hour: 'numeric', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata',
    })
  } catch {
    return iso
  }
}

export default function AdminUsers() {
  const { user } = useAuth()
  const [users, setUsers] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (user && user.role !== 'admin') {
      setError('This page is for admins only.')
      return
    }
    api.adminUsers()
      .then((d) => setUsers(d.users || []))
      .catch((e) => setError(e.message))
  }, [user])

  const students = users ? users.filter((u) => u.role !== 'admin').length : 0
  const admins = users ? users.filter((u) => u.role === 'admin').length : 0

  return (
    <>
      <h1>Registered Users 👥</h1>
      <p className="page-sub">
        Everyone who has signed up on this website — name, login email, role and joining date.
        Visible only to the admin login.
      </p>
      {error && <div className="alert alert-error">{error}</div>}
      {!users && !error && <Spinner />}

      {users && (
        <>
          <div className="grid grid-3" style={{ marginBottom: 18 }}>
            <div className="card center"><h2 style={{ margin: '4px 0' }}>{users.length}</h2><p className="muted" style={{ margin: 0 }}>Total users</p></div>
            <div className="card center"><h2 style={{ margin: '4px 0' }}>{students}</h2><p className="muted" style={{ margin: 0 }}>Students</p></div>
            <div className="card center"><h2 style={{ margin: '4px 0' }}>{admins}</h2><p className="muted" style={{ margin: 0 }}>Admins</p></div>
          </div>

          <div className="card">
            {users.map((u) => (
              <div key={u.id} style={{
                display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap',
                padding: '12px 0', borderBottom: '1px dashed var(--line)',
              }}>
                <div style={{
                  width: 42, height: 42, borderRadius: '50%', flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: 'linear-gradient(135deg,#6366f1,#d946ef)', color: '#fff',
                  fontWeight: 700, fontSize: 17,
                }}>{(u.name || '?').charAt(0).toUpperCase()}</div>
                <div style={{ flex: '1 1 200px', minWidth: 0 }}>
                  <div style={{ fontWeight: 600 }}>{u.name}</div>
                  <div className="muted" style={{ fontSize: 13.5 }}>{u.email}</div>
                </div>
                <span className={u.role === 'admin' ? 'btn btn-primary btn-sm' : 'btn btn-ghost btn-sm'}
                  style={{ pointerEvents: 'none', textTransform: 'capitalize' }}>
                  {u.role}
                </span>
                <div className="muted" style={{ fontSize: 13, flex: '0 1 190px' }}>
                  Joined: {fmtDate(u.created_at)}
                </div>
              </div>
            ))}
            {users.length === 0 && <p className="muted" style={{ margin: 0 }}>No users yet.</p>}
          </div>

          <p className="muted" style={{ fontSize: 13, marginTop: 12 }}>
            Note: passwords are stored encrypted (hashed) in the database — they cannot be seen by anyone, including the admin.
          </p>
        </>
      )}
    </>
  )
}

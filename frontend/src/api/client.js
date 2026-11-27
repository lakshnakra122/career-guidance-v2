// Thin fetch wrapper around the backend API.
// Base URL comes from VITE_API_URL (set per-environment: localhost in dev,
// the Render backend URL in production).
const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

export function getToken() {
  return localStorage.getItem('cg_token')
}
export function setToken(token) {
  if (token) localStorage.setItem('cg_token', token)
  else localStorage.removeItem('cg_token')
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (auth && token) headers.Authorization = `Bearer ${token}`
  let res
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new Error('Cannot reach the server. Is the backend running?')
  }
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data.detail || `Request failed (${res.status})`)
  }
  return data
}

export const api = {
  health: () => request('/health', { auth: false }),
  register: (payload) => request('/auth/register', { method: 'POST', body: payload, auth: false }),
  login: (payload) => request('/auth/login', { method: 'POST', body: payload, auth: false }),
  me: () => request('/users/me'),
  getProfile: () => request('/students/profile'),
  saveProfile: (payload) => request('/students/profile', { method: 'PUT', body: payload }),
  careers: () => request('/careers', { auth: false }),
  predict: (payload) => request('/assessment/predict', { method: 'POST', body: payload }),
  recommendations: (payload) => request('/recommendations', { method: 'POST', body: payload }),
  roadmap: (payload) => request('/roadmap', { method: 'POST', body: payload }),
  studyPlan: (payload) => request('/study-plan', { method: 'POST', body: payload }),
  chat: (payload) => request('/chat', { method: 'POST', body: payload }),
  chatHistory: (sessionId) => request(`/sessions/${encodeURIComponent(sessionId)}/messages`),
  adminUsers: () => request('/admin/users'),
  downloadResume: async (payload) => {
    const headers = { 'Content-Type': 'application/json' }
    const token = getToken()
    if (token) headers.Authorization = `Bearer ${token}`
    let res
    try {
      res = await fetch(`${API_URL}/resume/download`, {
        method: 'POST', headers, body: JSON.stringify(payload),
      })
    } catch {
      throw new Error('Cannot reach the server. Is the backend running?')
    }
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || `Request failed (${res.status})`)
    }
    const blob = await res.blob()
    const cd = res.headers.get('Content-Disposition') || ''
    const m = cd.match(/filename="([^"]+)"/)
    return { blob, filename: m ? m[1] : `resume.${payload.format}` }
  },
}

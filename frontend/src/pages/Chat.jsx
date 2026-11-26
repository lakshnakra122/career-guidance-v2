import { useEffect, useRef, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

const SUGGESTIONS = [
  'What is the roadmap for a Data Scientist?',
  'Which career suits me best?',
  'What are fresher salaries in India?',
  'How do I close my skill gap?',
  'Suggest projects for my resume',
]

function sourceBadge(meta) {
  if (!meta) return null
  const src = meta.resolution_source
  if (src === 'LIVE_INFERENCE') return <span className="src live">● LIVE · {meta.model?.split('/').pop() || 'LLM'}</span>
  if (src === 'LLM_CACHE') return <span className="src cache">⚡ CACHE</span>
  if (src === 'FALLBACK_KB') return <span className="src kb">📚 Knowledge Base</span>
  return <span className="src cache">{src}</span>
}

export default function Chat() {
  const { user } = useAuth()
  const [sessionId] = useState(() => `web-${user?.id || 'guest'}-${Math.random().toString(36).slice(2, 10)}`)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [health, setHealth] = useState(null)
  const logRef = useRef(null)

  useEffect(() => {
    api.health().then(setHealth).catch(() => {})
    api.chatHistory(sessionId)
      .then((d) => setMessages(d.messages || []))
      .catch(() => setMessages([]))
  }, [sessionId])

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, busy])

  async function send(text) {
    const message = (text ?? input).trim()
    if (!message || busy) return
    setInput('')
    setError('')
    setMessages((m) => [...m, { role: 'user', content: message }])
    setBusy(true)
    try {
      const data = await api.chat({ session_id: sessionId, message })
      setMessages((m) => [...m, { role: 'assistant', content: data.reply, metadata: data.metadata }])
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <h1>AI Mentor Chat 🤖</h1>
      <p className="page-sub">
        Ask about careers, roadmaps, skills and salaries. I know your profile and your latest assessment.
        {health && (
          <> Mode: <strong>{health.llm_available ? `Live LLM (${health.model})` : 'Built-in knowledge base'}</strong>
            {health.cache_enabled ? ' · response caching on' : ''}.</>
        )}
      </p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="card chat-wrap">
        <div className="chat-log" ref={logRef}>
          {messages.length === 0 && (
            <div className="empty" style={{ margin: 'auto', width: '100%' }}>
              <div style={{ fontSize: 32 }}>👋</div>
              <h3 style={{ marginTop: 6 }}>Hi {user?.name?.split(' ')[0]}! I am PathFinder AI.</h3>
              <p>Ask me anything about your career path — or tap a suggestion below.</p>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', justifyContent: 'center' }}>
                {SUGGESTIONS.map((s) => (
                  <button key={s} className="btn btn-ghost btn-sm" onClick={() => send(s)}>{s}</button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`bubble ${m.role === 'user' ? 'user' : 'bot'}`}>
              <div>{m.content}</div>
              {m.role === 'assistant' && m.metadata && (
                <div className="bubble-meta">
                  {sourceBadge(m.metadata)}
                  {m.metadata.latency_ms !== undefined && <span className="muted">{m.metadata.latency_ms} ms</span>}
                  {m.metadata.key_id && <span className="muted">{m.metadata.key_id}</span>}
                </div>
              )}
            </div>
          ))}
          {busy && (
            <div className="bubble bot typing"><span /><span /><span /></div>
          )}
        </div>
        <form className="chat-input" onSubmit={(e) => { e.preventDefault(); send() }}>
          <input className="input" placeholder="Ask about careers, roadmaps, salaries…"
            value={input} onChange={(e) => setInput(e.target.value)} disabled={busy} />
          <button className="btn btn-primary" disabled={busy || !input.trim()}>
            {busy ? '…' : 'Send →'}
          </button>
        </form>
      </div>
    </>
  )
}

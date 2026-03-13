import { useState } from 'react'
import { supabase } from './supabase'

export default function Auth() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async () => {
    setLoading(true)
    setMessage('')
    const { error } = isLogin
      ? await supabase.auth.signInWithPassword({ email, password })
      : await supabase.auth.signUp({ email, password, options: { data: { name } } })
    if (error) setMessage(error.message)
    else if (!isLogin) setMessage('Check your email to confirm your account!')
    setLoading(false)
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <span className="auth-star">✦</span>
          <h1>a moment to reflect</h1>
          <p>your daily journaling companion</p>
        </div>

        <div className="auth-form">
          {!isLogin && (
            <input
              className="auth-input"
              type="text"
              placeholder="your name"
              value={name}
              onChange={e => setName(e.target.value)}
            />
          )}
          <input
            className="auth-input"
            type="email"
            placeholder="your email"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
          <input
            className="auth-input"
            type="password"
            placeholder="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
          />
          {message && <p className="auth-message">{message}</p>}
          <button className="auth-btn" onClick={handleSubmit} disabled={loading}>
            {loading ? '...' : isLogin ? 'sign in' : 'create account'}
          </button>
          <button className="auth-toggle" onClick={() => setIsLogin(!isLogin)}>
            {isLogin ? "don't have an account? sign up" : 'already have an account? sign in'}
          </button>
        </div>
      </div>
    </div>
  )
}

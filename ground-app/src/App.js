import { useState, useEffect } from 'react'
import { supabase, isPasswordRecovery, supabaseConfigError } from './supabase'
import Auth from './Auth'
import Home from './Home'
import ResetPassword from './ResetPassword'
import './App.css'

export default function App() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState(supabaseConfigError)
  // Seed from URL hash — captured before Supabase clears it
  const [isRecovery, setIsRecovery] = useState(isPasswordRecovery)

  useEffect(() => {
    if (!supabase) {
      setLoading(false)
      return undefined
    }

    let cancelled = false

    const restoreSession = async () => {
      const { data, error } = await supabase.auth.getSession()
      if (cancelled) return
      if (error) {
        setErrorMessage(error.message)
      } else {
        setSession(data.session)
      }
      setLoading(false)
    }

    restoreSession()

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'PASSWORD_RECOVERY') {
        setIsRecovery(true)
        setSession(session)
        setErrorMessage('')
        setLoading(false)
      } else if (event === 'SIGNED_OUT') {
        setIsRecovery(false)
        setSession(null)
        setErrorMessage('')
        setLoading(false)
      } else {
        setSession(session)
        setErrorMessage('')
        setLoading(false)
      }
    })

    return () => {
      cancelled = true
      subscription.unsubscribe()
    }
  }, [])

  if (loading) return (
    <div className="loading-screen">
      <div className="loading-dot" />
    </div>
  )

  if (errorMessage) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <div className="auth-header">
            <h1>supabase needs attention</h1>
            <p>{errorMessage}</p>
          </div>
        </div>
      </div>
    )
  }

  if (isRecovery) return <ResetPassword onDone={() => setIsRecovery(false)} />
  return session ? <Home session={session} /> : <Auth />
}

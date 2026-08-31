import { FormEvent, useState } from 'react'
import { Blocks, Eye, EyeOff, ShieldCheck } from 'lucide-react'
import { api, type User } from '../lib/api'

export default function Auth({ onAuthenticated }: { onAuthenticated: (user: User) => void }) {
  const [mode, setMode] = useState<'login' | 'signup'>('login')
  const [email, setEmail] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [password, setPassword] = useState('')
  const [visible, setVisible] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    if (!email.trim() || !password) return setError('Enter your email and password.')
    if (mode === 'signup' && (!displayName.trim() || password.length < 12)) return setError('Enter a display name and a password of at least 12 characters.')
    setLoading(true)
    try {
      const user = mode === 'login' ? await api.login(email, password) : await api.signup(email, password, displayName)
      onAuthenticated(user)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Authentication failed.')
    } finally { setLoading(false) }
  }

  const changeMode = (next: 'login' | 'signup') => { setMode(next); setError(null); setPassword('') }
  return <main className="auth-page">
    <section className="auth-story">
      <div className="auth-brand"><span><Blocks size={18} /></span>EvoPay <b>Lab</b></div>
      <div className="auth-story-copy"><p>CONTROLLED ADVERSARIAL RESEARCH</p><h1>Your simulation records.<br />Your isolated workspace.</h1><span>Server-side sessions and strict record ownership keep each analyst's synthetic experiments separate.</span></div>
      <div className="auth-assurance"><ShieldCheck size={16} /><div><strong>Session protected</strong><small>Credentials and session tokens never enter browser storage.</small></div></div>
    </section>
    <section className="auth-panel">
      <div className="auth-form-wrap">
        <div className="auth-tabs" role="tablist"><button className={mode === 'login' ? 'active' : ''} onClick={() => changeMode('login')}>Sign in</button><button className={mode === 'signup' ? 'active' : ''} onClick={() => changeMode('signup')}>Create account</button></div>
        <header><p>{mode === 'login' ? 'WELCOME BACK' : 'NEW WORKSPACE'}</p><h2>{mode === 'login' ? 'Continue your research.' : 'Create your analyst account.'}</h2><span>{mode === 'login' ? 'Sign in to access your recorded simulations.' : 'Your new workspace starts empty and private.'}</span></header>
        <form onSubmit={submit} noValidate>
          {mode === 'signup' && <label>Display name<input autoComplete="name" value={displayName} onChange={(event) => setDisplayName(event.target.value)} maxLength={80} /></label>}
          <label>Email address<input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} /></label>
          <label>Password<div className="password-field"><input type={visible ? 'text' : 'password'} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} value={password} onChange={(event) => setPassword(event.target.value)} maxLength={128} /><button type="button" onClick={() => setVisible((value) => !value)} aria-label={visible ? 'Hide password' : 'Show password'}>{visible ? <EyeOff size={17} /> : <Eye size={17} />}</button></div>{mode === 'signup' && <small>12–128 characters, including a letter and number.</small>}</label>
          {error && <div className="auth-error" role="alert">{error}</div>}
          <button className="auth-submit" disabled={loading}>{loading ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create private workspace'}</button>
        </form>
      </div>
    </section>
  </main>
}

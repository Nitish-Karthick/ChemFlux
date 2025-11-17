import { useState } from 'react'
import { setCreds, clearCreds, testAuth } from '../api'

export default function Login({ onLoggedIn }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function handleLogin(e) {
    e.preventDefault()
    setError('')
    try {
      // verify first using temp auth
      await testAuth(username, password)
      // only persist on success
      setCreds(username, password)
      onLoggedIn()
    } catch (err) {
      setError('Invalid credentials or backend offline')
      clearCreds()
    }
  }

  return (
    <div className="card login-card">
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <div className="field">
          <label>Username</label>
          <input value={username} onChange={e => setUsername(e.target.value)} required />
        </div>
        <div className="field">
          <label>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </div>
        {error && <div className="error">{error}</div>}
        <button type="submit">Sign In</button>
      </form>
    </div>
  )
}

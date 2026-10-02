import { useEffect, useState } from 'react'
import './App.css'
import { getMe } from './api'
import AuthForm from './AuthForm'

const TOKEN_KEY = 'expense-tracker-token'

function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) return
    getMe(token)
      .then(setUser)
      .catch((err) => {
        if (err.status === 401) {
          localStorage.removeItem(TOKEN_KEY)
          setToken(null)
        } else {
          setError(err.message)
        }
      })
  }, [token])

  function handleLogin(newToken) {
    localStorage.setItem(TOKEN_KEY, newToken)
    setToken(newToken)
  }

  function handleLogout() {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
    setError('')
  }

  if (!token) {
    return (
      <main>
        <h1>Expense Tracker</h1>
        <AuthForm onLogin={handleLogin} />
      </main>
    )
  }

  let content = <p>Cargando...</p>
  if (error) {
    content = (
      <p className="error" role="alert">
        {error}
      </p>
    )
  } else if (user) {
    content = (
      <p>
        Sesión iniciada como <strong>{user.email}</strong>
      </p>
    )
  }

  return (
    <main>
      <h1>Expense Tracker</h1>
      <div className="card">
        {content}
        <button type="button" onClick={handleLogout}>
          Cerrar sesión
        </button>
      </div>
    </main>
  )
}

export default App
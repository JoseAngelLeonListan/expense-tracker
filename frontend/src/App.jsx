import { useEffect, useState } from 'react'
import './App.css'
import { getMe, setUnauthorizedHandler } from './api'
import AuthForm from './AuthForm'
import Expenses from './Expenses'

const TOKEN_KEY = 'expense-tracker-token'

function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  // Cualquier petición que reciba un 401 con token cierra la sesión desde aquí
  useEffect(() => {
    setUnauthorizedHandler(() => {
      localStorage.removeItem(TOKEN_KEY)
      setToken(null)
      setUser(null)
      setNotice('Tu sesión ha caducado. Vuelve a iniciar sesión.')
    })
    return () => setUnauthorizedHandler(null)
  }, [])

  useEffect(() => {
    if (!token) return
    getMe(token)
      .then(setUser)
      .catch((err) => {
        if (err.status !== 401) setError(err.message)
      })
  }, [token])

  function handleLogin(newToken) {
    localStorage.setItem(TOKEN_KEY, newToken)
    setToken(newToken)
    setNotice('')
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
        {notice && <p className="notice">{notice}</p>}
        <AuthForm onLogin={handleLogin} />
      </main>
    )
  }

  return (
    <main className="wide">
      <header className="topbar">
        <h1>Expense Tracker</h1>
        <div className="session">
          {user && <span>{user.email}</span>}
          <button type="button" className="secondary" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </div>
      </header>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      <Expenses token={token} />
    </main>
  )
}

export default App


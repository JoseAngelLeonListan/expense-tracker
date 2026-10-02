import { useEffect, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

function App() {
  const [status, setStatus] = useState('comprobando...')

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((response) => response.json())
      .then((data) => setStatus(data.status))
      .catch(() => setStatus('sin conexión con la API'))
  }, [])

  return (
    <main>
      <h1>Expense Tracker</h1>
      <p>Estado de la API: {status}</p>
    </main>
  )
}

export default App

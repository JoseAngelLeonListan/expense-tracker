const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

function errorMessage(data) {
  const detail = data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return 'Los datos enviados no son válidos'
  return 'Ha ocurrido un error inesperado'
}

async function request(path, { token, ...options } = {}) {
  const headers = { ...options.headers }
  if (token) headers.Authorization = `Bearer ${token}`

  let response
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers })
  } catch {
    throw new ApiError(0, 'No se puede conectar con el servidor')
  }

  if (response.status === 204) return null
  const data = await response.json().catch(() => null)
  if (!response.ok) throw new ApiError(response.status, errorMessage(data))
  return data
}

export function register(email, password) {
  return request('/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
}

export function login(email, password) {
  return request('/login', {
    method: 'POST',
    body: new URLSearchParams({ username: email, password }),
  })
}

export function getMe(token) {
  return request('/me', { token })
}
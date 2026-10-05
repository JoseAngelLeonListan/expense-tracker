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

let onUnauthorized = null

// App.jsx registra aquí qué hacer cuando el servidor rechaza el token
export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler
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

  // Un 401 con token enviado = token caducado o inválido: cerrar la sesión
  if (response.status === 401 && token && onUnauthorized) onUnauthorized()

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

const JSON_HEADERS = { 'Content-Type': 'application/json' }

// { dateFrom, dateTo, category } -> '?date_from=...&date_to=...&category=...' (omite los vacíos)
function filterQuery({ dateFrom, dateTo, category } = {}) {
  const params = new URLSearchParams()
  if (dateFrom) params.set('date_from', dateFrom)
  if (dateTo) params.set('date_to', dateTo)
  if (category) params.set('category', category)
  const text = params.toString()
  return text ? `?${text}` : ''
}

export function listExpenses(token, filters) {
  return request(`/expenses${filterQuery(filters)}`, { token })
}

export function getSummary(token, filters) {
  return request(`/summary${filterQuery(filters)}`, { token })
}

export function listCategories(token) {
  return request('/categories', { token })
}

export function createExpense(token, expense) {
  return request('/expenses', {
    token,
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify(expense),
  })
}

export function updateExpense(token, id, expense) {
  return request(`/expenses/${id}`, {
    token,
    method: 'PUT',
    headers: JSON_HEADERS,
    body: JSON.stringify(expense),
  })
}

export function deleteExpense(token, id) {
  return request(`/expenses/${id}`, { token, method: 'DELETE' })
}
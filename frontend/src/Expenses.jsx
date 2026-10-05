import { useEffect, useState } from 'react'
import { createExpense, deleteExpense, listExpenses, updateExpense } from './api'
import ExpenseForm from './ExpenseForm'
import ExpenseList from './ExpenseList'

function Expenses({ token }) {
  const [expenses, setExpenses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)

  // Pide la lista al montar, y otra vez cada vez que refreshKey cambia
  useEffect(() => {
    let ignore = false
    listExpenses(token)
      .then((data) => {
        if (ignore) return
        setExpenses(data)
        setError('')
      })
      .catch((err) => {
        if (!ignore && err.status !== 401) setError(err.message)
      })
      .finally(() => {
        if (!ignore) setLoading(false)
      })
    return () => {
      ignore = true
    }
  }, [token, refreshKey])

  function refresh() {
    setRefreshKey((key) => key + 1)
  }

  async function handleSave(data) {
    if (editing) {
      await updateExpense(token, editing.id, data)
      setEditing(null)
    } else {
      await createExpense(token, data)
    }
    refresh()
  }

  async function handleDelete(expense) {
    if (!window.confirm(`¿Borrar "${expense.category}" de ${expense.amount} €?`)) return
    try {
      await deleteExpense(token, expense.id)
      if (editing?.id === expense.id) setEditing(null)
    } catch (err) {
      if (err.status !== 401) setError(err.message)
    }
    refresh()
  }

  return (
    <>
      <ExpenseForm
        key={editing ? editing.id : 'new'}
        expense={editing}
        onSave={handleSave}
        onCancel={() => setEditing(null)}
      />

      <section className="panel">
        <h2>Mis gastos</h2>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        {loading ? (
          <p>Cargando...</p>
        ) : (
          <ExpenseList expenses={expenses} onEdit={setEditing} onDelete={handleDelete} />
        )}
      </section>
    </>
  )
}

export default Expenses
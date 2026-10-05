import { useEffect, useState } from 'react'
import {
  createExpense,
  deleteExpense,
  getSummary,
  listCategories,
  listExpenses,
  updateExpense,
} from './api'
import ExpenseForm from './ExpenseForm'
import ExpenseList from './ExpenseList'
import Filters from './Filters'
import Summary from './Summary'

const NO_FILTERS = { dateFrom: '', dateTo: '', category: '' }

function Expenses({ token }) {
  const [expenses, setExpenses] = useState([])
  const [summary, setSummary] = useState(null)
  const [categories, setCategories] = useState([])
  const [filters, setFilters] = useState(NO_FILTERS)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)

  // Pide lista, resumen y categorías al montar, y otra vez si cambian los filtros o refreshKey
  useEffect(() => {
    let ignore = false
    Promise.all([
      listExpenses(token, filters),
      getSummary(token, filters),
      listCategories(token),
    ])
      .then(([expensesData, summaryData, categoriesData]) => {
        if (ignore) return
        setExpenses(expensesData)
        setSummary(summaryData)
        setCategories(categoriesData)
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
  }, [token, filters, refreshKey])

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

      <Filters filters={filters} categories={categories} onChange={setFilters} />

      {summary && <Summary summary={summary} />}

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
          <ExpenseList
            expenses={expenses}
            filtered={Boolean(filters.dateFrom || filters.dateTo || filters.category)}
            onEdit={setEditing}
            onDelete={handleDelete}
          />
        )}
      </section>
    </>
  )
}

export default Expenses
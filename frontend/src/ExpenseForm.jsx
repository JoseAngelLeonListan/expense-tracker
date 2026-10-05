import { useState } from 'react'

// Fecha de hoy en formato AAAA-MM-DD según la hora LOCAL ('sv-SE' usa ese formato)
function today() {
  return new Date().toLocaleDateString('sv-SE')
}

function ExpenseForm({ expense, onSave, onCancel }) {
  const isEditing = expense !== null
  const [amount, setAmount] = useState(isEditing ? String(expense.amount) : '')
  const [category, setCategory] = useState(isEditing ? expense.category : '')
  const [description, setDescription] = useState(expense?.description ?? '')
  const [date, setDate] = useState(isEditing ? expense.date : today())
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSaving(true)
    try {
      await onSave({
        amount: Number(amount),
        category: category.trim(),
        description: description.trim() || null,
        date,
      })
      if (!isEditing) {
        setAmount('')
        setCategory('')
        setDescription('')
        setDate(today())
      }
    } catch (err) {
      if (err.status !== 401) setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="panel form-grid" onSubmit={handleSubmit}>
      <h2>{isEditing ? 'Editar gasto' : 'Nuevo gasto'}</h2>

      <label>
        Importe (€)
        <input
          type="number"
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
          min="0.01"
          step="0.01"
          required
        />
      </label>

      <label>
        Categoría
        <input
          type="text"
          value={category}
          onChange={(event) => setCategory(event.target.value)}
          maxLength={50}
          required
        />
      </label>

      <label>
        Fecha
        <input
          type="date"
          value={date}
          onChange={(event) => setDate(event.target.value)}
          required
        />
      </label>

      <label>
        Descripción (opcional)
        <input
          type="text"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          maxLength={200}
        />
      </label>

      {error && (
        <p className="error full-row" role="alert">
          {error}
        </p>
      )}

      <div className="actions full-row">
        <button type="submit" disabled={saving}>
          {saving ? 'Guardando...' : isEditing ? 'Guardar cambios' : 'Añadir gasto'}
        </button>
        {isEditing && (
          <button type="button" className="secondary" onClick={onCancel}>
            Cancelar
          </button>
        )}
      </div>
    </form>
  )
}

export default ExpenseForm
const money = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' })

// '2026-09-30' -> '30/09/2026' (se corta el texto: new Date() podría mover el día por la zona horaria)
function formatDate(isoDate) {
  return isoDate.split('-').reverse().join('/')
}

function ExpenseList({ expenses, filtered, onEdit, onDelete }) {
  if (expenses.length === 0) {
    return (
      <p className="empty">
        {filtered
          ? 'No hay gastos con estos filtros.'
          : 'Todavía no tienes gastos. Añade el primero arriba.'}
      </p>
    )
  }

  const total = expenses.reduce((sum, expense) => sum + expense.amount, 0)

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Categoría</th>
            <th>Descripción</th>
            <th className="num">Importe</th>
            <th>
              <span className="visually-hidden">Acciones</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {expenses.map((expense) => (
            <tr key={expense.id}>
              <td>{formatDate(expense.date)}</td>
              <td>{expense.category}</td>
              <td>{expense.description}</td>
              <td className="num">{money.format(expense.amount)}</td>
              <td className="row-actions">
                <button type="button" className="link" onClick={() => onEdit(expense)}>
                  Editar
                </button>
                <button type="button" className="link danger" onClick={() => onDelete(expense)}>
                  Borrar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th colSpan={3}>Total</th>
            <th className="num">{money.format(total)}</th>
            <td />
          </tr>
        </tfoot>
      </table>
    </div>
  )
}

export default ExpenseList
const money = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' })

// '2026-09' -> 'sept 2026'. Se construye la fecha con números (hora local): sin saltos por zona horaria.
function monthLabel(isoMonth) {
  const [year, month] = isoMonth.split('-').map(Number)
  return new Date(year, month - 1, 1).toLocaleDateString('es-ES', {
    month: 'short',
    year: 'numeric',
  })
}

function Bars({ title, rows }) {
  const max = Math.max(...rows.map((row) => row.total))
  return (
    <div className="bars">
      <h3>{title}</h3>
      <ul>
        {rows.map((row) => (
          <li key={row.label}>
            <span className="bar-label">{row.label}</span>
            <span className="bar-track" aria-hidden="true">
              <span className="bar-fill" style={{ width: `${(row.total / max) * 100}%` }} />
            </span>
            <span className="bar-value">{money.format(row.total)}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

function Summary({ summary }) {
  if (summary.count === 0) return null

  return (
    <section className="panel">
      <h2>Resumen</h2>
      <p className="headline">
        <strong>{money.format(summary.total)}</strong>
        <span>
          en {summary.count} {summary.count === 1 ? 'gasto' : 'gastos'}
        </span>
      </p>
      <div className="bars-grid">
        <Bars
          title="Por categoría"
          rows={summary.by_category.map((row) => ({ label: row.category, total: row.total }))}
        />
        <Bars
          title="Por mes"
          rows={summary.by_month.map((row) => ({ label: monthLabel(row.month), total: row.total }))}
        />
      </div>
    </section>
  )
}

export default Summary
function Filters({ filters, categories, onChange }) {
  const hasFilters = filters.dateFrom || filters.dateTo || filters.category

  // Si la categoría filtrada ya no existe (por ejemplo, se borró su último gasto), se sigue mostrando
  const options = filters.category && !categories.includes(filters.category)
    ? [...categories, filters.category]
    : categories

  function update(field, value) {
    onChange({ ...filters, [field]: value })
  }

  return (
    <section className="panel filters" aria-label="Filtros">
      <label>
        Desde
        <input
          type="date"
          value={filters.dateFrom}
          max={filters.dateTo || undefined}
          onChange={(event) => update('dateFrom', event.target.value)}
        />
      </label>

      <label>
        Hasta
        <input
          type="date"
          value={filters.dateTo}
          min={filters.dateFrom || undefined}
          onChange={(event) => update('dateTo', event.target.value)}
        />
      </label>

      <label>
        Categoría
        <select
          value={filters.category}
          onChange={(event) => update('category', event.target.value)}
        >
          <option value="">Todas</option>
          {options.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
      </label>

      <button
        type="button"
        className="secondary"
        disabled={!hasFilters}
        onClick={() => onChange({ dateFrom: '', dateTo: '', category: '' })}
      >
        Limpiar filtros
      </button>
    </section>
  )
}

export default Filters
# expense-tracker

[![CI](https://github.com/JoseAngelLeonListan/expense-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/JoseAngelLeonListan/expense-tracker/actions/workflows/ci.yml)

Aplicación web para apuntar gastos personales y ver cuánto gastas por categoría y por mes. Cada usuario se registra, inicia sesión y solo ve sus propios gastos.

<!-- Capturas: añade aquí imágenes de la pantalla de login y de la tabla con el gráfico. -->

## Funcionalidades

- Registro e inicio de sesión con **JWT** (contraseñas cifradas con Argon2).
- Crear, editar, borrar y listar gastos; cada usuario solo accede a los suyos.
- Filtros por fecha y categoría.
- Resumen: total, número de gastos, total por categoría y por mes, con gráfico de barras.
- Importes exactos: `NUMERIC(10, 2)` en la base de datos, nada de errores de redondeo con `float`.

## Tecnologías

| Parte | Tecnología |
|---|---|
| Backend | Python 3.14, FastAPI, SQLAlchemy 2, Pydantic, Alembic |
| Base de datos | PostgreSQL 16 (SQLite para desarrollo rápido y tests) |
| Frontend | React 19 + Vite, servido con nginx |
| Tests | pytest (60 tests + 3 contra PostgreSQL real) |
| Infraestructura | Docker Compose, GitHub Actions |

```
Navegador ──> frontend (nginx, :8080) 
    └──────> backend (FastAPI, :8000) ──> db (PostgreSQL, :5432)
                    ↑
              migrate (alembic upgrade head, se ejecuta una vez al arrancar)
```

## Arrancar todo con Docker

Requisitos: Docker con Docker Compose.

```bash
git clone https://github.com/JoseAngelLeonListan/expense-tracker.git
cd expense-tracker
cp .env.example .env
# Edita .env: pon una contraseña en POSTGRES_PASSWORD y una clave en SECRET_KEY
#   (genérala con: openssl rand -hex 32)
docker compose up -d --build --wait
```

- App: <http://localhost:8080>
- API y documentación interactiva (Swagger): <http://localhost:8000/docs>

Parar: `docker compose down` (los datos se conservan en el volumen `pgdata`; `docker compose down -v` los **borra**).

## Desarrollo sin Docker

**Backend** (en `backend/`):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # y rellena SECRET_KEY
alembic upgrade head
uvicorn main:app --reload
```

Por defecto usa SQLite (`expenses.db`). Para usar el PostgreSQL de Docker, arranca solo la base de datos con `docker compose up -d db` y define `DATABASE_URL` en `backend/.env` (hay un ejemplo en `backend/.env.example`).

**Frontend** (en `frontend/`):

```bash
npm install
npm run dev                 # http://localhost:5173
```

## Tests

```bash
cd backend
pytest                      # SQLite en memoria: no necesita nada más
```

Los tests de `tests/test_postgres.py` solo se ejecutan si defines `TEST_POSTGRES_URL` apuntando a una base de datos **solo para tests** (borran y recrean las tablas):

```bash
TEST_POSTGRES_URL=postgresql+psycopg://expenses:<contraseña>@127.0.0.1:5432/expenses_test pytest
```

En cada push y pull request, **GitHub Actions** ejecuta todos los tests contra PostgreSQL, el lint y la compilación del frontend, y arranca el `docker compose` completo para comprobar que todo responde.

## API

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/health` | Comprueba que la API responde |
| POST | `/register` | Crea un usuario |
| POST | `/login` | Devuelve un token JWT |
| GET | `/me` | Usuario actual |
| GET | `/expenses` | Lista de gastos (filtros `date_from`, `date_to`, `category`) |
| POST | `/expenses` | Crea un gasto |
| PUT | `/expenses/{id}` | Modifica un gasto |
| DELETE | `/expenses/{id}` | Borra un gasto |
| GET | `/summary` | Total y totales por categoría y mes (mismos filtros) |
| GET | `/categories` | Categorías del usuario |

## Estructura

```
backend/        API FastAPI, modelos, migraciones (Alembic) y tests
frontend/       App React (Vite)
docker-compose.yml
.github/workflows/ci.yml
```

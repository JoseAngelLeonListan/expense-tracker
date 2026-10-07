"""Tests contra un PostgreSQL real. Solo se ejecutan si defines TEST_POSTGRES_URL, por ejemplo:

    TEST_POSTGRES_URL=postgresql+psycopg://expenses:<contraseña>@127.0.0.1:5432/expenses_test pytest

¡Ojo! Borran y recrean las tablas: usa una base de datos solo para tests, nunca la de la app.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

TEST_POSTGRES_URL = os.environ.get("TEST_POSTGRES_URL")

pytestmark = pytest.mark.skipif(
    not TEST_POSTGRES_URL, reason="define TEST_POSTGRES_URL para probar contra PostgreSQL"
)


@pytest.fixture()
def pg_client():
    """Como la fixture client, pero con PostgreSQL: tablas nuevas en cada test."""
    engine = create_engine(TEST_POSTGRES_URL)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def login(client, email="ana@example.com", password="clave-de-prueba-123"):
    client.post("/register", json={"email": email, "password": password})
    token = client.post("/login", data={"username": email, "password": password}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {token}"}


def add(client, headers, amount, date="2026-09-30", category="comida"):
    response = client.post(
        "/expenses",
        json={"amount": amount, "category": category, "date": date},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_amount_is_a_json_number(pg_client):
    ana = login(pg_client)
    assert add(pg_client, ana, 12.5)["amount"] == 12.5
    assert pg_client.get("/expenses", headers=ana).json()[0]["amount"] == 12.5


def test_ten_times_ten_cents_is_exactly_one_euro(pg_client):
    # Con Float esto daría 0.9999999999999999; con Numeric la suma es exacta
    ana = login(pg_client)
    for _ in range(10):
        add(pg_client, ana, 0.10)
    body = pg_client.get("/summary", headers=ana).json()
    assert body["total"] == 1.0
    assert body["by_category"] == [{"category": "comida", "total": 1.0}]


def test_summary_by_month_in_postgres(pg_client):
    ana = login(pg_client)
    add(pg_client, ana, 10, "2026-08-15")
    add(pg_client, ana, 20.5, "2026-09-10")
    add(pg_client, ana, 40, "2026-09-20", "transporte")
    body = pg_client.get("/summary", headers=ana).json()
    assert body["by_month"] == [
        {"month": "2026-08", "total": 10},
        {"month": "2026-09", "total": 60.5},
    ]

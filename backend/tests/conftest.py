import os

# La clave debe existir ANTES de importar la app, porque security.py la lee al importarse.
os.environ["SECRET_KEY"] = "clave-secreta-solo-para-los-tests-no-usar-nunca-en-produccion-0123456789"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from database import Base, get_db  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture()
def client():
    """Un cliente de pruebas con una base de datos en memoria, nueva en cada test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

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
    engine.dispose()


@pytest.fixture()
def make_user(client):
    """Registra un usuario, hace login y devuelve las cabeceras con su token."""

    def _make_user(email, password="clave-de-prueba-123"):
        response = client.post("/register", json={"email": email, "password": password})
        assert response.status_code == 201
        response = client.post("/login", data={"username": email, "password": password})
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _make_user
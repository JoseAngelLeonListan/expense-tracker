import datetime

import jwt

from security import ALGORITHM, SECRET_KEY

PASSWORD = "clave-de-prueba-123"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_ok(client):
    response = client.post(
        "/register", json={"email": "ana@example.com", "password": PASSWORD}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ana@example.com"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email(client):
    data = {"email": "ana@example.com", "password": PASSWORD}
    assert client.post("/register", json=data).status_code == 201
    assert client.post("/register", json=data).status_code == 409


def test_register_email_is_case_insensitive(client):
    client.post("/register", json={"email": "Ana@Example.com", "password": PASSWORD})
    response = client.post(
        "/register", json={"email": "ana@example.com", "password": PASSWORD}
    )
    assert response.status_code == 409


def test_register_invalid_email(client):
    response = client.post(
        "/register", json={"email": "hola", "password": PASSWORD}
    )
    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post(
        "/register", json={"email": "ana@example.com", "password": "corta"}
    )
    assert response.status_code == 422


def test_login_ok(client, make_user):
    make_user("ana@example.com")
    response = client.post(
        "/login", data={"username": "ana@example.com", "password": PASSWORD}
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_wrong_password(client, make_user):
    make_user("ana@example.com")
    response = client.post(
        "/login", data={"username": "ana@example.com", "password": "otra-clave-123"}
    )
    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post(
        "/login", data={"username": "nadie@example.com", "password": PASSWORD}
    )
    assert response.status_code == 401


def test_me_requires_token(client):
    assert client.get("/me").status_code == 401


def test_me_with_token(client, make_user):
    headers = make_user("ana@example.com")
    response = client.get("/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "ana@example.com"


def test_invalid_token_is_rejected(client):
    response = client.get("/me", headers={"Authorization": "Bearer token-falso"})
    assert response.status_code == 401


def test_expired_token_is_rejected(client, make_user):
    make_user("ana@example.com")
    past = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)
    expired = jwt.encode({"sub": "1", "exp": past}, SECRET_KEY, algorithm=ALGORITHM)
    response = client.get("/me", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401
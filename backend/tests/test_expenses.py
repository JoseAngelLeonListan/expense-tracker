EXPENSE = {
    "amount": 12.5,
    "category": "comida",
    "description": "menú del día",
    "date": "2026-09-30",
}


def test_expenses_require_token(client):
    assert client.get("/expenses").status_code == 401
    assert client.post("/expenses", json=EXPENSE).status_code == 401
    assert client.put("/expenses/1", json=EXPENSE).status_code == 401
    assert client.delete("/expenses/1").status_code == 401


def test_create_and_list_expense(client, make_user):
    ana = make_user("ana@example.com")
    response = client.post("/expenses", json=EXPENSE, headers=ana)
    assert response.status_code == 201
    assert response.json()["amount"] == 12.5
    assert response.json()["category"] == "comida"

    response = client.get("/expenses", headers=ana)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_negative_amount_is_rejected(client, make_user):
    ana = make_user("ana@example.com")
    response = client.post("/expenses", json={**EXPENSE, "amount": -5}, headers=ana)
    assert response.status_code == 422


def test_user_only_sees_own_expenses(client, make_user):
    ana = make_user("ana@example.com")
    bruno = make_user("bruno@example.com")
    client.post("/expenses", json=EXPENSE, headers=ana)

    assert client.get("/expenses", headers=bruno).json() == []
    assert len(client.get("/expenses", headers=ana).json()) == 1


def test_cannot_update_another_users_expense(client, make_user):
    ana = make_user("ana@example.com")
    bruno = make_user("bruno@example.com")
    expense_id = client.post("/expenses", json=EXPENSE, headers=ana).json()["id"]

    response = client.put(
        f"/expenses/{expense_id}", json={**EXPENSE, "amount": 99}, headers=bruno
    )
    assert response.status_code == 404

    original = client.get("/expenses", headers=ana).json()[0]
    assert original["amount"] == 12.5


def test_cannot_delete_another_users_expense(client, make_user):
    ana = make_user("ana@example.com")
    bruno = make_user("bruno@example.com")
    expense_id = client.post("/expenses", json=EXPENSE, headers=ana).json()["id"]

    assert client.delete(f"/expenses/{expense_id}", headers=bruno).status_code == 404
    assert len(client.get("/expenses", headers=ana).json()) == 1


def test_update_own_expense(client, make_user):
    ana = make_user("ana@example.com")
    expense_id = client.post("/expenses", json=EXPENSE, headers=ana).json()["id"]

    response = client.put(
        f"/expenses/{expense_id}", json={**EXPENSE, "amount": 15}, headers=ana
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 15


def test_delete_own_expense(client, make_user):
    ana = make_user("ana@example.com")
    expense_id = client.post("/expenses", json=EXPENSE, headers=ana).json()["id"]

    assert client.delete(f"/expenses/{expense_id}", headers=ana).status_code == 204
    assert client.get("/expenses", headers=ana).json() == []
    assert client.delete(f"/expenses/{expense_id}", headers=ana).status_code == 404


def test_update_nonexistent_expense(client, make_user):
    ana = make_user("ana@example.com")
    response = client.put("/expenses/999", json=EXPENSE, headers=ana)
    assert response.status_code == 404


def test_user_id_sent_by_client_is_ignored(client, make_user):
    ana = make_user("ana@example.com")
    bruno = make_user("bruno@example.com")
    ana_id = client.get("/me", headers=ana).json()["id"]

    client.post("/expenses", json={**EXPENSE, "user_id": ana_id}, headers=bruno)

    assert client.get("/expenses", headers=ana).json() == []
    assert len(client.get("/expenses", headers=bruno).json()) == 1

def test_amount_with_three_decimals_is_rejected(client, make_user):
    ana = make_user("ana@example.com")
    response = client.post("/expenses", json={**EXPENSE, "amount": 1.234}, headers=ana)
    assert response.status_code == 422


def test_amount_is_returned_as_a_json_number(client, make_user):
    # amount es Decimal por dentro, pero la API debe seguir devolviendo un número, no "12.50"
    ana = make_user("ana@example.com")
    created = client.post("/expenses", json=EXPENSE, headers=ana).json()
    listed = client.get("/expenses", headers=ana).json()[0]
    assert isinstance(created["amount"], float)
    assert isinstance(listed["amount"], float)

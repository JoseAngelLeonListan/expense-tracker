def add(client, headers, amount, category, date, description=None):
    response = client.post(
        "/expenses",
        json={
            "amount": amount,
            "category": category,
            "description": description,
            "date": date,
        },
        headers=headers,
    )
    assert response.status_code == 201


def seed(client, headers):
    add(client, headers, 10, "comida", "2026-08-15")
    add(client, headers, 20.5, "comida", "2026-09-10")
    add(client, headers, 40, "transporte", "2026-09-20")
    add(client, headers, 5.25, "ocio", "2026-10-02")


def test_summary_and_categories_require_token(client):
    assert client.get("/summary").status_code == 401
    assert client.get("/categories").status_code == 401


def test_summary_empty(client, make_user):
    ana = make_user("ana@example.com")
    body = client.get("/summary", headers=ana).json()
    assert body == {"total": 0, "count": 0, "by_category": [], "by_month": []}


def test_summary_totals(client, make_user):
    ana = make_user("ana@example.com")
    seed(client, ana)
    body = client.get("/summary", headers=ana).json()
    assert body["total"] == 75.75
    assert body["count"] == 4


def test_summary_by_category_sorted_by_total_desc(client, make_user):
    ana = make_user("ana@example.com")
    seed(client, ana)
    body = client.get("/summary", headers=ana).json()
    assert body["by_category"] == [
        {"category": "transporte", "total": 40},
        {"category": "comida", "total": 30.5},
        {"category": "ocio", "total": 5.25},
    ]


def test_summary_by_month_sorted_chronologically(client, make_user):
    ana = make_user("ana@example.com")
    seed(client, ana)
    body = client.get("/summary", headers=ana).json()
    assert body["by_month"] == [
        {"month": "2026-08", "total": 10},
        {"month": "2026-09", "total": 60.5},
        {"month": "2026-10", "total": 5.25},
    ]


def test_summary_filters_by_date_range_inclusive(client, make_user):
    ana = make_user("ana@example.com")
    seed(client, ana)
    body = client.get(
        "/summary",
        params={"date_from": "2026-09-10", "date_to": "2026-09-20"},
        headers=ana,
    ).json()
    assert body["count"] == 2
    assert body["total"] == 60.5


def test_summary_filters_by_category(client, make_user):
    ana = make_user("ana@example.com")
    seed(client, ana)
    body = client.get("/summary", params={"category": "comida"}, headers=ana).json()
    assert body["total"] == 30.5
    assert [c["category"] for c in body["by_category"]] == ["comida"]
    assert [m["month"] for m in body["by_month"]] == ["2026-08", "2026-09"]


def test_summary_only_counts_own_expenses(client, make_user):
    ana = make_user("ana@example.com")
    bruno = make_user("bruno@example.com")
    seed(client, ana)
    add(client, bruno, 999, "otros", "2026-09-01")

    assert client.get("/summary", headers=ana).json()["total"] == 75.75
    assert client.get("/summary", headers=bruno).json()["total"] == 999


def test_summary_rejects_inverted_range(client, make_user):
    ana = make_user("ana@example.com")
    response = client.get(
        "/summary",
        params={"date_from": "2026-10-01", "date_to": "2026-09-01"},
        headers=ana,
    )
    assert response.status_code == 422


def test_summary_rejects_invalid_date(client, make_user):
    ana = make_user("ana@example.com")
    response = client.get("/summary", params={"date_from": "ayer"}, headers=ana)
    assert response.status_code == 422


def test_list_expenses_filters(client, make_user):
    ana = make_user("ana@example.com")
    seed(client, ana)

    by_category = client.get("/expenses", params={"category": "comida"}, headers=ana)
    assert len(by_category.json()) == 2

    by_date = client.get("/expenses", params={"date_from": "2026-09-15"}, headers=ana)
    assert [e["category"] for e in by_date.json()] == ["ocio", "transporte"]

    both = client.get(
        "/expenses",
        params={"category": "comida", "date_to": "2026-08-31"},
        headers=ana,
    )
    assert len(both.json()) == 1


def test_list_expenses_filters_do_not_leak_other_users(client, make_user):
    ana = make_user("ana@example.com")
    bruno = make_user("bruno@example.com")
    add(client, ana, 10, "comida", "2026-09-01")
    response = client.get("/expenses", params={"category": "comida"}, headers=bruno)
    assert response.json() == []


def test_categories_are_distinct_sorted_and_own(client, make_user):
    ana = make_user("ana@example.com")
    bruno = make_user("bruno@example.com")
    seed(client, ana)
    add(client, bruno, 1, "secreta", "2026-09-01")

    assert client.get("/categories", headers=ana).json() == [
        "comida",
        "ocio",
        "transporte",
    ]
    assert client.get("/categories", headers=bruno).json() == ["secreta"]
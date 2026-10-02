FRONTEND = "http://localhost:5173"


def test_cors_allows_frontend_origin(client):
    response = client.get("/health", headers={"Origin": FRONTEND})
    assert response.headers["access-control-allow-origin"] == FRONTEND


def test_cors_does_not_allow_unknown_origin(client):
    response = client.get("/health", headers={"Origin": "http://sitio-ajeno.example"})
    assert "access-control-allow-origin" not in response.headers


def test_cors_preflight_for_authenticated_post(client):
    response = client.options(
        "/expenses",
        headers={
            "Origin": FRONTEND,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND
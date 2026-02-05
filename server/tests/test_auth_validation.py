import json


def test_login_missing_fields_returns_400(client):
    response = client.post("/api/login", json={"email": "user@example.com"})
    assert response.status_code == 400

    response = client.post("/api/login", json={"password": "secret"})
    assert response.status_code == 400


def test_login_no_data_returns_400(client):
    response = client.post("/api/login")
    assert response.status_code == 400


def test_login_empty_fields_returns_400(client):
    response = client.post("/api/login", json={"email": "", "password": ""})
    assert response.status_code == 400


def test_login_wrong_credentials_returns_401(client, monkeypatch):
    class FakeAuthService:
        @staticmethod
        def login(_email, _password):
            return {"success": False, "error": "Invalid credentials"}

    monkeypatch.setattr(
        "controllers.auth_controller.get_auth_service",
        lambda: FakeAuthService(),
    )

    response = client.post(
        "/api/login",
        json={"email": "wrong@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_refresh_missing_token_returns_400(client):
    response = client.post("/api/refresh", json={})
    assert response.status_code == 400


def test_logout_missing_refresh_token_returns_400(client, monkeypatch):
    class FakeAuthService:
        @staticmethod
        def verify_token(_token):
            return {"id": "user-123", "role": "user"}

        @staticmethod
        def logout(_access_token, _refresh_token):
            return {"success": True}

    monkeypatch.setattr("middleware.auth.auth_service", FakeAuthService())

    response = client.post(
        "/api/logout",
        data=json.dumps({}),
        content_type="application/json",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 400

from flask import Flask, g, jsonify

from middleware.auth import attach_user, public_route, require_role


def make_app():
    app = Flask(__name__)
    app.before_request(attach_user)
    return app


def test_public_route_decorator_allows_request():
    app = make_app()

    @public_route
    def public_endpoint():
        return jsonify(ok=True)

    app.add_url_rule("/api/public-test", "public_test", public_endpoint)

    with app.test_client() as client:
        response = client.get("/api/public-test")

    assert response.status_code == 200


def test_protected_route_requires_auth():
    app = make_app()

    def protected_endpoint():
        return jsonify(ok=True)

    app.add_url_rule("/api/protected-test", "protected_test", protected_endpoint)

    with app.test_client() as client:
        response = client.get("/api/protected-test")

    assert response.status_code == 401


def test_protected_route_sets_user_id(monkeypatch):
    app = make_app()

    def protected_endpoint():
        return jsonify(user_id=g.user_id)

    app.add_url_rule("/api/protected-user", "protected_user", protected_endpoint)

    class FakeAuthService:
        @staticmethod
        def verify_token(_):
            return {"id": "user-123"}

    monkeypatch.setattr("middleware.auth.auth_service", FakeAuthService())

    with app.test_client() as client:
        response = client.get(
            "/api/protected-user",
            headers={"Authorization": "Bearer test-token"},
        )

    assert response.status_code == 200
    assert response.get_json()["user_id"] == "user-123"


def test_role_guard_rejects_wrong_role(monkeypatch):
    app = make_app()

    @require_role("admin")
    def admin_endpoint():
        return jsonify(ok=True)

    app.add_url_rule("/api/admin-test", "admin_test", admin_endpoint)

    class FakeAuthService:
        @staticmethod
        def verify_token(_):
            return {"id": "user-123", "role": "user"}

    monkeypatch.setattr("middleware.auth.auth_service", FakeAuthService())

    with app.test_client() as client:
        response = client.get(
            "/api/admin-test",
            headers={"Authorization": "Bearer test-token"},
        )

    assert response.status_code == 403


def test_role_guard_allows_correct_role(monkeypatch):
    app = make_app()

    @require_role("admin")
    def admin_endpoint():
        return jsonify(ok=True)

    app.add_url_rule("/api/admin-test-ok", "admin_test_ok", admin_endpoint)

    class FakeAuthService:
        @staticmethod
        def verify_token(_):
            return {"id": "admin-1", "role": "admin"}

    monkeypatch.setattr("middleware.auth.auth_service", FakeAuthService())

    with app.test_client() as client:
        response = client.get(
            "/api/admin-test-ok",
            headers={"Authorization": "Bearer test-token"},
        )

    assert response.status_code == 200

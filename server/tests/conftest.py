import os
import sys
import tempfile
from pathlib import Path
import types
import pytest
from pytest_bdd import given, then
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db import Base  # noqa: E402

# Provide a lightweight supabase stub for unit tests (avoid real dependency).
if "supabase" not in sys.modules:
    supabase_stub = types.ModuleType("supabase")

    class Client:  # pragma: no cover - placeholder for type imports
        pass

    def create_client(_url, _key):
        return Client()

    supabase_stub.Client = Client
    supabase_stub.create_client = create_client
    sys.modules["supabase"] = supabase_stub

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-key")
_db_path = Path(tempfile.gettempdir()) / "devops_assignment_test.db"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_db_path.as_posix()}")

_db_url = os.environ.get("DATABASE_URL", "")
_connect_args = {"check_same_thread": False} if _db_url.startswith("sqlite") else {}
_engine = create_engine(_db_url, connect_args=_connect_args)
Base.metadata.create_all(_engine)


@pytest.fixture
def app():
    from flask import Flask

    from routes import api_bp

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(api_bp, url_prefix="/api")
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@given("an authenticated user", target_fixture="auth_header")
def authenticated_user(monkeypatch):
    class FakeAuthService:
        @staticmethod
        def verify_token(_token):
            return {"id": "user-123", "email": "user@example.com", "role": "user"}

    monkeypatch.setattr("middleware.auth.auth_service", FakeAuthService())
    return {"Authorization": "Bearer test-token"}


@given("no authentication header", target_fixture="auth_header")
def no_auth():
    return None


@then("the response status is 401")
def response_is_unauthorized(request_file_list):
    response = request_file_list
    assert response.status_code == 401


@then("the response status is 404")
def response_is_not_found(request_file_list):
    response = request_file_list
    assert response.status_code == 404

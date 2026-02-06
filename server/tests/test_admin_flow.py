import io
import uuid


class FakeAuthService:
    def __init__(self):
        self._users = {}
        self._tokens = {}
        self._create_user(
            email="admin@example.com",
            password="AdminPass123!",
            role="admin",
            user_id="admin-1",
        )

    def _create_user(self, email, password, role, user_id=None):
        user_id = user_id or f"user-{uuid.uuid4().hex[:8]}"
        self._users[email] = {
            "id": user_id,
            "email": email,
            "role": role,
            "password": password,
            "created_at": "2026-01-01T00:00:00Z",
        }
        return self._users[email]

    def _issue_session(self, user):
        access_token = f"access-{user['id']}"
        refresh_token = f"refresh-{user['id']}"
        self._tokens[access_token] = user
        return {"access_token": access_token, "refresh_token": refresh_token}

    def verify_token(self, token):
        return self._tokens.get(token)

    def login(self, email, password):
        user = self._users.get(email)
        if not user or user["password"] != password:
            return {"success": False, "error": "Invalid credentials"}
        session = self._issue_session(user)
        return {
            "success": True,
            "user": {k: user[k] for k in ("id", "email", "role")},
            "session": session,
        }

    def logout(self, _access_token, _refresh_token):
        return {"success": True}

    def refresh_session(self, _refresh_token):
        return {"success": False, "error": "Not implemented"}

    def get_all_users(self):
        users = [
            {
                "id": user["id"],
                "email": user["email"],
                "role": user["role"],
                "created_at": user["created_at"],
            }
            for user in self._users.values()
        ]
        return {"success": True, "users": users}

    def create_user(self, email, password, role="user"):
        if email in self._users:
            return {"success": False, "error": "User already exists"}
        user = self._create_user(email=email, password=password, role=role)
        return {
            "success": True,
            "user": {"id": user["id"], "email": user["email"], "role": user["role"]},
            "message": "User created successfully",
        }

    def delete_user(self, user_id):
        for email, user in list(self._users.items()):
            if user["id"] == user_id:
                del self._users[email]
                return {"success": True, "message": "User deleted successfully"}
        return {"success": False, "error": "User not found"}


class FakeFileService:
    def __init__(self):
        self._files = []

    def save_file_record(
        self,
        user_id,
        filename,
        original_filename,
        file_path,
        file_size,
        mime_type,
        bucket,
    ):
        file_id = f"file-{uuid.uuid4().hex[:8]}"
        self._files.append(
            {
                "id": file_id,
                "user_id": user_id,
                "original_filename": original_filename,
                "file_path": file_path,
                "file_size": file_size,
                "mime_type": mime_type,
                "bucket": bucket,
                "uploaded_at": "2026-01-01T00:00:00Z",
            }
        )
        return file_id

    def get_user_files(self, user_id):
        return [file for file in self._files if file["user_id"] == user_id]

    def delete_file_record(self, file_id, user_id):
        for idx, file in enumerate(self._files):
            if file["id"] == file_id and file["user_id"] == user_id:
                del self._files[idx]
                return {"success": True, "deleted": True}
        return {"success": True, "deleted": False}


def _patch_services(monkeypatch):
    auth_service = FakeAuthService()
    file_service = FakeFileService()

    monkeypatch.setattr(
        "controllers.auth_controller.get_auth_service", lambda: auth_service
    )
    monkeypatch.setattr("controllers.auth_controller.auth_service", auth_service)
    monkeypatch.setattr("middleware.auth.auth_service", auth_service)
    monkeypatch.setattr("controllers.upload_controller.file_service", file_service)
    monkeypatch.setattr("controllers.file_controller.file_service", file_service)
    monkeypatch.setattr(
        "controllers.upload_controller.upload_file_to_supabase",
        lambda **_: {"bucket": "uploads", "path": "uploads/test-file.txt"},
    )

    return auth_service, file_service


def _login(client, email, password):
    response = client.post("/api/login", json={"email": email, "password": password})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    return payload


def _logout(client, access_token, refresh_token):
    response = client.post(
        "/api/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200


def test_admin_can_create_users_and_list_roles(client, monkeypatch):
    _patch_services(monkeypatch)

    admin_payload = _login(client, "admin@example.com", "AdminPass123!")
    admin_token = admin_payload["session"]["access_token"]
    admin_refresh = admin_payload["session"]["refresh_token"]
    assert admin_payload["user"]["role"] == "admin"

    user_email = f"user-{uuid.uuid4().hex[:6]}@example.com"
    user_password = "UserPass123!"
    user_create = client.post(
        "/api/users",
        json={"email": user_email, "password": user_password, "role": "user"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert user_create.status_code == 201
    user_payload = user_create.get_json()
    assert user_payload["success"] is True
    assert user_payload["user"]["role"] == "user"

    admin_email = f"admin-{uuid.uuid4().hex[:6]}@example.com"
    admin_password = "AdminPass456!"
    admin_create = client.post(
        "/api/users",
        json={"email": admin_email, "password": admin_password, "role": "admin"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_create.status_code == 201
    admin_create_payload = admin_create.get_json()
    assert admin_create_payload["success"] is True
    assert admin_create_payload["user"]["role"] == "admin"

    users_list = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert users_list.status_code == 200
    users_payload = users_list.get_json()
    assert users_payload["success"] is True
    roles = {user["email"]: user["role"] for user in users_payload["users"]}
    assert roles.get(user_email) == "user"
    assert roles.get(admin_email) == "admin"

    _logout(client, admin_token, admin_refresh)


def test_user_can_upload_and_delete_file(client, monkeypatch):
    _patch_services(monkeypatch)

    admin_payload = _login(client, "admin@example.com", "AdminPass123!")
    admin_token = admin_payload["session"]["access_token"]

    user_email = f"user-{uuid.uuid4().hex[:6]}@example.com"
    user_password = "UserPass123!"
    user_create = client.post(
        "/api/users",
        json={"email": user_email, "password": user_password, "role": "user"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert user_create.status_code == 201

    user_payload = _login(client, user_email, user_password)
    user_token = user_payload["session"]["access_token"]
    user_refresh = user_payload["session"]["refresh_token"]

    data = {"file": (io.BytesIO(b"hello"), "robot-file.txt")}
    upload = client.post(
        "/api/upload",
        data=data,
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert upload.status_code == 200

    files_response = client.get(
        "/api/files",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert files_response.status_code == 200
    files_payload = files_response.get_json()
    assert files_payload["success"] is True
    assert files_payload["files"]
    file_id = files_payload["files"][0]["id"]

    delete_response = client.delete(
        f"/api/files/{file_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert delete_response.status_code == 200

    _logout(client, user_token, user_refresh)


def test_new_admin_can_login(client, monkeypatch):
    _patch_services(monkeypatch)

    admin_payload = _login(client, "admin@example.com", "AdminPass123!")
    admin_token = admin_payload["session"]["access_token"]

    admin_email = f"admin-{uuid.uuid4().hex[:6]}@example.com"
    admin_password = "AdminPass456!"
    admin_create = client.post(
        "/api/users",
        json={"email": admin_email, "password": admin_password, "role": "admin"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_create.status_code == 201

    new_admin_payload = _login(client, admin_email, admin_password)
    assert new_admin_payload["user"]["role"] == "admin"

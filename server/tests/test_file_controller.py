from io import BytesIO

from services.supabase_storage import UploadError


def _auth_header(monkeypatch):
    class FakeAuthService:
        @staticmethod
        def verify_token(_token):
            return {"id": "user-123", "role": "user"}

    monkeypatch.setattr("middleware.auth.auth_service", FakeAuthService())
    return {"Authorization": "Bearer test-token"}


def test_upload_external_failure_returns_502(client, monkeypatch):
    headers = _auth_header(monkeypatch)

    monkeypatch.setattr(
        "controllers.upload_controller.upload_file_to_supabase",
        lambda **_: (_ for _ in ()).throw(UploadError(500, "boom")),
    )

    data = {"file": (BytesIO(b"data"), "fail.txt")}
    response = client.post(
        "/api/upload",
        data=data,
        content_type="multipart/form-data",
        headers=headers,
    )

    assert response.status_code == 502


def test_download_external_failure_returns_500(client, monkeypatch):
    headers = _auth_header(monkeypatch)

    monkeypatch.setattr(
        "controllers.file_controller.file_service.get_file_info",
        lambda _file_id, _user_id: {
            "success": True,
            "file": {
                "file_path": "uploads/file.txt",
                "bucket": "uploads",
                "original_filename": "file.txt",
            },
        },
    )

    monkeypatch.setattr(
        "controllers.file_controller.create_signed_url",
        lambda **_: (_ for _ in ()).throw(RuntimeError("storage down")),
    )

    response = client.get("/api/files/file-1/download", headers=headers)
    assert response.status_code == 500


def test_user_cannot_access_another_users_file(client, monkeypatch):
    headers = _auth_header(monkeypatch)

    monkeypatch.setattr(
        "controllers.file_controller.file_service.get_file_info",
        lambda _file_id, _user_id: {
            "success": False,
            "error": "File not found or access denied",
        },
    )

    response = client.get("/api/files/file-99/download", headers=headers)
    assert response.status_code == 404

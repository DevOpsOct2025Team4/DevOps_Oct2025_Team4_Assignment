from pytest_bdd import given, scenarios, then, when


scenarios("../features/download.feature")


@given("a file exists for the user", target_fixture="file_id")
def file_exists(monkeypatch):
    file_info = {
        "id": "file-1",
        "file_path": "uploads/file-1.txt",
        "bucket": "uploads",
        "original_filename": "file-1.txt",
    }
    monkeypatch.setattr(
        "controllers.file_controller.file_service.get_file_info",
        lambda _file_id, _user_id: {"success": True, "file": file_info},
    )

    monkeypatch.setattr(
        "controllers.file_controller.create_signed_url",
        lambda **_: {"signedURL": "https://example.com/file-1.txt"},
    )
    return "file-1"


@given("no file exists for the user", target_fixture="file_id")
def file_missing(monkeypatch):
    monkeypatch.setattr(
        "controllers.file_controller.file_service.get_file_info",
        lambda _file_id, _user_id: {"success": False, "error": "File not found"},
    )
    return "file-1"


@when("the user requests the file download", target_fixture="request_file_list")
def request_download(client, auth_header, file_id):
    headers = auth_header or {}
    return client.get(f"/api/files/{file_id}/download", headers=headers)


@then("the response includes a signed download url")
def response_has_signed_url(request_file_list):
    response = request_file_list
    data = response.get_json()
    assert response.status_code == 200
    assert data["download_url"] == "https://example.com/file-1.txt"


@then("the response status is 404")
def response_is_not_found(request_file_list):
    response = request_file_list
    assert response.status_code == 404

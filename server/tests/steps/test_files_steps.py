from pytest_bdd import given, scenarios, then, when


scenarios("../features/files.feature")


@given("the user has uploaded files")
def user_has_files(monkeypatch):
    fake_files = [
        {"id": "file-1", "original_filename": "one.txt"},
        {"id": "file-2", "original_filename": "two.txt"},
    ]
    monkeypatch.setattr(
        "controllers.file_controller.file_service.get_user_files",
        lambda _user_id: fake_files,
    )
    return fake_files


@when("the user requests the file list", target_fixture="request_file_list")
def request_file_list(client, auth_header):
    headers = auth_header or {}
    return client.get("/api/files", headers=headers)


@then("the response contains the user's files")
def response_contains_files(request_file_list):
    response = request_file_list
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert len(data["files"]) == 2

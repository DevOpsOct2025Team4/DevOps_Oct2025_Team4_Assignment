from pytest_bdd import given, scenarios, then, when


scenarios("../features/delete.feature")


@given("a file can be deleted", target_fixture="file_id")
def deletable_file(monkeypatch):
    monkeypatch.setattr(
        "controllers.file_controller.file_service.delete_file_record",
        lambda _file_id, _user_id: {"success": True, "deleted": True},
    )
    return "file-1"


@given("a file cannot be deleted", target_fixture="file_id")
def undeletable_file(monkeypatch):
    monkeypatch.setattr(
        "controllers.file_controller.file_service.delete_file_record",
        lambda _file_id, _user_id: {"success": True, "deleted": False},
    )
    return "file-1"


@when("the user deletes the file", target_fixture="request_file_list")
def delete_file(client, auth_header, file_id):
    headers = auth_header or {}
    return client.delete(f"/api/files/{file_id}", headers=headers)


@then("the delete response is successful")
def delete_success(request_file_list):
    response = request_file_list
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True

from io import BytesIO

from pytest_bdd import given, scenarios, then, when


scenarios("../features/upload.feature")


@given("a file ready to upload", target_fixture="upload_data")
def file_ready():
    return {"file": (BytesIO(b"hello"), "hello.txt")}


@when("the user uploads the file", target_fixture="request_file_list")
def upload_file(client, auth_header, upload_data, monkeypatch):
    monkeypatch.setattr(
        "controllers.upload_controller.upload_file_to_supabase",
        lambda **_: {"path": "uploads/hello.txt", "bucket": "uploads"},
    )
    monkeypatch.setattr(
        "controllers.upload_controller.file_service.save_file_record",
        lambda **_: {"success": True},
    )
    headers = auth_header or {}
    return client.post(
        "/api/upload",
        data=upload_data,
        content_type="multipart/form-data",
        headers=headers,
    )


@when("the user uploads without a file", target_fixture="request_file_list")
def upload_without_file(client, auth_header):
    headers = auth_header or {}
    return client.post("/api/upload", data={}, headers=headers)


@then("the upload response includes the stored path")
def upload_response_has_path(request_file_list):
    response = request_file_list
    data = response.get_json()
    assert response.status_code == 200
    assert data["path"] == "uploads/hello.txt"


@then("the response status is 400")
def response_is_bad_request(request_file_list):
    response = request_file_list
    assert response.status_code == 400

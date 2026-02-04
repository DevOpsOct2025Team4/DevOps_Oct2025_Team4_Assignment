from unittest.mock import MagicMock

from services.file_service import FileService


def make_service_with_mock(supabase_mock: MagicMock) -> FileService:
    service = FileService()
    service.supabase = supabase_mock
    return service


def test_save_file_record_success():
    supabase = MagicMock()
    execute_mock = MagicMock()
    execute_mock.data = [{"id": "file-1"}]
    (supabase.table.return_value.insert.return_value.execute).return_value = (
        execute_mock
    )

    service = make_service_with_mock(supabase)
    result = service.save_file_record(
        user_id="user-1",
        filename="stored.txt",
        original_filename="original.txt",
        file_path="uploads/stored.txt",
        file_size=123,
        mime_type="text/plain",
        bucket="uploads",
    )

    assert result["success"] is True
    assert result["file"]["id"] == "file-1"


def test_get_user_files_returns_list():
    supabase = MagicMock()
    execute_mock = MagicMock()
    execute_mock.data = [{"id": "file-1"}]
    (
        supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute
    ).return_value = execute_mock

    service = make_service_with_mock(supabase)
    files = service.get_user_files("user-1")

    assert files == [{"id": "file-1"}]


def test_get_user_files_on_exception_returns_empty():
    supabase = MagicMock()
    supabase.table.side_effect = Exception("boom")

    service = make_service_with_mock(supabase)
    files = service.get_user_files("user-1")

    assert files == []


def test_get_file_info_success():
    supabase = MagicMock()
    execute_mock = MagicMock()
    execute_mock.data = [{"id": "file-1"}]
    select_mock = supabase.table.return_value.select.return_value
    first_eq = select_mock.eq.return_value
    second_eq = first_eq.eq.return_value
    second_eq.execute.return_value = execute_mock

    service = make_service_with_mock(supabase)
    result = service.get_file_info("file-1", "user-1")

    assert result["success"] is True
    assert result["file"]["id"] == "file-1"
    select_mock.eq.assert_called_with("id", "file-1")
    first_eq.eq.assert_called_with("user_id", "user-1")


def test_get_file_info_not_found():
    supabase = MagicMock()
    execute_mock = MagicMock()
    execute_mock.data = []
    (
        supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute
    ).return_value = execute_mock

    service = make_service_with_mock(supabase)
    result = service.get_file_info("file-1", "user-1")

    assert result["success"] is False


def test_delete_file_record_returns_deleted_flag():
    supabase = MagicMock()
    execute_mock = MagicMock()
    execute_mock.data = [{"id": "file-1"}]
    (
        supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute
    ).return_value = execute_mock

    service = make_service_with_mock(supabase)
    result = service.delete_file_record("file-1", "user-1")

    assert result["success"] is True
    assert result["deleted"] is True

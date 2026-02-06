import pytest

from db.models import FileRecord
from db.session import get_session
from services.file_service import FileService


@pytest.fixture(autouse=True)
def clean_files():
    session = get_session()
    session.execute(FileRecord.__table__.delete())
    session.commit()
    session.close()


def test_save_file_record_success():
    service = FileService()
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
    assert result["file"]["user_id"] == "user-1"
    assert result["file"]["filename"] == "stored.txt"


def test_get_user_files_returns_list():
    session = get_session()
    record = FileRecord(
        user_id="user-1",
        filename="stored.txt",
        original_filename="original.txt",
        file_path="uploads/stored.txt",
        file_size=123,
        mime_type="text/plain",
        bucket="uploads",
    )
    session.add(record)
    session.commit()
    session.close()

    service = FileService()
    files = service.get_user_files("user-1")

    assert len(files) == 1
    assert files[0]["filename"] == "stored.txt"


def test_get_user_files_on_exception_returns_empty(monkeypatch):
    service = FileService()

    def _boom():
        raise RuntimeError("boom")

    monkeypatch.setattr("services.file_service.get_session", _boom)
    files = service.get_user_files("user-1")

    assert files == []


def test_get_file_info_success():
    session = get_session()
    record = FileRecord(
        user_id="user-1",
        filename="stored.txt",
        original_filename="original.txt",
        file_path="uploads/stored.txt",
        file_size=123,
        mime_type="text/plain",
        bucket="uploads",
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    session.close()

    service = FileService()
    result = service.get_file_info(record.id, "user-1")

    assert result["success"] is True
    assert result["file"]["id"] == record.id


def test_get_file_info_not_found():
    service = FileService()
    result = service.get_file_info("missing-id", "user-1")

    assert result["success"] is False


def test_delete_file_record_returns_deleted_flag():
    session = get_session()
    record = FileRecord(
        user_id="user-1",
        filename="stored.txt",
        original_filename="original.txt",
        file_path="uploads/stored.txt",
        file_size=123,
        mime_type="text/plain",
        bucket="uploads",
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    session.close()

    service = FileService()
    result = service.delete_file_record(record.id, "user-1")

    assert result["success"] is True
    assert result["deleted"] is True

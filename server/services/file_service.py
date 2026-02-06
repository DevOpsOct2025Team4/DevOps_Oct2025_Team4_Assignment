import os
from typing import List, Dict, Any

from sqlalchemy import desc, select
from db.models import FileRecord
from db.session import get_session


class FileService:
    def __init__(self):
        if not os.getenv("DATABASE_URL"):
            raise ValueError("DATABASE_URL must be set for file records")

    def save_file_record(
        self,
        user_id: str,
        filename: str,
        original_filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        bucket: str,
    ) -> Dict[str, Any]:
        """
        Save file metadata to database
        """
        try:
            session = get_session()
        except Exception as exc:
            return {"success": False, "error": str(exc)}
        try:
            record = FileRecord(
                user_id=user_id,
                filename=filename,
                original_filename=original_filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                bucket=bucket,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return {"success": True, "file": record.to_dict()}
        except Exception as exc:
            session.rollback()
            return {"success": False, "error": str(exc)}
        finally:
            session.close()

    def get_user_files(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all files uploaded by a specific user
        """
        try:
            session = get_session()
        except Exception:
            return []
        try:
            stmt = (
                select(FileRecord)
                .where(FileRecord.user_id == user_id)
                .order_by(desc(FileRecord.uploaded_at))
            )
            records = session.scalars(stmt).all()
            return [record.to_dict() for record in records]
        except Exception:
            return []
        finally:
            session.close()

    def get_file_info(self, file_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get file info for download (only if owned by user)
        """
        try:
            session = get_session()
        except Exception as exc:
            return {"success": False, "error": str(exc)}
        try:
            stmt = select(FileRecord).where(
                FileRecord.id == file_id, FileRecord.user_id == user_id
            )
            record = session.scalars(stmt).first()
            if record:
                return {"success": True, "file": record.to_dict()}
            return {"success": False, "error": "File not found or access denied"}
        except Exception as exc:
            return {"success": False, "error": str(exc)}
        finally:
            session.close()

    def delete_file_record(self, file_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete file record from database (only if owned by user)
        """
        try:
            session = get_session()
        except Exception as exc:
            return {"success": False, "error": str(exc)}
        try:
            stmt = (
                FileRecord.__table__.delete()
                .where(FileRecord.id == file_id)
                .where(FileRecord.user_id == user_id)
            )
            result = session.execute(stmt)
            session.commit()
            return {"success": True, "deleted": result.rowcount > 0}
        except Exception as exc:
            session.rollback()
            return {"success": False, "error": str(exc)}
        finally:
            session.close()

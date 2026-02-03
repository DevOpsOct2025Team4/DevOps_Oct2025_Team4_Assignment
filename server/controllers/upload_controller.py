import os

from flask import jsonify, request

from services.supabase_storage import UploadError, upload_file_to_supabase
from services.file_service import FileService
from services.auth_service import AuthService


file_service = FileService()
auth_service = AuthService()


def upload():
    # Verify authentication
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify(error="Authentication required"), 401
    
    access_token = auth_header.split(" ")[1]
    user = auth_service.verify_token(access_token)
    
    if not user:
        return jsonify(error="Invalid or expired token"), 401
    
    if "file" not in request.files:
        return jsonify(error="Missing file field"), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify(error="No file selected"), 400

    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    bucket = os.getenv("SUPABASE_BUCKET", "uploads").strip()
    is_public = os.getenv("SUPABASE_STORAGE_PUBLIC", "true").lower() in (
        "1",
        "true",
        "yes",
        "y",
    )

    missing = []
    if not supabase_url:
        missing.append("SUPABASE_URL")
    if not service_key:
        missing.append("SUPABASE_SERVICE_ROLE_KEY")
    if missing:
        return (
            jsonify(
                error="Supabase configuration missing",
                missing=missing,
            ),
            500,
        )

    try:
        payload = upload_file_to_supabase(
            file=file,
            supabase_url=supabase_url,
            service_key=service_key,
            bucket=bucket,
            is_public=is_public,
        )
        
        # Save file record to database
        file_service.save_file_record(
            user_id=user["id"],
            filename=payload.get("path", "").split("/")[-1],
            original_filename=file.filename,
            file_path=payload.get("path", ""),
            file_size=file.content_length or 0,
            mime_type=file.content_type or "application/octet-stream",
            bucket=bucket
        )
        
    except UploadError as exc:
        return (
            jsonify(
                error="Upload failed",
                status=exc.status_code,
                detail=exc.detail,
            ),
            502,
        )

    return jsonify(payload)

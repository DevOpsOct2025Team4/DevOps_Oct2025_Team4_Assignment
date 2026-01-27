import os

from flask import jsonify, request

from services.supabase_storage import UploadError, upload_file_to_supabase


def upload():
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

from flask import g, jsonify
from services.file_service import FileService


file_service = FileService()


def get_user_files():
    """
    GET /api/files
    Headers: Authorization: Bearer <access_token>
    Returns: List of files uploaded by the current user
    """
    try:
        user_id = getattr(g, "user_id", None)
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        files = file_service.get_user_files(user_id)

        return jsonify({"success": True, "files": files}), 200

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Failed to retrieve files: {str(e)}"}),
            500,
        )


def download_file(file_id):
    """
    GET /api/files/<file_id>/download
    Headers: Authorization: Bearer <access_token>
    Returns: File download URL or redirect
    """
    try:
        user_id = getattr(g, "user_id", None)
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        # Get file info from database
        result = file_service.get_file_info(file_id, user_id)

        if not result["success"]:
            return (
                jsonify(
                    {"success": False, "error": result.get("error", "File not found")}
                ),
                404,
            )

        file_info = result["file"]
        file_path = file_info["file_path"]
        bucket = file_info["bucket"]

        # Generate signed URL for download
        supabase = file_service.supabase
        signed_url = supabase.storage.from_(bucket).create_signed_url(
            file_path, 60
        )  # 60 seconds expiry

        return (
            jsonify(
                {
                    "success": True,
                    "download_url": signed_url["signedURL"],
                    "filename": file_info["original_filename"],
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Failed to generate download URL: {str(e)}",
                }
            ),
            500,
        )


def delete_file(file_id):
    """
    DELETE /api/files/<file_id>
    Headers: Authorization: Bearer <access_token>
    Returns: Success message
    """
    try:
        user_id = getattr(g, "user_id", None)
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        result = file_service.delete_file_record(file_id, user_id)

        if result["success"] and result.get("deleted"):
            return (
                jsonify({"success": True, "message": "File deleted successfully"}),
                200,
            )
        elif result["success"] and not result.get("deleted"):
            return (
                jsonify({"success": False, "error": "File not found or access denied"}),
                404,
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": result.get("error", "Failed to delete file"),
                    }
                ),
                500,
            )

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Failed to delete file: {str(e)}"}),
            500,
        )

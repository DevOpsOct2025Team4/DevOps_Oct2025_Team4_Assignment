from flask import request, jsonify
from services.file_service import FileService
from services.auth_service import AuthService


file_service = FileService()
auth_service = AuthService()


def get_user_files():
    """
    GET /api/files
    Headers: Authorization: Bearer <access_token>
    Returns: List of files uploaded by the current user
    """
    try:
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "error": "No access token provided"
            }), 401
        
        access_token = auth_header.split(" ")[1]
        user = auth_service.verify_token(access_token)
        
        if not user:
            return jsonify({
                "success": False,
                "error": "Invalid or expired token"
            }), 401
        
        files = file_service.get_user_files(user["id"])
        
        return jsonify({
            "success": True,
            "files": files
        }), 200
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve files: {str(e)}"
        }), 500


def delete_file(file_id):
    """
    DELETE /api/files/<file_id>
    Headers: Authorization: Bearer <access_token>
    Returns: Success message
    """
    try:
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "error": "No access token provided"
            }), 401
        
        access_token = auth_header.split(" ")[1]
        user = auth_service.verify_token(access_token)
        
        if not user:
            return jsonify({
                "success": False,
                "error": "Invalid or expired token"
            }), 401
        
        result = file_service.delete_file_record(file_id, user["id"])
        
        if result["success"] and result.get("deleted"):
            return jsonify({
                "success": True,
                "message": "File deleted successfully"
            }), 200
        elif result["success"] and not result.get("deleted"):
            return jsonify({
                "success": False,
                "error": "File not found or access denied"
            }), 404
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to delete file")
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to delete file: {str(e)}"
        }), 500

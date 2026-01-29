from flask import request, jsonify
from services.auth_service import AuthService


auth_service = AuthService()


def login():
    """
    POST /api/login
    Request body: { "email": "user@example.com", "password": "password123" }
    Returns: { "success": true, "user": {...}, "session": {...} }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({
                "success": False,
                "error": "Email and password are required"
            }), 400
        
        result = auth_service.login(email, password)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Login failed: {str(e)}"
        }), 500


def logout():
    """
    POST /api/logout
    Headers: Authorization: Bearer <access_token>
    Request body: { "refresh_token": "..." }
    Returns: { "success": true, "message": "Logged out successfully" }
    """
    try:
        auth_header = request.headers.get("Authorization")
        data = request.get_json(silent=True) or {}
        refresh_token = data.get("refresh_token")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "error": "No access token provided"
            }), 401
        
        if not refresh_token:
            return jsonify({
                "success": False,
                "error": "Refresh token is required"
            }), 400
        
        access_token = auth_header.split(" ")[1]
        result = auth_service.logout(access_token, refresh_token)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Logout failed: {str(e)}"
        }), 500


def verify():
    """
    GET /api/verify
    Headers: Authorization: Bearer <access_token>
    Returns: { "success": true, "user": {...} }
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
        
        if user:
            return jsonify({
                "success": True,
                "user": user
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Invalid or expired token"
            }), 401
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Verification failed: {str(e)}"
        }), 500


def refresh():
    """
    POST /api/refresh
    Request body: { "refresh_token": "..." }
    Returns: { "success": true, "session": {...} }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        refresh_token = data.get("refresh_token")
        
        if not refresh_token:
            return jsonify({
                "success": False,
                "error": "Refresh token is required"
            }), 400
        
        result = auth_service.refresh_session(refresh_token)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Token refresh failed: {str(e)}"
        }), 500

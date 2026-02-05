from flask import g, request, jsonify

from middleware.auth import public_route
from services.auth_service import AuthService


auth_service = None


def get_auth_service():
    global auth_service
    if auth_service is None:
        auth_service = AuthService()
    return auth_service


@public_route
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
            return (
                jsonify({"success": False, "error": "Email and password are required"}),
                400,
            )

        result = get_auth_service().login(email, password)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 401

    except Exception as e:
        return jsonify({"success": False, "error": f"Login failed: {str(e)}"}), 500


def logout():
    """
    POST /api/logout
    Headers: Authorization: Bearer <access_token>
    Request body: { "refresh_token": "..." }
    Returns: { "success": true, "message": "Logged out successfully" }
    """
    try:
        data = request.get_json(silent=True) or {}
        refresh_token = data.get("refresh_token")

        if not refresh_token:
            return (
                jsonify({"success": False, "error": "Refresh token is required"}),
                400,
            )

        access_token = getattr(g, "access_token", None)
        if not access_token:
            return jsonify({"success": False, "error": "No access token provided"}), 401

        result = auth_service.logout(access_token, refresh_token)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({"success": False, "error": f"Logout failed: {str(e)}"}), 500


def verify():
    """
    GET /api/verify
    Headers: Authorization: Bearer <access_token>
    Returns: { "success": true, "user": {...} }
    """
    try:
        user = getattr(g, "current_user", None)
        if user:
            return jsonify({"success": True, "user": user}), 200

        return jsonify({"success": False, "error": "Invalid or expired token"}), 401

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Verification failed: {str(e)}"}),
            500,
        )


@public_route
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
            return (
                jsonify({"success": False, "error": "Refresh token is required"}),
                400,
            )

        result = get_auth_service().refresh_session(refresh_token)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 401

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Token refresh failed: {str(e)}"}),
            500,
        )


def get_users():
    """
    GET /api/users
    Admin only endpoint to get all registered users
    Returns: { "success": true, "users": [...] }
    """
    try:
        # Check if user is admin
        user = g.get("current_user")
        
        if not user:
            return jsonify({"success": False, "error": "No user in context"}), 401
        
        user_role = user.get("role", "").lower() if user.get("role") else ""
        
        if user_role != "admin":
            return jsonify({
                "success": False, 
                "error": "Unauthorized. Admin access required"
            }), 403

        result = get_auth_service().get_all_users()

        if result["success"]:
            return jsonify(result), 200
        else:
            print(f"ERROR in get_all_users: {result}")
            return jsonify(result), 500

    except Exception as e:
        print(f"EXCEPTION in get_users: {str(e)}")
        import traceback
        traceback.print_exc()
        return (
            jsonify({"success": False, "error": f"Failed to fetch users: {str(e)}"}),
            500,
        )


def create_user():
    """
    POST /api/users
    Admin only endpoint to create a new user
    Request body: { "email": "user@example.com", "password": "password123", "role": "user" }
    Returns: { "success": true, "user": {...} }
    """
    try:
        # Check if user is admin
        user = g.get("current_user")
        
        if not user:
            return jsonify({"success": False, "error": "No user in context"}), 401
        
        user_role = user.get("role", "").lower() if user.get("role") else ""
        
        if user_role != "admin":
            return jsonify({
                "success": False, 
                "error": "Unauthorized. Admin access required"
            }), 403

        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "user")

        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"}), 400

        # Validate role
        if role not in ["user", "admin"]:
            return jsonify({"success": False, "error": "Role must be 'user' or 'admin'"}), 400

        result = get_auth_service().create_user(email, password, role)

        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Failed to create user: {str(e)}"}),
            500,
        )


def delete_user(user_id):
    """
    DELETE /api/users/<user_id>
    Admin only endpoint to delete a user
    Returns: { "success": true, "message": "User deleted successfully" }
    """
    try:
        # Check if user is admin
        user = g.get("current_user")
        
        if not user:
            return jsonify({"success": False, "error": "No user in context"}), 401
        
        user_role = user.get("role", "").lower() if user.get("role") else ""
        
        if user_role != "admin":
            return jsonify({
                "success": False, 
                "error": "Unauthorized. Admin access required"
            }), 403

        if not user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400

        if user_id == user.get("id"):
            return (
                jsonify({"success": False, "error": "You cannot delete your own account"}),
                400,
            )

        result = get_auth_service().delete_user(user_id)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        print(f"EXCEPTION in delete_user: {str(e)}")
        import traceback
        traceback.print_exc()
        return (
            jsonify({"success": False, "error": f"Failed to delete user: {str(e)}"}),
            500,
        )

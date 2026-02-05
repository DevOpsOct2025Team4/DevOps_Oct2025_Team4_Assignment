from typing import Optional, Tuple

from flask import current_app, g, jsonify, request

from services.auth_service import AuthService


auth_service = AuthService()

PUBLIC_PATHS = {
    "/api/hello",
    "/api/health",
    "/api/login",
    "/api/refresh",
}


def public_route(fn):
    """
    Mark a view function as public (skips auth in middleware).
    """
    setattr(fn, "_is_public", True)
    return fn


def require_role(role: str):
    """
    Restrict a view function to a specific user role.
    """

    def decorator(fn):
        setattr(fn, "_required_role", role)
        return fn

    return decorator


def attach_user() -> Optional[Tuple[dict, int]]:
    """
    Attach the authenticated user to the request context (g.current_user).
    Returns a Flask response tuple when authentication fails.
    """
    if request.method == "OPTIONS":
        return None

    view_fn = (
        request.endpoint
        and current_app
        and current_app.view_functions.get(request.endpoint)
    )
    if view_fn and getattr(view_fn, "_is_public", False):
        return None

    if request.path in PUBLIC_PATHS:
        return None

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"success": False, "error": "No access token provided"}), 401

    access_token = auth_header.split(" ", 1)[1]
    user = auth_service.verify_token(access_token)

    if not user:
        return jsonify({"success": False, "error": "Invalid or expired token"}), 401

    g.current_user = user
    g.user_id = user.get("id")
    g.access_token = access_token

    required_role = view_fn and getattr(view_fn, "_required_role", None)
    if required_role and user.get("role") != required_role:
        return jsonify({"success": False, "error": "Forbidden"}), 403

    return None

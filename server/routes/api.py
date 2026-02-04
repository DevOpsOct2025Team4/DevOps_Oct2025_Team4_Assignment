from flask import Blueprint

from controllers.health_controller import health
from controllers.hello_controller import hello
from controllers.upload_controller import upload
from controllers.auth_controller import login, logout, verify, refresh, get_users, create_user, delete_user
from controllers.file_controller import get_user_files, download_file, delete_file
from middleware.auth import attach_user


api_bp = Blueprint("api", __name__)
api_bp.before_request(attach_user)

api_bp.get("/hello")(hello)
api_bp.get("/health")(health)
api_bp.post("/upload")(upload)

# Auth routes
api_bp.post("/login")(login)
api_bp.post("/logout")(logout)
api_bp.get("/verify")(verify)
api_bp.post("/refresh")(refresh)
api_bp.get("/users")(get_users)
api_bp.post("/users")(create_user)
api_bp.delete("/users/<user_id>")(delete_user)

# File routes
api_bp.get("/files")(get_user_files)
api_bp.get("/files/<file_id>/download")(download_file)
api_bp.delete("/files/<file_id>")(delete_file)

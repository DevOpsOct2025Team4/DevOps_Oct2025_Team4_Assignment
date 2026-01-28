from flask import Blueprint

from controllers.health_controller import health
from controllers.hello_controller import hello
from controllers.upload_controller import upload
from controllers.auth_controller import login, logout, verify, refresh


api_bp = Blueprint("api", __name__)

api_bp.get("/hello")(hello)
api_bp.get("/health")(health)
api_bp.post("/upload")(upload)

# Auth routes
api_bp.post("/login")(login)
api_bp.post("/logout")(logout)
api_bp.get("/verify")(verify)
api_bp.post("/refresh")(refresh)

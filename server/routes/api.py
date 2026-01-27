from flask import Blueprint

from controllers.health_controller import health
from controllers.hello_controller import hello
from controllers.upload_controller import upload


api_bp = Blueprint("api", __name__)

api_bp.get("/hello")(hello)
api_bp.get("/health")(health)
api_bp.post("/upload")(upload)

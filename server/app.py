import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from routes import api_bp


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)

    # Enable CORS for frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    max_upload_mb = os.getenv("MAX_UPLOAD_MB")
    if max_upload_mb:
        try:
            app.config["MAX_CONTENT_LENGTH"] = int(max_upload_mb) * 1024 * 1024
        except ValueError:
            app.logger.warning("Invalid MAX_UPLOAD_MB=%s", max_upload_mb)

    app.register_blueprint(api_bp, url_prefix="/api")

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)

import os

from flask import current_app, jsonify

from services.health_service import check_database
from middleware.auth import public_route


@public_route
def health():
    database = check_database(os.getenv("DATABASE_URL"), current_app.logger)
    sha = (
        os.getenv("GIT_SHA")
        or os.getenv("RENDER_GIT_COMMIT")
        or os.getenv("SOURCE_VERSION")
    )
    return jsonify(server=True, database=database, sha=sha)

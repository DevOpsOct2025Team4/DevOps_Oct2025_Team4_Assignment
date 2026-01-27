import os

from flask import current_app, jsonify

from services.health_service import check_database


def health():
    database = check_database(os.getenv("DATABASE_URL"), current_app.logger)
    return jsonify(server=True, database=database)

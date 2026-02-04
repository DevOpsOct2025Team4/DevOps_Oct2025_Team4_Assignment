from flask import jsonify

from middleware.auth import public_route


@public_route
def hello():
    return jsonify(message="Hello from Flask!")

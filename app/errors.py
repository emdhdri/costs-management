from app import app
from flask import jsonify


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(409)
def duplicate_resource(e):
    return jsonify(error=str(e)), 409


@app.errorhandler(400)
def invalid_format(e):
    return jsonify(error=str(e)), 400

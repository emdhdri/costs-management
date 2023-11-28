from app.api import api_bp
from app.db.models import User
from flask_httpauth import HTTPBasicAuth
from flask_httpauth import HTTPTokenAuth
from flask import jsonify


basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    user = User.objects(username=username).first()
    if user and user.check_password(password):
        return user


@basic_auth.error_handler
def basic_auth_error(status):
    return jsonify(status=status)


@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status):
    return jsonify(status=status)


@api_bp.route("/login", methods=["GET"])
@basic_auth.login_required
def login():
    token = basic_auth.current_user().get_token()
    data = {"token": token}
    return jsonify(data)


@api_bp.route("/logout", methods=["GET"])
@token_auth.login_required
def logout():
    user = token_auth.current_user()
    user.revoke_token()
    return jsonify(status=200)

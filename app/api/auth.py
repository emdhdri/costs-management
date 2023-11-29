from app.api import api_bp
from app.utils.auth import basic_auth, token_auth
from flask import jsonify


@api_bp.route("/login", methods=["GET"])
@basic_auth.login_required
def login():
    """
    @api {get} /api/login login
    @apiName login
    @apiGroup login/logout
    @apiHeader {String} authorization base64-encoded username:password string

    @apiSuccess {String} token Authorization token
    """
    token = basic_auth.current_user().get_token()
    data = {"token": token}
    return jsonify(data)


@api_bp.route("/logout", methods=["GET"])
@token_auth.login_required
def logout():
    """
    @api {get} /api/logout logout
    @apiName logout
    @apiGroup login/logout
    @apiHeader {String} authorization Authorization token

    @apiDescription
    logs out the user with given token and revokes the token.

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    """
    user = token_auth.current_user()
    user.revoke_token()
    return jsonify(status=200)

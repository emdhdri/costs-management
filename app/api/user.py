from app.api import api_bp
from app.db.models import User
from flask import jsonify, request
from mongoengine.queryset.visitor import Q
from jsonschema import validate
from app.utils.json_schemas import UserSchema
from jsonschema.exceptions import ValidationError
import uuid
from app.utils.auth import token_auth
from app.utils.errors import error_response


@api_bp.route("/user", methods=["GET"])
@token_auth.login_required
def get_user():
    """
    @api {get} /api/user Get User data
    @apiName GetUser
    @apiGroup User
    @apiHeader {String} authorization Authorization token.

    @apiExample {curl} Example usage:
        curl -i http://localhost:5000/user

    @apiSuccess {String}    first_name Firstname of the User.
    @apiSuccess {String}    last_name Lastname of the User.
    @apiSuccess {String}    username username of the User.
    @apiSuccess {String}    email email of the User.
    @apiSuccess {String}    birth_date birth date of User.
    @apiSuccess {String}    user_id id of User.

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "first_name" : "steve",
            "last_name" : "jobs",
            "username" : "sjobs",
            "email" : "sjobs@apple",
            "birth_date" : "1955-02-24T00:00:00",
            "user_id" : "e3d23c73-7593-4ca3-80cb-4d06e6029456"
        }
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    """
    user = token_auth.current_user().to_dict()
    return jsonify(user), 200


@api_bp.route("/register", methods=["POST"])
def create_user():
    """
    @api {post} /api/register Create new User
    @apiName CreateUser
    @apiGroup User

    @apiBody {string} first_name User firstname
    @apiBody {string} last_name User lastname
    @apiBody {string} username User username
    @apiBody {string} email User email
    @apiBody {string} birth_date User birthdate in ISOformat
    @apiBody {string} password User password

    @apiSuccess (Created 201) {String}    first_name Firstname of the User.
    @apiSuccess (Created 201) {String}    last_name Lastname of the User.
    @apiSuccess (Created 201) {String}    username username of the User.
    @apiSuccess (Created 201) {String}    email email of the User.
    @apiSuccess (Created 201) {String}    birth_date birth date of User.
    @apiSuccess (Created 201) {String}    user_id id of User.

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "first_name" : "steve",
            "last_name" : "jobs",
            "username" : "sjobs",
            "email" : "sjobs@apple",
            "birth_date" : "1955-02-24T00:00:00",
            "user_id" : "e3d23c73-7593-4ca3-80cb-4d06e6029456"
        }

    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    @apiError (Conflict 409) Conflict Existing data with same field.
    """
    data = request.get_json() or {}
    try:
        validate(instance=data, schema=UserSchema.get_schema())
    except ValidationError:
        return error_response(400, message="Invalid data")

    check_user_query = Q(email=data["email"]) | Q(username=data["username"])
    if User.objects(check_user_query).first() is not None:
        return error_response(409, message="Duplicate resource")

    data["user_id"] = str(uuid.uuid4())
    user = User()
    user.from_dict(data)
    user.save()
    user_data = user.to_dict()
    return jsonify(user_data), 201

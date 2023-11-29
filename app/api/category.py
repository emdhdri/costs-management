from app.api import api_bp
from app.db.models import Expense, Category
from flask import jsonify, request
import mongoengine as me
from jsonschema import validate
from app.utils.json_schemas import CategorySchema
from jsonschema.exceptions import ValidationError
import uuid
from app.api.auth import token_auth
from app.utils.errors import error_response


@api_bp.route("/user/categories", methods=["GET"])
@token_auth.login_required
def get_user_categories():
    """
    @api {get} /api/user/categories Get User categories
    @apiName GetUserCategories
    @apiGroup Category
    @apiHeader {String} authorization Authorization token.
    @apiDescription
    Returns list of all categories created by user.

    @apiSuccess {object[]} expenses list of all user Categories

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.

    """
    user = token_auth.current_user()
    categories = [
        category.to_dict() for category in Category.objects(user=user).exclude("user")
    ]
    data = {"categories": categories}
    return jsonify(data), 200


@api_bp.route("/user/categories", methods=["POST"])
@token_auth.login_required
def create_category():
    """
    @api {post} /api/user/categories Create new Category
    @apiName CreateCategory
    @apiGroup Category
    @apiHeader {String} authorization Authorization token.
    @apiDescription
    Creates new category with provided data by user.

    @apiBody {String} name Category name

    @apiSuccess (Created 201) {string} name Category name
    @apiSuccess (Created 201) {string} category_id Category id

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Bad Request 400) BadRequest Invalid data sent by user.

    """
    user = token_auth.current_user()
    data = request.get_json() or {}
    try:
        validate(instance=data, schema=CategorySchema.get_schema())
    except ValidationError:
        return error_response(400, message="Invalid data")

    data["user"] = user
    data["category_id"] = str(uuid.uuid4())
    category = Category()
    category.from_dict(data)
    category.save()
    category_data = category.to_dict()
    return jsonify(category_data), 201


@api_bp.route("/user/categories/<string:category_id>", methods=["PUT"])
@token_auth.login_required
def edit_category(category_id):
    """
    @api {put} /api/user/categories/:category_id Modify Category
    @apiName ModifyCategory
    @apiGroup Category
    @apiHeader {String} authorization Authorization token.
    @apiDescription
    Modifies the category with given id.

    @apiBody {String} name Category name

    @apiSuccess {string} name Category name
    @apiSuccess {string} category_id Category id

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    @apiError (Not found 404) NotFound Category with given id not found.

    """
    try:
        user = token_auth.current_user()
        category = Category.objects.get(user=user, category_id=category_id)
    except me.DoesNotExist:
        return error_response(404, message="Resource not found")

    data = request.get_json() or {}
    try:
        validate(instance=data, schema=CategorySchema.get_schema())
    except ValidationError:
        return error_response(400, message="Invalid data")

    category.from_dict(data)
    category.save()
    data = category.to_dict()
    return jsonify(data), 200


@api_bp.route("/user/categories/<string:category_id>", methods=["DELETE"])
@token_auth.login_required
def delete_category(category_id):
    """
    @api {delete} /api/user/categories/:category_id Delete Category
    @apiName DeleteCategory
    @apiGroup Category
    @apiHeader {String} authorization Authorization token.
    @apiDescription
    Deletes the category with given id.

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound Category with given id not found.

    """
    try:
        user = token_auth.current_user()
        category = Category.objects.get(user=user, category_id=category_id)
    except me.DoesNotExist:
        return error_response(404, message="Resource not found")

    Expense.objects(category=category).update(set__category=None)
    category.delete()
    return jsonify(status=200)

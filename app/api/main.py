from app.api import api_bp
from app.db.models import User, Expense, Category
from flask import jsonify, request, abort
import mongoengine as me
from mongoengine.queryset.visitor import Q
from datetime import datetime
from jsonschema import validate
from app.db.json_schemas import (
    UserSchema,
    ExpenseSchema,
    CategorySchema,
    editExpenseSchema,
)
from jsonschema.exceptions import ValidationError
import uuid
from app.api.auth import basic_auth, token_auth


@api_bp.route("/user", methods=["GET"])
@token_auth.login_required
def get_user():
    """
    @api {get} /api/user
    @apiName GetUser
    @apiGroup User 

    @apiSuccess {String} first_name Firstname of the User.
    @apiSuccess {String} last_name Lastname of the User.
    @apiSuccess {String} username username of the User.
    @apiSuccess {String} email email of the User.
    @apiSuccess {String} birth_date birth date of User.
    @apiSuccess {String} user_id id of User.

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "first_name" : "steve",
            "last_name" : "jobs",
            "username" : "sjobs",
            "email" : "sjobs@apple,
            "birth_date" : "1955-02-24T00:00:00",
            "user_id" : "e3d23c73-7593-4ca3-80cb-4d06e6029456"
        }
    """
    user = token_auth.current_user().to_dict()
    return jsonify(user), 200


@api_bp.route("/register", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    try:
        validate(instance=data, schema=UserSchema.get_schema())
    except ValidationError:
        abort(400, description="Invalid data")

    check_user_query = Q(email=data["email"]) | Q(username=data["username"])
    if User.objects(check_user_query).first() is not None:
        abort(409, description="Duplicate resource")

    data["user_id"] = str(uuid.uuid4())
    user = User()
    user.from_dict(data)
    user.save()
    user_data = user.to_dict()
    return jsonify(user_data), 201


@api_bp.route("/user/expenses", methods=["GET"])
@token_auth.login_required
def get_user_expenses():
    """
    @api {get} /api/user/expenses
    @apiName GetUserExpenses
    @apiGroup User
    @apiQuery {Number} costgt Expense cost upper bound.
    @apiQuery {Number} costlt Expense cost lower bound.
    @apiQuery {String} category Expense category.
    @apiQuery {String} after Expense date after.
    @apiQuery {String} before Expense date before.


    @apiSuccess {object[]} expenses A list of Users Expenses.

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "expenses": [
                {
                    "category": "transportation",
                    "cost": 23,
                    "date": null,
                    "description": null,
                    "expense_id": "d1d97f7e-ecb2-4682-9128-2a726e4234ef"
                }
            ]
        }
    """
    user = token_auth.current_user()
    parameters = request.args
    query = Q(user=user)
    if "costgt" in parameters:
        cost_gt = parameters.get("costgt", type=int)
        query &= Q(cost__gt=cost_gt)
    if "costlt" in parameters:
        cost_lt = parameters.get("costlt", type=int)
        query &= Q(cost__lt=cost_lt)
    if "before" in parameters:
        before_date = datetime.fromisoformat(parameters.get("before", type=str))
        query &= Q(date__lt=before_date)
    if "after" in parameters:
        after_date = datetime.fromisoformat(parameters.get("after", type=str))
        query &= Q(date__gt=after_date)
    if "category" in parameters:
        category = Category.objects(name=parameters["category"]).first()
        if category is None:
            data = {"expenses": []}
            return jsonify(data)

        query &= Q(category=category)

    user_expenses = [
        expense.to_dict() for expense in Expense.objects(query).exclude("user")
    ]
    data = {"expenses": user_expenses}
    return jsonify(data), 200


@api_bp.route("/user/expenses/<string:expense_id>", methods=["GET"])
@token_auth.login_required
def get_specific_expense(expense_id):
    try:
        user = token_auth.current_user()
        expense = Expense.objects.get(user=user, expense_id=expense_id).to_dict()
    except me.DoesNotExist:
        abort(404, description="Resource not found")

    return jsonify(expense), 200


@api_bp.route("/user/expenses", methods=["POST"])
@token_auth.login_required
def create_expense():
    user = token_auth.current_user()
    data = request.get_json() or {}
    try:
        validate(instance=data, schema=ExpenseSchema.get_schema())
    except ValidationError:
        abort(400, description="Invalid data")

    data["user"] = user
    data["expense_id"] = str(uuid.uuid4())
    expense = Expense()

    if "category" in data:
        category_object = Category.objects(user=user, name=data["category"]).first()
        if category_object is None:
            category_object = Category()
            category_object.name = data["category"]
            category_object.user = user
            category_object.category_id = str(uuid.uuid4())
            category_object.save()
        data["category"] = category_object

    expense.from_dict(data)
    expense.save()
    expense_data = expense.to_dict()
    return jsonify(expense_data), 201


@api_bp.route("/user/expenses/<string:expense_id>", methods=["PUT"])
@token_auth.login_required
def edit_expense(expense_id):
    try:
        user = token_auth.current_user()
        expense = Expense.objects.get(user=user, expense_id=expense_id)
    except me.DoesNotExist:
        abort(404, description="Resource not found")

    data = request.get_json() or {}
    try:
        validate(instance=data, schema=editExpenseSchema.get_schema())
    except ValidationError:
        abort(400, description="Invalid data")

    if "category" in data:
        category_object = Category.objects(user=user, name=data["category"]).first()
        if category_object is None:
            category_object = Category()
            category_object.name = data["category"]
            category_object.user = user
            category_object.category_id = str(uuid.uuid4())
            category_object.save()
        data["category"] = category_object

    print(data)
    expense.from_dict(data)
    expense.save()
    return jsonify(status=200)


@api_bp.route("/user/expenses/<string:expense_id>", methods=["DELETE"])
@token_auth.login_required
def delete_expense(expense_id):
    try:
        user = token_auth.current_user()
        expense = Expense.objects.get(user=user, expense_id=expense_id)
    except me.DoesNotExist:
        abort(404, description="Resource not found")

    expense.delete()
    return jsonify(status=200)


@api_bp.route("/user/categories", methods=["GET"])
@token_auth.login_required
def get_user_categories():
    user = token_auth.current_user()
    categories = [
        category.to_dict() for category in Category.objects(user=user).exclude("user")
    ]
    data = {"categories": categories}
    return jsonify(data), 200


@api_bp.route("/user/categories", methods=["POST"])
@token_auth.login_required
def create_category():
    user = token_auth.current_user()
    data = request.get_json() or {}
    try:
        validate(instance=data, schema=CategorySchema.get_schema())
    except ValidationError:
        abort(400, description="Invalid data")

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
    try:
        user = token_auth.current_user()
        category = Category.objects.get(user=user, category_id=category_id)
    except me.DoesNotExist:
        abort(404, description="Resource not found")

    data = request.get_json() or {}
    try:
        validate(instance=data, schema=CategorySchema.get_schema())
    except ValidationError:
        abort(400, description="Invalid data")

    category.from_dict(data)
    category.save()
    return jsonify(status=200)


@api_bp.route(
    "/user/<string:username>/categories/<string:category_id>", methods=["DELETE"]
)
@token_auth.login_required
def delete_category(category_id):
    try:
        user = token_auth.current_user()
        category = Category.objects.get(user=user, category_id=category_id)
    except me.DoesNotExist:
        abort(404, description="Resource not found")

    Expense.objects(category=category).update(set__category=None)
    category.delete()
    return jsonify(status=200)

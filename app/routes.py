from app import app
from app.models import User, Expense, Category
from flask import jsonify, request, abort
import mongoengine as me
from mongoengine.queryset.visitor import Q
from datetime import datetime
from jsonschema import validate
from app.json_schemas import (
    UserSchema,
    ExpenseSchema,
    CategorySchema,
    editExpenseSchema,
)
from jsonschema.exceptions import ValidationError
import uuid


@app.route("/")
def index():
    pass


@app.route("/users", methods=["GET"])
def get_users():
    users = [user.to_dict() for user in User.objects()]
    data = {"users": users}
    return jsonify(data), 200


@app.route("/users/<string:username>", methods=["GET"])
def get_user(username):
    try:
        user = User.objects.get(username=username).to_dict()
    except me.DoesNotExist:
        abort(404, description="Resource not found")

    return jsonify(user), 200


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    try:
        validate(instance=data, schema=UserSchema.get_schema())
    except ValidationError:
        abort(400, description="Invalid data")

    data["user_id"] = uuid.uuid4().hex
    user = User()
    user.from_dict(data)
    try:
        user.save()
    except me.errors.NotUniqueError:
        abort(409, description="Duplicate resource")
    user_data = user.to_dict()
    return jsonify(user_data), 201


@app.route("/users/<string:username>/expenses", methods=["GET"])
def get_user_expenses(username):
    try:
        user = User.objects.get(username=username)
    except me.DoesNotExist:
        abort(404, description="Resource not found")

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


@app.route("/users/<string:username>/expenses/<string:expense_id>", methods=["GET"])
def get_specific_expense(username, expense_id):
    try:
        user = User.objects.get(username=username)
        expense = Expense.objects.get(user=user, expense_id=expense_id).to_dict()
    except me.DoesNotExist:
        abort(404, description="Resource not found")

    return jsonify(expense), 200


@app.route("/users/<string:username>/expenses", methods=["POST"])
def create_expense(username):
    try:
        user = User.objects.get(username=username)
    except me.DoesNotExist:
        abort(404, description="User resource not found")

    data = request.get_json() or {}
    try:
        validate(instance=data, schema=ExpenseSchema.get_schema())
    except ValidationError:
        abort(400, description="Invalid data")

    data["user"] = user
    data["expense_id"] = uuid.uuid4().hex
    expense = Expense()

    if "category" in data:
        category_object = Category.objects(user=user, name=data["category"]).first()
        if category_object is None:
            category_object = Category()
            category_object.name = data["category"]
            category_object.user = user
            category_object.category_id = uuid.uuid4().hex
            category_object.save()
        data["category"] = category_object

    expense.from_dict(data)
    expense.save()
    expense_data = expense.to_dict()
    return jsonify(expense_data), 201


@app.route("/users/<string:username>/expenses/<string:expense_id>", methods=["PUT"])
def edit_expense(username, expense_id):
    try:
        user = User.objects.get(username=username)
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
            category_object.category_id = uuid.uuid4().hex
            category_object.save()
        data["category"] = category_object

    print(data)
    expense.from_dict(data)
    expense.save()
    return jsonify(status=200)


@app.route("/users/<string:username>/expenses/<string:expense_id>", methods=["DELETE"])
def delete_expense(username, expense_id):
    try:
        user = User.objects.get(username=username)
        expense = Expense.objects.get(user=user, expense_id=expense_id)
    except me.DoesNotExist:
        abort(404, description="Resource not found")

    expense.delete()
    return jsonify(status=200)


@app.route("/users/<string:username>/categories", methods=["GET"])
def get_user_categories(username):
    try:
        user = User.objects.get(username=username)
    except me.DoesNotExist:
        abort(404, description="Resource not found")

    categories = [
        category.to_dict() for category in Category.objects(user=user).exclude("user")
    ]
    data = {"categories": categories}
    return jsonify(data), 200


@app.route("/users/<string:username>/categories", methods=["POST"])
def create_category(username):
    try:
        user = User.objects.get(username=username)
    except me.DoesNotExist:
        abort(404, description="Resource not found")

    data = request.get_json() or {}
    try:
        validate(instance=data, schema=CategorySchema.get_schema())
    except ValidationError:
        abort(400, description="Invalid data")

    data["user"] = user
    data["category_id"] = uuid.uuid4().hex
    category = Category()
    category.from_dict(data)
    category.save()
    category_data = category.to_dict()
    return jsonify(category_data), 201


@app.route("/users/<string:username>/categories/<string:category_id>", methods=["PUT"])
def edit_category(username, category_id):
    try:
        user = User.objects.get(username=username)
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


@app.route(
    "/users/<string:username>/categories/<string:category_id>", methods=["DELETE"]
)
def delete_category(username, category_id):
    try:
        user = User.objects.get(username=username)
        category = Category.objects.get(user=user, category_id=category_id)
    except me.DoesNotExist:
        abort(404, description="Resource not found")

    Expense.objects(category=category).update(set__category=None)
    category.delete()
    return jsonify(status=200)

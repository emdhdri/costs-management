from app.api import api_bp
from app.db.models import Expense, Category
from flask import jsonify, request
import mongoengine as me
from mongoengine.queryset.visitor import Q
from datetime import datetime
from jsonschema import validate
from app.utils.json_schemas import (
    ExpenseSchema,
    editExpenseSchema,
)
from jsonschema.exceptions import ValidationError
import uuid
from app.api.auth import token_auth
from app.utils.errors import error_response


@api_bp.route("/user/expenses", methods=["GET"])
@token_auth.login_required
def get_user_expenses():
    """
    @api {get} /api/user/expenses Get User expenses
    @apiName GetUserExpenses
    @apiGroup Expense
    @apiHeader {String} authorization Authorization token.
    @apiDescription
    Returns a list of user's expenses and if query parameters for filtering are provided
    then filters will be applied.


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
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.

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
    """
    @api {get} /api/user/expenses/:expense_id Get User specific expense
    @apiName GetUserSpecificExpense
    @apiGroup Expense
    @apiHeader {String} authorization Authorization token.
    @apiDescription
    Returns a specific user expense by its id.


    @apiSuccess {object} expense Expense data.

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "category": "transportation",
            "cost": 23,
            "date": null,
            "description": null,
            "expense_id": "d1d97f7e-ecb2-4682-9128-2a726e4234ef"
        }
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound Expense resource with given id not found.

    """
    try:
        user = token_auth.current_user()
        expense = Expense.objects.get(user=user, expense_id=expense_id).to_dict()
    except me.DoesNotExist:
        return error_response(404, message="Resource not found")

    return jsonify(expense), 200


@api_bp.route("/user/expenses", methods=["POST"])
@token_auth.login_required
def create_expense():
    """
    @api {post} /api/user/expense Create new Expense
    @apiName CreateExpense
    @apiGroup Expense
    @apiHeader {String} authorization Authorization token.

    @apiBody {Number} cost Expense cost
    @apiBody {string} date date of Expense in ISOformat
    @apiBody {string} description expense description
    @apiBody {string} category Expense category

    @apiSuccess (Created 201) {Number} cost Expense cost
    @apiSuccess (Created 201) {String} date date of Expense in ISOformat
    @apiSuccess (Created 201) {String} description expense description
    @apiSuccess (Created 201) {String} category Expense category
    @apiSuccess (Created 201) {String} Expense_id Expense id

    @apiSuccessExample success-response:
        HTTP/1.1 201 OK
        {
            "category": "transportation",
            "cost": 23,
            "date": "2023-11-19T15:43:00",
            "description": null,
            "expense_id": "d1d97f7e-ecb2-4682-9128-2a726e4234ef"
        }
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    """
    user = token_auth.current_user()
    data = request.get_json() or {}
    try:
        validate(instance=data, schema=ExpenseSchema.get_schema())
    except ValidationError:
        return error_response(400, message="Invalid data")

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
    """
    @api {put} /user/expenses/:expense_id Modify user Expense
    @apiName ModifyExpense
    @apiGroup Expense
    @apiHeader {String} authorization Authorization token.

    @apiBody {Number} cost Expense cost
    @apiBody {string} date date of Expense in ISOformat
    @apiBody {string} description expense description
    @apiBody {string} category Expense category

    @apiSuccess {Number} cost Expense cost
    @apiSuccess {String} date date of Expense in ISOformat
    @apiSuccess {String} description expense description
    @apiSuccess {String} category Expense category
    @apiSuccess {String} Expense_id Expense id


    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    @apiError (Not found 404) NotFound Expense with given id not found.
    """
    try:
        user = token_auth.current_user()
        expense = Expense.objects.get(user=user, expense_id=expense_id)
    except me.DoesNotExist:
        return error_response(404, message="Resource not found")

    data = request.get_json() or {}
    try:
        validate(instance=data, schema=editExpenseSchema.get_schema())
    except ValidationError:
        return error_response(400, message="Invalid data")

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
    data = expense.to_dict()
    return jsonify(data), 200


@api_bp.route("/user/expenses/<string:expense_id>", methods=["DELETE"])
@token_auth.login_required
def delete_expense(expense_id):
    """
    @api {delete} /user/expenses/:expense_id Delete expense
    @apiName DeleteExpense
    @apiGroup Expense
    @apiHeader {String} authorization Authorization token.

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound Expense with given id not found.
    """
    try:
        user = token_auth.current_user()
        expense = Expense.objects.get(user=user, expense_id=expense_id)
    except me.DoesNotExist:
        return error_response(404, message="Resource not found")

    expense.delete()
    return jsonify(status=200)

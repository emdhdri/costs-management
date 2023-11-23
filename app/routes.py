from app import app
from app.models import User, Expense, Category
from flask import jsonify, request, abort, Response
import mongoengine as me
from mongoengine.queryset.visitor import Q
from datetime import datetime
from functools import reduce
import operator
from jsonschema import validate
from app.json_schemas import UserSchema, ExpenseSchema, CategorySchema, editExpenseSchema
from jsonschema.exceptions import ValidationError


@app.route('/')
def index():
    pass


@app.route('/users', methods=['GET'])
def get_users():
    data = [user.to_dict() for user in User.objects()]
    return jsonify(data)


@app.route('/users/<string:username>', methods=['GET'])
def get_user(username):
    try:
        user = User.objects.get(username=username).to_dict()
    except User.DoesNotExist:
        abort(404, description="Resource not found")
    
    return jsonify(user)


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    try:
        validate(instance=data, schema=UserSchema.get_schema())
    except ValidationError:
        abort(403, description='Invalid data')

    user = User()
    user.from_dict(data)
    try:
        user.save()
    except me.errors.NotUniqueError:
        abort(409, description='Duplicate resource')

    return jsonify(status=200)


@app.route('/users/<string:username>/expenses', methods=['GET'])
def get_user_expenses(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        abort(404, description='Resource not found')

    parameters = request.args
    query = (Q(user_ref=user))
    if('costgt' in parameters):
        cost_gt = parameters.get('costgt', type=float)
        query &= Q(cost__gt=cost_gt)
    if('costlt' in parameters):
        cost_lt = parameters.get('costlt', type=float)
        query &= Q(cost__lt=cost_lt)
    if('before' in parameters):
        before_date = datetime.fromisoformat(parameters.get('before', type=str))
        query &= Q(date__lt=before_date)
    if('after' in parameters):
        after_date = datetime.fromisoformat(parameters.get('after', type=str))
        query &= Q(date__gt=after_date)
    if('category' in parameters):
        category = Category.objects(category=parameters['category']).first()
        if(category == None):
            data = {
                "expenses" : []
                }
            return jsonify(data)
        
        query &= Q(category_ref=category)
        
    user_expenses = [expense.to_dict() for expense in Expense.objects(query).exclude('user_ref')]
    data = {
        "expenses" : user_expenses
        }
    return jsonify(data)


@app.route('/users/<string:username>/expenses/<string:expense_id>', methods=['GET'])
def get_specific_expense(username, expense_id):
    try:
        user = User.objects.get(username=username)
        expense = Expense.objects.get(user_ref=user, id=expense_id).to_dict()
    except Expense.DoesNotExist:
        abort(404, description='Resource not found')
    except User.DoesNotExist:
        abort(404, description='Resource not found')

    return jsonify(expense)


@app.route('/users/<string:username>/expenses', methods=['POST'])
def create_expense(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        abort(404, description="User resource not found")
    
    data = request.get_json() or {}
    try:
        validate(instance=data, schema=ExpenseSchema.get_schema())
    except ValidationError:
        abort(403, description='Invalid data')

    data['user_ref'] = user
    expense = Expense()
    
    if('category' in data):
        category_object = Category.objects(user_ref=user, category=data['category']).first()
        if(category_object == None):
            category_object = Category()
            category_object.category = data['category']
            category_object.user_ref = user
            category_object.save()
        data['category_ref'] = category_object

    expense.from_dict(data)
    expense.save()
    return jsonify(status=200)


@app.route('/users/<string:username>/expenses/<string:expense_id>', methods=['PUT'])
def edit_expense(username, expense_id):
    try:
        user = User.objects.get(username=username)
        expense = Expense.objects.get(user_ref=user, id=expense_id)
    except Expense.DoesNotExist:
        abort(404, description='Resource not found')
    except User.DoesNotExist:
        abort(404, description='Resource not found')
    
    data = request.get_json() or {}
    try:
        validate(instance=data, schema=editExpenseSchema.get_schema())
    except ValidationError:
        abort(403, description='Invalid data')

    if('category' in data):
        category_object = Category.objects(category=data['category']).first()
        if(category_object == None):
            category_object = Category()
            category_object.category = data['category']
            category_object.user_ref = user.id
            category_object.save()
        data['category_ref'] = category_object

    print(data)
    expense.from_dict(data)
    expense.save()
    return jsonify(status=200)


@app.route('/users/<string:username>/expenses/<string:expense_id>', methods=['DELETE'])
def delete_expense(username, expense_id):
    try:
        user = User.objects.get(username=username)
        expense = Expense.objects.get(user_ref=user, id=expense_id)
    except Expense.DoesNotExist:
        abort(404, description='Resource not found')
    except User.DoesNotExist:
        abort(404, description='Resource not found')

    expense.delete()
    return jsonify(status=200)


@app.route('/users/<string:username>/categories', methods=['GET'])
def get_user_categories(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        abort(404, description="Resource not found")

    categories = [category.to_dict() for category in Category.objects(user_ref=user).exclude('user_ref')]
    data = {
        'categories' : categories
    }
    return jsonify(data)


@app.route('/users/<string:username>/categories', methods=['POST'])
def create_category(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        abort(404, description="Resource not found")
    
    data = request.get_json() or {}
    try:
        validate(instance=data, schema=CategorySchema.get_schema())
    except ValidationError:
        abort(403, description='Invalid data')

    data['user_ref'] = user
    category = Category()
    category.from_dict(data)
    category.save()
    return jsonify(status=200)


@app.route('/users/<string:username>/categories/<string:category_id>', methods=['PUT'])
def edit_category(username, category_id):
    try:
        user = User.objects.get(username=username)
        category = Category.objects.get(user_ref = user, id=category_id)
    except Category.DoesNotExist:
        abort(404, description="Resource not found")
    except User.DoesNotExist:
        abort(404, description="Resource not found")
    data = request.get_json() or {}
    try:
        validate(instance=data, schema=CategorySchema.get_schema())
    except ValidationError:
        abort(403, description='Invalid data')

    category.from_dict(data)
    category.save()
    return jsonify(status=200)


@app.route('/users/<string:username>/categories/<string:category_id>', methods=['DELETE'])
def delete_category(username, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        abort(404, description='Resource not found')
    Expense.objects(category_ref=category).update(set__category_ref=None)

    category.delete()
    return jsonify(status=200)

    
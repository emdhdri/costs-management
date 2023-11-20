from app import app
from app.models import User, Expense
from flask import jsonify, request, abort, Response
import mongoengine as me
from mongoengine.queryset.visitor import Q
from datetime import datetime


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


@app.route('/users/<string:username>/expenses', methods=['GET'])
def get_expenses(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        abort(404, description='Resource not found')
    
    parameters = request.args
    query = (Q(user_ref=user))
    if('costgt' in parameters):
        cost_gt = parameters.get('costgt', type=int)
        query &= Q(cost__gt=cost_gt)
    if('costlt' in parameters):
        cost_lt = parameters.get('costlt', type=int)
        query &= Q(cost__lt=cost_lt)
    if('before' in parameters):
        before_date = datetime.fromisoformat(parameters.get('before', type=str))
        query &= Q(date__lt=before_date)
    if('after' in parameters):
        after_date = datetime.fromisoformat(parameters.get('after', type=str))
        query &= Q(date__gt=after_date)

    user_expenses = [expense.to_dict() for expense in Expense.objects(query).exclude('user_ref')]
    return jsonify(user_expenses)


@app.route('/users/<string:username>/expenses/<string:expense_id>', methods=['GET'])
def get_expense(username, expense_id):
    try:
        user = User.objects.get(username=username)
        expense = Expense.objects.get(user_ref= user, id=expense_id).to_dict()
    except User.DoesNotExist:
        abort(404, description='Resource not found')
    except Expense.DoesNotExist:
        abort(404, description='Resource not found')
    except me.ValidationError:
        abort(403, description='Invalid data')

    return jsonify(expense)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    user = User()
    user.from_dict(data)
    try:
        user.save()
    except me.errors.NotUniqueError:
        abort(409, description='Duplicate resource')
    except me.ValidationError:
        abort(403, description='Invalid data')
    return jsonify(status=200)


@app.route('/users/<string:username>/expenses', methods=['POST'])
def create_expense(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        abort(404, description="Resource not found")
    
    data = request.get_json() or {}
    data['user_ref'] = user
    expense = Expense()
    expense.from_dict(data)
    try:
        expense.save()
    except me.ValidationError:
        abort(403, description='Invalid data')

    return jsonify(status=200)

@app.route('/users/<string:username>/expenses/<string:expense_id>', methods=['PUT'])
def edit_expense(username, expense_id):
    try:
        expense = Expense.objects.get(id=expense_id)
    except Expense.DoesNotExist:
        abort(404, description='Resource not found')
    data = request.get_json() or {}
    expense.from_dict(data)
    print(expense.cost)
    try:
        expense.save()
    except me.ValidationError:
        abort(403, description='Invalid data')

    return jsonify(status=200)

@app.route('/users/<string:username>/expenses/<string:expense_id>', methods=['DELETE'])
def delete_expense(username, expense_id):
    try:
        expense = Expense.objects.get(id=expense_id)
    except Expense.DoesNotExist:
        abort(404, description='Resource not found')
    expense.delete()

    return jsonify(status=200)

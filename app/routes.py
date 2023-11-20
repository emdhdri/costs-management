from app import app
from app.models import User, Expense
from flask import jsonify, request, abort, Response
import mongoengine as me

@app.route('/')
def index():
    pass

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(status = 404, error=str(e))

@app.errorhandler(409)
def duplicate_resource(e):
    return jsonify(status = 409, error=str(e))


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
    
    user_expenses = [expense.to_dict() for expense in Expense.objects(user_ref=user).exclude('user_ref')]
    return jsonify(user_expenses)


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    user = User()
    user.from_dict(data)
    try:
        user.save()
    except me.errors.NotUniqueError:
        abort(409, description='duplicate resource')
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
    expense.save()
    return jsonify(status=200)

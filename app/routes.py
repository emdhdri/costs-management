from app import app
from app.models import User, Expense
from flask import jsonify, request
import mongoengine as me

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
        user = User.objects.get(usernmae=username)
    except User.DoesNotExist:
        return "Not found 404"
    
    return jsonify(user)

@app.route('/users/<string:username>/expenses', methods=['GET'])
def get_expenses(username):
    try:
        user = User.objects.get(usernmae=username)
    except User.DoesNotExist:
        return "Not found 404"
    
    user_expenses = [expense.to_dict() for expense in Expense.objects(user_ref=user)]
    return jsonify(user_expenses)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    user = User()
    user.from_dict(data)
    user.save()

@app.route('/users/<string:username>/expenses', methods=['POST'])
def create_expense(username):
    try:
        user = User.objects.get(usernmae=username)
    except User.DoesNotExist:
        return "Not found 404"
    
    data = request.get_json() or {}
    data['user_ref'] = user
    expense = Expense()
    expense.from_dict(data)
    expense.save()
    return "OK"

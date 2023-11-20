import mongoengine as me
from datetime import datetime

class User(me.Document):
    first_name = me.StringField()
    last_name = me.StringField()
    username = me.StringField(required=True)
    #password will be added and it is omitted now
    birth_date = me.DateField()

class Expense(me.Document):
    cost = me.DecimalField(required=True)
    date = me.DateTimeField()
    user_ref = me.ReferenceField(User, required=True)
    

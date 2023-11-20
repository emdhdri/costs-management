import mongoengine as me
from datetime import datetime

me.connect('t')
class User(me.Document):
    first_name = me.StringField()
    last_name = me.StringField()
    username = me.StringField(required=True)
    #password will be added and it is omitted now
    birth_date = me.DateField()

    def to_dict(self):
        user_birth_date = self.birth_date.to_python().isoformat() if self.birth_date else None
        data = {
            'first_name' : self.first_name.to_python(),
            'last_name' : self.last_name.to_python(),
            'username' : self.username.to_python(),
            'birth_date' : user_birth_date,
        }
        return data
    
    def from_dict(self, data):
        if('username' not in data):
            return
        if('birth_date' in data):
            user_birth_date = datetime.fromisoformat(data['birth_date'])
            setattr(self, 'birth_date', user_birth_date)
        
        for field in ['firs_name', 'last_name', 'username']:
            if(field in data):
                setattr(self, field, data[field])


class Expense(me.Document):
    cost = me.DecimalField(required=True)
    date = me.DateTimeField()
    user_ref = me.ReferenceField(User, required=True)
    
    def to_dict(self):
        expense_date = self.date.to_python().isoformat() if self.date else None
        data = {
            'cost' : self.cost.to_python(),
            'date' : expense_date,
            'user' : self.user_ref.to_dict(),
        }
        return data
    
    def from_dict(self, data):
        if('cost' not in data):
            return
        if('user_ref' not in data):
            return
        for field in ['cost', 'user_ref', 'date']:
            if(field in data):
                setattr(self, field, data[field])
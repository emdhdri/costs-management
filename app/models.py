import mongoengine as me
from datetime import datetime

me.connect("costs_db")


class User(me.Document):
    first_name = me.StringField()
    last_name = me.StringField()
    username = me.StringField(required=True, unique=True)
    email = me.EmailField(unique=True)
    # password will be added and it is omitted now
    birth_date = me.DateField()
    user_id = me.StringField(unique=True, required=True)

    def to_dict(self):
        user_birth_date = (
            self.birth_date.isoformat() if (self.birth_date is not None) else None
        )
        data = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "email": self.email,
            "birth_date": user_birth_date,
            "user_id": self.user_id,
        }
        return data

    def from_dict(self, data):
        if "birth_date" in data:
            user_birth_date = datetime.fromisoformat(data["birth_date"])
            setattr(self, "birth_date", user_birth_date)

        for field in ["first_name", "last_name", "username", "email", "user_id"]:
            if field in data:
                setattr(self, field, data[field])


class Category(me.Document):
    name = me.StringField(required=True)
    user = me.ReferenceField(User, required=True, reverse_delete_rule=me.CASCADE)
    category_id = me.StringField(unique=True, required=True)

    def to_dict(self, include_user=False):
        data = {"name": self.name, "category_id": self.category_id}
        if include_user and self.user:
            data["user"] = self.user.to_dict()
        return data

    def from_dict(self, data):
        for field in ["name", "user", "category_id"]:
            if field in data:
                setattr(self, field, data[field])


class Expense(me.Document):
    cost = me.IntField(required=True)
    date = me.DateTimeField()
    user = me.ReferenceField(User, required=True, reverse_delete_rule=me.CASCADE)
    description = me.StringField()
    category = me.ReferenceField(Category)
    expense_id = me.StringField(unique=True, required=True)

    def to_dict(self, include_user=True):
        expense_date = self.date.isoformat() if (self.date is not None) else None
        category = self.category.category if (self.category is not None) else None
        data = {
            "expense_id": self.expense_id,
            "cost": self.cost,
            "date": expense_date,
            "description": self.description,
            "category": category,
        }
        if include_user and self.user:
            data["user"] = self.user.to_dict()
        return data

    def from_dict(self, data):
        if "date" in data:
            expense_date = datetime.fromisoformat(data["date"])
            setattr(self, "date", expense_date)
        for field in ["cost", "user", "description", "category", "expense_id"]:
            if field in data:
                setattr(self, field, data[field])

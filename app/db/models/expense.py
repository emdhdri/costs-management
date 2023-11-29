import mongoengine as me
from datetime import datetime
from app.db.models import User, Category



class Expense(me.Document):
    cost = me.IntField(required=True)
    date = me.DateTimeField()
    user = me.ReferenceField(User, required=True, reverse_delete_rule=me.CASCADE)
    description = me.StringField()
    category = me.ReferenceField(Category)
    expense_id = me.StringField(unique=True, required=True)

    def to_dict(self, include_user=True):
        expense_date = self.date.isoformat() if (self.date is not None) else None
        category = self.category.name if (self.category is not None) else None
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
import mongoengine as me
from app.db.models import User


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
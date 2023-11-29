import mongoengine as me
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from datetime import datetime, timedelta
import os

class User(me.Document):
    user_id = me.StringField(primary_key=True)
    username = me.StringField(required=True, unique=True)
    email = me.EmailField(unique=True)
    password_hash = me.StringField(required=True)
    first_name = me.StringField()
    last_name = me.StringField()
    birth_date = me.DateField()
    token = me.StringField(unique=True)
    token_expiration = me.DateTimeField()

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
            self.birth_date = user_birth_date
        if "first_name" in data:
            self.first_name = data["first_name"]
        if "last_name" in data:
            self.last_name = data["last_name"]
        if "username" in data:
            self.username = data["username"]
        if "email" in data:
            self.email = data["email"]
        if "user_id" in data:
            self.user_id = data["user_id"]
        if "password" in data:
            self.password = data["password"]

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode("utf-8")
        self.token_expiration = now + timedelta(seconds=expires_in)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
        self.save()

    @staticmethod
    def check_token(token):
        user = User.objects(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user
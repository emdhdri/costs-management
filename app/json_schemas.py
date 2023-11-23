import jsl

email_pattern = r'^\S+@\S+\.\S+$'
datetime_pattern = r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2}(?:\.\d*)?)((-(\d{2}):(\d{2})|Z)?)$'

class UserSchema(jsl.Document):
    first_name = jsl.StringField()
    last_name = jsl.StringField()
    username = jsl.StringField(required=True)
    email = jsl.EmailField(pattern=email_pattern)
    birth_date = jsl.DateTimeField(pattern=datetime_pattern)

class ExpenseSchema(jsl.Document):
    cost = jsl.NumberField(required=True)
    date = jsl.DateTimeField(pattern=datetime_pattern)
    description = jsl.StringField()
    category = jsl.StringField()

class CategorySchema(jsl.Document):
    category = jsl.StringField(required=True)

class editExpenseSchema(jsl.Document):
    cost = jsl.NumberField()
    date = jsl.DateTimeField(pattern=datetime_pattern)
    description = jsl.StringField()
    category = jsl.StringField()


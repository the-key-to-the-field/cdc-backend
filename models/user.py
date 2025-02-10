from marshmallow import Schema, fields, validate
from werkzeug.security import generate_password_hash, check_password_hash

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, load_only=True)
    role = fields.Str(required=True, validate=validate.OneOf(["user", "admin"]))

    def hash_password(self, password):
        return generate_password_hash(password)

    def verify_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)

user_schema = UserSchema() 
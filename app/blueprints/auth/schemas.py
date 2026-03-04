from marshmallow import Schema, fields, validate, post_load
from app.extensions import ma
from app.models import User


class LoginSchema(Schema):
    username = fields.Str(allow_none=True)
    email = fields.Email(allow_none=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))


class SignupSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    password_confirm = fields.Str(required=True, validate=validate.Length(min=8))
    
    @post_load
    def validate_passwords(self, data, **kwargs):
        if data['password'] != data['password_confirm']:
            raise ValueError("Passwords do not match")
        return data


login_schema = LoginSchema()
signup_schema = SignupSchema()

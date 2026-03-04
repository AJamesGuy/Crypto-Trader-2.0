from marshmallow import Schema, fields, validate
from app.extensions import ma
from app.models import User


class UpdateProfileSchema(Schema):
    username = fields.Str(allow_none=True, validate=validate.Length(min=3, max=100))
    email = fields.Email(allow_none=True)


class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True, validate=validate.Length(min=8))
    new_password = fields.Str(required=True, validate=validate.Length(min=8))
    confirm_password = fields.Str(required=True, validate=validate.Length(min=8))
    
    def load(self, *args, **kwargs):
        data = super().load(*args, **kwargs)
        if data.get('new_password') != data.get('confirm_password'):
            raise ValueError("Passwords do not match")
        return data


class ResetBalanceSchema(Schema):
    confirm = fields.Bool(required=True)


class DeleteAccountSchema(Schema):
    password = fields.Str(required=True, validate=validate.Length(min=8))
    confirm = fields.Bool(required=True)


update_profile_schema = UpdateProfileSchema()
change_password_schema = ChangePasswordSchema()
reset_balance_schema = ResetBalanceSchema()
delete_account_schema = DeleteAccountSchema()
from flask import Markup, render_template
from flask_wtf import FlaskForm as Form
from notifications_utils.formatters import strip_all_whitespace
from notifications_utils.recipients import (
    InvalidEmailError,
    validate_email_address,
)
from wtforms import StringField, ValidationError
from wtforms.validators import DataRequired


class ValidEmail:
    message = 'Not a valid email address'

    def __call__(self, form, field):
        if not field.data:
            return

        try:
            validate_email_address(field.data)
        except InvalidEmailError:
            raise ValidationError(self.message)


class EmailAddressField(StringField):
    def widget(self, field, **kwargs):
        if field.errors:
            error_message = {"text": field.errors[0]}
        else:
            error_message = None

        params = {
            "id": self.id,
            "name": self.name,
            "type": "email",
            "errorMessage": error_message,
            "label": {
                "text": "Email address",
                "for": self.id,
            },
            "spellcheck": False,
            "autocomplete": "email",
            "value": field.data
        }
        return Markup(render_template("components/govuk_input.html", params=params))


class EmailAddressForm(Form):
    email_address = EmailAddressField(
        'Email address',
        validators=[DataRequired('Enter your email address'), ValidEmail()],
        filters=[strip_all_whitespace],
    )

import pytest
from werkzeug.datastructures import MultiDict

from app.forms import EmailAddressForm


def test_email_address_form_strips_whitespace(client):
    form = EmailAddressForm(formdata=MultiDict([("email_address", "     me@example.com   ")]))

    form.validate()

    assert form.email_address.data == "me@example.com"


@pytest.mark.parametrize(
    "email_address,error",
    [
        ("invalid_email", "Not a valid email address"),
        ("", "Enter your email address"),
    ],
)
def test_email_address_form_validates(client, email_address, error):
    form = EmailAddressForm(formdata=MultiDict([("email_address", email_address)]))

    form.validate()

    assert form.email_address.errors == [error]

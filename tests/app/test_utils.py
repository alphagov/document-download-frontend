import pytest

from app.utils import assess_contact_type


@pytest.mark.parametrize(
    "contact_info,expected_result",
    [
        ("07123456789", "other"),
        ("pinkdiamond@homeworld.gem", "email"),
        ("pink.diamond@digital.diamond-office.gov.uk", "email"),
        ("https://homeworld.gem/contact-us", "link"),
        ("http://homeworld.gem/contact-us", "link"),
        ("www.homeworld.gem", "other"),
        ("homeworld.gem", "other"),
        ("pinkdiamond", "other"),
    ],
)
def test_assess_contact_type_recognises_email_phone_and_link(contact_info, expected_result):
    assert assess_contact_type(contact_info) == expected_result

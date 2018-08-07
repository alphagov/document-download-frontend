from app.utils import get_cdn_domain, assess_contact_type
import pytest


def test_get_cdn_domain_on_localhost(client, mocker):
    mocker.patch.dict('app.current_app.config', values={'ADMIN_BASE_URL': 'http://localhost:6012'})
    domain = get_cdn_domain()
    assert domain == 'static-logos.notify.tools'


def test_get_cdn_domain_on_non_localhost(client, mocker):
    mocker.patch.dict('app.current_app.config', values={'ADMIN_BASE_URL': 'https://some.admintest.com'})
    domain = get_cdn_domain()
    assert domain == 'static-logos.admintest.com'


@pytest.mark.parametrize(
    "contact_info,expected_result",
    [
        ("07123456789", "phone"),
        ("0300 200 3300", "phone"),
        ("020 3049 7444", "phone"),
        ("pinkdiamond@homeworld.gem", "email"),
        ("pink.diamond@digital.diamond-office.gov.uk", "email"),
        ("https://homeworld.gem/contact-us", "link"),
        ("http://homeworld.gem/contact-us", "link"),
        ("www.homeworld.gem", "unrecognised"),
        ("homeworld.gem", "unrecognised"),
        ("pinkdiamond", "unrecognised")
    ]
)
def test_assess_contact_type_recognises_email_phone_and_link(contact_info, expected_result):
    assert assess_contact_type(contact_info) == expected_result

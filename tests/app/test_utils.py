import pytest

from app.utils import (
    assess_contact_type,
    bytes_to_pretty_file_size,
    get_cdn_domain,
)


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
        ("07123456789", "other"),
        ("pinkdiamond@homeworld.gem", "email"),
        ("pink.diamond@digital.diamond-office.gov.uk", "email"),
        ("https://homeworld.gem/contact-us", "link"),
        ("http://homeworld.gem/contact-us", "link"),
        ("www.homeworld.gem", "other"),
        ("homeworld.gem", "other"),
        ("pinkdiamond", "other")
    ]
)
def test_assess_contact_type_recognises_email_phone_and_link(contact_info, expected_result):
    assert assess_contact_type(contact_info) == expected_result


@pytest.mark.parametrize(
    "bytes,expected_result",
    [
        (0, "0.1KB"),
        (1, "0.1KB"),
        (51, "0.1KB"),  # 0.0498046875KB which rounds to 0.0KB but we force it to 0.1KB
        (52, "0.1KB"),  # 0.05078125KB so rounds to 0.1KB
        (153, "0.1KB"),  # 0.1494140625KB so rounds to 0.1KB
        (154, "0.2KB"),  # 0.150390625KB so rounds to 0.2KB
        (1023, "1KB"),
        (1024, "1KB"),  # exactly 1KB
        (1025, "1KB"),
        (2048, "2KB"),  # exactly 2KB
        (52428, "51.2KB"),  # 0.049999MB so stays as KB
        (52429, "0.1MB"),  # 0.0500001MB so rounds to 0.1MB
        (1048576, "1MB"),  # exactly 1MB
        (2023751, "1.9MB"),
        (2097151, "2MB"),
        (2097152, "2MB"),  # exactly 2MB
    ]
)
def test_bytes_to_pretty_file_size(bytes, expected_result):
    assert bytes_to_pretty_file_size(bytes) == expected_result

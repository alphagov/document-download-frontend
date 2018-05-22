from app.utils import get_cdn_domain


def test_get_cdn_domain_on_localhost(client, mocker):
    mocker.patch.dict('app.current_app.config', values={'ADMIN_BASE_URL': 'http://localhost:6012'})
    domain = get_cdn_domain()
    assert domain == 'static-logos.notify.tools'


def test_get_cdn_domain_on_non_localhost(client, mocker):
    mocker.patch.dict('app.current_app.config', values={'ADMIN_BASE_URL': 'https://some.admintest.com'})
    domain = get_cdn_domain()
    assert domain == 'static-logos.admintest.com'

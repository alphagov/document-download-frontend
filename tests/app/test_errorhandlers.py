from bs4 import BeautifulSoup
from flask import url_for
from flask_wtf.csrf import CSRFError

from tests import normalize_spaces


def test_bad_url_returns_page_not_found(client):
    response = client.get('/bad_url')
    assert response.status_code == 404
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert page.h1.string.strip() == 'Page not found'


def test_csrf_error_returns_400_status_code_and_500_error_page(
    service_id,
    document_id,
    key,
    document_has_metadata_no_confirmation,
    client,
    mocker,
    sample_service,
):
    # we turn off CSRF handling for tests, so fake a CSRF response here.
    csrf_err = CSRFError('400 Bad Request: The CSRF tokens do not match.')
    mocker.patch('app.main.views.index.redirect', side_effect=csrf_err)
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})

    response = client.post(
        url_for(
            'main.confirm_email_address',
            service_id=service_id,
            document_id=document_id,
            key=key,
        ),
        data={'email_address': 'me@example.com'}
    )
    assert response.status_code == 400

    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert normalize_spaces(page.h1.text) == 'Sorry, there’s a problem with the service'

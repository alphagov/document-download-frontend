import uuid

from bs4 import BeautifulSoup
from flask import url_for
from flask_wtf.csrf import CSRFError


def test_bad_url_returns_page_not_found(client):
    response = client.get('/bad_url')
    assert response.status_code == 404
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert page.h1.string.strip() == 'Page not found'


def test_csrf_returns_400(client, mocker, sample_service):
    # we turn off CSRF handling for tests, so fake a CSRF response here.
    csrf_err = CSRFError('400 Bad Request: The CSRF tokens do not match.')
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    mocker.patch('app.main.views.index.render_template', side_effect=csrf_err)

    metadata = {'direct_file_url': 'url'}
    mocker.patch('app.main.views.index.get_document_metadata', return_value=metadata)

    response = client.get(
        url_for(
            'main.landing',
            service_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            key='1234'
        )
    )

    assert response.status_code == 400
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert page.h1.string.strip() == 'Page not found'

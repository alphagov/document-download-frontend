import re
from unittest.mock import Mock
from uuid import uuid4

import pytest
from bs4 import BeautifulSoup
from flask import current_app, url_for
from notifications_python_client.errors import HTTPError

from tests import normalize_spaces


@pytest.fixture
def service_id():
    return uuid4()


@pytest.fixture
def document_id():
    return uuid4()


@pytest.fixture
def key():
    return '1234'


@pytest.fixture
def document_has_metadata(service_id, document_id, key, rmock, client):
    json_response = {"document": {"direct_file_url": "url"}}

    rmock.get(
        '{}/services/{}/documents/{}/check?key={}'.format(
            current_app.config['DOCUMENT_DOWNLOAD_API_HOST_NAME'],
            service_id,
            document_id,
            key
        ),
        json=json_response
    )


def test_status(client):
    response = client.get(url_for('main.status'))
    assert response.status_code == 200
    assert response.get_data(as_text=True) == 'ok'


@pytest.mark.parametrize('view', ['main.landing', 'main.download_document'])
def test_404_if_no_key_in_query_string(service_id, document_id, view, client):
    response = client.get(
        url_for(
            view,
            service_id=service_id,
            document_id=document_id,
        )
    )
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert response.status_code == 404
    assert normalize_spaces(page.title.text) == 'Page not found – GOV.UK'
    assert normalize_spaces(page.h1.text) == 'Page not found'


@pytest.mark.parametrize('view', ['main.landing', 'main.download_document'])
def test_notifications_api_error(
    view,
    service_id,
    document_id,
    client,
    mocker,
    sample_service
):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    mocker.patch('app.service_api_client.get_service', side_effect=HTTPError(response=Mock(status_code=404)))
    response = client.get(
        url_for(
            view,
            service_id=uuid4(),
            document_id=uuid4(),
            key='1234'
        )
    )

    assert response.status_code == 404


@pytest.mark.parametrize('view', ['main.landing', 'main.download_document'])
def test_when_document_is_unavailable(
    view,
    service_id,
    document_id,
    key,
    client,
    mocker,
    sample_service
):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    mocker.patch('app.main.views.index._get_document_metadata', return_value=None)
    response = client.get(
        url_for(
            view,
            service_id=service_id,
            document_id=document_id,
            key=key,
        )
    )

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert normalize_spaces(page.h1.text) == 'No longer available'

    contact_link = page.select('main a')[0]
    assert normalize_spaces(contact_link.text) == 'contact Sample Service'
    assert contact_link['href'] == 'https://sample-service.gov.uk'


@pytest.mark.parametrize('view', [
    'main.landing',
    'main.download_document',
])
@pytest.mark.parametrize('json_response', [
    {"error": "Missing decryption key"},
    {"error": "Invalid decryption key"},
    {"error": "Forbidden"},
])
def test_404_hides_incorrect_credentials(
    view,
    client,
    service_id,
    document_id,
    key,
    rmock,
    mocker,
    json_response,
    sample_service,
):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})

    rmock.get(
        '{}/services/{}/documents/{}/check?key={}'.format(
            current_app.config['DOCUMENT_DOWNLOAD_API_HOST_NAME'],
            service_id,
            document_id,
            key
        ),
        status_code=400,
        json=json_response
    )
    response = client.get(
        url_for(
            'main.landing',
            service_id=service_id,
            document_id=document_id,
            key=key
        )
    )
    assert response.status_code == 404


def test_landing_page_creates_link_for_document(
    service_id,
    document_id,
    key,
    document_has_metadata,
    client,
    mocker,
    sample_service
):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})

    response = client.get(
        url_for(
            'main.landing',
            service_id=service_id,
            document_id=document_id,
            key=key,
        )
    )

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert normalize_spaces(page.title.text) == 'You have a file to download – GOV.UK'
    assert normalize_spaces(page.h1.text) == 'You have a file to download'
    assert page.find('a', string=re.compile("Continue"))['href'] == url_for(
        'main.download_document',
        service_id=service_id,
        document_id=document_id,
        key='1234'
    )


def test_download_document_creates_link_to_actual_doc_from_api(
    service_id,
    document_id,
    key,
    document_has_metadata,
    client,
    mocker,
    sample_service
):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})

    response = client.get(
        url_for(
            'main.download_document',
            service_id=service_id,
            document_id=document_id,
            key=key
        )
    )

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert normalize_spaces(page.title.text) == 'Download your file – GOV.UK'
    assert normalize_spaces(page.h1.text) == 'Download your file'
    assert page.select('main a')[0]['href'] == 'url'


def test_download_document_shows_contact_information(
    service_id,
    document_id,
    key,
    document_has_metadata,
    client,
    mocker,
    sample_service
):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})

    response = client.get(
        url_for(
            'main.download_document',
            service_id=service_id,
            document_id=document_id,
            key=key
        )
    )

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')

    contact_link = page.select('main a')[1]
    assert contact_link.text.strip() == 'contact Sample Service'
    assert contact_link['href'] == 'https://sample-service.gov.uk'


@pytest.mark.parametrize('view', ['main.landing', 'main.download_document'])
def test_pages_are_not_indexed(
    view,
    service_id,
    document_id,
    key,
    document_has_metadata,
    client,
    mocker,
    sample_service
):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})

    response = client.get(
        url_for(
            view,
            service_id=service_id,
            document_id=document_id,
            key=key
        )
    )

    assert response.status_code == 200
    assert response.headers['X-Robots-Tag'] == 'noindex, nofollow'


@pytest.mark.parametrize('contact_info,type,expected_result', [
    ('https://sample-service.gov.uk', 'link', 'https://sample-service.gov.uk'),
    ('info@sample-service.gov.uk', 'email', 'mailto:info@sample-service.gov.uk'),
    ('07123456789', 'number', 'call 07123456789'),

])
def test_landing_page_has_supplier_contact_info(
    service_id,
    document_id,
    key,
    document_has_metadata,
    client,
    mocker,
    sample_service,
    contact_info,
    type,
    expected_result
):
    service = {'name': 'Sample Service', 'contact_link': contact_info}
    mocker.patch('app.service_api_client.get_service', return_value={'data': service})

    response = client.get(
        url_for(
            'main.landing',
            service_id=service_id,
            document_id=document_id,
            key=key,
        )
    )

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    if type == 'number':
        assert page.findAll(text=re.compile(expected_result))
    else:
        assert page.findAll(attrs={'href': expected_result})

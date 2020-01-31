import re
from unittest.mock import Mock
from uuid import uuid4

import pytest
from bs4 import BeautifulSoup
from flask import url_for
from notifications_python_client.errors import HTTPError


def test_status(client):
    response = client.get(url_for('main.status'))
    assert response.status_code == 200
    assert response.get_data(as_text=True) == 'ok'


def test_landing_page_404s_if_no_key_in_query_string(client):
    response = client.get(
        url_for(
            'main.landing',
            service_id=uuid4(),
            document_id=uuid4()
        )
    )
    assert response.status_code == 404


def test_landing_page_notifications_api_error(client, mocker, sample_service):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    mocker.patch('app.service_api_client.get_service', side_effect=HTTPError(response=Mock(status_code=404)))
    response = client.get(
        url_for(
            'main.landing',
            service_id=uuid4(),
            document_id=uuid4(),
            key='1234'
        )
    )

    assert response.status_code == 404


def test_landing_page_creates_link_for_document(client, mocker, sample_service):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    service_id = uuid4()
    document_id = uuid4()
    response = client.get(
        url_for(
            'main.landing',
            service_id=service_id,
            document_id=document_id,
            key='1234'
        )
    )

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')

    assert page.find('a', string=re.compile("Continue"))['href'] == url_for(
        'main.download_document',
        service_id=service_id,
        document_id=document_id,
        key='1234'
    )


def test_download_document_creates_link_to_actual_doc_from_api(client, mocker, sample_service):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    service_id = uuid4()
    document_id = uuid4()
    key = '1234'

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

    assert page.select('main a')[0]['href'] == 'http://test-doc-download-api/services/{}/documents/{}?key={}'.format(
        service_id,
        document_id,
        key
    )


def test_download_document_shows_contact_information(client, mocker, sample_service):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    service_id = uuid4()
    document_id = uuid4()
    key = '1234'

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
def test_pages_are_not_indexed(view, client, mocker, sample_service):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    service_id = uuid4()
    document_id = uuid4()
    key = '1234'

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
def test_landing_page_has_supplier_contact_info(client, mocker, sample_service, contact_info, type, expected_result):
    service = {'name': 'Sample Service', 'contact_link': contact_info}
    mocker.patch('app.service_api_client.get_service', return_value={'data': service})
    service_id = uuid4()
    document_id = uuid4()
    response = client.get(
        url_for(
            'main.landing',
            service_id=service_id,
            document_id=document_id,
            key='1234'
        )
    )

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    if type == 'number':
        assert page.findAll(text=re.compile(expected_result))
    else:
        assert page.findAll(attrs={'href': expected_result})

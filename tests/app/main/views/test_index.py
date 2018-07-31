from uuid import uuid4
from unittest.mock import Mock

import pytest
from bs4 import BeautifulSoup
from flask import url_for
from notifications_python_client.errors import HTTPError


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

    assert page.select_one('main a')['href'] == url_for(
        'main.download_document',
        service_id=service_id,
        document_id=document_id,
        key='1234'
    )


def test_download_document_creates_link_to_actual_doc_from_api(client, mocker, sample_service):
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

    assert page.select_one('main a')['href'] == 'http://test-doc-download-api/services/{}/documents/{}?key={}'.format(
        service_id,
        document_id,
        key
    )


@pytest.mark.parametrize('view', ['post_my_document'])
def test_static_pages(client, view):
    response = client.get(url_for('main.{}'.format(view)))

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')

    assert not page.select_one('meta[name=description]')


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

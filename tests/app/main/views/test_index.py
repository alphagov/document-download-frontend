from unittest.mock import Mock

import pytest
from bs4 import BeautifulSoup
from flask import url_for
from notifications_python_client.errors import HTTPError


def test_download_document_landing_404s_if_no_key_in_query_string(client):
    response = client.get(
        url_for(
            'main.download_document_landing',
            service_id='1234',
            document_id='1234'
        )
    )
    assert response.status_code == 404


def test_download_document_download_404s_if_no_key_in_query_string(client):
    response = client.get(
        url_for(
            'main.download_document_download',
            service_id='1234',
            document_id='1234'
        )
    )
    assert response.status_code == 404


def test_download_document_notifications_api_error(client, mocker, sample_service):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    mocker.patch('app.service_api_client.get_service', side_effect=HTTPError(response=Mock(status_code=404)))
    response = client.get(
        url_for(
            'main.download_document_landing',
            service_id='1234',
            document_id='1234',
            key='1234'
        )
    )

    assert response.status_code == 404


def test_download_document_create_creates_link_for_document(client, mocker, sample_service):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    response = client.get(
        url_for(
            'main.download_document_landing',
            service_id='1234',
            document_id='1234',
            key='1234'
        )
    )

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')

    assert page.select_one('main a')['href'] == url_for(
        'main.download_document_download',
        service_id='1234',
        document_id='1234',
        key='1234'
    )


def test_document_download_redirects_not_via_landing(client, mocker, sample_service):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    response = client.get(
        url_for(
            'main.download_document_download',
            service_id='1234',
            document_id='1234',
            key='1234'
        )
    )

    assert response.status_code == 302


def test_download_document_download(client, mocker, sample_service):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})

    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    landing_response = client.get(
        url_for(
            'main.download_document_landing',
            service_id='1234',
            document_id='1234',
            key='1234'
        )
    )

    assert landing_response.status_code == 200

    download_response = client.get(
        url_for(
            'main.download_document_download',
            service_id='1234',
            document_id='1234',
            key='1234'
        )
    )

    assert download_response.status_code == 200


@pytest.mark.parametrize('view', ['post_my_document'])
def test_static_pages(client, view):
    response = client.get(url_for('main.{}'.format(view)))

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')

    assert not page.select_one('meta[name=description]')

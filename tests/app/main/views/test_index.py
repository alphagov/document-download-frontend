import pytest
from bs4 import BeautifulSoup
from flask import url_for


def test_download_document_404s_if_no_key_in_query_string(client):
    response = client.get(
        url_for(
            'main.download_document_landing',
            service_id='1234',
            document_id='1234'
        )
    )
    assert response.status_code == 404


def test_download_document_create_creates_link_for_document(client):
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


@pytest.mark.parametrize('view', ['post_my_document'])
def test_static_pages(client, view):
    response = client.get(url_for('main.{}'.format(view)))

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')

    assert not page.select_one('meta[name=description]')

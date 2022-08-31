import re
from unittest.mock import Mock

import pytest
from bs4 import BeautifulSoup
from flask import current_app, url_for
from notifications_python_client.errors import HTTPError

from tests import normalize_spaces


def test_status(client):
    response = client.get(url_for('main.status'))
    assert response.status_code == 200
    assert response.get_data(as_text=True) == 'ok'


@pytest.mark.parametrize('url', [
    '/security.txt',
    '/.well-known/security.txt',
])
def test_security_policy_redirects_to_policy(client, url):
    response = client.get(
        url
    )

    assert response.status_code == 302
    assert response.location == "https://vdp.cabinetoffice.gov.uk/.well-known/security.txt"


@pytest.mark.parametrize('view, method', [
    ('main.landing', 'get'),
    ('main.download_document', 'get'),
    ('main.confirm_email_address', 'get'),
    ('main.confirm_email_address', 'post'),
])
def test_404_if_no_key_in_query_string(service_id, document_id, view, method, client):
    response = client.open(
        url_for(
            view,
            service_id=service_id,
            document_id=document_id,
        ),
        method=method,
    )
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert response.status_code == 404
    assert normalize_spaces(page.title.text) == 'Page not found – GOV.UK'
    assert normalize_spaces(page.h1.text) == 'Page not found'


@pytest.mark.parametrize('view, method', [
    ('main.landing', 'get'),
    ('main.download_document', 'get'),
    ('main.confirm_email_address', 'get'),
    ('main.confirm_email_address', 'post'),
])
def test_notifications_api_error(
    view,
    method,
    service_id,
    document_id,
    client,
    mocker,
    sample_service
):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    mocker.patch('app.service_api_client.get_service', side_effect=HTTPError(response=Mock(status_code=404)))

    response = client.open(
        url_for(
            view,
            service_id=service_id,
            document_id=document_id,
            key='1234'
        ),
        method=method,
    )

    assert response.status_code == 404


@pytest.mark.parametrize('view, method', [
    ('main.landing', 'get'),
    ('main.download_document', 'get'),
    ('main.confirm_email_address', 'get'),
    ('main.confirm_email_address', 'post'),
])
def test_when_document_is_unavailable(
    view,
    method,
    service_id,
    document_id,
    key,
    client,
    mocker,
    sample_service
):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})
    mocker.patch('app.main.views.index._get_document_metadata', return_value=None)
    response = client.open(
        url_for(
            view,
            service_id=service_id,
            document_id=document_id,
            key=key,
        ),
        method=method,
    )

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert normalize_spaces(page.h1.text) == 'No longer available'

    contact_link = page.select('main a')[0]
    assert normalize_spaces(contact_link.text) == 'contact Sample Service'
    assert contact_link['href'] == 'https://sample-service.gov.uk'


@pytest.mark.parametrize('view, method', [
    ('main.landing', 'get'),
    ('main.download_document', 'get'),
    ('main.confirm_email_address', 'get'),
    ('main.confirm_email_address', 'post'),
])
@pytest.mark.parametrize('json_response', [
    {"error": "Missing decryption key"},
    {"error": "Invalid decryption key"},
    {"error": "Forbidden"},
])
def test_404_hides_incorrect_credentials(
    view,
    method,
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
    response = client.open(
        url_for(
            view,
            service_id=service_id,
            document_id=document_id,
            key=key
        ),
        method=method,
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


def test_confirm_email_address_page_show_email_address_form(
    service_id,
    document_id,
    key,
    document_has_metadata,
    client,
    mocker,
    sample_service,
):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})

    response = client.get(
        url_for(
            'main.confirm_email_address',
            service_id=service_id,
            document_id=document_id,
            key=key,
        )
    )
    assert response.status_code == 200

    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert normalize_spaces(page.title.text) == 'Confirm your email address – GOV.UK'
    assert normalize_spaces(page.h1.text) == 'Confirm your email address'
    assert page.select_one('form')
    assert not page.select('.govuk-error-summary')


def test_confirm_email_address_page_redirects_to_download_document_page(
    service_id,
    document_id,
    key,
    document_has_metadata,
    client,
    mocker,
    sample_service,
):
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
    assert response.status_code == 302

    assert response.location == url_for(
        'main.download_document',
        service_id=service_id,
        document_id=document_id,
        key=key,
    )


def test_confirm_email_address_page_shows_an_error_if_the_email_address_is_invalid(
    service_id,
    document_id,
    key,
    document_has_metadata,
    client,
    mocker,
    sample_service,
):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})

    response = client.post(
        url_for(
            'main.confirm_email_address',
            service_id=service_id,
            document_id=document_id,
            key=key,
        ),
        data={'email_address': 'fake address'}
    )
    assert response.status_code == 200

    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert normalize_spaces(page.title.text) == 'Error: Confirm your email address – GOV.UK'
    assert normalize_spaces(page.h1.text) == 'Confirm your email address'

    # Error summary in banner at the top of the page
    assert normalize_spaces(page.select_one('.govuk-error-summary__title').text) == 'There is a problem'
    assert normalize_spaces(page.select_one('.govuk-error-summary__list').text) == 'Not a valid email address'

    # Error above the form input
    assert normalize_spaces(page.select_one('#email-address-input-error').text) == 'Error: Not a valid email address'


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


@pytest.mark.parametrize('view, method', [
    ('main.landing', 'get'),
    ('main.download_document', 'get'),
    ('main.confirm_email_address', 'get'),
    ('main.confirm_email_address', 'post'),
])
def test_pages_contain_key_security_headers(
    view,
    method,
    service_id,
    document_id,
    key,
    document_has_metadata,
    client,
    mocker,
    sample_service
):
    mocker.patch('app.service_api_client.get_service', return_value={'data': sample_service})

    response = client.open(
        url_for(
            view,
            service_id=service_id,
            document_id=document_id,
            key=key
        ),
        method=method,
    )

    assert response.status_code == 200
    assert response.headers['X-Robots-Tag'] == 'noindex, nofollow'
    assert response.headers['Referrer-Policy'] == 'no-referrer'


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
        assert page.find_all(string=re.compile(expected_result))
    else:
        assert page.find_all(attrs={'href': expected_result})


def test_footer_doesnt_link_to_national_archives(
    service_id,
    document_id,
    key,
    document_has_metadata,
    client,
    mocker,
):
    service = {'name': 'Sample Service', 'contact_link': 'blah blah blah'}
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

    links = page.find_all('a')
    assert not any('nationalarchives.gov.uk' in a.attrs['href'] for a in links)

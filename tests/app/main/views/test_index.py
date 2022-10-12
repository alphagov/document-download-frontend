import re
from datetime import date, timedelta
from unittest.mock import Mock

import pytest
from bs4 import BeautifulSoup
from flask import current_app, url_for
from freezegun import freeze_time
from notifications_python_client.errors import HTTPError
from notifications_utils.base64_uuid import uuid_to_base64

from tests import normalize_spaces


def test_status(client):
    response = client.get(url_for("main.status"))
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "ok"


@pytest.mark.parametrize(
    "url",
    [
        "/security.txt",
        "/.well-known/security.txt",
    ],
)
def test_security_policy_redirects_to_policy(client, url):
    response = client.get(url)

    assert response.status_code == 302
    assert response.location == "https://vdp.cabinetoffice.gov.uk/.well-known/security.txt"


@pytest.mark.parametrize(
    "view, method",
    [
        ("main.landing", "get"),
        ("main.download_document", "get"),
        ("main.confirm_email_address", "get"),
        ("main.confirm_email_address", "post"),
    ],
)
def test_404_if_no_key_in_query_string(service_id, document_id, view, method, client):
    response = client.open(
        url_for(
            view,
            service_id=service_id,
            document_id=document_id,
        ),
        method=method,
    )
    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    assert response.status_code == 404
    assert normalize_spaces(page.title.text) == "Page not found – GOV.UK"
    assert normalize_spaces(page.h1.text) == "Page not found"


@pytest.mark.parametrize(
    "view, method",
    [
        ("main.landing", "get"),
        ("main.download_document", "get"),
        ("main.confirm_email_address", "get"),
        ("main.confirm_email_address", "post"),
    ],
)
def test_notifications_api_error(view, method, service_id, document_id, client, mocker, sample_service):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})
    mocker.patch("app.service_api_client.get_service", side_effect=HTTPError(response=Mock(status_code=404)))

    response = client.open(
        url_for(view, service_id=service_id, document_id=document_id, key="1234"),
        method=method,
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "view, method",
    [
        ("main.landing", "get"),
        ("main.download_document", "get"),
        ("main.confirm_email_address", "get"),
        ("main.confirm_email_address", "post"),
    ],
)
def test_when_document_is_unavailable(view, method, service_id, document_id, key, client, mocker, sample_service):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})
    mocker.patch("app.main.views.index._get_document_metadata", return_value=None)
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
    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    assert normalize_spaces(page.h1.text) == "No longer available"

    contact_link = page.select("main a")[0]
    assert normalize_spaces(contact_link.text) == "contact Sample Service"
    assert contact_link["href"] == "https://sample-service.gov.uk"


@pytest.mark.parametrize(
    "view, method",
    [
        ("main.landing", "get"),
        ("main.download_document", "get"),
        ("main.confirm_email_address", "get"),
        ("main.confirm_email_address", "post"),
    ],
)
@pytest.mark.parametrize(
    "json_response",
    [
        {"error": "Missing decryption key"},
        {"error": "Invalid decryption key"},
        {"error": "Forbidden"},
    ],
)
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
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    rmock.get(
        "{}/services/{}/documents/{}/check?key={}".format(
            current_app.config["DOCUMENT_DOWNLOAD_API_HOST_NAME"], service_id, document_id, key
        ),
        status_code=400,
        json=json_response,
    )
    response = client.open(
        url_for(view, service_id=service_id, document_id=document_id, key=key),
        method=method,
    )
    assert response.status_code == 404


def test_landing_page_creates_link_for_document(
    service_id, document_id, key, document_has_metadata_no_confirmation, client, mocker, sample_service
):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    response = client.get(
        url_for(
            "main.landing",
            service_id=service_id,
            document_id=document_id,
            key=key,
        )
    )

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    assert normalize_spaces(page.title.text) == "You have a file to download – GOV.UK"
    assert normalize_spaces(page.h1.text) == "You have a file to download"
    assert page.find("a", string=re.compile("Continue"))["href"] == url_for(
        "main.download_document", service_id=service_id, document_id=document_id, key="1234"
    )


def test_landing_page_creates_link_to_confirm_email_address(
    service_id, document_id, key, document_has_metadata_requires_confirmation, client, mocker, sample_service
):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    response = client.get(
        url_for(
            "main.landing",
            service_id=service_id,
            document_id=document_id,
            key=key,
        )
    )

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    assert normalize_spaces(page.title.text) == "You have a file to download – GOV.UK"
    assert normalize_spaces(page.h1.text) == "You have a file to download"
    assert page.find("a", string=re.compile("Continue"))["href"] == url_for(
        "main.confirm_email_address", service_id=service_id, document_id=document_id, key="1234"
    )


def test_confirm_email_address_page_show_email_address_form(
    service_id,
    document_id,
    key,
    document_has_metadata_requires_confirmation,
    client,
    mocker,
    sample_service,
):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    response = client.get(
        url_for(
            "main.confirm_email_address",
            service_id=service_id,
            document_id=document_id,
            key=key,
        )
    )
    assert response.status_code == 200

    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    assert normalize_spaces(page.title.text) == "Confirm your email address – GOV.UK"
    assert normalize_spaces(page.h1.text) == "Confirm your email address"
    assert page.select_one("form")
    assert not page.select(".govuk-error-summary")


def test_confirm_email_address_page_redirects_to_download_page_if_confirmation_not_required(
    service_id,
    document_id,
    key,
    document_has_metadata_no_confirmation,
    client,
    mocker,
    sample_service,
):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    response = client.get(
        url_for(
            "main.confirm_email_address",
            service_id=service_id,
            document_id=document_id,
            key=key,
        ),
    )
    assert response.status_code == 302
    assert response.location == url_for(
        "main.download_document",
        service_id=service_id,
        document_id=document_id,
        key=key,
    )


def test_confirm_email_address_page_shows_an_error_if_the_email_address_is_invalid(
    service_id,
    document_id,
    key,
    document_has_metadata_requires_confirmation,
    client,
    mocker,
    sample_service,
):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    response = client.post(
        url_for(
            "main.confirm_email_address",
            service_id=service_id,
            document_id=document_id,
            key=key,
        ),
        data={"email_address": "fake address"},
    )
    assert response.status_code == 400

    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    assert normalize_spaces(page.title.text) == "Error: Confirm your email address – GOV.UK"
    assert normalize_spaces(page.h1.text) == "Confirm your email address"

    # Error summary in banner at the top of the page
    assert normalize_spaces(page.select_one(".govuk-error-summary__title").text) == "There is a problem"
    assert normalize_spaces(page.select_one(".govuk-error-summary__list").text) == "Not a valid email address"

    # Error above the form input
    assert normalize_spaces(page.select_one("#email_address-error").text) == "Error: Not a valid email address"


def test_confirm_email_address_page_shows_error_if_wrong_email_address(
    service_id,
    document_id,
    key,
    document_has_metadata_requires_confirmation,
    client,
    mocker,
    sample_service,
    rmock,
):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    rmock.post(
        "{}/services/{}/documents/{}/authenticate".format(
            current_app.config["DOCUMENT_DOWNLOAD_API_HOST_NAME"],
            service_id,
            document_id,
        ),
        status_code=400,
        json={"error": "Authentication failure"},
    )

    response = client.post(
        url_for(
            "main.confirm_email_address",
            service_id=service_id,
            document_id=document_id,
            key=key,
        ),
        data={"email_address": "me@example.com"},
    )
    assert response.status_code == 400

    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    assert normalize_spaces(page.title.text) == "Error: Confirm your email address – GOV.UK"
    assert normalize_spaces(page.h1.text) == "Confirm your email address"

    # Error summary in banner at the top of the page
    assert normalize_spaces(page.select_one(".govuk-error-summary__title").text) == "There is a problem"
    assert normalize_spaces(page.select_one(".govuk-error-summary__list").text) == (
        "This is not the email address the file was sent to."
        "To confirm the file was meant for you, enter the email address Sample Service sent the file to."
    )

    # Error above the form input
    assert not page.select_one("#email_address-error")


def test_confirm_email_address_page_shows_429_error_page_if_auth_rate_limited(
    service_id,
    document_id,
    key,
    document_has_metadata_requires_confirmation,
    client,
    mocker,
    sample_service,
    rmock,
):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    rmock.post(
        "{}/services/{}/documents/{}/authenticate".format(
            current_app.config["DOCUMENT_DOWNLOAD_API_HOST_NAME"],
            service_id,
            document_id,
        ),
        status_code=429,
        json={"error": "Too many requests"},
    )

    response = client.post(
        url_for(
            "main.confirm_email_address",
            service_id=service_id,
            document_id=document_id,
            key=key,
        ),
        data={"email_address": "me@example.com"},
    )
    assert response.status_code == 429

    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    assert normalize_spaces(page.title.text) == "Cannot access document – GOV.UK"
    assert normalize_spaces(page.h1.text) == "Cannot access document"

    assert page.find("a", text="Go back to confirm your email address").get("href") == (
        "http://document-download-frontend.gov/"
        f"d/{uuid_to_base64(service_id)}/{uuid_to_base64(document_id)}/confirm-email-address?key=1234"
    )

    assert "notify-support@digital.cabinet-office.gov.uk" in page.text


@freeze_time("2000-01-01T12:34:56Z")
def test_confirm_email_address_page_redirects_and_sets_cookie_on_success(
    service_id,
    document_id,
    key,
    document_has_metadata_requires_confirmation,
    client,
    mocker,
    sample_service,
    rmock,
):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    rmock.post(
        "{}/services/{}/documents/{}/authenticate".format(
            current_app.config["DOCUMENT_DOWNLOAD_API_HOST_NAME"],
            service_id,
            document_id,
        ),
        status_code=200,
        json={"signed_data": "blah", "direct_file_url": "http://test-doc-download-api.com/my/file/path?key=foo"},
    )

    response = client.post(
        url_for(
            "main.confirm_email_address",
            service_id=service_id,
            document_id=document_id,
            key=key,
        ),
        data={"email_address": "me@example.com"},
    )
    assert response.status_code == 302
    assert response.location == url_for(
        "main.download_document", service_id=service_id, document_id=document_id, key=key
    )
    assert any(
        header == ("Set-Cookie", "document_access_signed_data=blah; HttpOnly; Path=/my/file/path")
        for header in response.headers
    )


def test_download_document_creates_link_to_actual_doc_from_api(
    service_id, document_id, key, document_has_metadata_no_confirmation, client, mocker, sample_service
):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    response = client.get(url_for("main.download_document", service_id=service_id, document_id=document_id, key=key))

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    assert normalize_spaces(page.title.text) == "Download your file – GOV.UK"
    assert normalize_spaces(page.h1.text) == "Download your file"
    assert page.select("main a")[0]["href"] == "url"
    assert page.select("main a")[0].text == "Download this text file (0.7MB) to your device"


@pytest.mark.parametrize(
    "file_extension,expected_pretty_file_type",
    [("pdf", "PDF"), ("txt", "text file"), ("docx", "Microsoft Word document")],
)
def test_download_document_shows_pretty_file_type(
    service_id, document_id, key, client, mocker, sample_service, file_extension, expected_pretty_file_type
):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})
    mocked_metadata = {
        "direct_file_url": "url",
        "confirm_email": False,
        "size_in_bytes": 712099,
        "file_extension": file_extension,
        "available_until": str(date.today() + timedelta(days=5)),
    }
    mocker.patch("app.main.views.index._get_document_metadata", return_value=mocked_metadata)

    response = client.get(url_for("main.download_document", service_id=service_id, document_id=document_id, key=key))

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    assert page.select("main a")[0].text == f"Download this {expected_pretty_file_type} (0.7MB) to your device"


def test_download_document_shows_contact_information(
    service_id, document_id, key, document_has_metadata_no_confirmation, client, mocker, sample_service
):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    response = client.get(url_for("main.download_document", service_id=service_id, document_id=document_id, key=key))

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")

    contact_link = page.select("main a")[1]
    assert contact_link.text.strip() == "contact Sample Service"
    assert contact_link["href"] == "https://sample-service.gov.uk"


@freeze_time("2022-10-12 13:30")
@pytest.mark.parametrize(
    "days_till_expiry,expected_content", [(30, "Friday 11 November 2022"), (31, "12 November 2022")]
)
def test_download_document_shows_expiry_date(
    service_id, document_id, key, client, mocker, sample_service, days_till_expiry, expected_content
):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    mocked_metadata = {
        "direct_file_url": "url",
        "confirm_email": False,
        "size_in_bytes": 712099,
        "file_extension": "pdf",
        "available_until": str(date.today() + timedelta(days=days_till_expiry)),
    }
    mocker.patch("app.main.views.index._get_document_metadata", return_value=mocked_metadata)

    response = client.get(url_for("main.download_document", service_id=service_id, document_id=document_id, key=key))

    assert response.status_code == 200

    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    content_about_expiry_date = page.select("main p")[2]

    assert f"This file is available until {expected_content}." in content_about_expiry_date.text


@pytest.mark.parametrize("view", ["main.landing", "main.download_document", "main.confirm_email_address"])
def test_pages_contain_key_security_headers(
    view, service_id, document_id, key, document_has_metadata_requires_confirmation, client, mocker, sample_service
):
    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    response = client.get(
        url_for(view, service_id=service_id, document_id=document_id, key=key),
    )

    assert response.status_code == 200
    assert response.headers["X-Robots-Tag"] == "noindex, nofollow"
    assert response.headers["Referrer-Policy"] == "no-referrer"


@pytest.mark.parametrize(
    "contact_info,type,expected_result",
    [
        ("https://sample-service.gov.uk", "link", "https://sample-service.gov.uk"),
        ("info@sample-service.gov.uk", "email", "mailto:info@sample-service.gov.uk"),
        ("07123456789", "number", "call 07123456789"),
    ],
)
def test_landing_page_has_supplier_contact_info(
    service_id,
    document_id,
    key,
    document_has_metadata_no_confirmation,
    client,
    mocker,
    contact_info,
    type,
    expected_result,
):
    service = {"name": "Sample Service", "contact_link": contact_info}
    mocker.patch("app.service_api_client.get_service", return_value={"data": service})

    response = client.get(
        url_for(
            "main.landing",
            service_id=service_id,
            document_id=document_id,
            key=key,
        )
    )

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    if type == "number":
        assert page.find_all(string=re.compile(expected_result))
    else:
        assert page.find_all(attrs={"href": expected_result})


def test_footer_doesnt_link_to_national_archives(
    service_id,
    document_id,
    key,
    document_has_metadata_no_confirmation,
    client,
    mocker,
):
    service = {"name": "Sample Service", "contact_link": "blah blah blah"}
    mocker.patch("app.service_api_client.get_service", return_value={"data": service})

    response = client.get(
        url_for(
            "main.landing",
            service_id=service_id,
            document_id=document_id,
            key=key,
        )
    )

    assert response.status_code == 200
    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")

    links = page.find_all("a")
    assert not any("nationalarchives.gov.uk" in a.attrs["href"] for a in links)

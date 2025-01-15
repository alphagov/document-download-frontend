from datetime import date, timedelta
from uuid import uuid4

import pytest
import requests_mock
from flask import Flask, current_app

from app import create_app, reset_memos


@pytest.fixture
def app_(request):
    app = Flask("app")
    create_app(app)

    reset_memos()
    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()
    reset_memos()


@pytest.fixture(scope="function")
def client(app_):
    with app_.test_request_context(), app_.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def sample_service():
    return {"name": "Sample Service", "contact_link": "https://sample-service.gov.uk"}


@pytest.fixture
def rmock():
    with requests_mock.mock() as rmock:
        yield rmock


@pytest.fixture
def service_id():
    return uuid4()


@pytest.fixture
def document_id():
    return uuid4()


@pytest.fixture
def key():
    return "1234"


@pytest.fixture
def document_has_metadata_no_confirmation(service_id, document_id, key, rmock, client):
    json_response = {
        "document": {
            "direct_file_url": "url",
            "confirm_email": False,
            "size_in_bytes": 712099,
            "file_extension": "txt",
            "available_until": str(date.today() + timedelta(days=5)),
        }
    }

    rmock.get(
        "{}/services/{}/documents/{}/check?key={}".format(
            current_app.config["DOCUMENT_DOWNLOAD_API_HOST_NAME_INTERNAL"], service_id, document_id, key
        ),
        json=json_response,
    )


@pytest.fixture
def document_has_metadata_requires_confirmation(service_id, document_id, key, rmock, client):
    json_response = {
        "document": {
            "direct_file_url": "url",
            "confirm_email": True,
            "size_in_bytes": 1923823,
            "file_extension": "pdf",
            "available_until": str(date.today() + timedelta(days=5)),
        }
    }

    rmock.get(
        "{}/services/{}/documents/{}/check?key={}".format(
            current_app.config["DOCUMENT_DOWNLOAD_API_HOST_NAME_INTERNAL"], service_id, document_id, key
        ),
        json=json_response,
    )


@pytest.fixture(scope="function")
def fake_nonce():
    return "TESTs5Vr8v3jgRYLoQuVwA"

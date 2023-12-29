import pytest
from flask import Flask

from app.config import Config


@pytest.mark.parametrize(
    ["api_host_name", "frontend_host_name", "expected_cookie_domain"],
    [
        # prod
        ("https://documents.download.service.gov.uk", "https://download.service.gov.uk", "download.service.gov.uk"),
        # notifications-local docker-compose
        (
            "http://api.document-download.localhost",
            "http://frontend.document-download.localhost",
            "document-download.localhost",
        ),
        # running locally outside of docker is no longer supported? :thinking_face:
        pytest.param(
            "http://localhost:7001", "http://localhost:7002", None, marks=pytest.mark.xfail(raises=ValueError)
        ),
    ],
)
def test_cookie_domain_set_correctly(api_host_name, frontend_host_name, expected_cookie_domain):
    conf = Config()
    conf.DOCUMENT_DOWNLOAD_API_HOST_NAME = api_host_name
    conf.DOCUMENT_DOWNLOAD_FRONTEND_HOST_NAME = frontend_host_name

    app = Flask("app")
    app.config.from_object(conf)

    assert app.config["COOKIE_DOMAIN"] == expected_cookie_domain

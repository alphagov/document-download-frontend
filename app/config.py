import os
from urllib.parse import urlparse


class Config:
    ADMIN_CLIENT_SECRET = os.environ.get("ADMIN_CLIENT_SECRET")
    ADMIN_CLIENT_USER_NAME = "notify-admin"
    SECRET_KEY = os.environ.get("SECRET_KEY")

    API_HOST_NAME = os.environ.get("API_HOST_NAME")
    NOTIFY_RUNTIME_PLATFORM = os.environ.get("NOTIFY_RUNTIME_PLATFORM", "paas")

    CHECK_PROXY_HEADER = False

    # Logging
    DEBUG = False

    DOCUMENT_DOWNLOAD_API_HOST_NAME = os.environ.get("DOCUMENT_DOWNLOAD_API_HOST_NAME")
    DOCUMENT_DOWNLOAD_API_HOST_NAME_INTERNAL = os.environ.get("DOCUMENT_DOWNLOAD_API_HOST_NAME_INTERNAL", "")
    DOCUMENT_DOWNLOAD_FRONTEND_HOST_NAME = os.environ.get("DOCUMENT_DOWNLOAD_FRONTEND_HOST_NAME", "")

    HEADER_COLOUR = "#FFBF47"  # $yellow
    HTTP_PROTOCOL = "http"

    ROUTE_SECRET_KEY_1 = os.environ.get("ROUTE_SECRET_KEY_1", "")

    # needs to refer to notify for utils
    NOTIFY_LOG_PATH = os.getenv("NOTIFY_LOG_PATH")

    @property
    def COOKIE_DOMAIN(self):
        # the cookie is set by the frontend, and read by the api. setting the domain attribute allows us to specify
        # a domain (settable to the current domain or any superdomain) - and importantly all pages on subdomains of
        # the cookie's domain can access that cookie.
        # docs: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#domain_attribute
        api_domain = urlparse(self.DOCUMENT_DOWNLOAD_API_HOST_NAME).netloc
        fe_domain = urlparse(self.DOCUMENT_DOWNLOAD_FRONTEND_HOST_NAME).netloc

        shared_domain = []
        for api_path, fe_path in zip(reversed(api_domain.split(".")), reversed(fe_domain.split("."))):
            if api_path != fe_path:
                break
            shared_domain.append(api_path)

        # shared_domain must be at least a website with a TLD `documents.service.gov.uk` or `notify.localhost`
        if len(shared_domain) < 2:
            raise ValueError(
                f"{self.DOCUMENT_DOWNLOAD_API_HOST_NAME=} and {self.DOCUMENT_DOWNLOAD_FRONTEND_HOST_NAME=} "
                "must have a valid shared domain to set cookie on"
            )

        return ".".join(reversed(shared_domain))


class Development(Config):
    SERVER_NAME = os.getenv("DOCUMENT_DOWNLOAD_FRONTEND_HOST_NAME")

    API_HOST_NAME = os.environ.get("API_HOST_NAME", "http://localhost:6011")

    # we dont need to distinguish between internal and external when running locally/in docker
    DOCUMENT_DOWNLOAD_API_HOST_NAME = os.environ.get("DOCUMENT_DOWNLOAD_API_HOST_NAME", "http://localhost:7000")
    DOCUMENT_DOWNLOAD_API_HOST_NAME_INTERNAL = os.environ.get(
        "DOCUMENT_DOWNLOAD_API_HOST_NAME", "http://localhost:7000"
    )
    DOCUMENT_DOWNLOAD_FRONTEND_HOST_NAME = os.environ.get(
        "DOCUMENT_DOWNLOAD_FRONTEND_HOST_NAME", "https://localhost:7001"
    )

    ADMIN_CLIENT_SECRET = "dev-notify-secret-key"
    SECRET_KEY = "dev-notify-secret-key"

    DEBUG = True
    NOTIFY_LOG_PATH = "application.log"

    NOTIFY_RUNTIME_PLATFORM = "local"


class Test(Development):
    TESTING = True
    WTF_CSRF_ENABLED = False

    # used during tests as a domain name
    SERVER_NAME = "document-download-frontend.gov"

    API_HOST_NAME = "http://test-notify-api"
    DOCUMENT_DOWNLOAD_API_HOST_NAME = "https://api.test-doc-download-api.gov.uk"
    DOCUMENT_DOWNLOAD_API_HOST_NAME_INTERNAL = "https://api-internal.test-doc-download-api-internal.gov.uk"
    DOCUMENT_DOWNLOAD_FRONTEND_HOST_NAME = "https://frontend.test-doc-download-api.gov.uk"

    NOTIFY_RUNTIME_PLATFORM = "test"


class Preview(Config):
    HTTP_PROTOCOL = "https"
    HEADER_COLOUR = "#F499BE"  # $baby-pink


class Staging(Config):
    HTTP_PROTOCOL = "https"
    HEADER_COLOUR = "#6F72AF"  # $mauve


class Production(Config):
    HEADER_COLOUR = "#005EA5"  # $govuk-blue
    HTTP_PROTOCOL = "https"


configs = {
    "development": Development(),
    "test": Test(),
    "preview": Preview(),
    "staging": Staging(),
    "production": Production(),
}

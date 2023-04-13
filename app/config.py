import os


class Config(object):
    # if we're not on cloudfoundry, we can get to this app from localhost. but on cloudfoundry its different
    ADMIN_CLIENT_SECRET = os.environ.get("ADMIN_CLIENT_SECRET")
    ADMIN_CLIENT_USER_NAME = "notify-admin"
    SECRET_KEY = os.environ.get("SECRET_KEY")

    API_HOST_NAME = os.environ.get("API_HOST_NAME")
    NOTIFY_RUNTIME_PLATFORM = os.environ.get("NOTIFY_RUNTIME_PLATFORM", "paas")

    CHECK_PROXY_HEADER = False

    # Logging
    DEBUG = False

    DOCUMENT_DOWNLOAD_API_HOST_NAME = os.environ.get("DOCUMENT_DOWNLOAD_API_HOST_NAME")

    HEADER_COLOUR = "#FFBF47"  # $yellow
    HTTP_PROTOCOL = "http"

    ROUTE_SECRET_KEY_1 = os.environ.get("ROUTE_SECRET_KEY_1", "")

    # needs to refer to notify for utils
    NOTIFY_LOG_PATH = os.getenv("NOTIFY_LOG_PATH")


class Development(Config):
    API_HOST_NAME = os.environ.get("API_HOST_NAME", "http://localhost:6011")
    DOCUMENT_DOWNLOAD_API_HOST_NAME = os.environ.get("DOCUMENT_DOWNLOAD_API_HOST_NAME", "http://localhost:7000")

    ADMIN_CLIENT_SECRET = "dev-notify-secret-key"
    SECRET_KEY = "dev-notify-secret-key"

    DEBUG = True
    NOTIFY_LOG_PATH = "application.log"


class Test(Development):
    TESTING = True
    WTF_CSRF_ENABLED = False

    # used during tests as a domain name
    SERVER_NAME = "document-download-frontend.gov"

    API_HOST_NAME = "http://test-notify-api"
    DOCUMENT_DOWNLOAD_API_HOST_NAME = "http://test-doc-download-api"


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
    "development": Development,
    "test": Test,
    "preview": Preview,
    "staging": Staging,
    "production": Production,
}

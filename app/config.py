import os


class Config:
    ADMIN_CLIENT_SECRET = os.environ.get("ADMIN_CLIENT_SECRET")
    ADMIN_CLIENT_USER_NAME = "notify-admin"
    SECRET_KEY = os.environ.get("SECRET_KEY")

    API_HOST_NAME = os.environ.get("API_HOST_NAME")

    # Logging
    DEBUG = False

    NOTIFY_REQUEST_LOG_LEVEL = os.getenv("NOTIFY_REQUEST_LOG_LEVEL", "INFO")

    DOCUMENT_DOWNLOAD_API_HOST_NAME = os.environ.get("DOCUMENT_DOWNLOAD_API_HOST_NAME")
    DOCUMENT_DOWNLOAD_API_HOST_NAME_INTERNAL = os.environ.get("DOCUMENT_DOWNLOAD_API_HOST_NAME_INTERNAL")

    HEADER_COLOUR = os.environ.get("HEADER_COLOUR", "#FFBF47")  # $yellow
    HTTP_PROTOCOL = os.environ.get("HTTP_PROTOCOL", "http")


class Development(Config):
    SERVER_NAME = os.getenv("SERVER_NAME")
    API_HOST_NAME = os.environ.get("API_HOST_NAME", "http://localhost:6011")
    DOCUMENT_DOWNLOAD_API_HOST_NAME = os.environ.get("DOCUMENT_DOWNLOAD_API_HOST_NAME", "http://localhost:7000")
    DOCUMENT_DOWNLOAD_API_HOST_NAME_INTERNAL = os.environ.get(
        "DOCUMENT_DOWNLOAD_API_HOST_NAME", "http://localhost:7000"
    )

    ADMIN_CLIENT_SECRET = "dev-notify-secret-key"
    SECRET_KEY = "dev-notify-secret-key"

    DEBUG = True


class Test(Development):
    TESTING = True
    WTF_CSRF_ENABLED = False

    # used during tests as a domain name
    SERVER_NAME = "document-download-frontend.gov"

    API_HOST_NAME = "http://test-notify-api"
    DOCUMENT_DOWNLOAD_API_HOST_NAME = "https://download.test-doc-download-api.gov.uk"
    DOCUMENT_DOWNLOAD_API_HOST_NAME_INTERNAL = "https://download.test-doc-download-api-internal.gov.uk"


configs = {
    "development": Development,
    "test": Test,
}

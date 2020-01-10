import os


class Config(object):
    # if we're not on cloudfoundry, we can get to this app from localhost. but on cloudfoundry its different
    ADMIN_BASE_URL = os.environ.get('ADMIN_BASE_URL', 'http://localhost:6012')
    ADMIN_CLIENT_SECRET = os.environ.get('ADMIN_CLIENT_SECRET')
    ADMIN_CLIENT_USER_NAME = 'notify-admin'

    API_HOST_NAME = os.environ.get('API_HOST_NAME')

    CHECK_PROXY_HEADER = False

    # Logging
    DEBUG = False

    DOCUMENT_DOWNLOAD_API_HOST_NAME = os.environ.get('DOCUMENT_DOWNLOAD_API_HOST_NAME')

    HEADER_COLOUR = '#FFBF47'  # $yellow
    HTTP_PROTOCOL = 'http'

    ROUTE_SECRET_KEY_1 = os.environ.get('ROUTE_SECRET_KEY_1', '')

    # needs to refer to notify for utils
    NOTIFY_LOG_PATH = '/home/vcap/logs/app.log'


class Development(Config):
    API_HOST_NAME = os.environ.get('API_HOST_NAME', 'http://localhost:6011')
    ADMIN_BASE_URL = os.environ.get('ADMIN_BASE_URL', 'http://localhost:6012')
    DOCUMENT_DOWNLOAD_API_HOST_NAME = os.environ.get('DOCUMENT_DOWNLOAD_API_HOST_NAME', 'http://localhost:7000')

    ADMIN_CLIENT_SECRET = 'dev-notify-secret-key'

    DEBUG = True
    NOTIFY_LOG_PATH = 'application.log'


class Test(Development):
    TESTING = True

    # used during tests as a domain name
    SERVER_NAME = 'document-download-frontend'

    API_HOST_NAME = 'http://test-notify-api'
    ADMIN_BASE_URL = 'http://test-notify-admin'
    DOCUMENT_DOWNLOAD_API_HOST_NAME = 'http://test-doc-download-api'


class Preview(Config):
    HTTP_PROTOCOL = 'https'
    HEADER_COLOUR = '#F499BE'  # $baby-pink


class Staging(Config):
    HTTP_PROTOCOL = 'https'
    HEADER_COLOUR = '#6F72AF'  # $mauve


class Production(Config):
    HEADER_COLOUR = '#005EA5'  # $govuk-blue
    HTTP_PROTOCOL = 'https'


configs = {
    'development': Development,
    'test': Test,
    'preview': Preview,
    'staging': Staging,
    'production': Production,
}

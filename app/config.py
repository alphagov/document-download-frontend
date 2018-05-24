import os


class Config(object):
    DOCUMENT_DOWNLOAD_API_HOST_NAME = os.environ.get('DOCUMENT_DOWNLOAD_API_HOST_NAME')

    # if we're not on cloudfoundry, we can get to this app from localhost. but on cloudfoundry its different
    ADMIN_BASE_URL = os.environ.get('ADMIN_BASE_URL', 'http://localhost:6012')

    # Logging
    DEBUG = False
    DOCUMENT_DOWNLOAD_LOG_PATH = os.getenv('DOCUMENT_DOWNLOAD_LOG_PATH')

    HEADER_COLOUR = '#FFBF47'  # $yellow
    HTTP_PROTOCOL = 'http'
    SHOW_STYLEGUIDE = True

    DOCUMENT_DOWNLOAD_ENVIRONMENT = 'development'
    CHECK_PROXY_HEADER = False

    NOTIFY_LOG_PATH = '/home/vcap/logs/app.log'


class Development(Config):
    DEBUG = False
    NOTIFY_LOG_PATH = 'application.log'


class Test(Development):
    TESTING = True
    DOCUMENT_DOWNLOAD_ENVIRONMENT = 'test'


class Preview(Config):
    HTTP_PROTOCOL = 'https'
    HEADER_COLOUR = '#F499BE'  # $baby-pink
    DOCUMENT_DOWNLOAD_ENVIRONMENT = 'preview'


class Staging(Config):
    HTTP_PROTOCOL = 'https'
    HEADER_COLOUR = '#6F72AF'  # $mauve
    DOCUMENT_DOWNLOAD_ENVIRONMENT = 'staging'


class Live(Config):
    HEADER_COLOUR = '#005EA5'  # $govuk-blue
    HTTP_PROTOCOL = 'https'
    DOCUMENT_DOWNLOAD_ENVIRONMENT = 'live'


configs = {
    'development': Development,
    'test': Test,
    'preview': Preview,
    'staging': Staging,
    'live': Live,
    'production': Live,
}

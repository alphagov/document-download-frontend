import os


class Config(object):
    # if we're not on cloudfoundry, we can get to this app from localhost. but on cloudfoundry its different
    ADMIN_BASE_URL = os.environ.get('ADMIN_BASE_URL', 'http://localhost:6012')
    ADMIN_CLIENT_SECRET = os.environ.get('ADMIN_CLIENT_SECRET')
    ADMIN_CLIENT_USER_NAME = 'notify-admin'

    API_HOST_NAME = os.environ.get('API_HOST_NAME')

    CHECK_PROXY_HEADER = False

    SECRET_KEY = os.environ.get('SECRET_KEY')
    DANGEROUS_SALT = os.environ.get('DANGEROUS_SALT')

    # Logging
    DEBUG = False

    DOCUMENT_DOWNLOAD_API_HOST_NAME = os.environ.get('DOCUMENT_DOWNLOAD_API_HOST_NAME')
    DOCUMENT_DOWNLOAD_ENVIRONMENT = 'development'
    DOCUMENT_DOWNLOAD_LOG_PATH = os.getenv('DOCUMENT_DOWNLOAD_LOG_PATH')

    HEADER_COLOUR = '#FFBF47'  # $yellow
    HTTP_PROTOCOL = 'http'

    ROUTE_SECRET_KEY_1 = os.environ.get('ROUTE_SECRET_KEY_1', '')

    SHOW_STYLEGUIDE = True

    NOTIFY_LOG_PATH = '/home/vcap/logs/app.log'


class Development(Config):
    DEBUG = True
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

import os

<<<<<<< HEAD
from flask import (
=======
import itertools
from flask import (
    session,
>>>>>>> initial build for document download
    render_template,
    make_response,
    current_app,
)
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError

<<<<<<< HEAD
=======
from notifications_python_client.errors import HTTPError
>>>>>>> initial build for document download
from notifications_utils import logging, request_helper
from notifications_utils.clients.statsd.statsd_client import StatsdClient

from app.config import configs
from app.asset_fingerprinter import AssetFingerprinter
from app.utils import get_cdn_domain

csrf = CSRFProtect()

statsd_client = StatsdClient()
asset_fingerprinter = AssetFingerprinter()


def create_app(application):

    notify_environment = os.environ['DOCUMENT_DOWNLOAD_ENVIRONMENT']

    application.config.from_object(configs[notify_environment])

    init_app(application)
    statsd_client.init_app(application)
    logging.init_app(application, statsd_client)
    csrf.init_app(application)
    request_helper.init_app(application)

    from app.main import main as main_blueprint
    application.register_blueprint(main_blueprint)

    # from .status import status as status_blueprint
    # application.register_blueprint(status_blueprint)

    # add_template_filters(application)

    register_errorhandlers(application)


def init_app(application):
    application.after_request(useful_headers_after_request)

    @application.context_processor
    def inject_global_template_variables():
        return {
            'asset_path': '/static/',
            'header_colour': application.config['HEADER_COLOUR'],
            'asset_url': asset_fingerprinter.get_url
        }


#  https://www.owasp.org/index.php/List_of_useful_HTTP_headers
def useful_headers_after_request(response):
    response.headers.add('X-Frame-Options', 'deny')
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('X-XSS-Protection', '1; mode=block')
    response.headers.add('Content-Security-Policy', (
        "default-src 'self' 'unsafe-inline';"
        "script-src 'self' *.google-analytics.com 'unsafe-inline' 'unsafe-eval' data:;"
        "connect-src 'self' *.google-analytics.com;"
        "object-src 'self';"
        "font-src 'self' data:;"
        "img-src 'self' *.google-analytics.com *.notifications.service.gov.uk {} data:;"
        "frame-src www.youtube.com;".format(get_cdn_domain())
    ))
    if 'Cache-Control' in response.headers:
        del response.headers['Cache-Control']
    response.headers.add(
        'Cache-Control', 'no-store, no-cache, private, must-revalidate')
    return response


def register_errorhandlers(application):  # noqa (C901 too complex)
    def _error_response(error_code):
        resp = make_response(render_template("error/{0}.html".format(error_code)), error_code)
        return useful_headers_after_request(resp)

    @application.errorhandler(410)
    @application.errorhandler(404)
    @application.errorhandler(403)
    @application.errorhandler(401)
    def handle_http_error(error):
        return _error_response(error.code)

    @application.errorhandler(CSRFError)
    def handle_csrf(reason):
        application.logger.warning('csrf.error_message: {}'.format(reason))

        resp = make_response(render_template(
            "error/400.html",
            message=['Something went wrong, please go back and try again.']
        ), 400)
        return useful_headers_after_request(resp)

    @application.errorhandler(500)
    @application.errorhandler(Exception)
    def handle_bad_request(error):
        current_app.logger.exception(error)
        # We want the Flask in browser stacktrace
        if current_app.config.get('DEBUG', None):
            raise error
        return _error_response(500)

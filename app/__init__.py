import os
from functools import partial

import jinja2
from flask import current_app, make_response, render_template
from flask.globals import _lookup_req_object
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from govuk_frontend_jinja.flask_ext import init_govuk_frontend
from notifications_utils import logging, request_helper
from notifications_utils.base64_uuid import base64_to_uuid, uuid_to_base64
from notifications_utils.clients.statsd.statsd_client import StatsdClient
from werkzeug.local import LocalProxy
from werkzeug.routing import BaseConverter, ValidationError

from app.asset_fingerprinter import AssetFingerprinter
from app.config import configs
from app.notify_client.service_api_client import ServiceApiClient
from app.utils import get_cdn_domain

csrf = CSRFProtect()

statsd_client = StatsdClient()
asset_fingerprinter = AssetFingerprinter()
service_api_client = ServiceApiClient()

# The current service attached to the request stack.
current_service = LocalProxy(partial(_lookup_req_object, 'service'))


class Base64UUIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return base64_to_uuid(value)
        except ValueError:
            raise ValidationError()

    def to_url(self, value):
        try:
            return uuid_to_base64(value)
        except Exception:
            raise ValidationError()


def create_app(application):
    application.config.from_object(configs[application.env])

    application.url_map.converters['base64_uuid'] = Base64UUIDConverter

    init_app(application)
    init_govuk_frontend(application)
    init_jinja(application)
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

    service_api_client.init_app(application)


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
    response.headers.add('X-Robots-Tag', 'noindex, nofollow')
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
        return make_response(render_template("error/{0}.html".format(error_code)), error_code)

    @application.errorhandler(410)
    @application.errorhandler(404)
    @application.errorhandler(403)
    @application.errorhandler(401)
    @application.errorhandler(400)
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


def init_jinja(application):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_folders = [
        os.path.join(repo_root, 'app/templates'),
        os.path.join(repo_root, 'app/templates/vendor/govuk_frontend'),
    ]
    jinja_loader = jinja2.FileSystemLoader(template_folders)
    application.jinja_loader = jinja_loader

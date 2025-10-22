import os
import secrets
from collections.abc import Callable
from contextvars import ContextVar

import jinja2
from flask import current_app, make_response, render_template, request
from flask_wtf.csrf import CSRFError
from gds_metrics import GDSMetrics
from notifications_utils import request_helper
from notifications_utils.asset_fingerprinter import asset_fingerprinter
from notifications_utils.base64_uuid import base64_to_uuid, uuid_to_base64
from notifications_utils.clients.statsd.statsd_client import StatsdClient
from notifications_utils.eventlet import EventletTimeout
from notifications_utils.local_vars import LazyLocalGetter
from notifications_utils.logging import flask as utils_logging
from werkzeug.local import LocalProxy
from werkzeug.routing import BaseConverter, ValidationError

from app.config import Config, configs
from app.notify_client.service_api_client import ServiceApiClient

metrics = GDSMetrics()
statsd_client = StatsdClient()

memo_resetters: list[Callable] = []

#
# "clients" that need thread-local copies
#

_service_api_client_context_var: ContextVar[ServiceApiClient] = ContextVar("service_api_client")
get_service_api_client: LazyLocalGetter[ServiceApiClient] = LazyLocalGetter(
    _service_api_client_context_var,
    lambda: ServiceApiClient(app=current_app),
)
memo_resetters.append(lambda: get_service_api_client.clear())
service_api_client = LocalProxy(get_service_api_client)


class Base64UUIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return base64_to_uuid(value)
        except ValueError as e:
            raise ValidationError from e

    def to_url(self, value):
        try:
            return uuid_to_base64(value)
        except Exception as e:
            raise ValidationError from e


def create_app(application):
    notify_environment = os.environ["NOTIFY_ENVIRONMENT"]
    if notify_environment in configs:
        application.config.from_object(configs[notify_environment])
    else:
        application.config.from_object(Config)

    application.url_map.converters["base64_uuid"] = Base64UUIDConverter

    init_app(application)
    # Metrics intentionally high up to give the most accurate timing and reliability that the metric is recorded
    metrics.init_app(application)
    init_jinja(application)
    statsd_client.init_app(application)
    utils_logging.init_app(application, statsd_client)
    request_helper.init_app(application)

    from app.main import main as main_blueprint

    application.register_blueprint(main_blueprint)

    # from .status import status as status_blueprint
    # application.register_blueprint(status_blueprint)

    # add_template_filters(application)

    register_errorhandlers(application)


def init_app(application):
    application.after_request(useful_headers_after_request)

    application.before_request(make_nonce_before_request)

    @application.context_processor
    def inject_global_template_variables():
        return {
            "asset_path": "/static/",
            "header_colour": application.config["HEADER_COLOUR"],
            "asset_url": asset_fingerprinter.get_url,
        }


def reset_memos():
    """
    Reset all memos registered in memo_resetters
    """
    for resetter in memo_resetters:
        resetter()


def make_nonce_before_request():
    # `govuk_frontend_jinja/template.html` can be extended and inline `<script>` can be added without CSP complaining
    if not getattr(request, "csp_nonce", None):
        request.csp_nonce = secrets.token_urlsafe(16)


#  https://www.owasp.org/index.php/List_of_useful_HTTP_headers
def useful_headers_after_request(response):
    response.headers.add("X-Robots-Tag", "noindex, nofollow")
    response.headers.add("X-Frame-Options", "deny")
    response.headers.add("X-Content-Type-Options", "nosniff")
    response.headers.add("X-XSS-Protection", "1; mode=block")
    response.headers.add("Referrer-Policy", "no-referrer")
    response.headers.add(
        "Content-Security-Policy",
        (
            "default-src 'self';"
            "script-src 'self' 'nonce-{csp_nonce}';"
            "connect-src 'self';"
            "object-src 'self';"
            "font-src 'self' data:;"
            "img-src 'self' data:;"
            "style-src 'self' 'nonce-{csp_nonce}';"
            "frame-ancestors 'self';"
            "frame-src 'self';".format(
                csp_nonce=getattr(request, "csp_nonce", ""),
            )
        ),
    )
    if "Cache-Control" in response.headers:
        del response.headers["Cache-Control"]
    response.headers.add("Cache-Control", "no-store, no-cache, private, must-revalidate")

    response.headers.add("Strict-Transport-Security", "max-age=31536000; preload")
    response.headers.add("Cross-Origin-Embedder-Policy", "require-corp;")
    response.headers.add("Cross-Origin-Opener-Policy", "same-origin;")
    response.headers.add("Cross-Origin-Resource-Policy", "same-origin;")
    response.headers.add(
        "Permissions-Policy",
        "geolocation=(), microphone=(), camera=(), autoplay=(), payment=(), sync-xhr=()",
    )
    response.headers.add("Server", "Cloudfront")
    return response


def register_errorhandlers(application):
    def _error_response(error_code, error_page_template=None):
        if not error_page_template:
            error_page_template = error_code

        return make_response(render_template(f"error/{error_page_template}.html"), error_code)

    @application.errorhandler(410)
    @application.errorhandler(404)
    @application.errorhandler(403)
    @application.errorhandler(401)
    @application.errorhandler(400)
    def handle_http_error(error):
        return _error_response(error.code)

    @application.errorhandler(500)
    @application.errorhandler(Exception)
    def handle_bad_request(error):
        current_app.logger.exception(error)
        # We want the Flask in browser stacktrace
        if current_app.config.get("DEBUG", None):
            raise error
        return _error_response(500)

    @application.errorhandler(CSRFError)
    def handle_csrf(reason):
        application.logger.warning("CSRF error message: %s", reason)

        return _error_response(400, error_page_template=500)

    @application.errorhandler(EventletTimeout)
    def eventlet_timeout(error):
        application.logger.exception(error)
        return _error_response(504, error_page_template=500)


def init_jinja(application):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_folders = [os.path.join(repo_root, "app/templates")]
    jinja_loader = jinja2.ChoiceLoader(
        [
            jinja2.FileSystemLoader(template_folders),
            jinja2.PrefixLoader({"govuk_frontend_jinja": jinja2.PackageLoader("govuk_frontend_jinja")}),
        ]
    )
    application.jinja_loader = jinja_loader
    application.jinja_env.undefined = jinja2.Undefined

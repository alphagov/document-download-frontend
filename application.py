import os

from notifications_utils import greenlet as utils_greenlet

from app.performance import init_performance_monitoring

init_performance_monitoring()

import os  # noqa

from flask import Flask  # noqa
from whitenoise import WhiteNoise  # noqa

from app import create_app  # noqa

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, "app", "static")
STATIC_URL = "static/"

application = Flask("app")

create_app(application)
application.wsgi_app = WhiteNoise(application.wsgi_app, STATIC_ROOT, STATIC_URL)

if utils_greenlet.using_eventlet or utils_greenlet.using_gevent:
    application.wsgi_app = utils_greenlet.RequestHandlingTimeoutMiddleware(
        application.wsgi_app,
        timeout_seconds=int(os.getenv("HTTP_SERVE_TIMEOUT_SECONDS", 30)),
    )

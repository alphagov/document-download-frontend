import os

from app.performance import init_performance_monitoring

init_performance_monitoring()

import os  # noqa

from flask import Flask  # noqa
from whitenoise import WhiteNoise  # noqa

from app import create_app  # noqa

from notifications_utils.eventlet import EventletTimeoutMiddleware, using_eventlet  # noqa

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, "app", "static")
STATIC_URL = "static/"

application = Flask("app")

create_app(application)
application.wsgi_app = WhiteNoise(application.wsgi_app, STATIC_ROOT, STATIC_URL)

if using_eventlet:
    application.wsgi_app = EventletTimeoutMiddleware(
        application.wsgi_app,
        timeout_seconds=int(os.getenv("HTTP_SERVE_TIMEOUT_SECONDS", 30)),
    )

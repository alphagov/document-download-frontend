from flask import Blueprint

main = Blueprint('main', __name__)  # noqa

from app.main.views import (  # noqa
    index
)

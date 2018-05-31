import pytest
from flask import Flask

from app import create_app


@pytest.fixture
def app_(request):
    app = Flask('app')
    create_app(app)

    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture(scope='function')
def client(app_):
    with app_.test_request_context(), app_.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def sample_service():
    return {'name': 'Sample Service'}

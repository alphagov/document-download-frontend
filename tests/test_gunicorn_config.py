from gunicorn_config import keepalive, timeout, worker_class, worker_connections, workers


def test_gunicorn_config():
    assert workers == 10
    assert worker_class == "eventlet"
    assert worker_connections == 1000
    assert keepalive == 90
    assert timeout == 30

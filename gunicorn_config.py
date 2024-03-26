from notifications_utils.gunicorn_defaults import set_gunicorn_defaults

set_gunicorn_defaults(globals())


workers = 10
worker_class = "eventlet"
worker_connections = 1000
keepalive = 90

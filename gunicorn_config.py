import os

import gunicorn

workers = 10
worker_class = "eventlet"
worker_connections = 1000
bind = "0.0.0.0:{}".format(os.getenv("PORT"))
errorlog = "/home/vcap/logs/gunicorn_error.log"
gunicorn.SERVER_SOFTWARE = "None"
keepalive = 90

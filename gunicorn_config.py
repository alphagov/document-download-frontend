import os

bind = "0.0.0.0:{}".format(os.getenv("PORT"))

workers = 10

worker_class = "eventlet"
worker_connections = 1000

errorlog = "/home/vcap/logs/gunicorn_error.log"
disable_redirect_access_to_syslog = True

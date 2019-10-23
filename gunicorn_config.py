import os
import gunicorn

bind = "0.0.0.0:{}".format(os.getenv("PORT"))

workers = 10

worker_class = "eventlet"
worker_connections = 1000

errorlog = "/home/vcap/logs/gunicorn_error.log"
gunicorn.SERVER_SOFTWARE = 'None'

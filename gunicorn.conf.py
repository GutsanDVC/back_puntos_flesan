"""Configuración de Gunicorn para FastAPI"""

import multiprocessing
import os

# Configuración del servidor
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = os.getenv("SERVER_PORT", "8001")
WORKERS = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))

bind = f"{SERVER_HOST}:{SERVER_PORT}"
workers = WORKERS
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Configuración de logs
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración de proceso
user = "www-data"
group = "www-data"
tmp_upload_dir = None
keepalive = 5
timeout = 120
graceful_timeout = 30

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configuración de desarrollo (cambiar en producción)
reload = False
preload_app = True

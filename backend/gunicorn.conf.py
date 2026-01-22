"""
Gunicorn configuration file for production deployment
"""
import multiprocessing
import os

# Server Socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
graceful_timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests_per_child = 1000

# Logging
accesslog = "/var/log/docgen/gunicorn-access.log"
errorlog = "/var/log/docgen/gunicorn-error.log"
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True

# Process naming
proc_name = "docgen-backend"

# Server mechanics
daemon = False
pidfile = "/var/run/docgen-gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if not using Nginx for SSL termination)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment variables
raw_env = [
    "PYTHONPATH=/home/docgen/backend",
]

# Pre-load application for better performance
preload_app = True

# Enable reloading in development
reload = os.environ.get("APP_ENV") == "development"

# StatsD integration (optional)
# statsd_host = "localhost:8125"
# statsd_prefix = "docgen"
"""
Gunicorn configuration file for production deployment on Hostinger VPS
"""
import multiprocessing
import os

# Server Socket
bind = "127.0.0.1:8000"  # Only listen on localhost, Nginx will proxy
backlog = 2048

# Worker Processes
# Recommended: (2 x CPU cores) + 1
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
daemon = False  # Managed by systemd
pidfile = "/var/run/docgen/gunicorn.pid"
user = None  # Will be set by systemd
group = None  # Will be set by systemd
tmp_upload_dir = "/tmp/docgen-uploads"

# SSL (handled by Nginx)
# keyfile = None
# certfile = None

# Environment variables
raw_env = [
    "PYTHONPATH=/home/docgen/backend",
    "APP_ENV=production",
]

# Pre-load application for better performance
preload_app = True

# Disable reload in production
reload = False

# StatsD integration (optional - uncomment if using monitoring)
# statsd_host = "localhost:8125"
# statsd_prefix = "docgen"

# Worker timeout handling
worker_tmp_dir = "/dev/shm"  # Use RAM for better performance

# Thread pools for async workers
threads = 4

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
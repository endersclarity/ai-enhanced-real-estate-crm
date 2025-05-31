# Gunicorn Configuration for Production Deployment
# AI-Enhanced Real Estate CRM

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Application
module = "deployment.production_app:app"
pythonpath = "/var/www/narissa-realty-crm"

# Logging
accesslog = "/var/log/narissa-realty-crm/access.log"
errorlog = "/var/log/narissa-realty-crm/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "narissa-realty-crm"

# Server mechanics
daemon = False
pidfile = "/var/run/narissa-realty-crm.pid"
user = "crm-app"
group = "www-data"
tmp_upload_dir = None

# SSL (will be handled by Nginx reverse proxy)
# keyfile = None
# certfile = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance tuning
preload_app = True  # Load application code before forking worker processes
sendfile = True     # Use sendfile() for static files

# Worker tmp directory
worker_tmp_dir = "/dev/shm"  # Use RAM filesystem for temporary files

# Environment variables for production
raw_env = [
    'FLASK_ENV=production',
    'FLASK_APP=deployment.production_app:app',
    'DATABASE_URL=postgresql://crm_app:CRM_App_2025_Secure!@db-narissa-realty-crm-prod.db.ondigitalocean.com:25060/narissa_realty_crm?sslmode=require',
    'REDIS_URL=redis://localhost:6379/0',
    'SECRET_KEY=CRM_Prod_Secret_2025_Ultra_Secure_Key!',
]

# Restart worker after handling this many requests
max_requests = 1000

# Restart worker after this much random jitter
max_requests_jitter = 100

# Kill and restart workers after this many seconds
timeout = 60

# Workers silent for more than this many seconds are killed and restarted
graceful_timeout = 30

# Time to wait for workers to finish current requests before killing
graceful_timeout = 30

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Narissa Realty CRM server is ready. Listening on: %s", server.address)

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker %s received SIGINT/SIGQUIT", worker.pid)

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker aborted (pid: %s)", worker.pid)
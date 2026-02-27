#!/bin/bash
# Start script for production
# Uses gunicorn with uvicorn workers for high concurrency

# Default to 4 workers (adjust based on CPU cores, e.g., 2 x cores + 1)
# You can override this by setting the WORKERS environment variable
WORKERS=${WORKERS:-4}
PORT=${PORT:-16384}
HOST=${HOST:-0.0.0.0}

# Add current directory to PYTHONPATH to ensure bit_login can be imported
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "Starting BIT Login Server with $WORKERS workers on $HOST:$PORT..."

# Exec gunicorn to replace the shell process
exec gunicorn server:app \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind $HOST:$PORT \
    --access-logfile - \
    --error-logfile - \
    --log-level info

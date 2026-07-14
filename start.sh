#!/bin/sh
set -e
export PORT="${PORT:-8000}"
echo "PORT=$PORT"
echo "Running migrations..."
python manage.py migrate --run-syncdb
echo "Starting gunicorn on 0.0.0.0:$PORT"
exec gunicorn onestep.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers 1 \
    --timeout 120 \
    --log-level info

#!/bin/sh
set -e
PORT=${PORT:-8000}
echo "Starting server on port $PORT"
python manage.py migrate --run-syncdb
exec gunicorn moiat_plan_50.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers 1 \
    --timeout 120 \
    --log-level info

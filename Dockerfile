FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN SECRET_KEY=build-only-dummy-key python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["/bin/sh", "-c", "python manage.py migrate --run-syncdb && gunicorn moiat_plan_50.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120 --log-level debug"]

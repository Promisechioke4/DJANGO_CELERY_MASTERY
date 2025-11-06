#!/bin/sh

echo "Apply database migrations"
python manage.py migrate

echo "Starting Django + Celery..."
# Start Django in background
python manage.py runserver 0.0.0.0:8000 &

# Start Celery worker
celery -A chatapp worker -l info -E

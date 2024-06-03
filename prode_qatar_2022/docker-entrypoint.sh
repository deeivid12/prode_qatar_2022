#!/bin/sh

set -e

if [ "$ENVIRONMENT" = "DEV" ]; then
  echo 'Running in development mode...'
  exec python manage.py runserver 0.0.0.0:8000
else
  echo 'Running collectstatic...'
  python manage.py collectstatic --no-input

  echo 'Applying migrations...'
  python manage.py wait_for_db
  python manage.py migrate

  echo 'Running server...'
  exec gunicorn prode_qatar_2022.wsgi:application --bind 0.0.0.0:$PORT
fi
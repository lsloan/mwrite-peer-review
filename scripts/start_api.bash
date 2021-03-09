#!/usr/bin/env bash

set -x

GUNICORN_WORKERS="${GUNICORN_WORKERS:-4}"
GUNICORN_PORT=8000
GUNICORN_WORKER_TIMEOUT=${GUNICORN_WORKER_TIMEOUT-30}
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-mwrite_peer_review.settings.api}"

read DB_HOST DB_PORT < <(echo $(jq -r '.HOST, .PORT' ${MPR_DB_CONFIG_PATH}))

echo "Waiting for DB (${DB_HOST}:${DB_PORT})..."
while ! nc -z "${DB_HOST}" "${DB_PORT}"; do
  sleep 1 # wait 1 sec., then check again
done
echo 'DB ready.'

echo 'Applying Django migrations...'
python manage.py migrate
echo 'Django migrations complete.'

gunicorn \
    --workers="$GUNICORN_WORKERS"        \
    --bind=0.0.0.0:"$GUNICORN_PORT"      \
    --timeout="$GUNICORN_WORKER_TIMEOUT" \
    mwrite_peer_review.wsgi:application

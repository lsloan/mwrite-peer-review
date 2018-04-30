#!/usr/bin/env bash

set -x

GUNICORN_WORKERS="${GUNICORN_WORKERS:-4}"
GUNICORN_PORT=8000
GUNICORN_WORKER_TIMEOUT=${GUNICORN_WORKER_TIMEOUT-30}
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-mwrite_peer_review.settings.api}"

gunicorn \
    --workers="$GUNICORN_WORKERS"        \
    --bind=0.0.0.0:"$GUNICORN_PORT"      \
    --timeout="$GUNICORN_WORKER_TIMEOUT" \
    mwrite_peer_review.wsgi:application

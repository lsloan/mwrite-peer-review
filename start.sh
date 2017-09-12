#!/usr/bin/env bash

GUNICORN_WORKERS="${GUNICORN_WORKERS:-4}"
GUNICORN_PORT=8000

printenv >> /etc/environment

set -x

cron

gunicorn \
    --workers="$GUNICORN_WORKERS" \
    --bind=0.0.0.0:"$GUNICORN_PORT" \
    mwrite_peer_review.wsgi:application

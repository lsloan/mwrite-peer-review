#!/usr/bin/env bash

GUNICORN_WORKERS=1
GUNICORN_PORT=8000

env > /root/mwrite-peer-review-env.sh

set -x

gunicorn \
    --workers="$GUNICORN_WORKERS" \
    --bind=0.0.0.0:"$GUNICORN_PORT" \
    mwrite_peer_review.wsgi:application

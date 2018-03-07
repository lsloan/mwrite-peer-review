#!/usr/bin/env bash

LAST_DIR=$(pwd)
cd /usr/src/app

source /etc/environment
DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-mwrite_peer_review.settings.api}"
python manage.py distribute_reviews

cd ${LAST_DIR}

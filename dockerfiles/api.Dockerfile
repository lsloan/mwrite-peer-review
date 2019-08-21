FROM python:3.6-alpine3.7
ARG MPR_WORKING_DIRECTORY=/usr/src/app

COPY requirements.txt /tmp/requirements.txt

# Build-time dependencies are all in a single RUN
# command so that useless layers aren't persisted.
RUN apk --no-cache --virtual build-deps add --update build-base                       && \
    apk --no-cache add --update mariadb-dev libffi-dev libxml2-dev libxslt-dev bash

# Run pip separate from the base build incase this changes
RUN pip --no-cache-dir install -r /tmp/requirements.txt && \
    pip --no-cache-dir install gunicorn

# Cleanup
RUN apk --no-cache del build-deps

# Set up the directory afterward, doing this before invalidates the previous cache

RUN mkdir -p $MPR_WORKING_DIRECTORY
WORKDIR $MPR_WORKING_DIRECTORY
COPY . $MPR_WORKING_DIRECTORY

EXPOSE 8000
CMD scripts/start_api.bash

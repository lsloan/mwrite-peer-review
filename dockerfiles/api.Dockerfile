FROM python:3.6-alpine
ARG MPR_WORKING_DIRECTORY=/usr/src/app

RUN mkdir -p $MPR_WORKING_DIRECTORY
COPY ./ $MPR_WORKING_DIRECTORY
WORKDIR $MPR_WORKING_DIRECTORY

# Build-time dependencies are all in a single RUN
# command so that useless layers aren't persisted.
RUN apk --no-cache --virtual build-deps add --update build-base                       && \
    apk --no-cache add --update mariadb-dev libffi-dev libxml2-dev libxslt-dev bash   && \
    pip --no-cache-dir install -r requirements.txt                                    && \
    apk --no-cache del build-deps
RUN pip --no-cache-dir install gunicorn

EXPOSE 8000
CMD scripts/start_api.bash

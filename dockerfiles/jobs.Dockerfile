FROM python:3-alpine
ARG MPR_WORKING_DIRECTORY=/usr/src/app

RUN mkdir -p $MPR_WORKING_DIRECTORY
COPY ./ $MPR_WORKING_DIRECTORY
WORKDIR $MPR_WORKING_DIRECTORY

# Build-time dependencies are all in a single RUN
# command so that useless layers aren't persisted.
RUN apk --no-cache --virtual build-deps add --update                   \
        build-base mariadb-dev libffi-dev libxml2-dev libxslt-dev   && \
    pip --no-cache-dir install -r requirements.txt                  && \
    apk --no-cache del build-deps
RUN pip --no-cache-dir install gunicorn
RUN apk --no-cache add bash

ADD ../scripts/distribute_reviews.bash /etc/periodic/15min
RUN chmod 0500 /etc/periodic/15min/distribute_reviews.bash

CMD ./scripts/start_jobs.bash


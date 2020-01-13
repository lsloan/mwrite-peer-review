FROM python:3.6-alpine3.7
ARG MPR_WORKING_DIRECTORY=/usr/src/app

# Build-time dependencies are all in a single RUN command so that useless layers aren't persisted.
RUN apk --no-cache --virtual build-deps add --update build-base                                      && \
    apk --no-cache add --update mariadb-dev mysql-client libffi-dev libxml2-dev libxslt-dev bash jq

# Run pip separate from the base build
COPY requirements.txt /tmp/requirements.txt
RUN pip --no-cache-dir install -r /tmp/requirements.txt && \
    pip --no-cache-dir install awscli

# Cleanup
RUN apk --no-cache del build-deps

# Set up the directory afterward, doing this before invalidates the previous cache
RUN mkdir -p $MPR_WORKING_DIRECTORY
WORKDIR $MPR_WORKING_DIRECTORY
COPY . $MPR_WORKING_DIRECTORY
COPY scripts/distribute_reviews.bash /etc/periodic/15min
COPY scripts/backup_data.bash /etc/periodic/daily
RUN chmod ugo=rx /etc/periodic/15min/distribute_reviews.bash
RUN chmod ugo=rx /etc/periodic/daily/backup_data.bash
RUN mv /etc/periodic/15min/distribute_reviews.bash /etc/periodic/15min/distribute_reviews   # otherwise run-parts refuses to run this
RUN mv /etc/periodic/daily/backup_data.bash /etc/periodic/weekly/backup_data                # otherwise run-parts refuses to run this

# Set up credentials for backup_data job
RUN mkdir /root/.aws && ln -s /etc/mwrite-peer-review/aws_credentials /root/.aws/credentials

# Save build environment variables for use at runtime
RUN touch /etc/environment
RUN chmod g+w /etc/environment
CMD scripts/start_jobs.bash

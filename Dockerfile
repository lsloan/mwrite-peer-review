FROM python:3.6

RUN apt-get update && \
    apt-get --no-install-recommends upgrade --yes && \
    apt-get --no-install-recommends install mysql-client cron --yes

ADD crontab /etc/cron.d/mwrite-peer-review
RUN chmod 0644 /etc/cron.d/mwrite-peer-review

RUN mkdir -p /tmp/mwrite-peer-review-build
WORKDIR /tmp/mwrite-peer-review-build

RUN pip install gunicorn
COPY requirements.txt /tmp/mwrite-peer-review-build
RUN pip install -r requirements.txt

RUN mkdir -p /usr/src/app
COPY . /usr/src/app

WORKDIR /usr/src/app
EXPOSE 8000
CMD cron && ./start.sh

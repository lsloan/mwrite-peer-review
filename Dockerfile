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

# TODO long term, make a "management" settings file and pass it to collectstatic
ENV MWRITE_PEER_REVIEW_SECRET_KEY_PATH /dev/null
ENV MWRITE_PEER_REVIEW_APP_HOST build
ENV MWRITE_PEER_REVIEW_LTI_CREDENTIALS_PATH /dev/null
ENV MWRITE_PEER_REVIEW_LANDING_ROUTE build
ENV MWRITE_PEER_REVIEW_CANVAS_API_URL BUILD
ENV MWRITE_PEER_REVIEW_CANVAS_API_TOKEN BUILD
ENV MWRITE_PEER_REVIEW_LMS_URL build
ENV MWRITE_PEER_REVIEW_DATABASE_CONFIG_PATH /dev/null
ENV MWRITE_PEER_REVIEW_TIMEZONE America/Detroit

RUN python manage.py collectstatic

EXPOSE 8000
CMD ./start.sh

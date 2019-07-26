FROM httpd:2.4-alpine
ARG MPR_API_URL

# TODO can we remove npm stuff afterwards, or should this be done in CI?
RUN mkdir -p /tmp/build
COPY ./ /tmp/build
WORKDIR /tmp/build

# Build-time dependencies are all in a single RUN
# command so that useless layers aren't persisted.
RUN apk --no-cache --virtual build-deps add --update nodejs nodejs-npm   && \
    npm install                                                          && \
    npm run build                                                        && \
    cp -Rv /tmp/build/dist/* /usr/local/apache2/htdocs                   && \
    rm -rf /tmp/build                                                    && \
    apk --no-cache del build-deps

EXPOSE 8080

RUN chown -R root:root /usr/local/apache2/logs /var/lock /var/run/lock

RUN chmod 777 /usr/local/apache2/conf /usr/local/apache2/conf/extra

RUN chmod g+rw /usr/local/apache2 /usr/local/apache2/logs /usr/local/apache2/htdocs \
        /var/lock /var/run/lock

WORKDIR $HTTPD_PREFIX

RUN chmod +x /tmp/build/scripts/start_frontend.bash
CMD /tmp/build/scripts/start_frontend.bash

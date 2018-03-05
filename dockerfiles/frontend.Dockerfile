FROM httpd:alpine

# TODO can we remove npm stuff afterwards, or should this be done in CI?

RUN apk add --update nodejs nodejs-npm

RUN mkdir -p /tmp/build
COPY ../ /tmp/build
WORKDIR /tmp/build

RUN npm install
RUN npm run build
RUN cp -Rv /tmp/build/dist/* /usr/local/apache2/htdocs/

WORKDIR $HTTPD_PREFIX
RUN rm -rf /tmp/build

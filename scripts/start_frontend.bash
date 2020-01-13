#!/usr/bin/env bash

set -x

# link apache httpd configuration files from mounted secret/configmap
if [ -f /mnt/apache2/httpd.conf ];
then
  ln -sf /mnt/apache2/httpd.conf /usr/local/apache2/conf/httpd.conf
fi

if [ -f /mnt/apache2/httpd-cosign.conf ];
then
  ln -sf /mnt/apache2/httpd-cosign.conf /usr/local/apache2/conf/extra/httpd-cosign.conf
fi

if [ -f /mnt/apache2/httpd-ssl.conf ];
then
  ln -sf /mnt/apache2/httpd-ssl.conf /usr/local/apache2/conf/extra/httpd-ssl.conf
fi

if [ -f /mnt/apache2/httpd-site.conf ];
then
  ln -sf /mnt/apache2/httpd-site.conf /usr/local/apache2/conf/extra/httpd-site.conf
fi

# copy cert/key from secret volume to a location that can be written to.
if [ -e /mnt/ssl ];
then
  cp /mnt/ssl/* /usr/local/apache2/certs/
fi

#
# If it exists, include cms.start.sh
#
if [ -f /usr/local/bin/cms.start.sh ]
then
  /bin/sh /usr/local/bin/cms.start.sh
fi

#
# If it exists, include app.start.sh
#
if [ -f /usr/local/bin/app.start.sh ]
then
  /bin/sh /usr/local/bin/app.start.sh
fi

# If it exists, include local.start.sh
if [ -f /mnt/local/local.start.sh ]
then
  /bin/sh /mnt/local/local.start.sh
fi

# Redirect logs to stdout and stderr for docker reasons.
ln -sf /dev/stdout /usr/local/apache2/logs/access_log
ln -sf /dev/stderr /usr/local/apache2/logs/error_log

/usr/local/apache2/bin/httpd -DFOREGROUND

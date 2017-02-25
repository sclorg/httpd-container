#!/bin/bash

sed -i -f /opt/app-root/httpdconf.sed /opt/rh/httpd24/root/etc/httpd/conf/httpd.conf && \
sed -i -f /opt/app-root/sslconf.sed /opt/rh/httpd24/root/etc/httpd/conf.d/ssl.conf && \
sed -ri ' s!^(\s*CustomLog)\s+\S+!\1 |/usr/bin/cat!g; s!^(\s*ErrorLog)\s+\S+!\1 |/usr/bin/cat!g;' /opt/rh/httpd24/root/etc/httpd/conf/httpd.conf && \
sed -ri ' s!^(\s*CustomLog)\s+\S+!\1 |/usr/bin/cat!g; s!^(\s*TransferLog)\s+\S+!\1 |/usr/bin/cat!g; s!^(\s*ErrorLog)\s+\S+!\1 |/usr/bin/cat!g;' /opt/rh/httpd24/root/etc/httpd/conf.d/ssl.conf

# Check whether we run as s2i
echo "$@" | grep --quiet "$STI_SCRIPTS_PATH"
if [ $? -ne 0 -a "$(id -u)" == "0" ]; then

  # Change the s2i permissions back to the normal ones
  chmod 644 /opt/rh/httpd24/root/etc/httpd/conf/* && \
  chmod 755 /opt/rh/httpd24/root/etc/httpd/conf && \
  chmod 644 /opt/rh/httpd24/root/etc/httpd/conf.d/* && \
  chmod 755 /opt/rh/httpd24/root/etc/httpd/conf.d && \
  chmod 600 /etc/pki/tls/certs/localhost.crt && \
  chmod 600 /etc/pki/tls/private/localhost.key && \
  chmod 710 /opt/rh/httpd24/root/var/run/httpd

  if [ ! -v HTTPD_LOG_TO_VOLUME ]; then
    sed -ri ' s!^(\s*CustomLog)\s+\S+!\1 /proc/self/fd/1!g; s!^(\s*ErrorLog)\s+\S+!\1 /proc/self/fd/2!g;' /opt/rh/httpd24/root/etc/httpd/conf/httpd.conf
    sed -ri ' s!^(\s*CustomLog)\s+\S+!\1 /proc/self/fd/1!g; s!^(\s*TransferLog)\s+\S+!\1 /proc/self/fd/1!g; s!^(\s*ErrorLog)\s+\S+!\1 /proc/self/fd/2!g;' /opt/rh/httpd24/root/etc/httpd/conf.d/ssl.conf
  fi
else
  # We run as non-root or as s2i
  sed -i -f /opt/app-root/httpdconf-nonroot.sed /opt/rh/httpd24/root/etc/httpd/conf/httpd.conf
fi

set -eu

exec "$@"

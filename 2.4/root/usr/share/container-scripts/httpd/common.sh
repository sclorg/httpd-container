# Set of functions used in other scripts

config_general() {
  sed -i -f /opt/app-root/httpdconf.sed ${HTTPD_MAIN_CONF_PATH}/httpd.conf && \
  sed -i -f /opt/app-root/sslconf.sed ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf && \
  sed -ri " s!^(\s*CustomLog)\s+\S+!\1 |/usr/bin/cat!g; s!^(\s*ErrorLog)\s+\S+!\1 |/usr/bin/cat!g;" ${HTTPD_MAIN_CONF_PATH}/httpd.conf && \
  sed -ri " s!^(\s*CustomLog)\s+\S+!\1 |/usr/bin/cat!g; s!^(\s*TransferLog)\s+\S+!\1 |/usr/bin/cat!g; s!^(\s*ErrorLog)\s+\S+!\1 |/usr/bin/cat!g;" ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf
}


runs_privileged() {
  test "$(id -u)" == "0"
  return $?
}

config_privileged() {
  # Change the s2i permissions back to the normal ones
  chmod 644 ${HTTPD_MAIN_CONF_PATH}/* && \
  chmod 755 ${HTTPD_MAIN_CONF_PATH} && \
  chmod 644 ${HTTPD_MAIN_CONF_D_PATH}/* && \
  chmod 755 ${HTTPD_MAIN_CONF_D_PATH} && \
  chmod 600 /etc/pki/tls/certs/localhost.crt && \
  chmod 600 /etc/pki/tls/private/localhost.key && \
  chmod 710 ${HTTPD_VAR_RUN}

  if [ ! -v HTTPD_LOG_TO_VOLUME ]; then
    sed -ri ' s!^(\s*CustomLog)\s+\S+!\1 /proc/self/fd/1!g; s!^(\s*ErrorLog)\s+\S+!\1 /proc/self/fd/2!g;' ${HTTPD_MAIN_CONF_PATH}/httpd.conf
    sed -ri ' s!^(\s*CustomLog)\s+\S+!\1 /proc/self/fd/1!g; s!^(\s*TransferLog)\s+\S+!\1 /proc/self/fd/1!g; s!^(\s*ErrorLog)\s+\S+!\1 /proc/self/fd/2!g;' ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf
  fi
}

config_s2i() {
  #sed -i -f /opt/app-root/httpdconf-s2i.sed ${HTTPD_MAIN_CONF_PATH}/httpd.conf && \
  sed -ie "s%^DocumentRoot \"${HTTPD_DATA_PATH}/html\"%DocumentRoot \"/opt/app-root/src\"%" ${HTTPD_MAIN_CONF_PATH}/httpd.conf
  sed -ie "s%^<Directory \"${HTTPD_DATA_PATH}/html\"%<Directory \"/opt/app-root/src\"%" ${HTTPD_MAIN_CONF_PATH}/httpd.conf
  sed -ie "s%^<Directory \"${HTTPD_VAR_PATH}/html\"%<Directory \"/opt/app-root/src\"%" ${HTTPD_MAIN_CONF_PATH}/httpd.conf
  echo "IncludeOptional ${HTTPD_CONFIGURATION_PATH}/*.conf" >> ${HTTPD_MAIN_CONF_PATH}/httpd.conf && \
  head -n151 ${HTTPD_MAIN_CONF_PATH}/httpd.conf | tail -n1 | grep "AllowOverride All" || exit
}

config_non_root() {
  sed -ie "s/^User apache/User default/" ${HTTPD_MAIN_CONF_PATH}/httpd.conf
  sed -ie "s/^Group apache/Group root/" ${HTTPD_MAIN_CONF_PATH}/httpd.conf
}


# Set of functions used in other scripts

config_general() {
  sed -i -e 's/^Listen 80/Listen 0.0.0.0:8080/' ${HTTPD_MAIN_CONF_PATH}/httpd.conf && \
  sed -i -e '151s%AllowOverride None%AllowOverride All%' ${HTTPD_MAIN_CONF_PATH}/httpd.conf && \
  sed -i -e 's/^Listen 443/Listen 0.0.0.0:8443/' ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf
}

config_log_to_stdout() {
  sed -ri " s!^(\s*CustomLog)\s+\S+!\1 |/usr/bin/cat!g; s!^(\s*ErrorLog)\s+\S+!\1 |/usr/bin/cat!g;" ${HTTPD_MAIN_CONF_PATH}/httpd.conf
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

  if ! [ -v HTTPD_LOG_TO_VOLUME ] ; then
    config_log_to_stdout
  fi
}

config_s2i() {
  sed -i -e "s%^DocumentRoot \"${HTTPD_DATA_ORIG_PATH}/html\"%DocumentRoot \"${HTTPD_APP_ROOT}/src\"%" ${HTTPD_MAIN_CONF_PATH}/httpd.conf
  sed -i -e "s%^<Directory \"${HTTPD_DATA_ORIG_PATH}/html\"%<Directory \"${HTTPD_APP_ROOT}/src\"%" ${HTTPD_MAIN_CONF_PATH}/httpd.conf
  sed -i -e "s%^<Directory \"${HTTPD_VAR_PATH}/html\"%<Directory \"${HTTPD_APP_ROOT}/src\"%" ${HTTPD_MAIN_CONF_PATH}/httpd.conf
  echo "IncludeOptional ${HTTPD_CONFIGURATION_PATH}/*.conf" >> ${HTTPD_MAIN_CONF_PATH}/httpd.conf && \
  head -n151 ${HTTPD_MAIN_CONF_PATH}/httpd.conf | tail -n1 | grep "AllowOverride All" || exit
}

config_non_privileged() {
  sed -i -e "s/^User apache/User default/" ${HTTPD_MAIN_CONF_PATH}/httpd.conf
  sed -i -e "s/^Group apache/Group root/" ${HTTPD_MAIN_CONF_PATH}/httpd.conf
  config_log_to_stdout
  if [ -v HTTPD_LOG_TO_VOLUME ] ; then
    echo "Error: Option HTTPD_LOG_TO_VOLUME is only valid for privileged runs (as UID 0)."
    return 1
  fi
}

# Set current user in nss_wrapper
generate_container_user() {
  local passwd_output_dir="${HTTPD_APP_ROOT}/etc"

  export USER_ID=$(id -u)
  export GROUP_ID=$(id -g)
  envsubst < ${HTTPD_CONTAINER_SCRIPTS_PATH}/passwd.template > ${passwd_output_dir}/passwd
  export LD_PRELOAD=libnss_wrapper.so
  export NSS_WRAPPER_PASSWD=${passwd_output_dir}/passwd
  export NSS_WRAPPER_GROUP=/etc/group
}


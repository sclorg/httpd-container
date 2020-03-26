# Set of functions used in other scripts

if head "/etc/redhat-release" | grep -q "^Red Hat Enterprise Linux release 8"; then
  HTTPCONF_LINENO=154
else
  HTTPCONF_LINENO=151
fi

gen_ssl_certs() {
  local sslcert=$HTTPD_TLS_CERT_PATH/localhost.crt
  local sslkey=$HTTPD_TLS_CERT_PATH/localhost.key
  local fqdn=`hostname`

  # A >59 char FQDN means "root@FQDN" exceeds 64-char max length for emailAddress
  if [ "x${fqdn}" = "x" -o ${#fqdn} -gt 59 ]; then
    fqdn=localhost.localdomain
  fi

  if [ -f ${sslcert} -o -f ${sslkey} ]; then
    return 0
  fi

  echo "---> Generating SSL key pair for httpd..."
  if [ -x "/usr/bin/sscg" ]; then
    sscg -q                                                           \
       --cert-file           $sslcert                                 \
       --cert-key-file       $sslkey                                  \
       --ca-file             $sslcert                                 \
       --lifetime            365                                      \
       --hostname            $fqdn                                    \
       --email               root@$fqdn
  else
    openssl genrsa -rand /proc/apm:/proc/cpuinfo:/proc/dma:/proc/filesystems:/proc/interrupts:/proc/ioports:/proc/pci:/proc/rtc:/proc/uptime 2048 > ${sslkey} 2> /dev/null

    cat << EOF | openssl req -new -key ${sslkey} \
              -x509 -sha256 -days 365 -set_serial $RANDOM -extensions v3_req \
              -out ${sslcert} 2>/dev/null
--
SomeState
SomeCity
SomeOrganization
SomeOrganizationalUnit
${fqdn}
root@${fqdn}
EOF
   fi

   chmod 644 ${sslcert}
   chmod 644 ${sslkey}
}

config_general() {
  sed -i -e 's/^Listen 80/Listen 0.0.0.0:8080/' ${HTTPD_MAIN_CONF_PATH}/httpd.conf && \
  sed -i -e ${HTTPCONF_LINENO}'s%AllowOverride None%AllowOverride All%' ${HTTPD_MAIN_CONF_PATH}/httpd.conf && \
  sed -i -e 's/^Listen 443/Listen 0.0.0.0:8443/' ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf
  sed -i -e 's/_default_:443/_default_:8443/' ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf

  # do sed for SSLCertificateFile and SSLCertificateKeyFile
  sed -i -e "s|^SSLCertificateFile .*$|SSLCertificateFile ${HTTPD_TLS_CERT_PATH}/localhost.crt|" ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf
  sed -i -e "s|^SSLCertificateKeyFile .*$|SSLCertificateKeyFile ${HTTPD_TLS_CERT_PATH}/localhost.key|" ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf
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
  chmod 644 ${HTTPD_MAIN_CONF_MODULES_D_PATH}/* && \
  chmod 755 ${HTTPD_MAIN_CONF_MODULES_D_PATH} && \
  chmod 600 ${HTTPD_TLS_CERT_PATH}/localhost.crt && \
  chmod 600 ${HTTPD_TLS_CERT_PATH}/localhost.key && \
  chmod 710 ${HTTPD_VAR_RUN}

  if ! [ -v HTTPD_LOG_TO_VOLUME ] ; then
    config_log_to_stdout
  fi
}

config_s2i() {
  sed -i -e "s%^DocumentRoot \"${HTTPD_DATA_ORIG_PATH}/html\"%DocumentRoot \"${HTTPD_APP_ROOT}/src\"%" ${HTTPD_MAIN_CONF_PATH}/httpd.conf
  sed -i -e "s%^<Directory \"${HTTPD_DATA_ORIG_PATH}/html\"%<Directory \"${HTTPD_APP_ROOT}/src\"%" ${HTTPD_MAIN_CONF_PATH}/httpd.conf
  echo "IncludeOptional ${HTTPD_CONFIGURATION_PATH}/*.conf" >> ${HTTPD_MAIN_CONF_PATH}/httpd.conf && \
  head -n${HTTPCONF_LINENO} ${HTTPD_MAIN_CONF_PATH}/httpd.conf | tail -n1 | grep "AllowOverride All" || exit
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

config_mpm() {
  if [ -v HTTPD_MPM -a -f ${HTTPD_MAIN_CONF_MODULES_D_PATH}/00-mpm.conf ]; then
    local mpmconf=${HTTPD_MAIN_CONF_MODULES_D_PATH}/00-mpm.conf
    sed -i -e 's,^LoadModule,#LoadModule,' ${mpmconf}
    sed -i -e "/LoadModule mpm_${HTTPD_MPM}/s,^#LoadModule,LoadModule," ${mpmconf}
    echo "---> Set MPM to ${HTTPD_MPM} in ${mpmconf}"
  fi
}

# get_matched_files finds file for image extending
function get_matched_files() {
  local custom_dir default_dir
  custom_dir="$1"
  default_dir="$2"
  files_matched="$3"
  find "$default_dir" -maxdepth 1 -type f -name "$files_matched" -printf "%f\n"
  [ -d "$custom_dir" ] && find "$custom_dir" -maxdepth 1 -type f -name "$files_matched" -printf "%f\n"
}

# process_extending_files process extending files in $1 and $2 directories
# - source all *.sh files
#   (if there are files with same name source only file from $1)
function process_extending_files() {
  local custom_dir default_dir
  custom_dir=$1
  default_dir=$2
  while read filename ; do
    echo "=> sourcing $filename ..."
    # Custom file is prefered
    if [ -f $custom_dir/$filename ]; then
      source $custom_dir/$filename
    elif [ -f $default_dir/$filename ]; then 
      source $default_dir/$filename
    fi
  done <<<"$(get_matched_files "$custom_dir" "$default_dir" '*.sh' | sort -u)"
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

# Copy config files from application to the location where httd expects them
# Param sets the directory where to look for files
process_config_files() {
  local dir=${1:-.}
  if [ -d ${dir}/httpd-cfg ]; then
    echo "---> Copying httpd configuration files..."
    if [ "$(ls -A ${dir}/httpd-cfg/*.conf)" ]; then
      cp -v ${dir}/httpd-cfg/*.conf "${HTTPD_CONFIGURATION_PATH}"
      rm -rf ${dir}/httpd-cfg
    fi
  else
    if [ -d ${dir}/cfg ]; then
      echo "---> Copying httpd configuration files from deprecated './cfg' directory, use './httpd-cfg' instead..."
      if [ "$(ls -A ${dir}/cfg/*.conf)" ]; then
        cp -v ${dir}/cfg/*.conf "${HTTPD_CONFIGURATION_PATH}"
        rm -rf ${dir}/cfg
      fi
    fi
  fi
}

# Copy SSL files provided in application source
process_ssl_certs() {
  local dir=${1:-.}
  if [ -d ${dir}/httpd-ssl/private ] && [ -d ${dir}/httpd-ssl/certs ]; then
    echo "---> Moving the httpd-ssl directory included in the source to a directory that isn't exposed by httpd..."
    mv ${dir}/httpd-ssl ${HTTPD_APP_ROOT}
  fi
  if [ -d ${HTTPD_APP_ROOT}/httpd-ssl/private ] && [ -d ${HTTPD_APP_ROOT}/httpd-ssl/certs ]; then
    echo "---> Looking for SSL certs for httpd..."
    local ssl_cert="$(ls -A ${HTTPD_APP_ROOT}/httpd-ssl/certs/*.pem | head -n 1)"
    local ssl_private="$(ls -A ${HTTPD_APP_ROOT}/httpd-ssl/private/*.pem | head -n 1)"
    if [ -f "${ssl_cert}" ] ; then
      # do sed for SSLCertificateFile and SSLCertificateKeyFile
      echo "---> Setting SSL cert file for httpd..."
      sed -i -e "s|^SSLCertificateFile .*$|SSLCertificateFile ${ssl_cert}|" ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf
      if [ -f "${ssl_private}" ]; then
        echo "---> Setting SSL key file for httpd..."
        sed -i -e "s|^SSLCertificateKeyFile .*$|SSLCertificateKeyFile ${ssl_private}|" ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf
      else
        echo "---> Removing SSL key file settings for httpd..."
        sed -i '/^SSLCertificateKeyFile .*/d'  ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf
      fi
    else
      # Generate TLS key pair if no SSL cert was found
      gen_ssl_certs
    fi
  else
    gen_ssl_certs
  fi
}


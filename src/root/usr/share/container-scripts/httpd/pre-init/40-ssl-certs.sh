source ${HTTPD_CONTAINER_SCRIPTS_PATH}/common.sh

# Copy SSL files provided in application source
process_ssl_certs ${HTTPD_APP_ROOT}/src

source ${HTTPD_CONTAINER_SCRIPTS_PATH}/common.sh

# Copy config files from application to the location where httd expects them
process_config_files ${HTTPD_APP_ROOT}/src

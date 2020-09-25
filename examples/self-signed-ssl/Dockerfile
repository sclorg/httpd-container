FROM registry.redhat.io/rhel8/httpd-24

# Add application sources
ADD index.html /var/www/html/index.html

# Add self-signed certificate files
# TODO: Test that we do not use a newly generated certs by:
# podman exec ... curl -kvvI https://127.0.0.1:8443 must match "start date: Dec  3 23:33:57 2017 GMT" or whatever the testing certs have
ADD httpd-ssl "${APP_ROOT}/httpd-ssl"

# Run script uses standard ways to run the application and also puts
# the certificate files into a correct directory
CMD run-httpd

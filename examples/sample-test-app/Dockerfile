FROM registry.redhat.io/rhel8/httpd-24

# Add application sources
ADD index.html /var/www/html/index.html

# Run script uses standard ways to run the application and also generates
# self-signed certificates in order to allow SSL-protected connection
CMD run-httpd

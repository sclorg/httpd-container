FROM registry.redhat.io/rhel10/httpd-24

# This image supports the Source-to-Image
# In order to support the Source-to-Image framework, there are some interesting
# scripts inside the builder image, that can be run in a Dockerfile directly as well:
# * The `/usr/libexec/s2i/assemble` script inside the image is run in order
#   to produce a new image with the application artifacts.
#   The script takes sources of a given application and places them into
#   appropriate directories inside the image.
# * The `/usr/libexec/s2i/run` script executes the application and is set as
#   a default command in the resulting container image.
# Add application sources
ADD index.html /var/www/html/index.html

# Run script uses standard ways to run the application and also generates
# self-signed certificates in order to allow SSL-protected connection
CMD run-httpd

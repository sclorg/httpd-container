FROM centos/s2i-base-centos7

# RHSCL httpd24 image.
#
# Volumes:
#  * /opt/rh/httpd24/root/var/www - Datastore for httpd
#  * /var/log/httpd24 - Storage for logs when $HTTPD_LOG_TO_VOLUME is set
# Environment:
#  * $HTTPD_LOG_TO_VOLUME (optional) - When set, httpd will log into /var/log/httpd24

# Labels consumed by Red Hat build service
LABEL io.k8s.description="Platform for running Apache httpd or building httpd-based application" \
      io.k8s.display-name="httpd 2.4.18" \
      io.openshift.expose-services="8080:http" \
      io.openshift.expose-services="8443:https" \
      io.openshift.tags="builder,httpd,httpd24"

EXPOSE 80
EXPOSE 443
EXPOSE 8080
EXPOSE 8443

RUN yum install -y yum-utils gettext hostname && \
    yum install -y centos-release-scl epel-release && \
    INSTALL_PKGS="nss_wrapper bind-utils httpd24 httpd24-mod_ssl" && \
    yum install -y --setopt=tsflags=nodocs $INSTALL_PKGS && \
    rpm -V $INSTALL_PKGS && \
    yum clean all

ENV HTTPD_CONTAINER_SCRIPTS_PATH=/usr/share/container-scripts/httpd/ \
    HTTPD_APP_ROOT=/opt/app-root \
    HTTPD_CONFIGURATION_PATH=${HTTPD_APP_ROOT}/etc/httpd.d \
    HTTPD_MAIN_CONF_PATH=/opt/rh/httpd24/root/etc/httpd/conf \
    HTTPD_MAIN_CONF_D_PATH=/opt/rh/httpd24/root/etc/httpd/conf.d \
    HTTPD_VAR_RUN=/opt/rh/httpd24/root/var/run/httpd \
    HTTPD_VAR_PATH=/opt/rh/httpd24/root/var \
    HTTPD_DATA_PATH=/opt/rh/httpd24/root/var/www \
    HTTPD_LOG_PATH=/var/log/httpd24

# When bash is started non-interactively, to run a shell script, for example it
# looks for this variable and source the content of this file. This will enable
# the SCL for all scripts without need to do 'scl enable'.
ENV BASH_ENV=${HTTPD_APP_ROOT}/scl_enable \
    ENV=${HTTPD_APP_ROOT}/scl_enable \
    PROMPT_COMMAND=". ${HTTPD_APP_ROOT}/scl_enable"

COPY ./s2i/bin/ $STI_SCRIPTS_PATH
COPY ./root /

RUN /usr/libexec/httpd-prepare

USER 1001

VOLUME ["${HTTPD_DATA_PATH}"]
VOLUME ["${HTTPD_LOG_PATH}"]

CMD ["/usr/bin/run-httpd"]

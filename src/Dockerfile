FROM {{ spec.s2i_base }}

# Apache HTTP Server image.
#
# Volumes:
#  * /var/www - Datastore for httpd
{% if spec.prod == "fedora" %}
#  * /var/log/httpd - Storage for logs when $HTTPD_LOG_TO_VOLUME is set
# Environment:
#  * $HTTPD_LOG_TO_VOLUME (optional) - When set, httpd will log into /var/log/httpd
{% else %}
#  * /var/log/httpd24 - Storage for logs when $HTTPD_LOG_TO_VOLUME is set
# Environment:
#  * $HTTPD_LOG_TO_VOLUME (optional) - When set, httpd will log into /var/log/httpd24
{% endif %}

ENV HTTPD_VERSION={{ spec.version }} \
    HTTPD_SHORT_VERSION={{ spec.short }} \
    NAME=httpd

ENV SUMMARY="Platform for running Apache httpd ${HTTPD_VERSION} or building httpd-based application" \
    DESCRIPTION="Apache httpd ${HTTPD_VERSION} available as container, is a powerful, efficient, \
and extensible web server. Apache supports a variety of features, many implemented as compiled modules \
which extend the core functionality. \
These can range from server-side programming language support to authentication schemes. \
Virtual hosting allows one Apache installation to serve many different Web sites."

LABEL summary="${SUMMARY}" \
      description="${DESCRIPTION}" \
      io.k8s.description="${DESCRIPTION}" \
      io.k8s.display-name="Apache httpd ${HTTPD_VERSION}" \
      io.openshift.expose-services="8080:http,8443:https" \
      io.openshift.tags="builder,httpd,httpd-{{ spec.short }}" \
      name="{{ spec.img_name }}" \
      version="{{ spec.version_label }}" \
{% if spec.license_terms %}
      com.redhat.license_terms="{{ spec.license_terms }}" \
{% endif %}
      com.redhat.component="{{ spec.redhat_component }}" \
      usage="s2i build https://github.com/sclorg/httpd-container.git --context-dir=examples/sample-test-app/ {{ spec.usage_image }} sample-server" \
      maintainer="SoftwareCollections.org <sclorg@redhat.com>"

EXPOSE 8080
EXPOSE 8443

{% if spec.extra_install %}
RUN {{ spec.extra_install }}
    INSTALL_PKGS="{{ spec.pkgs }}" && \
    dnf install -y --setopt=tsflags=nodocs ${INSTALL_PKGS} && \
    httpd -v | grep -qe "Apache/${HTTPD_VERSION}" && echo "Found VERSION ${HTTPD_VERSION}" && \
{% if spec.pkg_clean %}
    {{ spec.pkg_clean }}
{% else %}
    dnf -y clean all --enablerepo='*'
{% endif %}
{% elif spec.pkg_verify %}
RUN {% if spec.module_enable %}{{ spec.module_enable }}
    {% endif %}{% if spec.var_style == "dollar" %}    INSTALL_PKGS="{{ spec.pkgs }}" && \
    dnf install -y --setopt=tsflags=nodocs $INSTALL_PKGS && \
    rpm -V $INSTALL_PKGS && \
    httpd -v | grep -qe "Apache/$HTTPD_VERSION" && echo "Found VERSION $HTTPD_VERSION" && \
{% else %}INSTALL_PKGS="{{ spec.pkgs }}" && \
    dnf install -y --setopt=tsflags=nodocs ${INSTALL_PKGS} && \
    rpm -V ${INSTALL_PKGS} && \
    httpd -v | grep -qe "Apache/${HTTPD_VERSION}" && echo "Found VERSION ${HTTPD_VERSION}" && \
{% endif %}
    dnf -y clean all --enablerepo='*'
{% else %}
RUN INSTALL_PKGS="{{ spec.pkgs }}" && \
    dnf install -y --setopt=tsflags=nodocs ${INSTALL_PKGS} && \
    httpd -v | grep -qe "Apache/${HTTPD_VERSION}" && echo "Found VERSION ${HTTPD_VERSION}" && \
    dnf -y clean all --enablerepo='*'
{% endif %}

ENV HTTPD_CONTAINER_SCRIPTS_PATH=/usr/share/container-scripts/httpd/ \
    HTTPD_APP_ROOT=${APP_ROOT} \
    HTTPD_CONFIGURATION_PATH=${APP_ROOT}/etc/httpd.d \
    HTTPD_MAIN_CONF_PATH=/etc/httpd/conf \
    HTTPD_MAIN_CONF_MODULES_D_PATH=/etc/httpd/conf.modules.d \
    HTTPD_MAIN_CONF_D_PATH=/etc/httpd/conf.d \
    HTTPD_TLS_CERT_PATH=/etc/httpd/tls \
    HTTPD_VAR_RUN=/var/run/httpd \
    HTTPD_DATA_PATH=/var/www \
    HTTPD_DATA_ORIG_PATH=/var/www \
    HTTPD_LOG_PATH=/var/log/httpd

COPY {{ spec.version }}/s2i/bin/ ${STI_SCRIPTS_PATH}
COPY {{ spec.version }}/root /

# Reset permissions of filesystem to default values
RUN /usr/libexec/httpd-prepare && rpm-file-permissions

USER 1001

# Not using VOLUME statement since it's not working in OpenShift Online:
# https://github.com/sclorg/httpd-container/issues/30
# VOLUME ["${HTTPD_DATA_PATH}"]
# VOLUME ["${HTTPD_LOG_PATH}"]

CMD ["/usr/bin/run-httpd"]

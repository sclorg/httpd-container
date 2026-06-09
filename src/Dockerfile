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

{% if spec.env_init == "simple" %}
ENV HTTPD_VERSION={{ spec.version }}

ENV SUMMARY="Platform for running Apache httpd $HTTPD_VERSION or building httpd-based application" \
    DESCRIPTION="Apache httpd $HTTPD_VERSION available as container, is a powerful, efficient, \
{% elif spec.env_init == "combined" %}
ENV HTTPD_VERSION={{ spec.version }} \
    HTTPD_SHORT_VERSION={{ spec.short }} \
    NAME=httpd

ENV SUMMARY="Platform for running Apache httpd ${HTTPD_VERSION} or building httpd-based application" \
    DESCRIPTION="Apache httpd ${HTTPD_VERSION} available as container, is a powerful, efficient, \
{% else %}
ENV HTTPD_VERSION={{ spec.version }} \
    HTTPD_SHORT_VERSION={{ spec.short }} \
    NAME=httpd \
    ARCH=x86_64

ENV SUMMARY="Platform for running Apache httpd ${HTTPD_VERSION} or building httpd-based application" \
    DESCRIPTION="Apache httpd ${HTTPD_VERSION} available as container, is a powerful, efficient, \
{% endif %}
and extensible web server. Apache supports a variety of features, many implemented as compiled modules \
which extend the core functionality. \
These can range from server-side programming language support to authentication schemes. \
Virtual hosting allows one Apache installation to serve many different Web sites."

{% if spec.var_style == "dollar" %}
LABEL summary="$SUMMARY" \
      description="$DESCRIPTION" \
      io.k8s.description="$DESCRIPTION" \
      io.k8s.display-name="Apache httpd $HTTPD_VERSION" \
      io.openshift.expose-services="8080:http,8443:https" \
      io.openshift.tags="builder,httpd,httpd-{{ spec.short }}" \
      name="{{ spec.img_name }}" \
{% if spec.version_label %}
      version="{{ spec.version_label }}" \
{% endif %}
{% if spec.license_terms %}
      com.redhat.license_terms="{{ spec.license_terms }}" \
{% endif %}
      com.redhat.component="{{ spec.redhat_component }}" \
      usage="s2i build https://github.com/sclorg/httpd-container.git --context-dir=examples/sample-test-app/ {{ spec.usage_image }} sample-server" \
      maintainer="SoftwareCollections.org <sclorg@redhat.com>"
{% elif spec.fedora_specific %}
LABEL summary="${SUMMARY}" \
      description="${DESCRIPTION}" \
      io.k8s.description="${SUMMARY}" \
      io.k8s.display-name="Apache httpd ${HTTPD_VERSION}" \
      io.openshift.expose-services="8080:http,8443:https" \
      io.openshift.tags="builder,${NAME},${NAME}${HTTPD_SHORT_VERSION}" \
      com.redhat.component="{{ spec.redhat_component }}" \
      name="{{ spec.img_name }}" \
      version="${HTTPD_VERSION}" \
      usage="s2i build https://github.com/sclorg/httpd-container.git --context-dir=examples/sample-test-app/ {{ spec.usage_image }} sample-server" \
      maintainer="SoftwareCollections.org <sclorg@redhat.com>"
{% else %}
LABEL summary="${SUMMARY}" \
      description="${DESCRIPTION}" \
      io.k8s.description="${DESCRIPTION}" \
      io.k8s.display-name="Apache httpd ${HTTPD_VERSION}" \
      io.openshift.expose-services="8080:http,8443:https" \
      io.openshift.tags="builder,${NAME},${NAME}-${HTTPD_SHORT_VERSION}" \
      name="{{ spec.img_name }}" \
{% if spec.version_label %}
      version="{{ spec.version_label }}" \
{% endif %}
{% if spec.license_terms %}
      com.redhat.license_terms="{{ spec.license_terms }}" \
{% endif %}
      com.redhat.component="{{ spec.redhat_component }}" \
      usage="s2i build https://github.com/sclorg/httpd-container.git --context-dir=examples/sample-test-app/ {{ spec.usage_image }} sample-server" \
      maintainer="SoftwareCollections.org <sclorg@redhat.com>"
{% endif %}

EXPOSE 8080
EXPOSE 8443

{% if spec.extra_install %}
RUN {{ spec.extra_install }}
    INSTALL_PKGS="{{ spec.pkgs }}" && \
    {{ spec.pkg_manager }} install -y --setopt=tsflags=nodocs ${INSTALL_PKGS} && \
    httpd -v | grep -qe "Apache/${HTTPD_VERSION}" && echo "Found VERSION ${HTTPD_VERSION}" && \
{% if spec.pkg_clean %}
    {{ spec.pkg_clean }}
{% else %}
    {{ spec.pkg_manager }} -y clean all --enablerepo='*'
{% endif %}
{% elif spec.pkg_verify %}
RUN {% if spec.module_enable %}{{ spec.module_enable }}
    {% endif %}{% if spec.var_style == "dollar" %}    INSTALL_PKGS="{{ spec.pkgs }}" && \
    {{ spec.pkg_manager }} install -y --setopt=tsflags=nodocs $INSTALL_PKGS && \
    rpm -V $INSTALL_PKGS && \
    httpd -v | grep -qe "Apache/$HTTPD_VERSION" && echo "Found VERSION $HTTPD_VERSION" && \
{% else %}INSTALL_PKGS="{{ spec.pkgs }}" && \
    {{ spec.pkg_manager }} install -y --setopt=tsflags=nodocs ${INSTALL_PKGS} && \
    rpm -V ${INSTALL_PKGS} && \
    httpd -v | grep -qe "Apache/${HTTPD_VERSION}" && echo "Found VERSION ${HTTPD_VERSION}" && \
{% endif %}
    {{ spec.pkg_manager }} -y clean all --enablerepo='*'
{% else %}
RUN INSTALL_PKGS="{{ spec.pkgs }}" && \
    {{ spec.pkg_manager }} install -y --setopt=tsflags=nodocs ${INSTALL_PKGS} && \
    httpd -v | grep -qe "Apache/${HTTPD_VERSION}" && echo "Found VERSION ${HTTPD_VERSION}" && \
    {{ spec.pkg_manager }} -y clean all --enablerepo='*'
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

{% if spec.copy_version %}
COPY {{ spec.copy_version }}/s2i/bin/ $STI_SCRIPTS_PATH
COPY {{ spec.copy_version }}/root /
{% else %}
COPY ${HTTPD_VERSION}/s2i/bin/ ${STI_SCRIPTS_PATH}
COPY ${HTTPD_VERSION}/root /
{% endif %}

{% if spec.fedora_specific %}
# Generate SSL certs and reset permissions of filesystem to default values
# Reset permissions of filesystem to default values
{% else %}
# Reset permissions of filesystem to default values
{% endif %}
RUN /usr/libexec/httpd-prepare && rpm-file-permissions

USER 1001

# Not using VOLUME statement since it's not working in OpenShift Online:
# https://github.com/sclorg/httpd-container/issues/30
# VOLUME ["${HTTPD_DATA_PATH}"]
# VOLUME ["${HTTPD_LOG_PATH}"]

CMD ["/usr/bin/run-httpd"]

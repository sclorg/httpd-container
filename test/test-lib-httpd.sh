#!/bin/bash
#
# Functions for tests for the httpd image in OpenShift.
#
# IMAGE_NAME specifies a name of the candidate image used for testing.
# The image has to be available before this script is executed.
#

THISDIR=$(dirname ${BASH_SOURCE[0]})

source ${THISDIR}/test-lib.sh
source ${THISDIR}/test-lib-openshift.sh

function test_httpd_integration() {
  local image_name=$1
  ct_os_test_s2i_app "${image_name}" \
                     "https://github.com/sclorg/httpd-container.git" \
                     "examples/sample-test-app" \
                     "This is a sample s2i application with static content"
}

# Check the imagestream
function test_httpd_imagestream() {
  case ${OS} in
    rhel7|centos7) ;;
    *) echo "Imagestream testing not supported for $OS environment." ; return 0 ;;
  esac

  ct_os_test_image_stream_s2i "${THISDIR}/imagestreams/httpd-${OS}.json" "${IMAGE_NAME}" \
                              "https://github.com/sclorg/httpd-container.git" \
                              "examples/sample-test-app" \
                              "This is a sample s2i application with static content"
}

# vim: set tabstop=2:shiftwidth=2:expandtab:

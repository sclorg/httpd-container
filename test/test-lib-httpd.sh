#!/bin/bash
#
# Functions for tests for the httpd image in OpenShift.
#
# IMAGE_NAME specifies a name of the candidate image used for testing.
# The image has to be available before this script is executed.
#

THISDIR=$(dirname ${BASH_SOURCE[0]})

source "${THISDIR}/test-lib.sh"
source "${THISDIR}/test-lib-openshift.sh"

function test_httpd_integration() {
  ct_os_test_s2i_app "${IMAGE_NAME}" \
                     "https://github.com/sclorg/httpd-container.git" \
                     "examples/sample-test-app" \
                     "This is a sample s2i application with static content"
}

# Check the imagestream
function test_httpd_imagestream() {
  ct_os_test_image_stream_s2i "${THISDIR}/imagestreams/httpd-${OS//[0-9]/}.json" "${IMAGE_NAME}" \
                              "https://github.com/sclorg/httpd-container.git" \
                              "examples/sample-test-app" \
                              "This is a sample s2i application with static content"
}

function test_httpd_example_repo {
  BRANCH_TO_TEST=master
  # test remote example app
  ct_os_test_s2i_app "${IMAGE_NAME}" "https://github.com/sclorg/httpd-ex#${BRANCH_TO_TEST}" \
                      "." \
                      'Welcome to your static httpd application on OpenShift'
}

function test_latest_imagestreams() {
  # Switch to root directory of a container
  pushd ${THISDIR}/../.. >/dev/null
  ct_check_latest_imagestreams
  popd >/dev/null
}

# vim: set tabstop=2:shiftwidth=2:expandtab:

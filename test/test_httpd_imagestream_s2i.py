import os
import sys

import pytest

from container_ci_suite.openshift import OpenShiftAPI
from container_ci_suite.utils import get_service_image, check_variables

if not check_variables():
    print("At least one variable from IMAGE_NAME, OS, SINGLE_VERSION is missing.")
    sys.exit(1)

BRANCH_TO_TEST = "master"
IMAGE_NAME = os.getenv("IMAGE_NAME")
OS = os.getenv("OS")
VERSION = os.getenv("VERSION")


class TestHTTPDImagestreamS2I:

    def setup_method(self):
        self.template_name = get_service_image(IMAGE_NAME)
        self.oc_api = OpenShiftAPI(pod_name_prefix=self.template_name, version=VERSION, shared_cluster=True)

    def teardown_method(self):
        self.oc_api.delete_project()

    def test_inside_cluster(self):
        if VERSION == "rhel10":
            pytest.skip("Do NOT test on RHEL10.")
        os_name = ''.join(i for i in OS if not i.isdigit())
        assert self.oc_api.deploy_imagestream_s2i(
            imagestream_file=f"imagestreams/httpd-{os_name}.json",
            image_name=IMAGE_NAME,
            app="https://github.com/sclorg/httpd-container.git",
            context="examples/sample-test-app",
            service_name=self.template_name
        )
        assert self.oc_api.is_s2i_pod_running(pod_name_prefix=self.template_name)
        assert self.oc_api.check_response_inside_cluster(
            name_in_template=self.template_name, expected_output="This is a sample s2i application with static content"
        )

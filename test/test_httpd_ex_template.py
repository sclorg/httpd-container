import os
import sys
import pytest
from pathlib import Path

from container_ci_suite.openshift import OpenShiftAPI
from container_ci_suite.utils import get_service_image, check_variables
TEST_DIR = Path(os.path.abspath(os.path.dirname(__file__)))

if not check_variables():
    print("At least one variable from IMAGE_NAME, OS, SINGLE_VERSION is missing.")
    sys.exit(1)

VERSION = os.getenv("SINGLE_VERSION")
IMAGE_NAME = os.getenv("IMAGE_NAME")
BRANCH_TO_TEST = "master"


class TestHTTPDExExampleRepo:

    def setup_method(self):
        self.template_name = get_service_image(IMAGE_NAME)
        self.oc_api = OpenShiftAPI(pod_name_prefix=self.template_name, version=VERSION)

    def teardown_method(self):
        self.oc_api.delete_project()

    def test_httpd_ex_template_inside_cluster(self):
        assert self.oc_api.deploy_s2i_app(
            image_name=IMAGE_NAME,
            app=f"https://github.com/sclorg/httpd-ex#{BRANCH_TO_TEST}",
            context="."
        )
        assert self.oc_api.template_deployed(name_in_template=self.template_name)
        assert self.oc_api.check_response_inside_cluster(
            name_in_template=self.template_name, expected_output="Welcome to your static httpd"
        )

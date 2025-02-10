import os

import pytest
from pathlib import Path

from container_ci_suite.helm import HelmChartsAPI

test_dir = Path(os.path.abspath(os.path.dirname(__file__)))

VERSION = os.getenv("VERSION")
IMAGE_NAME = os.getenv("IMAGE_NAME")
BRANCH_TO_TEST = "master"
OS = os.getenv("OS")

TAGS = {
    "rhel8": "-el8",
    "rhel9": "-el9"
}

TAG = TAGS.get(OS, None)


class TestHelmHTTPDTemplate:

    def setup_method(self):
        package_name = "redhat-httpd-template"
        path = test_dir
        self.hc_api = HelmChartsAPI(path=path, package_name=package_name, tarball_dir=test_dir)
        self.hc_api.clone_helm_chart_repo(
            repo_url="https://github.com/sclorg/helm-charts", repo_name="helm-charts",
            subdir="charts/redhat"
        )

    def teardown_method(self):
        self.hc_api.delete_project()

    def test_package_persistent_by_curl(self):
        if self.hc_api.oc_api.shared_cluster:
            pytest.skip("Do NOT test on shared cluster")
        new_version = VERSION
        if "micro" in VERSION:
            new_version = VERSION.replace("-micro", "")
        self.hc_api.package_name = "redhat-httpd-imagestreams"
        assert self.hc_api.helm_package()
        assert self.hc_api.helm_installation()
        self.hc_api.package_name = "redhat-httpd-template"
        assert self.hc_api.helm_package()
        assert self.hc_api.helm_installation(
            values={
                "httpd_version": f"{new_version}{TAG}",
                "namespace": self.hc_api.namespace
            }
        )
        assert self.hc_api.is_s2i_pod_running(pod_name_prefix="httpd-example")
        assert self.hc_api.test_helm_curl_output(
            route_name="httpd-example",
            expected_str="Welcome to your static httpd application on OpenShift"
        )

    def test_package_persistent_by_helm_chart_test(self):
        new_version = VERSION
        if "micro" in VERSION:
            new_version = VERSION.replace("-micro", "")
        self.hc_api.package_name = "redhat-httpd-imagestreams"
        self.hc_api.helm_package()
        assert self.hc_api.helm_installation()
        self.hc_api.package_name = "redhat-httpd-template"
        self.hc_api.helm_package()
        assert self.hc_api.helm_installation(
            values={
                "httpd_version": f"{new_version}{TAG}",
                "namespace": self.hc_api.namespace
            }
        )
        assert self.hc_api.is_s2i_pod_running(pod_name_prefix="httpd-example")
        assert self.hc_api.test_helm_chart(expected_str=["Welcome to your static httpd application on OpenShift"])

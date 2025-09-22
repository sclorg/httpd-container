import os
import sys

from pathlib import Path

from container_ci_suite.helm import HelmChartsAPI
from container_ci_suite.utils import check_variables

from constants import TAGS


if not check_variables():
    print("At least one variable from OS, VERSION is missing.")
    sys.exit(1)

test_dir = Path(os.path.abspath(os.path.dirname(__file__)))

VERSION = os.getenv("VERSION")
IMAGE_NAME = os.getenv("IMAGE_NAME")
OS = os.getenv("OS")

TAG = TAGS.get(OS)


class TestHelmHTTPDTemplate:

    def setup_method(self):
        package_name = "redhat-httpd-template"
        path = test_dir
        self.hc_api = HelmChartsAPI(path=path, package_name=package_name, tarball_dir=test_dir, shared_cluster=True)
        self.hc_api.clone_helm_chart_repo(
            repo_url="https://github.com/sclorg/helm-charts", repo_name="helm-charts",
            subdir="charts/redhat"
        )

    def teardown_method(self):
        self.hc_api.delete_project()

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

from container_ci_suite.helm import HelmChartsAPI

from conftest import VARS


class TestHelmHTTPDTemplate:

    def setup_method(self):
        package_name = "redhat-httpd-template"
        self.hc_api = HelmChartsAPI(
            path=VARS.TEST_DIR, package_name=package_name,
            tarball_dir=VARS.TEST_DIR,
            shared_cluster=True
        )
        self.hc_api.clone_helm_chart_repo(
            repo_url="https://github.com/sclorg/helm-charts",
            repo_name="helm-charts",
            subdir="charts/redhat"
        )

    def teardown_method(self):
        self.hc_api.delete_project()

    def test_package_persistent_by_helm_chart_test(self):
        new_version = VARS.VERSION
        if "micro" in VARS.VERSION:
            new_version = VARS.VERSION.replace("-micro", "")
        self.hc_api.package_name = "redhat-httpd-imagestreams"
        self.hc_api.helm_package()
        assert self.hc_api.helm_installation()
        self.hc_api.package_name = "redhat-httpd-template"
        self.hc_api.helm_package()
        assert self.hc_api.helm_installation(
            values={
                "httpd_version": f"{new_version}{VARS.TAG}",
                "namespace": self.hc_api.namespace
            }
        )
        assert self.hc_api.is_s2i_pod_running(pod_name_prefix="httpd-example")
        assert self.hc_api.test_helm_chart(
            expected_str=["Welcome to your static httpd application on OpenShift"]
        )

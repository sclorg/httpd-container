import os
import re
import tempfile

from pathlib import Path

import pytest

from container_ci_suite.container_lib import ContainerTestLib
from container_ci_suite.utils import ContainerTestLibUtils


TEST_DIR = Path(__file__).parent.absolute()
VERSION = os.getenv("VERSION")
OS = os.getenv("OS").lower()
IMAGE_NAME = os.getenv("IMAGE_NAME")


class TestHttpdAppContainer:

    def setup_method(self):
        self.app = ContainerTestLib(image_name=IMAGE_NAME, s2i_image=True)

    def teardown_method(self):
        self.app.cleanup()

    @pytest.mark.parametrize(
        "container_arg",
        [
            "",
            "--user 0"
        ]
    )
    def test_default_page(self, container_arg):
        assert self.app.create_container(cid_file_name="test_default_page", container_args=container_arg)
        cip = self.app.get_cip("test_default_page")
        assert cip
        response = "HTTP Server"
        assert self.app.test_response(url=cip, expected_code=403, expected_output=response, max_attempts=3)

    def test_run_s2i_usage(self):
        output = self.app.s2i_usage()
        assert output

    @pytest.mark.parametrize(
        "dockerfile",
        [
            "Dockerfile",
            "Dockerfile.s2i"
        ]
    )
    def test_dockerfiles(self, dockerfile):
        assert self.app.build_test_container(
            dockerfile=TEST_DIR / "examples" / dockerfile, app_url="https://github.com/sclorg/httpd-ex.git",
            app_dir="app-src"
        )
        assert self.app.test_app_dockerfile()
        cip = self.app.get_cip()
        assert cip
        assert self.app.test_response(url=cip, expected_code=200, expected_output="Welcome to your static httpd application on OpenShift")

    @pytest.mark.parametrize(
        "mpm_config",
        [
            "worker",
            "event",
            "prefork",
        ]
    )
    def test_mpm_config(self, mpm_config):
        cid_name = f"test_mpm_{mpm_config}"
        assert self.app.create_container(cid_file_name=cid_name, container_args=f"-e HTTPD_MPM={mpm_config} --user 1001")
        cip = self.app.get_cip(cid_file_name=cid_name)
        # Let's check that server really response HTTP-403
        # See function here: in test/run `_run_mpm_config_test`
        # https://github.com/sclorg/httpd-container/blob/master/test/run#L97
        assert self.app.test_response(url=f"{cip}", port=8080, expected_code=403)
        logs = self.app.get_logs(cid_file_name=cid_name)
        assert re.search(f"mpm_{mpm_config}:notice.*resuming normal operations", logs)


    def test_log_to_data_volume(self):
        data_dir = tempfile.mkdtemp(prefix="/tmp/httpd-test_log_dir")
        ContainerTestLibUtils.commands_to_run(
            commands_to_run = [
                f"mkdir -p {data_dir}",
                f"chown -R 1001:1001 {data_dir}",
                f"chcon -Rvt svirt_sandbox_file_t {data_dir}/"
            ]
        )
        assert self.app.create_container(
            cid_file_name="test_log_dir",
            container_args=f"-e HTTPD_LOG_TO_VOLUME=1 --user 0 -v {data_dir}:/var/log/httpd"
        )
        cip = self.app.get_cip(cid_file_name="test_log_dir")
        assert self.app.test_response(url=f"{cip}", port=8080, expected_code=403)
        assert ContainerTestLibUtils.check_files_are_present(
            dir_name=data_dir, file_name_to_check=[
                "access_log",
                "error_log",
                "ssl_access_log",
                "ssl_error_log",
                "ssl_request_log",
            ]
        )

    def test_data_volume(self):
        data_dir = tempfile.mkdtemp(prefix="/tmp/httpd-test-volume")
        ContainerTestLibUtils.commands_to_run(
            commands_to_run = [
                f"mkdir -p {data_dir}/html",
                f"echo hello > {data_dir}/html/index.html",
                f"chown -R 1001:1001 {data_dir}",
                f"chcon -Rvt svirt_sandbox_file_t {data_dir}/"
            ]
        )
        assert self.app.create_container(
            cid_file_name="doc_root",
            container_args=f"-v {data_dir}:/var/www"
        )
        cip = self.app.get_cip(cid_file_name="doc_root")
        assert cip
        assert self.app.test_response(url=f"{cip}", port=8080, expected_code=200, expected_output="hello")

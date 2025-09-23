import os
import sys

import pytest

from pathlib import Path

from container_ci_suite.container_lib import ContainerTestLib
from container_ci_suite.utils import check_variables, ContainerTestLibUtils


if not check_variables():
    print("At least one variable from OS, VERSION is missing.")
    sys.exit(1)


TEST_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
VERSION = os.getenv("VERSION")
OS = os.getenv("OS")
IMAGE_NAME = os.getenv("IMAGE_NAME")
if not IMAGE_NAME:
    print(f"Built container for version {VERSION} on OS {OS} does not exist.")
    sys.exit(1)
print(f"Test dir is: {TEST_DIR}")


@pytest.fixture(scope="module")
def app():
    app = ContainerTestLib(image_name=IMAGE_NAME, s2i_image=True)
    yield app
    app.clean_containers()
    app.clean_app_images()


class TestHttpdAppContainer:

    def test_default_page(self, app):
        assert app.create_container(cid_file_name="test_default_page")
        cip = app.get_cip("test_default_page")
        assert cip
        if OS == "c9s" or OS == "c10s":
            response = "HTTP Server Test Page"
        else:
            # The RHEL and Fedora OS gets this response
            response = "Test Page for the HTTP Server on"
        assert app.test_response(url=f"{cip}", expected_code=403, expected_output=response, max_attempts=3)

    def test_run_as_root(self, app):
        assert app.create_container(cid_file_name="test_default_page", container_args="--user 0")
        cip = app.get_cip("test_default_page")
        assert cip
        if OS == "c9s" or OS == "c10s":
            response = "HTTP Server Test Page"
        else:
            response = "Test Page for the HTTP Server on"
        assert app.test_response(url=f"{cip}", expected_code=403, expected_output=response, max_attempts=3)

    def test_run_s2i_usage(self, app):
        output = app.s2i_usage()
        print(f"S2i_USAGE output: '{output}'")
        assert output != ""

    @pytest.mark.parametrize(
        "dockerfile",
        [
            "Dockerfile",
            "Dockerfile.s2i"
        ]
    )
    def test_dockerfiles(self, app, dockerfile):
        assert app.build_test_container(
            dockerfile=f"{TEST_DIR}/examples/{dockerfile}", app_url="https://github.com/sclorg/httpd-ex.git",
            app_dir="app-src"
        )
        assert app.test_app_dockerfile()
        cip = app.get_cip()
        assert cip
        assert app.test_response(url=f"{cip}", expected_code=200, expected_output="Welcome to your static httpd application on OpenShift")

    @pytest.mark.parametrize(
        "mpm_config",
        [
            "worker",
            "event",
            "prefork",
        ]
    )
    def test_mpm_config(self, app, mpm_config):
        cid_name = f"test_mpm_{mpm_config}"
        assert app.create_container(cid_file_name=cid_name, container_args=f"-e HTTPD_MPM={mpm_config} --user 1001")
        cip = app.get_cip(cid_file_name=cid_name)
        # Let's check that server really response HTTP-403
        # See function here: in test/run `_run_mpm_config_test`
        # https://github.com/sclorg/httpd-container/blob/master/test/run#L97
        assert app.test_response(url=f"{cip}", port=8080, expected_code=403, expected_output=".*" )
        logs = app.get_logs(cid_file_name=cid_name)
        assert ContainerTestLibUtils.check_regexp_output(
            regexp_to_check=f"mpm_{mpm_config}:notice.*resuming normal operations",
            logs_to_check=logs
        )
    def test_log_to_data_volume(self, app):
        data_dir = ContainerTestLibUtils.create_local_temp_dir(
            dir_name="/tmp/httpd-test_log_dir"
        )
        ContainerTestLibUtils.commands_to_run(
            commands_to_run = [
                f"mkdir -p {data_dir}",
                f"chown -R 1001:1001 {data_dir}",
                f"chcon -Rvt svirt_sandbox_file_t {data_dir}/"
            ]
        )
        assert app.create_container(
            cid_file_name="test_log_dir",
            container_args=f"-e HTTPD_LOG_TO_VOLUME=1 --user 0 -v {data_dir}:/var/log/httpd"
        )
        cip = app.get_cip(cid_file_name="test_log_dir")
        assert app.test_response(url=f"{cip}", port=8080, expected_code=403, expected_output=".*")
        assert ContainerTestLibUtils.check_files_are_present(
            dir_name=data_dir, file_name_to_check=[
                "access_log",
                "error_log",
                "ssl_access_log",
                "ssl_error_log",
                "ssl_request_log",
            ]
        )

    def test_data_volume(self, app):
        data_dir = ContainerTestLibUtils.create_local_temp_dir(
            dir_name="/tmp/httpd-test-volume"
        )
        ContainerTestLibUtils.commands_to_run(
            commands_to_run = [
                f"mkdir -p {data_dir}/html",
                f"echo hello > {data_dir}/html/index.html",
                f"chown -R 1001:1001 {data_dir}",
                f"chcon -Rvt svirt_sandbox_file_t {data_dir}/"
            ]
        )
        assert app.create_container(
            cid_file_name="doc_root",
            container_args=f"-v {data_dir}:/var/www"
        )
        cip = app.get_cip(cid_file_name="doc_root")
        assert cip
        assert app.test_response(url=f"{cip}", port=8080, expected_code=200, expected_output="hello")

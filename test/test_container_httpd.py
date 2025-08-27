import os
import sys
import time

import pytest

from pathlib import Path

from container_ci_suite.container_lib import ContainerTestLib
from container_ci_suite.utils import check_variables

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
print(IMAGE_NAME)

image_name = IMAGE_NAME.split(":")[0]
image_tag = IMAGE_NAME.split(":")[1]
test_dir = os.path.join(os.getcwd())
print(f"Test dir is: {TEST_DIR}")


@pytest.fixture(scope="module")
def app(request):
    app = ContainerTestLib(image_name=IMAGE_NAME, s2i_image=True)
    # app_name = os.path.basename(request.param)
    yield app
    pass


class TestHttpdAppContainer:
    def test_default_path(self, app):
        assert app.create_container(cid_file="test_default_page")
        cip = app.get_cip("test_default_page")
        assert cip
        if OS == "c9s" or OS == "c10s":
            response = "HTTP Server Test Page"
        else:
            response = "Test Page for the HTTP Server on"
        assert app.test_response(url=f"{cip}", expected_code=403, expected_output=response, max_attempts=3)

    def test_run_as_root(self, app):
        assert app.create_container(cid_file="test_default_page", container_args="--user 0")
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
        # app.clean_app_images()

    def test_invalid_log_volume(self, app):
        assert app.create_container(cid_file="invalid_log_dir", container_args="-e HTTPD_LOG_TO_VOLUME=1 --user 1001")
        time.sleep(3)
        result_from_app = app.test_app_dockerfile()
        print(result_from_app)
        assert result_from_app == True
        assert app.get_container_exitcode(container_id="app_dockerfile") == "1"

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
        assert app.create_container(cid_file=cid_name, container_args=f"-e HTTPD_MPM={mpm_config} --user 1001")
        cid = app.get_cid(cid_name=cid_name)
        cip = app.get_cip(cid_name=cid_name)
        assert app.test_response(url=f"{cip}", port=8080, expected_code=403, expected_output=".*" )
        logs = app.get_logs(cid_name=cid_name)
        assert app.check_regexp_output(
            regexp_to_check=f"mpm_{mpm_config}:notice.*resuming normal operations",
            logs_to_check=logs
        )

    def test_data_volume(self, app):

        assert app.create_container(cid_file="data_volume", container_args="-e HTTPD_LOG_TO_VOLUME=1 --user 1001")
        result_from_app = app.test_app_dockerfile()
        print(result_from_app)
        assert result_from_app == True
        assert app.get_container_exitcode(container_id="app_dockerfile") == "1"
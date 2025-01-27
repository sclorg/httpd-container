import os
import sys
import pytest

from container_ci_suite.engines.container import ContainerImage
from container_ci_suite.utils import check_variables

if not check_variables():
    print("At least one variable from IMAGE_NAME, OS, VERSION is missing.")
    sys.exit(1)

VERSION = os.getenv("VERSION")
IMAGE_NAME = os.getenv("IMAGE_NAME")
OS = os.getenv("OS")

image_name = os.environ.get("IMAGE_NAME").split(":")[0]
image_tag = os.environ.get("IMAGE_NAME").split(":")[1]
test_dir = os.path.abspath(os.path.dirname(__file__))
print(f"Test dir is: {test_dir}")


@pytest.fixture(scope="module")
def app(request):
    app = ContainerImage(image_name)
    print(request)
    # app_name = os.path.basename(request.param)
    yield app
    pass
    app.cleanup_container()


class TestHttpdAppContainer:
    def test_default_path(self, app):
        assert app.create_container(cid_file="test_default_page")
        cip = app.get_cip()
        assert cip
        if OS == "c9s" or OS == "c10s":
            response = "HTTP Server Test Page"
        else:
            response = "Test Page for the HTTP Server on"
        assert app.test_response(url=f"{cip}", expected_code=403, expected_output=response, max_tests=3)

    def test_run_as_root(self, app):
        assert app.create_container(cid_file="test_default_page", container_args="--user 0")
        cip = app.get_cip()
        assert cip
        if OS == "c9s" or OS == "c10s":
            response = "HTTP Server Test Page"
        else:
            response = "Test Page for the HTTP Server on"
        assert app.test_response(url=f"{cip}", expected_code=403, expected_output=response, max_tests=3)

    def test_run_s2i_usage(self, app):
        assert app.s2i_usage() != ""

    @pytest.mark.parametrize(
        "dockerfile",
        [
            "Dockerfile",
            "Dockerfile.s2i"
        ]
    )
    def test_dockerfiles(self, app, dockerfile):
        assert app.build_test_container(
            dockerfile=f"test/examples/{dockerfile}", app_url="https://github.com/sclorg/httpd-ex.git",
            app_dir="app-src"
        )
        assert app.test_run_app_dockerfile()
        cip = app.get_app_cip()
        assert cip
        assert app.test_response(url=f"{cip}", expected_code=200, expected_output="Welcome to your static httpd application on OpenShift")
        app.rmi_app()


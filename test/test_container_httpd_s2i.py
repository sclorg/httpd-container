import os
import sys
import pytest

from pathlib import Path

from container_ci_suite.container_lib import ContainerTestLib
from container_ci_suite.utils import check_variables


from constants import return_app_name


if not check_variables():
    print("At least one variable from OS, VERSION is missing.")
    sys.exit(1)


TEST_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
VERSION = os.getenv("VERSION")
OS = os.getenv("TARGET")
IMAGE_NAME = os.getenv("IMAGE_NAME")
if not IMAGE_NAME:
    print(f"Built container for version {VERSION} on OS {OS} does not exist.")
    sys.exit(1)

image_tag_wo_tag = IMAGE_NAME.split(":")[0]
image_tag = IMAGE_NAME.split(":")[1]
pre_init_test_app = os.path.join(TEST_DIR, "pre-init-test-app")
sample_test_app = os.path.join(TEST_DIR, "sample-test-app")


@pytest.fixture(scope="module", params=[pre_init_test_app])
def s2i_app_pre_init(request):
    container_lib = ContainerTestLib(IMAGE_NAME)
    app_name = return_app_name(request)
    s2i_app = container_lib.build_as_df(
        app_path=request.param,
        s2i_args="--pull-policy=never",
        src_image=IMAGE_NAME,
        dst_image=f"{IMAGE_NAME}-{app_name}"
    )
    yield s2i_app
    s2i_app.clean_containers()


@pytest.fixture(scope="module", params=[sample_test_app])
def s2i_sample_app(request):
    ci = ContainerTestLib(IMAGE_NAME)
    app_name = return_app_name(request)
    s2i_app = ci.build_as_df(
        app_path=request.param,
        s2i_args="--pull-policy=never",
        src_image=IMAGE_NAME,
        dst_image=f"{IMAGE_NAME}-{app_name}"
    )
    yield s2i_app
    s2i_app.clean_containers()


class TestHttpdS2IPreInitContainer:

    def test_run_pre_init_test(self, s2i_app_pre_init):
        assert s2i_app_pre_init.create_container(cid_file_name=s2i_app_pre_init.app_name, container_args="--user 1000")
        cip = s2i_app_pre_init.get_cip(cid_file_name=s2i_app_pre_init.app_name)
        assert cip
        response = f"This content was replaced by pre-init script."
        assert s2i_app_pre_init.test_response(url=f"{cip}", expected_code=200, expected_output=response)


class TestHttpdS2ISampleAppContainer:

    def test_sample_app(self, s2i_sample_app):
        assert s2i_sample_app.create_container(cid_file_name=s2i_sample_app.app_name, container_args="--user 1000")
        cip = s2i_sample_app.get_cip(cid_file_name=s2i_sample_app.app_name)
        assert cip
        response = "This is a sample s2i application with static content."
        assert s2i_sample_app.test_response(url=f"{cip}", expected_code=200, expected_output=response)
        assert s2i_sample_app.test_response(
            url=f"https://{cip}",
            port=8443,
            expected_output=response
        )


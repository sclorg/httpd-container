import os
import sys
import pytest

from container_ci_suite.engines.s2i_container import S2IContainerImage
from container_ci_suite.utils import check_variables

if not check_variables():
    print("At least one variable from IMAGE_NAME, OS, VERSION is missing.")
    sys.exit(1)

VERSION = os.getenv("VERSION")
IMAGE_NAME = os.getenv("IMAGE_NAME")
OS = os.getenv("TARGET")

full_image_name = os.environ.get("IMAGE_NAME")
image_tag_wo_tag = os.environ.get("IMAGE_NAME").split(":")[0]
image_tag = os.environ.get("IMAGE_NAME").split(":")[1]
test_dir = os.path.abspath(os.path.dirname(__file__))
pre_init_test_app = os.path.join(test_dir, "..", "pre-init-test-app")
self_cert_test = os.path.join(test_dir, "..", "self-signed-ssl")
sample_test_app = os.path.join(test_dir, "..", "sample-test-app")

app_params_pre = [pre_init_test_app]
app_params_sample = [sample_test_app]


@pytest.fixture(scope="module", params=app_params_pre)
def s2i_app_pre_init(request):
    ci = S2IContainerImage(full_image_name)
    app_name = os.path.basename(request.param)
    s2i_app = ci.s2i_build_as_df(
        app_path=request.param,
        s2i_args="--pull-policy=never",
        src_image=full_image_name,
        dst_image=f"{full_image_name}-{app_name}"
    )
    yield s2i_app
    pass
    if s2i_app:
        s2i_app.cleanup_container()


@pytest.fixture(scope="module", params=app_params_sample)
def s2i_sample_app(request):
    ci = S2IContainerImage(full_image_name)
    app_name = os.path.basename(request.param)
    s2i_app = ci.s2i_build_as_df(
        app_path=request.param,
        s2i_args="--pull-policy=never",
        src_image=full_image_name,
        dst_image=f"{full_image_name}-{app_name}"
    )
    yield s2i_app
    pass
    if s2i_app:
        s2i_app.cleanup_container()


@pytest.mark.usefixtures("s2i_app_pre_init")
class TestHttpdS2IPreInitContainer:

    def test_run_pre_init_test(self, s2i_app_pre_init):
        print("run_pre_init_test")
        assert s2i_app_pre_init
        assert s2i_app_pre_init.create_container(cid_file="testing-app-pre-init", container_args="--user 1000", image_name=s2i_app_pre_init.image_name)
        cip = s2i_app_pre_init.get_cip()
        assert cip
        response = "This content was replaced by pre-init script."
        assert s2i_app_pre_init.test_response(url=f"{cip}", expected_code=200, expected_output=response)


@pytest.mark.usefixtures("s2i_sample_app")
class TestHttpdS2ISampleAppContainer:

    def test_self_cert_test(self, s2i_sample_app):
        print("run_pre_init_test")
        assert s2i_sample_app
        assert s2i_sample_app.create_container(cid_file="testing-sample=app", container_args="--user 1000", image_name=s2i_sample_app.image_name)
        cip = s2i_sample_app.get_cip()
        assert cip
        response = "This is a sample s2i application with static content."
        assert s2i_sample_app.test_response(url=f"{cip}", expected_code=200, expected_output=response)

import os
import sys
import pytest
import time

from pathlib import Path
from datetime import datetime

from container_ci_suite.container_lib import ContainerTestLib
from container_ci_suite.utils import check_variables, ContainerTestLibUtils
from container_ci_suite.engines.podman_wrapper import PodmanCLIWrapper

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
self_cert_test = os.path.join(TEST_DIR, "self-signed-ssl")
sample_test_app = os.path.join(TEST_DIR, "sample-test-app")

app_params_sample = [sample_test_app]
app_params_ssl = [self_cert_test]


@pytest.fixture(scope="module", params=app_params_sample)
def s2i_sample_app(request):
    ci = ContainerTestLib(IMAGE_NAME)
    s2i_app = ci.build_as_df(
        app_path=request.param,
        s2i_args="--pull-policy=never",
        src_image=IMAGE_NAME,
        dst_image=f"{IMAGE_NAME}-cert-age"
    )
    yield s2i_app
    pass
    s2i_app.clean_containers()

@pytest.fixture(scope="module", params=app_params_ssl)
def ssl_app(request):
    ci = ContainerTestLib(IMAGE_NAME)
    app_name = os.path.basename(request.param)
    s2i_app = ci.build_as_df(
        app_path=request.param,
        s2i_args="--pull-policy=never",
        src_image=IMAGE_NAME,
        dst_image=f"{IMAGE_NAME}-self-signed"
    )
    yield s2i_app
    pass
    s2i_app.clean_containers()

@pytest.fixture(scope="module")
def app(request):
    app = ContainerTestLib(image_name=IMAGE_NAME, s2i_image=True)
    yield app
    pass
    app.clean_containers()
    app.clean_app_images()


@pytest.mark.usefixtures("ssl_app")
class TestHttpdS2ISslSelfSignedAppContainer:

    def test_self_cert_test(self, ssl_app):
        ssl_app.set_new_image(image_name=f"{IMAGE_NAME}-self-signed")
        assert ssl_app.create_container(cid_file="test-ssl-cert", container_args="--user 1000")
        cip = ssl_app.get_cip(cid_name="test-ssl-cert")
        assert cip
        response = ".*"
        assert ssl_app.test_response(url=f"{cip}", expected_code=200, expected_output=response)
        assert ssl_app.test_response(url=f"https://{cip}", port=8443, expected_output="SSL test works")
        server_cmd = f"openssl s_client -showcerts -servername {cip} -connect {cip}:8443 2>/dev/null"
        server_output = ContainerTestLibUtils.run_command(cmd=server_cmd, return_output=True, debug=True)
        print(f"server out from openssl command {server_output}")
        certificate_dir = ContainerTestLibUtils.create_local_temp_dir("server_cert_dir")
        with open(Path(certificate_dir) / "output", mode="wt+") as f:
            f.write(server_output)
        server_cert = ContainerTestLibUtils.run_command(
            cmd=f"openssl x509 -inform pem -noout -text -in {Path(certificate_dir)}/output",
            return_output=True,
            debug=True
        )
        config_cmd = f"openssl x509 -in {TEST_DIR}/self-signed-ssl/httpd-ssl/certs/server-cert-selfsigned.pem -inform pem -noout -text"
        config_cert = ContainerTestLibUtils.run_command(cmd=config_cmd, return_output=True)
        assert server_cert == config_cert


@pytest.mark.usefixtures("s2i_sample_app")
class TestHttpdCertAgeContainer:

    def test_cert_age(self, s2i_sample_app):
        assert s2i_sample_app.create_container(cid_file="cert-age", container_args="--user 1000")
        image_age_s = PodmanCLIWrapper.podman_inspect(
            field="{{.Created}}", src_image=IMAGE_NAME
        ).strip().split(' ')
        image_age = time.time() - float(ContainerTestLibUtils.run_command(
            cmd=f"date -d '{image_age_s[0]} {image_age_s[1]} {image_age_s[2]}' '+%s'", return_output=True
        ))
        cid = s2i_sample_app.get_cid("cert-age")
        certificate_age_s = PodmanCLIWrapper.podman_exec_bash_command(
            image_name=cid, cmd="cat \\$HTTPD_TLS_CERT_PATH/localhost.crt"
        ).strip()
        certificate_dir = ContainerTestLibUtils.create_local_temp_dir("cert_dir")
        with open(Path(certificate_dir) / "cert", mode="wt+") as f:
            f.write(certificate_age_s)
        certificate_age_s = ContainerTestLibUtils.run_command(
            cmd=f"openssl x509 -startdate -noout -in {Path(certificate_dir)}/cert", return_output=True
        ).strip().replace("notBefore=", "")
        certificate_age = time.time() - float(ContainerTestLibUtils.run_command(
            cmd=f"date '+%s' --date='{certificate_age_s}'")
        )
        assert certificate_age < image_age
        assert PodmanCLIWrapper.podman_exec_bash_command(
            image_name=cid, cmd="ls -la \\$HTTPD_TLS_CERT_PATH/localhost.crt"
        )
        assert PodmanCLIWrapper.podman_exec_bash_command(
            image_name=cid, cmd="ls -la \\$HTTPD_TLS_CERT_PATH/localhost.key"
        )

import os
import sys
import time
import tempfile

from pathlib import Path

from container_ci_suite.container_lib import ContainerTestLib
from container_ci_suite.utils import ContainerTestLibUtils, check_variables
from container_ci_suite.engines.podman_wrapper import PodmanCLIWrapper

if not check_variables():
    sys.exit(1)

TEST_DIR = Path(__file__).parent.absolute()
VERSION = os.getenv("VERSION")
OS = os.getenv("OS").lower()
IMAGE_NAME = os.getenv("IMAGE_NAME")


pre_init_test_app = TEST_DIR / "pre-init-test-app"
sample_test_app = TEST_DIR / "sample-test-app"
self_cert_test = TEST_DIR / "self-signed-ssl"


def build_s2i_app(app_path: Path) -> ContainerTestLib:
    container_lib = ContainerTestLib(IMAGE_NAME)
    app_name = app_path.name
    s2i_app = container_lib.build_as_df(
        app_path=app_path,
        s2i_args="--pull-policy=never",
        src_image=IMAGE_NAME,
        dst_image=f"{IMAGE_NAME}-{app_name}"
    )
    return s2i_app


class TestHttpdS2IPreInitContainer:

    def setup_method(self):
        self.s2i_app = build_s2i_app(pre_init_test_app)

    def teardown_method(self):
        self.s2i_app.cleanup()

    def test_run_pre_init_test(self):
        assert self.s2i_app.create_container(cid_file_name=self.s2i_app.app_name, container_args="--user 1000")
        cip = self.s2i_app.get_cip(cid_file_name=self.s2i_app.app_name)
        assert cip
        assert self.s2i_app.test_response(
            url=cip,
            expected_code=200,
            expected_output="This content was replaced by pre-init script."
        )


class TestHttpdS2ISampleAppContainer:

    def setup_method(self):
        self.s2i_app = build_s2i_app(sample_test_app)

    def teardown_method(self):
        self.s2i_app.cleanup()

    def test_sample_app(self):
        assert self.s2i_app.create_container(cid_file_name=self.s2i_app.app_name, container_args="--user 1000")
        cip = self.s2i_app.get_cip(cid_file_name=self.s2i_app.app_name)
        assert cip
        response = "This is a sample s2i application with static content."
        assert self.s2i_app.test_response(
            url=cip,
            expected_code=200,
            expected_output=response
        )
        assert self.s2i_app.test_response(
            url=f"https://{cip}",
            port=8443,
            expected_output=response
        )


class TestHttpdCertAgeContainer:

    def setup_method(self):
        self.s2i_app = build_s2i_app(sample_test_app)

    def teardown_method(self):
        self.s2i_app.cleanup()

    def test_cert_age(self):
        """
        We need to make sure the certificate is generated no sooner than in assemble phase,
        because shipping the same certs in the image would make it easy to exploit
        Let's see how old the certificate is and compare with how old the image is
        """
        assert self.s2i_app.create_container(cid_file_name=self.s2i_app.app_name, container_args="--user 1000")
        image_age_s = PodmanCLIWrapper.podman_inspect(
            field="{{.Created}}", src_image=IMAGE_NAME
        ).strip().split(' ')
        image_age = time.time() - float(ContainerTestLibUtils.run_command(
            cmd=f"date -d '{image_age_s[0]} {image_age_s[1]} {image_age_s[2]}' '+%s'"
        ))
        cid = self.s2i_app.get_cid(self.s2i_app.app_name)
        # Testing of not presence of a certificate in the production image
        certificate_content = PodmanCLIWrapper.podman_exec_shell_command(
            cid_file_name=cid, cmd="cat \\$HTTPD_TLS_CERT_PATH/localhost.crt"
        )
        assert certificate_content
        certificate_dir = tempfile.mkdtemp(prefix="/tmp/cert_dir")
        with open(Path(certificate_dir) / "cert", mode="w") as f:
            f.write(certificate_content.strip())
        certificate_age_s = ContainerTestLibUtils.run_command(
            cmd=f"openssl x509 -startdate -noout -in {Path(certificate_dir)}/cert"
        ).strip().replace("notBefore=", "")
        certificate_age = time.time() - float(ContainerTestLibUtils.run_command(
            cmd=f"date '+%s' --date='{certificate_age_s}'")
        )
        # Testing whether the certificate was freshly generated after the image
        assert certificate_age < image_age
        # Testing presence and permissions of the generated certificate
        assert PodmanCLIWrapper.podman_exec_shell_command(
            cid_file_name=cid, cmd="ls -l \\$HTTPD_TLS_CERT_PATH/localhost.crt"
        )
        # Testing presence and permissions of the generated certificate
        assert PodmanCLIWrapper.podman_exec_shell_command(
            cid_file_name=cid, cmd="ls -l \\$HTTPD_TLS_CERT_PATH/localhost.key"
        )

class TestHttpdS2ISslSelfSignedAppContainer:

    def setup_method(self):
        self.s2i_app = build_s2i_app(self_cert_test)

    def teardown_method(self):
        self.s2i_app.cleanup()

    def test_self_cert_test(self):
        """
        Test s2i use case #3 - using own ssl certs
        Since we built the candidate image locally, we don't want S2I attempt to pull
        it from Docker hub
        """
        self.s2i_app.set_new_image(image_name=f"{IMAGE_NAME}-{self.s2i_app.app_name}")
        assert self.s2i_app.create_container(cid_file_name=self.s2i_app.app_name, container_args="--user 1000")
        cip = self.s2i_app.get_cip(cid_file_name=self.s2i_app.app_name)
        assert cip
        assert self.s2i_app.test_response(url=cip, expected_code=200, expected_output="SSL test works")
        assert self.s2i_app.test_response(url=f"https://{cip}", port=8443, expected_output="SSL test works")
        server_cmd = f"openssl s_client -showcerts -servername {cip} -connect {cip}:8443 2>/dev/null"
        server_output = ContainerTestLibUtils.run_command(cmd=server_cmd)
        certificate_dir = tempfile.mkdtemp(prefix="/tmp/server_cert_dir")
        with open(Path(certificate_dir) / "output", mode="wt+") as f:
            f.write(server_output)
        server_cert = ContainerTestLibUtils.run_command(
            cmd=f"openssl x509 -inform pem -noout -text -in {Path(certificate_dir)}/output"
        )
        config_cmd = f"openssl x509 -in {TEST_DIR}/{self.s2i_app.app_name}/httpd-ssl/certs/server-cert-selfsigned.pem -inform pem -noout -text"
        config_cert = ContainerTestLibUtils.run_command(cmd=config_cmd)
        assert server_cert == config_cert

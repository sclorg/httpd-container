import os
import time
import tempfile

from pathlib import Path

from container_ci_suite.container_lib import ContainerTestLib
from container_ci_suite.utils import ContainerTestLibUtils
from container_ci_suite.engines.podman_wrapper import PodmanCLIWrapper


TEST_DIR = Path(__file__).parent.absolute()
VERSION = os.getenv("VERSION")
OS = os.getenv("TARGET")
IMAGE_NAME = os.getenv("IMAGE_NAME")


pre_init_test_app = TEST_DIR / "pre-init-test-app"
sample_test_app = TEST_DIR / "sample-test-app"


class TestHttpdS2IPreInitContainer:

    def setup_method(self):
        self.container_lib = ContainerTestLib(IMAGE_NAME)
        print(self.container_lib)
        app_name = pre_init_test_app.name
        print(app_name)
        self.s2i_app = self.container_lib.build_as_df(
            app_path=pre_init_test_app,
            s2i_args="--pull-policy=never",
            src_image=IMAGE_NAME,
            dst_image=f"{IMAGE_NAME}-{app_name}"
        )

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
        self.ci = ContainerTestLib(IMAGE_NAME)
        app_name = sample_test_app.name
        self.s2i_app = self.ci.build_as_df(
            app_path=sample_test_app,
            s2i_args="--pull-policy=never",
            src_image=IMAGE_NAME,
            dst_image=f"{IMAGE_NAME}-{app_name}"
        )

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
        self.ci = ContainerTestLib(IMAGE_NAME)
        app_name = sample_test_app.name
        self.s2i_app = self.ci.build_as_df(
            app_path=sample_test_app,
            s2i_args="--pull-policy=never",
            src_image=IMAGE_NAME,
            dst_image=f"{IMAGE_NAME}-{app_name}"
        )

    def teardown_method(self):
        self.s2i_app.cleanup()

    """
    This tests checks whether the certificate was freshly generated after the image
    We need to make sure the certificate is generated no sooner than in assemble phase,
    because shipping the same certs in the image would make it easy to exploit
    Let's see how old the certificate is and compare with how old the image is
    """
    def test_cert_age(self):
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
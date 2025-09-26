import os
import tempfile

from pathlib import Path

from container_ci_suite.container_lib import ContainerTestLib
from container_ci_suite.utils import ContainerTestLibUtils


TEST_DIR = Path(__file__).parent.absolute()
VERSION = os.getenv("VERSION")
OS = os.getenv("TARGET")
IMAGE_NAME = os.getenv("IMAGE_NAME")


self_cert_test = TEST_DIR / "self-signed-ssl"


class TestHttpdS2ISslSelfSignedAppContainer:

    def setup_method(self):
        self.ci = ContainerTestLib(IMAGE_NAME)
        app_name = self_cert_test.name
        self.s2i_app = self.ci.build_as_df(
            app_path=self_cert_test,
            s2i_args="--pull-policy=never",
            src_image=IMAGE_NAME,
            dst_image=f"{IMAGE_NAME}-{app_name}"
        )

    def teardown_method(self):
        self.s2i_app.cleanup()

    """
        Test s2i use case #3 - using own ssl certs
        Since we built the candidate image locally, we don't want S2I attempt to pull
        it from Docker hub
    """
    def test_self_cert_test(self):
        self.s2i_app.set_new_image(image_name=f"{IMAGE_NAME}-{self.s2i_app.app_name}")
        assert self.s2i_app.create_container(cid_file_name=self.s2i_app.app_name, container_args="--user 1000")
        cip = self.s2i_app.get_cip(cid_file_name=self.s2i_app.app_name)
        assert cip
        response = ".*"
        assert self.s2i_app.test_response(url=cip, expected_code=200, expected_output=response)
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

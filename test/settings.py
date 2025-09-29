import os

from pathlib import Path


VERSION = os.getenv("VERSION")
OS = os.getenv("OS").lower()
IMAGE_NAME = os.getenv("IMAGE_NAME")
TEST_DIR = Path(__file__).parent.absolute()

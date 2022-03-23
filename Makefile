# Variables are documented in common/build.sh.
BASE_IMAGE_NAME = httpd
VERSIONS = 2.4 2.4-micro
OPENSHIFT_NAMESPACES = 
DOCKER_BUILD_CONTEXT = ..

# HACK:  Ensure that 'git pull' for old clones doesn't cause confusion.
# New clones should use '--recursive'.
.PHONY: $(shell test -f common/common.mk || echo >&2 'Please do "git submodule update --init" first.')

include common/common.mk

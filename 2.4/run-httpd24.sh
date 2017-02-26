#!/bin/bash

source /usr/share/container-scripts/httpd/common.sh

config_general

# Check whether we run as s2i
echo "$@" | grep --quiet "$STI_SCRIPTS_PATH"
if [ $? -ne 0 ] && runs_privileged ; then
  config_privileged
else
  # We run as non-root or as s2i
  config_s2i
fi

set -eu

exec "$@"

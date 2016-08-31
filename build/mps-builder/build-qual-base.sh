#!/bin/sh

# This script builds the base packages needed for a Qual build.
# It should be run from within the docker container.

set -e

git config --global credential.helper 'cache --timeout=7200'

cd /mnt/workspace
./build.sh kernel
./build.sh kernel-modules
./build.sh packages

echo
echo "Still in docker; at root prompt below type:"
echo "   exit"

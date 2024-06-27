#!/bin/bash

echo "os: $OSTYPE"
echo "shell: $SHELL"
export PATH=$PATH:$PWD

# --------------------------------------------
# Options that must be configured by app owner
# --------------------------------------------
# shellcheck disable=SC2034
APP_NAME="hccm"  # name of app-sre "application" folder this component lives in
# shellcheck disable=SC2034
COMPONENT_NAME="nise-populator"  # name of app-sre "resourceTemplate" in deploy.yaml for this component
# shellcheck disable=SC2034
IMAGE="quay.io/cloudservices/nise-populator"

echo "LABEL quay.expires-after=3d" >> ./Dockerfile # tag expire in 3 days

# Install bonfire repo/initialize
CICD_URL=https://raw.githubusercontent.com/RedHatInsights/bonfire/master/cicd
curl -s "$CICD_URL"/bootstrap.sh > .cicd_bootstrap.sh && source .cicd_bootstrap.sh

source "$CICD_ROOT"/build.sh

source "$CICD_ROOT"/_common_deploy_logic.sh
NAMESPACE=$(bonfire namespace reserve)
export NAMESPACE
oc process --local -f deploy/clowdapp.yaml -p IMAGE_TAG="${IMAGE_TAG}" | oc apply -f - -n "$NAMESPACE"

mkdir -p "$WORKSPACE"/artifacts
cat << EOF > "${WORKSPACE}"/artifacts/junit-dummy.xml
<testsuite tests="1">
    <testcase classname="dummy" name="dummytest"/>
</testsuite>
EOF

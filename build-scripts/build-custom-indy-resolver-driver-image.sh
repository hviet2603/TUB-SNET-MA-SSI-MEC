#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Variables
REPO_URL="https://github.com/decentralized-identity/uni-resolver-driver-did-indy.git"
REPO_NAME="uni-resolver-driver-did-indy"
DOCKERFILE_SOURCE="../../dockerfiles/custom_indy_resolver_driver.dockerfile"
VON_NET_GENESIS_FILE="../../bootstrap/genesis.txt"
GENESIS_DESTINATION="./sovrin"
RELEASE_TAG="0.17.0"

# Clone the repository
git clone "$REPO_URL"
cd "$REPO_NAME"

# Checkout the specific release tag
git checkout "tags/$RELEASE_TAG"

# Replace the Dockerfile
if [ ! -f "$DOCKERFILE_SOURCE" ]; then
    echo "Error: Dockerfile not found in the upper folder."
    exit 1
fi
cp "$DOCKERFILE_SOURCE" docker/Dockerfile

# Copy the genesis file
if [ ! -f "$VON_NET_GENESIS_FILE" ]; then
    echo "Error: Genesis file not found in the bootstrap folder."
    exit 1
fi
cp "$VON_NET_GENESIS_FILE" "$GENESIS_DESTINATION/snet-hv.txn"

# Build Docker image
docker build -t vdocker2603/ma-ssi-custom-indy-resolver-driver:latest -f docker/Dockerfile .

# Go back and remove the cloned repository
cd ..
rm -rf "$REPO_NAME"
#!/bin/bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

cd "$(dirname "$SCRIPT_PATH")/../"

docker build -t vdocker2603/ma-ssi-apps:latest -f ./dockerfiles/apps.dockerfile .
#!/bin/sh
# What Kermo checks before it takes this catalog, checked here first: catalog.json is what the folders make (every
# file's sha256), and catalog.json.sig is its signature by the key whose public half is kermo-tools.pub.
set -eu
cd "$(dirname "$0")/.."
ssl=${OPENSSL:-openssl}
python3 scripts/build-catalog.py --check
sig=$(mktemp)
trap 'rm -f "$sig"' EXIT
base64 -d < catalog.json.sig > "$sig"
"$ssl" pkeyutl -verify -pubin -inkey kermo-tools.pub -rawin -in catalog.json -sigfile "$sig"

#!/bin/sh
# Signs catalog.json with the catalog's Ed25519 key: catalog.json.sig, the signature in base64. Needs OpenSSL 3
# (`brew install openssl@3`: the openssl macOS ships can't sign with Ed25519). Then checks it with kermo-tools.pub.
#   scripts/sign.sh /Volumes/<your key's disk>/kermo-tools.key
set -eu
key=${1:?usage: scripts/sign.sh <private key .pem>}
ssl=$(command -v /opt/homebrew/opt/openssl@3/bin/openssl /usr/local/opt/openssl@3/bin/openssl openssl | head -1)
"$ssl" version | grep -q '^OpenSSL 3' || { echo "sign.sh: needs OpenSSL 3 (brew install openssl@3)" >&2; exit 1; }
cd "$(dirname "$0")/.."
"$ssl" pkeyutl -sign -inkey "$key" -rawin -in catalog.json | base64 > catalog.json.sig
OPENSSL="$ssl" scripts/verify.sh

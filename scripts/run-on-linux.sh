#!/bin/sh
# Run inside a Linux image (CI: Debian, Ubuntu, Fedora, Alpine) from the repository's root: every script parses under
# that system's sh, and the scripts that only read the system run. Their output goes to <out>, which the macOS job
# parses with each tool's preset (tools-lint --fixtures): the preset reads what that system really prints.
#   docker run --rm -v "$PWD:/w" -w /w debian:12 sh scripts/run-on-linux.sh out
set -u
out=${1:?usage: scripts/run-on-linux.sh <out folder>}
mkdir -p "$out"
failed=0
for f in $(find tools community -name '*.sh' 2>/dev/null | sort); do
  sh -n "$f" || { echo "✕ $f doesn't parse with this system's sh"; failed=1; }
done
newest() { ls -d "tools/$1"/* | sort -t/ -k3 -n | tail -1; }
EVERY=1 timeout 5 sh "$(newest system)/system.stream.sh" > "$out/system.stream.jsonl"
[ -s "$out/system.stream.jsonl" ] || { echo "✕ system.stream.sh printed nothing"; failed=1; }
ONCE=1 TOP=0 timeout 15 sh "$(newest system)/system.stream.sh" > "$out/system.list.json"   # All Processes: one line, every process
[ -s "$out/system.list.json" ] || { echo "✕ system.stream.sh with ONCE=1 TOP=0 printed nothing"; failed=1; }
sh "$(newest sysinfo)/sysinfo.report.sh" > "$out/sysinfo.report.txt" || { echo "✕ sysinfo.report.sh failed"; failed=1; }
[ "$failed" = 0 ] && echo "✓ $(sed -n 's/^PRETTY_NAME=//p' /etc/os-release | tr -d '"'): scripts parse, system (stream and list) and sysinfo run"
exit "$failed"

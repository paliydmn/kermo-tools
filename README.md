# kermo-tools

The catalog of tools for [Kermo](https://github.com/paliydmn/kermo): ready-made presets — a server's firewall, its
deployments, backups, its load — that Kermo's **Tools window ▸ Catalog** lists, and **Get** puts in your
`~/.config/dfilemanager/tools/`. A preset is a JSON file (and maybe a script) that says what to run on a server and how
to show it; [docs/tools.md](https://github.com/paliydmn/kermo/blob/master/docs/tools.md) has every field.

Kermo fetches this catalog only when you open the Catalog or choose Check for Updates…. It takes `catalog.json` only
signed with the key built into Kermo (`catalog.json.sig`), never an index older than one it has seen (`serial`), and
each file only with the sha256 the signed index gives it. Whoever could change the files here couldn't sign them.

## Layout

```
catalog.json          the index: each tool's versions, their files by path and sha256, a serial that only grows
catalog.json.sig      its Ed25519 signature, base64 (wrapped or not)
kermo-tools.pub       the public key (the same one built into Kermo)
tools/<id>/<version>/ a reviewed tool ("verified"): <id>.json, whose catalogVersion is <version>, and its scripts
community/<id>/<version>/  one sent by someone else, not reviewed ("community")
fixtures/             recorded output of the programs, without real names or addresses: CI parses it with the presets
scripts/              build-catalog.py, sign.sh, verify.sh, run-on-linux.sh
```

A version's folder holds the preset and the scripts it names — nothing else, or Kermo won't take it. Each script is
named `<id>.<name>` (`restic.backup.sh`) and isn't JSON, so none can land on another tool's file or on one of Kermo's
own in `~/.config/dfilemanager/tools/`; 20 files at most. A new version is a new folder; an old one stays for the
Kermo versions that can't read the new (`minKermo`).

## Adding or changing a tool

1. A new folder `tools/<id>/<version>/` with `<id>.json` (`"catalogVersion": <version>`) and its scripts.
2. Recorded output in `fixtures/<id>.<list|stream|poll>.<ext>`, with names and addresses made up.
3. `python3 scripts/build-catalog.py` — the index, its serial one higher.
4. `scripts/sign.sh <key>` — the signature, then checked.
5. A pull request: CI runs Kermo's own checks on every preset and its recorded output, and each script on Debian,
   Ubuntu, Fedora and Alpine.

Someone else's tool goes to `community/` and is signed like the rest: the signature says it came through this
repository, "verified" that it was reviewed.

## CI

- **catalog**: `catalog.json` is what the folders make, and its signature checks with `kermo-tools.pub`.
- **linux** (Debian 12, Ubuntu 24.04, Fedora 41, Alpine 3.20): every script parses under that system's `sh` (dash, bash,
  busybox); System's stream and Server Info's report run there, their output kept.
- **presets** (macOS): `tools-lint`, built from Kermo's source, loads every preset, and parses `fixtures/` and what the
  Linux jobs recorded with the newest version of each tool.

## The key

The private key never touches this repository, CI or a machine that's online for long: it lives offline, and only signs
`catalog.json`. If it's ever lost or exposed, a Kermo release with a new key is the only way out — so it has a backup,
offline too. Generating it (OpenSSL 3; macOS's own `openssl` can't):

```sh
openssl genpkey -algorithm ed25519 -out kermo-tools.key
openssl pkey -in kermo-tools.key -pubout -out kermo-tools.pub
openssl pkey -in kermo-tools.key -pubout -outform DER | tail -c 32 | base64   # the key Kermo has built in
```

## License

MIT, as Kermo.

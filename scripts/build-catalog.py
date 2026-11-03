#!/usr/bin/env python3
"""Writes catalog.json, the index Kermo reads, from the tools' folders.

Each tools/<id>/<version>/ (reviewed: "verified") or community/<id>/<version>/ (not reviewed) folder is one version of
a tool: its <id>.json, whose catalogVersion is that version, and the scripts it names, each <id>.<name> and not JSON
(20 files at most) — nothing else, or Kermo won't take it. Each file is listed by its path and sha256. The serial
grows by one with every index written: Kermo takes no index older than one it has seen. Sign it with scripts/sign.sh.

  scripts/build-catalog.py           write catalog.json, serial + 1
  scripts/build-catalog.py --check   exit 1 if catalog.json isn't what the folders make (CI)
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "catalog.json")


def sha256(path):
    with open(os.path.join(ROOT, path), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def entries():
    out = []
    for kind, verified in (("tools", True), ("community", False)):
        base = os.path.join(ROOT, kind)
        for tid in sorted(os.listdir(base)) if os.path.isdir(base) else []:
            for ver in sorted((v for v in os.listdir(os.path.join(base, tid)) if v.isdigit()), key=int):
                folder = f"{kind}/{tid}/{ver}"
                with open(os.path.join(ROOT, folder, tid + ".json"), encoding="utf-8") as f:
                    p = json.load(f)
                if p.get("id") != tid or p.get("catalogVersion") != int(ver):
                    sys.exit(f"{folder}/{tid}.json: its id must be {tid} and its catalogVersion {ver}")
                e = {"id": tid, "title": p["title"], "version": int(ver), "verified": verified}
                e.update({k: p[k] for k in ("tool", "icon", "about", "author", "minKermo") if k in p})
                names = sorted(n for n in os.listdir(os.path.join(ROOT, folder)) if not n.startswith("."))
                odd = [n for n in names if n != tid + ".json" and (not n.startswith(tid + ".") or n.endswith((".json", ".bak")))]
                if odd or len(names) > 20:
                    sys.exit(f"{folder}: a script is named {tid}.<name>, not JSON, 20 files at most: {', '.join(odd) or len(names)}")
                e["files"] = [{"path": f"{folder}/{n}", "sha256": sha256(f"{folder}/{n}")} for n in names]
                out.append(e)
    return out


def main():
    old = {}
    if os.path.exists(INDEX):
        with open(INDEX, encoding="utf-8") as f:
            old = json.load(f)
    tools = entries()
    if sys.argv[1:] == ["--check"]:
        if old.get("tools") != tools:
            sys.exit("catalog.json isn't what the folders make: run scripts/build-catalog.py, then scripts/sign.sh")
        print(f"catalog.json: {len(tools)} versions, serial {old.get('serial')}: as the folders make it")
        return
    index = {"catalog": 1, "serial": old.get("serial", 0) + 1, "tools": tools}
    with open(INDEX, "w", encoding="utf-8") as f:
        f.write(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    print(f"catalog.json: {len(tools)} versions, serial {index['serial']}. Now sign it: scripts/sign.sh <key.pem>")


if __name__ == "__main__":
    main()

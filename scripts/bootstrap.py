"""Install checksum-pinned external tools into .tools/bin (Linux x86_64)."""

import argparse
import hashlib
import io
import json
import platform
import tarfile
import urllib.request
from pathlib import Path

import files

ROOT = Path(__file__).resolve().parents[1]


def install(name, spec, root=ROOT):
    request = urllib.request.Request(spec["url"], headers={"User-Agent": "project-blueprints"})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != spec["sha256"]:
        raise ValueError(f"{name}: archive checksum mismatch")
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        member = archive.getmember(spec["member"])
        if not member.isfile():
            raise ValueError(f"{name}: binary member is not a file")
        binary = archive.extractfile(member).read()
    target = root / ".tools/bin" / spec["binary"]
    files.check_paths(root, [target])
    target.parent.mkdir(parents=True, exist_ok=True)
    files.write_bytes(root, target, binary, mode=0o755)
    print(f"Installed {name} {spec['version']} (verified SHA-256)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tools", nargs="*", default=[])
    args = parser.parse_args()
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "AMD64"}:
        parser.error("external-tool assets currently support Linux x86_64; see CONTRIBUTING.md")
    config = json.loads((ROOT / "tools/versions.json").read_text())["tools"]
    for name in args.tools or config:
        if name not in config:
            parser.error(f"unknown tool {name}")
        install(name, config[name])


if __name__ == "__main__":
    main()

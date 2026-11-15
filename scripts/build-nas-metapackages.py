#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build reproducible dependency-only iGPU profiles; no maintainer scripts/reboots."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    publication = json.loads((root / "publications/nas-manager-dependencies-2026-11-15.json").read_text())
    epoch = int(datetime(2026, 11, 15, tzinfo=timezone.utc).timestamp())
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    for row in publication["metapackages"]:
        assert row["package"] in ("nas-manager-igpu-host", "nas-manager-igpu-guest")
        assert row["architecture"] == "amd64" and row["version"] == "2026.11.15.1"
        filename = row["package"] + "_" + row["version"] + "_amd64.deb"
        with tempfile.TemporaryDirectory(prefix="nas-apt-meta-", dir=args.output) as directory:
            stage = Path(directory)
            control = stage / "DEBIAN"
            control.mkdir(mode=0o755)
            text = ("Package: " + row["package"] + "\nVersion: " + row["version"]
                    + "\nArchitecture: amd64\nSection: metapackages\nPriority: optional\n"
                    "Maintainer: the-ab <ab.insidex@googlemail.com>\n"
                    "Homepage: https://github.com/the-ab/deb\n"
                    "Depends: " + ", ".join(row["depends"]) + "\n"
                    "Description: NAS Manager qualified iGPU dependency profile\n"
                    " Tracks the matched kernel/headers/driver package set through APT.\n"
                    " Kernel activation requires a separately planned reboot.\n")
            (control / "control").write_text(text)
            profile = stage / "usr/share/nas-manager" / (row["package"] + ".json")
            profile.parent.mkdir(parents=True, mode=0o755)
            profile.write_text(json.dumps({"schema": 1, "metapackage": row["package"],
                "metapackage_version": row["version"], **row["target"]}, indent=2) + "\n")
            doc = stage / "usr/share/doc" / row["package"]
            doc.mkdir(parents=True, mode=0o755)
            (doc / "copyright").write_text(
                "Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/\n"
                "Upstream-Name: NAS Manager iGPU dependency profiles\n"
                "Source: https://github.com/the-ab/deb\n\nFiles: *\n"
                "Copyright: 2026 the-ab\nLicense: GPL-2\n"
                " See /usr/share/common-licenses/GPL-2 for the complete license text.\n")
            for path in sorted(stage.rglob("*"), reverse=True):
                path.chmod(0o755 if path.is_dir() else 0o644)
                os.utime(path, (epoch, epoch), follow_symlinks=False)
            os.utime(stage, (epoch, epoch))
            output = args.output / filename
            subprocess.run(["dpkg-deb", "--root-owner-group", "--build", str(stage), str(output)],
                           check=True, env=dict(os.environ, SOURCE_DATE_EPOCH=str(epoch)),
                           stdout=subprocess.DEVNULL)
        with output.open("rb") as stream:
            sha = hashlib.file_digest(stream, "sha256").hexdigest()
        results.append({"package": row["package"], "version": row["version"],
                        "architecture": "amd64", "filename": filename,
                        "bytes": output.stat().st_size, "sha256": sha})
    print(json.dumps({"schema": 1, "packages": results}, indent=2))


if __name__ == "__main__":
    main()

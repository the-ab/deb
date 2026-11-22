#!/usr/bin/env python3
"""Verified release-backed pool files for a signed, static APT Pages site.

Large packages stay out of Git. The ordinary Git pool retains its 95 MiB limit;
an external asset is accepted only with an exact path, size and SHA256 pin.
Signatures are made by the maintainer before deployment, never in this module.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen

GIT_POOL_LIMIT = 95 * 1024**2
SITE_LIMIT = 1_000_000_000
MANIFEST = "release-assets.json"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path, algorithm="sha256"):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def assets(root):
    path = root / MANIFEST
    if not path.exists():
        return {}
    value = json.loads(path.read_text())
    require(set(value) == {"schema", "assets"} and value["schema"] == 1, "asset manifest schema")
    require(type(value["assets"]) is list, "asset list")
    result = {}
    for row in value["assets"]:
        require(type(row) is dict and set(row) == {"path", "url", "bytes", "sha256"}, "asset fields")
        rel = PurePosixPath(row["path"])
        require(not rel.is_absolute() and len(rel.parts) == 3 and rel.parts[0] in ("pool", "sources")
                and all(part not in ("", ".", "..") for part in rel.parts)
                and re.fullmatch(r"[a-z0-9-]+", rel.parts[1])
                and re.fullmatch(r"[A-Za-z0-9.+_~%-]+", rel.name)
                and (rel.name.endswith(".deb") if rel.parts[0] == "pool" else
                     rel.name.endswith((".dsc", ".tar.xz", ".tar.gz"))), "asset pool/source path")
        require(str(rel) == row["path"] and row["path"] not in result, "duplicate or noncanonical asset path")
        url = urlsplit(row["url"])
        require(url.scheme == "https" and url.netloc == "github.com" and not url.query and not url.fragment,
                "asset HTTPS origin")
        parts = PurePosixPath(unquote(url.path)).parts
        require(len(parts) == 7 and parts[1:5] == ("the-ab", "deb", "releases", "download")
                and re.fullmatch(r"[A-Za-z0-9._-]+", parts[5])
                # GitHub normalizes '~' in uploaded release names to '.'.
                # The APT pool keeps the original Debian filename and bytes.
                and parts[6] == rel.name.replace("~", "."),
                "asset release URL")
        require(type(row["bytes"]) is int and 0 < row["bytes"] < SITE_LIMIT
                and re.fullmatch(r"[0-9a-f]{64}", row["sha256"]), "asset content pin")
        result[row["path"]] = row
    require(len({row["url"] for row in result.values()}) == len(result), "duplicate release asset URL")
    require(sum(row["bytes"] for row in result.values()) < SITE_LIMIT, "asset set too large")
    return result


def verified(path, row):
    require(path.is_file() and not path.is_symlink() and path.stat().st_nlink == 1,
            "asset must be a regular, unshared file")
    require(path.stat().st_size == row["bytes"] and digest(path) == row["sha256"],
            "asset size or SHA256 mismatch: " + row["path"])


def pool_admission(root, path, catalogue):
    rel = path.relative_to(root).as_posix()
    require(path.is_file() and not path.is_symlink(), "pool file type")
    if rel in catalogue:
        verified(path, catalogue[rel])
        # These payloads are materialized locally or during deployment only.
        indexed = subprocess.run(["git", "-c", "safe.directory=" + str(root), "-C", str(root),
                                  "ls-files", "--error-unmatch", "--", rel],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        require(indexed.returncode in (0, 1), "cannot inspect package Git tracking state")
        require(indexed.returncode != 0, "release-backed package must not be tracked in Git")
    else:
        require(path.stat().st_size < GIT_POOL_LIMIT, "ordinary Git pool package exceeds95MiB")


def fetch(root):
    catalogue = assets(root)
    for rel, row in catalogue.items():
        path = root / rel
        if path.exists():
            verified(path, row)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        require(not path.parent.is_symlink(), "asset directory link")
        fd, temporary = tempfile.mkstemp(prefix=".download-", dir=path.parent)
        try:
            count = 0
            sha = hashlib.sha256()
            with os.fdopen(fd, "wb") as out, urlopen(row["url"], timeout=60) as response:
                require(urlsplit(response.url).scheme == "https", "asset redirect transport")
                while chunk := response.read(1024 * 1024):
                    count += len(chunk)
                    require(count <= row["bytes"], "oversized asset response")
                    sha.update(chunk)
                    out.write(chunk)
                out.flush()
                os.fsync(out.fileno())
            require(count == row["bytes"] and sha.hexdigest() == row["sha256"], "asset download content mismatch")
            os.chmod(temporary, 0o644)
            os.replace(temporary, path)
            verified(path, row)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    return catalogue


def control_paragraphs(raw):
    for paragraph in raw.strip().split("\n\n"):
        if not paragraph.strip():
            continue
        value = {}
        for line in paragraph.splitlines():
            if line.startswith((" ", "\t")):
                continue
            key, separator, content = line.partition(": ")
            require(separator and key not in value, "package index syntax")
            value[key] = content
        yield value


def verify_site(root):
    config = json.loads((root / "repository.json").read_text())
    dist = root / "dists" / config["suite"]
    subprocess.run(["gpgv", "--keyring", str(root / "the-ab-archive-keyring.gpg"),
                    str(dist / "InRelease")], check=True, capture_output=True)
    # Compare the authenticated plaintext with the separate Release as well.
    plain = subprocess.check_output(["gpg", "--batch", "--no-default-keyring", "--keyring",
                                    str(root / "the-ab-archive-keyring.gpg"), "--decrypt",
                                    str(dist / "InRelease")], stderr=subprocess.DEVNULL)
    require(plain == (dist / "Release").read_bytes(), "signed Release plaintext mismatch")
    release = plain.decode()
    require("Components: " + " ".join(config["components"]) + "\n" in release,
            "signed component catalogue mismatch")
    in_hashes = False
    authenticated = set()
    for line in release.splitlines():
        if line == "SHA256:":
            in_hashes = True
            continue
        if in_hashes and line and not line.startswith(" "):
            break
        if in_hashes:
            sha, size, rel = line.split()
            path = dist / rel
            require(not PurePosixPath(rel).is_absolute() and ".." not in PurePosixPath(rel).parts,
                    "Release index path")
            require(path.is_file() and not path.is_symlink() and path.stat().st_size == int(size)
                    and digest(path) == sha, "signed index content mismatch")
            authenticated.add(rel)
    require("SHA256:\n" in release, "missing signed index hashes")
    require(authenticated == {p.relative_to(dist).as_posix() for p in dist.glob("*/binary-*/Packages*")
                              if p.is_file()}, "unsigned or missing package index")
    count = 0
    for index in dist.glob("*/binary-*/Packages"):
        for row in control_paragraphs(index.read_text()):
            rel = PurePosixPath(row["Filename"])
            require(not rel.is_absolute() and rel.parts[0] == "pool" and ".." not in rel.parts,
                    "index package path")
            path = root / rel
            require(path.is_file() and not path.is_symlink() and path.stat().st_size == int(row["Size"])
                    and digest(path) == row["SHA256"], "signed package content mismatch")
            count += 1
    return count


def assemble(root, site):
    require(not site.exists() and not site.is_relative_to(root), "site must be a new directory outside the checkout")
    catalogue = fetch(root)
    require(all((root / rel).exists() for rel in catalogue), "missing release assets")
    verify_site(root)
    site.mkdir(parents=True)
    # The runner can keep materialized assets from older commits. Publish
    # tracked public paths and the current pins, independent of those files.
    tracked = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z", "--",
                                       "dists", "pool", "sources", "publications"])
    paths = {os.fsdecode(path) for path in tracked.split(b"\0") if path} | set(catalogue)
    for name in sorted(paths):
        source = root / name
        require(source.is_file() and source.resolve() == source, "invalid public file: " + name)
        target = site / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for name in (".nojekyll", "the-ab-archive-keyring.gpg", "repository.json", "KEYRING.json", MANIFEST,
                 "README.md", "README.de.md", "LICENSE"):
        source = root / name
        require(source.is_file() and not source.is_symlink(), "missing public site file: " + name)
        shutil.copyfile(source, site / name)
    files = [p for p in site.rglob("*") if p.is_file()]
    require(all(not p.is_symlink() and p.stat().st_nlink == 1 for p in files), "site contains a link")
    size = sum(p.stat().st_size for p in files)
    require(size < SITE_LIMIT, "Pages site exceeds1GB")
    return {"bytes": size, "files": len(files), "package_index_entries": verify_site(site),
            "release_assets": len(catalogue)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("fetch", "verify", "assemble"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--site", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.action == "fetch":
        result = {"verified_assets": len(fetch(root))}
    elif args.action == "verify":
        result = {"package_index_entries": verify_site(root)}
    else:
        require(args.site is not None, "missing site directory")
        result = assemble(root, args.site.resolve())
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

"""External package admission must preserve the ordinary Git limit and pins."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("repository_assets", Path(__file__).parents[1] / "scripts/repository_assets.py")
assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets)


class ReleaseAssets(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        subprocess.run(["git", "init", "-q", self.root], check=True, capture_output=True)
        self.path = self.root / "pool/nas-manager/test_1_amd64.deb"
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b"pinned package")
        self.row = {"path": self.path.relative_to(self.root).as_posix(),
                    "url": "https://github.com/the-ab/deb/releases/download/test/test_1_amd64.deb",
                    "bytes": self.path.stat().st_size, "sha256": assets.digest(self.path)}

    def catalogue(self, row):
        (self.root / assets.MANIFEST).write_text(json.dumps({"schema": 1, "assets": [row]}))
        return assets.assets(self.root)

    def test_pinned_untracked_asset_and_cached_fetch(self):
        catalogue = self.catalogue(self.row)
        assets.pool_admission(self.root, self.path, catalogue)
        self.assertEqual(assets.fetch(self.root), catalogue)

    def test_tracked_external_payload_refused(self):
        subprocess.run(["git", "-C", self.root, "add", self.row["path"]], check=True)
        with self.assertRaisesRegex(ValueError, "must not be tracked"):
            assets.pool_admission(self.root, self.path, self.catalogue(self.row))

    def test_tamper_and_link_refused(self):
        self.path.write_bytes(b"changed bytes")
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            assets.verified(self.path, self.row)
        target = self.path.with_suffix(".original")
        self.path.rename(target)
        self.path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "regular"):
            assets.verified(self.path, self.row)

    def test_ordinary_git_size_limit_stays_in_force(self):
        with self.path.open("wb") as stream:
            stream.truncate(assets.GIT_POOL_LIMIT)
        with self.assertRaisesRegex(ValueError, "exceeds95MiB"):
            assets.pool_admission(self.root, self.path, {})

    def test_foreign_url_and_traversal_refused(self):
        for changes in ({"url": self.row["url"].replace("the-ab/deb", "other/repo")},
                        {"path": "pool/../test.deb"}, {"path": "/pool/nas-manager/test.deb"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.catalogue(dict(self.row, **changes))

    def test_corresponding_source_asset(self):
        source = dict(self.row, path="sources/nas-manager/linux_1.orig.tar.xz",
                      url="https://github.com/the-ab/deb/releases/download/test/linux_1.orig.tar.xz")
        self.assertIn(source["path"], self.catalogue(source))

    def test_github_normalized_debian_backports_filename(self):
        row = dict(self.row, path="pool/nas-manager/linux_1~bpo1_amd64.deb",
                   url="https://github.com/the-ab/deb/releases/download/test/linux_1.bpo1_amd64.deb")
        self.assertIn(row["path"], self.catalogue(row))
        row["url"] = row["url"].replace("1.bpo1", "2.bpo1")
        with self.assertRaises(ValueError):
            self.catalogue(row)


if __name__ == "__main__":
    unittest.main()

import copy
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sync_release
from update_release import update_website, version_key


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / "website", self.root / "website")
        self.current = json.loads((self.root / "website/release.json").read_text())
        self.next = dict(self.current, tag="v9.9.9", asset="Raven-Translate-9.9.9-arm64.dmg", prerelease=True)

    def tearDown(self):
        self.temp.cleanup()

    def snapshot(self):
        return {p.name: p.read_bytes() for p in (self.root / "website").glob("*") if p.is_file()}

    def test_update_all_static_links_and_both_languages_is_idempotent(self):
        update_website(self.root, self.next)
        html = (self.root / "website/index.html").read_text()
        log = (self.root / "website/changelog.html").read_text()
        self.assertEqual((html + log).count("/download/v9.9.9/"), 4)
        self.assertIn("/tag/v9.9.9", html)
        i18n = (self.root / "website/i18n.js").read_text()
        self.assertIn("9.9.9 预览版", i18n)
        self.assertIn("9.9.9 preview", i18n)
        before = self.snapshot()
        update_website(self.root, self.next)
        self.assertEqual(before, self.snapshot())

    def test_stable_promotion_removes_preview_and_cannot_be_demoted(self):
        self.current["prerelease"] = True
        (self.root / "website/release.json").write_text(json.dumps(self.current))
        stable = dict(self.current, prerelease=False)
        update_website(self.root, stable)
        before = self.snapshot()
        self.assertFalse(update_website(self.root, self.current))
        self.assertEqual(before, self.snapshot())
        self.assertNotIn(f'{self.current["tag"][1:]} preview', before["i18n.js"].decode())

    def test_older_version_and_same_version_different_binary(self):
        before = self.snapshot()
        old = dict(self.current, tag="v0.0.1", asset="Raven-Translate-0.0.1-arm64.dmg")
        self.assertFalse(update_website(self.root, old))
        with self.assertRaises(ValueError):
            update_website(self.root, dict(self.current, sha256="a" * 64))
        self.assertEqual(before, self.snapshot())

    def test_layout_drift_fails_before_any_file_write(self):
        path = self.root / "website/changelog.html"
        path.write_text(path.read_text().replace("/releases/download/", "/changed/"))
        before = self.snapshot()
        with self.assertRaises(ValueError):
            update_website(self.root, self.next)
        self.assertEqual(before, self.snapshot())

    def test_semver_and_untrusted_input(self):
        tags = ["v1.0.0-beta.2", "v1.0.0-beta.10", "v1.0.0-rc.1", "v1.0.0", "v1.1.0"]
        keys = [version_key({"tag": t, "prerelease": "-" in t}) for t in tags]
        self.assertEqual(keys, sorted(keys))
        for tag in ["../../bad", "v1.0.0;echo bad", "v1.00.0", "v1.0.0-beta.01"]:
            with self.assertRaises(ValueError):
                version_key({"tag": tag, "prerelease": True})

    def test_anonymous_download_verifies_hash_and_bounds_retry(self):
        data = b"verified DMG test bytes"
        digest = hashlib.sha256(data).hexdigest()
        with patch.object(sync_release.urllib.request, "urlopen", return_value=io.BytesIO(data)):
            sync_release.verify_public("https://example.invalid/test", digest, len(data))
        with patch.object(sync_release.urllib.request, "urlopen", return_value=io.BytesIO(data)):
            with self.assertRaises(ValueError):
                sync_release.verify_public("https://example.invalid/test", "0" * 64, len(data))
        with patch.object(sync_release.urllib.request, "urlopen", side_effect=urllib.error.URLError("offline")) as request:
            with patch.object(sync_release.time, "sleep"):
                with self.assertRaises(RuntimeError):
                    sync_release.verify_public("https://example.invalid/test", digest, len(data))
            self.assertEqual(request.call_count, 6)

    def simulate_sync(self, *, missing=False, mismatch=False, inaccessible=False, rerun=False, corrupt_upload=False, resume_draft=False):
        data = b"fixture DMG bytes, never published"
        digest = hashlib.sha256(data).hexdigest()
        name = self.next["asset"]
        asset = {"name": name, "state": "uploaded", "size": len(data), "digest": f"sha256:{digest}"}
        source = {"tag_name": "v9.9.9", "draft": False, "prerelease": True,
                  "body": "PRIVATE NOTES MUST NOT LEAVE APP", "assets": [] if missing else [asset]}
        target = {"id": 123, "tag_name": "v9.9.9", "draft": resume_draft, "prerelease": True,
                  "assets": [] if resume_draft else [asset]} if rerun or mismatch or resume_draft else None
        created = []

        def api(token, endpoint, payload=None, allow_missing=False, paginate=False):
            nonlocal target
            if token == "source-token":
                self.assertIn(sync_release.SOURCE, endpoint)
                return source
            self.assertEqual(token, "site-token")
            if paginate:
                return [[copy.deepcopy(target)]] if target else [[]]
            if "/tags/" in endpoint and target and target["draft"]:
                return None
            if payload is not None:
                created.append(payload)
                target = dict(payload, id=123, assets=[])
            return copy.deepcopy(target)

        def gh(token, *args, **kwargs):
            if args[1] == "download":
                directory = Path(args[args.index("--dir") + 1])
                (directory / name).write_bytes(b"different" if mismatch and token == "site-token" else data)
            elif args[1] == "upload":
                target["assets"].append(dict(asset, digest="sha256:" + "0" * 64) if corrupt_upload else asset)
            elif args[1] == "edit":
                target["draft"] = False
            else:
                self.fail(f"Unexpected operation {args[1]}")

        before = self.snapshot()
        with patch.object(sync_release, "api", side_effect=api), patch.object(sync_release, "gh", side_effect=gh):
            with patch.object(sync_release, "verify_public", side_effect=RuntimeError("not public") if inaccessible else None):
                if missing or mismatch or inaccessible or corrupt_upload:
                    with self.assertRaises((ValueError, RuntimeError)):
                        sync_release.sync(self.root, "v9.9.9", "source-token", "site-token")
                    self.assertEqual(before, self.snapshot())
                else:
                    sync_release.sync(self.root, "v9.9.9", "source-token", "site-token")
                    self.assertEqual(json.loads((self.root / "website/release.json").read_text())["sha256"], digest)
        self.assertNotIn("PRIVATE NOTES", json.dumps(created))
        if created:
            self.assertTrue(created[0]["draft"])
        if corrupt_upload:
            self.assertTrue(target["draft"])
        if resume_draft:
            self.assertEqual(created, [])
            self.assertFalse(target["draft"])

    def test_full_mirror_then_update(self):
        self.simulate_sync()

    def test_existing_identical_release_is_reusable(self):
        self.simulate_sync(rerun=True)

    def test_missing_dmg_keeps_current_website(self):
        self.simulate_sync(missing=True)

    def test_conflicting_binary_keeps_current_website(self):
        self.simulate_sync(mismatch=True)

    def test_unavailable_public_download_keeps_current_website(self):
        self.simulate_sync(inaccessible=True)

    def test_upload_digest_failure_keeps_release_draft_and_current_website(self):
        self.simulate_sync(corrupt_upload=True)

    def test_resume_unpublished_draft_instead_of_creating_duplicate(self):
        self.simulate_sync(resume_draft=True)


if __name__ == "__main__":
    unittest.main()

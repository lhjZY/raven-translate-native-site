"""Mirror one private App release, then update the public site's static entries.

Run only from the App's trusted release workflow. SOURCE_TOKEN reads the App;
SITE_TOKEN writes only the public website. Private release notes are not copied.
"""

import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from update_release import RELEASES, REPOSITORY, update_website, version_key

SOURCE = "lhjZY/Raven-t"


def gh(token, *args, payload=None, allow_missing=False):
    env = os.environ.copy()
    # Keep the two repository credentials out of child environments except GH_TOKEN.
    env.pop("SOURCE_TOKEN", None)
    env.pop("SITE_TOKEN", None)
    env["GH_TOKEN"] = token
    result = subprocess.run(
        ["gh", *args], input=json.dumps(payload) if payload is not None else None,
        text=True, capture_output=True, env=env, timeout=300,
    )
    if result.returncode:
        if allow_missing and "(HTTP 404)" in result.stderr:
            return None
        # Do not echo command output: it may contain private release notes or URLs.
        status = re.search(r"HTTP \d{3}", result.stderr)
        detail = status[0] if status else f"exit {result.returncode}"
        raise RuntimeError(f"GitHub {args[0]} operation failed ({detail}); check credential permissions and release assets")
    return result.stdout


def api(token, endpoint, payload=None, allow_missing=False, paginate=False):
    args = ["api", endpoint]
    if paginate:
        args += ["--paginate", "--slurp"]
    if payload is not None:
        args += ["--method", "POST", "--input", "-"]
    result = gh(token, *args, payload=payload, allow_missing=allow_missing)
    return json.loads(result) if result is not None else None


def file_digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_public(url, expected, size):
    """Anonymous download verifies both accessibility and bytes before website changes."""
    for attempt in range(6):
        try:
            digest = hashlib.sha256()
            total = 0
            with urllib.request.urlopen(url, timeout=30) as response:
                while block := response.read(1024 * 1024):
                    total += len(block)
                    if total > size:
                        raise ValueError("Public asset is larger than the verified source")
                    digest.update(block)
            if total != size or digest.hexdigest() != expected:
                raise ValueError("Public DMG checksum does not match the source")
            return
        except (urllib.error.URLError, TimeoutError):
            if attempt == 5:
                raise RuntimeError("Public DMG is unavailable; website download remains unchanged") from None
            time.sleep(5 * (attempt + 1))


def sync(root, tag, source_token, site_token):
    # Validate before using tag in API paths, filenames, commands or published content.
    version_key({"tag": tag, "prerelease": True})
    source = api(source_token, f"repos/{SOURCE}/releases/tags/{tag}")
    if source["draft"] or source["tag_name"] != tag:
        raise ValueError("Only a published source release can be synchronized")
    version_key({"tag": tag, "prerelease": source["prerelease"]})
    name = f"Raven-Translate-{tag[1:]}-arm64.dmg"
    assets = [asset for asset in source["assets"] if asset["name"] == name]
    if len(assets) != 1 or assets[0]["state"] != "uploaded" or assets[0]["size"] <= 0:
        raise ValueError(f"Upload {name} to the App release before publishing, then rerun")

    with tempfile.TemporaryDirectory(prefix="raven-release-") as directory:
        temp = Path(directory)
        gh(source_token, "release", "download", tag, "--repo", SOURCE,
           "--pattern", name, "--dir", str(temp))
        package = temp / name
        checksum = file_digest(package)
        if package.stat().st_size != assets[0]["size"]:
            raise ValueError("Downloaded source DMG size mismatch")
        if assets[0].get("digest") and assets[0]["digest"] != f"sha256:{checksum}":
            raise ValueError("Downloaded source DMG checksum mismatch")
        release = {"tag": tag, "prerelease": source["prerelease"], "asset": name, "sha256": checksum}
        endpoint = f"repos/{REPOSITORY}/releases/tags/{tag}"
        target = api(site_token, endpoint, allow_missing=True)
        if target is None:
            # The tag endpoint documents published releases only. Recover an earlier
            # upload's draft from the authenticated, paginated list before creating one.
            pages = api(site_token, f"repos/{REPOSITORY}/releases?per_page=100", paginate=True)
            matches = [item for page in pages for item in page if item["tag_name"] == tag]
            if len(matches) > 1:
                raise ValueError("Multiple destination releases use this tag; resolve them manually")
            target = matches[0] if matches else None
        if target is None:
            # Create a draft first. An upload failure must not publish an empty release.
            target = api(site_token, f"repos/{REPOSITORY}/releases", payload={
                "tag_name": tag, "target_commitish": "main", "draft": True,
                "prerelease": source["prerelease"], "make_latest": "false",
                "name": f"Raven Translate {tag[1:]}" + (" · Preview" if source["prerelease"] else ""),
                "body": (
                    f"安装包：`{name}`\n\nApple Silicon（arm64）· macOS 26+。\n\n"
                    "打开 DMG，将 Raven-Translate 拖入 Applications。\n\n"
                    "本同步流程不执行签名或 Apple 公证；请以安装包实际签名状态为准。\n\n"
                    f"SHA-256：\n```text\n{checksum}\n```\n\n"
                    "[官方网站](https://lhjzy.github.io/raven-translate-native-site/)\n\n"
                    "本仓库分发安装包；Source code 压缩包仅包含官网源码。"
                ),
            })
        if not target["prerelease"] and source["prerelease"]:
            raise ValueError("An existing stable release cannot be demoted to a preview")
        existing = [asset for asset in target["assets"] if asset["name"] == name]
        if existing:
            # Never delete/overwrite an existing binary. Reruns must prove it is identical.
            check = temp / "existing"
            check.mkdir()
            gh(site_token, "release", "download", tag, "--repo", REPOSITORY,
               "--pattern", name, "--dir", str(check))
            if file_digest(check / name) != checksum:
                raise ValueError("Existing public asset differs; publish a new version instead")
        else:
            gh(site_token, "release", "upload", tag, str(package), "--repo", REPOSITORY)
            uploaded = api(site_token, f"repos/{REPOSITORY}/releases/{target['id']}")
            match = [asset for asset in uploaded["assets"] if asset["name"] == name]
            if len(match) != 1 or match[0].get("digest") != f"sha256:{checksum}":
                raise ValueError("Uploaded asset digest mismatch; release is not promoted")
        if target["draft"] or target["prerelease"] != source["prerelease"]:
            gh(site_token, "release", "edit", tag, "--repo", REPOSITORY,
               "--draft=false", f"--prerelease={str(source['prerelease']).lower()}", "--latest=false",
               "--title", f"Raven Translate {tag[1:]}" + (" · Preview" if source["prerelease"] else ""))
        verify_public(f"{RELEASES}/download/{tag}/{name}", checksum, package.stat().st_size)
        update_website(root, release)
        print(f"Verified public release {tag}: SHA-256 {checksum}")


if __name__ == "__main__":
    sync(Path(__file__).resolve().parents[1], os.environ["RELEASE_TAG"],
         os.environ["SOURCE_TOKEN"], os.environ["SITE_TOKEN"])

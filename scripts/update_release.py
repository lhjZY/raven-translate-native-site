"""Update static download entries only after sync_release verifies the public DMG."""

import json
import re
from pathlib import Path

REPOSITORY = "lhjZY/raven-translate-native-site"
RELEASES = f"https://github.com/{REPOSITORY}/releases"
TAG = re.compile(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?")


def version_key(release):
    """Compare SemVer, including numeric prerelease identifiers and preview flags."""
    match = TAG.fullmatch(release["tag"])
    if not match or type(release["prerelease"]) is not bool:
        raise ValueError("Expected a vMAJOR.MINOR.PATCH tag and a boolean prerelease flag")
    suffix = match[4]
    if suffix and not release["prerelease"]:
        raise ValueError("A prerelease tag must be marked as a prerelease")
    parts = []
    for part in suffix.split(".") if suffix else []:
        if part.isdigit() and len(part) > 1 and part.startswith("0"):
            raise ValueError("Numeric prerelease identifiers cannot have leading zeroes")
        parts.append((0, int(part)) if part.isdigit() else (1, part))
    return (*map(int, match.group(1, 2, 3)), not release["prerelease"], tuple(parts))


def validate_release(release):
    version_key(release)
    expected = f"Raven-Translate-{release['tag'][1:]}-arm64.dmg"
    if release["asset"] != expected or not re.fullmatch(r"[0-9a-f]{64}", release["sha256"]):
        raise ValueError("Unexpected DMG filename or SHA-256")


def update_website(root, release):
    """Validate every replacement before writing; old releases never move the website back."""
    root = Path(root)
    validate_release(release)
    current = json.loads((root / "website/release.json").read_text())
    validate_release(current)
    if version_key(release) < version_key(current):
        print("Older release mirrored; current website download is retained.")
        return False
    if release["tag"] == current["tag"] and release["sha256"] != current["sha256"]:
        raise ValueError("The same version cannot silently replace its published DMG")
    old_download = f"{RELEASES}/download/{current['tag']}/{current['asset']}"
    new_download = f"{RELEASES}/download/{release['tag']}/{release['asset']}"
    version = release["tag"][1:]
    labels = [
        f"{version}{' 预览版' if release['prerelease'] else ''} · Apple Silicon · macOS 26+",
        f"{version}{' preview' if release['prerelease'] else ''} · Apple Silicon · macOS 26+",
    ]
    updates = {}
    for name, count in (("index.html", 3), ("changelog.html", 1)):
        path = root / "website" / name
        text = path.read_text()
        if text.count(old_download) != count:
            raise ValueError(f"Expected {count} download links in {name}; website layout changed")
        text = text.replace(old_download, new_download)
        if name == "index.html":
            old_notes = f"{RELEASES}/tag/{current['tag']}"
            if text.count(old_notes) != 1:
                raise ValueError("Expected one release notes link")
            text = text.replace(old_notes, f"{RELEASES}/tag/{release['tag']}")
            text, matches = re.subn(r'(data-i18n="download.req">)[^<]+', lambda m: m[1] + labels[0], text)
            if matches != 1:
                raise ValueError("Expected one fallback version label")
        updates[path] = text
    path = root / "website/i18n.js"
    matches = list(re.finditer(r'("download.req": )"[^"\n]+"', path.read_text()))
    if len(matches) != 2:
        raise ValueError("Expected Chinese and English download version labels")
    text = path.read_text()
    for match, label in reversed(list(zip(matches, labels))):
        text = text[:match.start()] + match[1] + json.dumps(label, ensure_ascii=False) + text[match.end():]
    updates[path] = text
    updates[root / "website/release.json"] = json.dumps(release, ensure_ascii=False, indent=2) + "\n"
    for path, text in updates.items():
        path.write_text(text)
    return True

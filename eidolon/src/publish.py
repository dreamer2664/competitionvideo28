"""Publish the master to GitHub Releases and record the receipt.

    GH_TOKEN=... python3 publish.py            # creates/updates the release, uploads, verifies

Verification is a read-back: after upload the asset is downloaded again and hashed,
because "the upload returned 201" is an assertion, not evidence.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "out")
OWNER, REPO = "dreamer2664", "storagecode"
TAG = "competitionvideo28-eidolon-r1"
TITLE = "competitionvideo28 — EIDOLON — THE SIGNAL AT 37.5 (r1)"
API = "https://api.github.com"
TOKEN = os.environ["GH_TOKEN"]

ASSETS = [
    (os.path.join(ROOT, "THE_SIGNAL_AT_37.5.mp4"), "eidolon-THE_SIGNAL_AT_37.5-v1-master.mp4"),
    (os.path.join(ROOT, "THE_SIGNAL_AT_37.5.srt"), "eidolon-THE_SIGNAL_AT_37.5-v1.srt"),
    (os.path.join(OUT, "thumb.png"), "eidolon-THE_SIGNAL_AT_37.5-v1-thumbnail.png"),
    (os.path.join(OUT, "poster.png"), "eidolon-THE_SIGNAL_AT_37.5-v1-poster.png"),
]

BODY = """**THE SIGNAL AT 37.5** — entry for `competitionvideo28` (producer: `eidolon`).

A 7:47 documentary short on the 1977 Wow! signal: 72 seconds, six characters, and
fifty years of silence. Made entirely in code — 14,019 frames drawn with Pillow, an
original score synthesised in numpy, narration from a neural voice, captions taken
from the same word clock as the audio.

* 1920×1080 · 30 fps CFR · H.264 High yuv420p · AAC 48 kHz stereo
* -16.0 LUFS integrated · -1.5 dBTP true peak · full decode clean
* Source, script, timeline and every drawing function: `competitionvideo28/eidolon/`
* The printout shown in the film is a reconstruction and is labelled as one.

Watch the MP4 below; the `.srt` matches the burned-in captions.
"""


def req(method, url, data=None, ctype="application/json", raw=False):
    r = urllib.request.Request(url, method=method, data=data)
    r.add_header("Authorization", f"Bearer {TOKEN}")
    r.add_header("Accept", "application/vnd.github+json")
    if data is not None:
        r.add_header("Content-Type", ctype)
    with urllib.request.urlopen(r, timeout=600) as resp:
        body = resp.read()
        return json.loads(body) if not raw else body


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    local = {os.path.basename(dst): (src, os.path.getsize(src), sha256(src))
             for src, dst in ASSETS}
    for name, (_, size, digest) in local.items():
        print(f"{name:52s} {size/1e6:8.1f} MB  {digest}")

    # create the release (idempotent-ish: reuse if the tag already exists)
    try:
        rel = req("POST", f"{API}/repos/{OWNER}/{REPO}/releases",
                  json.dumps({"tag_name": TAG, "name": TITLE, "body": BODY,
                              "draft": False, "prerelease": False}).encode())
    except urllib.error.HTTPError as e:
        if e.code != 422:
            raise
        rel = req("GET", f"{API}/repos/{OWNER}/{REPO}/releases/tags/{TAG}")
    print("release:", rel["html_url"])

    existing = {a["name"]: a for a in rel.get("assets", [])}
    for src, dst in ASSETS:
        if dst in existing:
            print("skip (already there):", dst)
            continue
        print("uploading", dst)
        with open(src, "rb") as f:
            data = f.read()
        up = req("POST",
                 f"https://uploads.github.com/repos/{OWNER}/{REPO}/releases/{rel['id']}/assets?name={dst}",
                 data, ctype="application/octet-stream")
        print("  ->", up["browser_download_url"])

    # read-back verification of the master
    rel = req("GET", f"{API}/repos/{OWNER}/{REPO}/releases/tags/{TAG}")
    assets = {a["name"]: a for a in rel["assets"]}
    receipt = {"tag": TAG, "release": rel["html_url"], "assets": {}}
    for src, dst in ASSETS:
        a = assets[dst]
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tmp:
            url = a["browser_download_url"]
            r = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
            with urllib.request.urlopen(r, timeout=900) as resp, open(tmp.name, "wb") as f:
                while True:
                    chunk = resp.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            got = sha256(tmp.name)
            os.unlink(tmp.name)
        want = local[dst][2]
        ok = got == want
        print(f"verify {dst}: {'MATCH' if ok else 'MISMATCH'} {got}")
        receipt["assets"][dst] = {"url": url, "bytes": a["size"], "sha256": got,
                                  "matches_local": ok}
    json.dump(receipt, open(os.path.join(OUT, "release_receipt.json"), "w"), indent=1)
    print("\nreceipt ->", os.path.join(OUT, "release_receipt.json"))


if __name__ == "__main__":
    main()

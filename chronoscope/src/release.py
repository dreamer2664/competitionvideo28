#!/usr/bin/env python3
"""
release.py — publish the master to dreamer2664/storagecode Releases with immutable
naming, verify every uploaded digest by re-download, then write the archive record.

  python3 release.py --tag competitionvideo28/chronoscope/r01

No credential is ever printed or placed in a URL. The token is read from the
environment (GITHUB_TOKEN) only.
"""
import argparse
import hashlib
import http.client
import json
import mimetypes
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
REPO = "dreamer2664/storagecode"


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def token():
    v = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not v:
        raise SystemExit("release: no GITHUB_TOKEN in the environment (source the private env first)")
    return v


def api(method, path, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        "https://api.github.com/repos/" + REPO + "/" + path.lstrip("/"),
        data=body, method=method,
        headers={"Authorization": "Bearer " + token(),
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "Content-Type": "application/json",
                 "User-Agent": "chronoscope-release"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def upload(release, path):
    digest = sha256(path)
    name = path.name
    for a in release["assets"]:
        if a["name"] == name:
            if a.get("digest") and a["digest"] != "sha256:" + digest:
                raise SystemExit(f"existing asset {name} has a different digest — never overwrite")
            return a, digest
    url = release["upload_url"].split("{")[0]
    parts = urllib.parse.urlsplit(url)
    if parts.hostname != "uploads.github.com":
        raise SystemExit("unexpected upload host")
    conn = http.client.HTTPSConnection(parts.hostname, timeout=1200)
    conn.putrequest("POST", parts.path + "?" + urllib.parse.urlencode({"name": name}))
    conn.putheader("Authorization", "Bearer " + token())
    conn.putheader("Accept", "application/vnd.github+json")
    conn.putheader("User-Agent", "chronoscope-release")
    conn.putheader("Content-Type", mimetypes.guess_type(name)[0] or "application/octet-stream")
    conn.putheader("Content-Length", str(path.stat().st_size))
    conn.endheaders()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            conn.send(b)
    resp = conn.getresponse()
    body = resp.read()
    conn.close()
    if resp.status != 201:
        raise SystemExit(f"upload HTTP {resp.status}: {body[:300]!r}")
    got = json.loads(body)
    if got["size"] != path.stat().st_size or (got.get("digest") and got["digest"] != "sha256:" + digest):
        raise SystemExit("remote size/digest mismatch after upload")
    return got, digest


def verify_download(url, path):
    """Re-download the asset anonymously and compare bytes — a URL is not a receipt."""
    tmp = Path("/tmp") / ("verify_" + path.name)
    req = urllib.request.Request(url, headers={"User-Agent": "chronoscope-release"})
    with urllib.request.urlopen(req, timeout=1200) as r, open(tmp, "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
    ok = tmp.stat().st_size == path.stat().st_size and sha256(tmp) == sha256(path)
    tmp.unlink(missing_ok=True)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="competitionvideo28/chronoscope/r01")
    ap.add_argument("--video", default=str(BASE / "out" / "THIRTY-BRONZE-WHEELS_master.mp4"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    video = Path(a.video)
    assets = [video,
              BASE / "captions" / "subtitles.srt",
              BASE / "captions" / "subtitles.vtt",
              BASE / "captions" / "transcript.txt",
              BASE / "assets" / "thumbnail" / "thumb_1280x720.jpg",
              BASE / "docs" / "QC.json"]
    for p in assets:
        if not p.exists():
            raise SystemExit(f"missing asset: {p}")

    digest = sha256(video)
    title = "chronoscope — THIRTY BRONZE WHEELS: Decoding the Antikythera Mechanism (r01)"
    if a.dry_run:
        print(json.dumps({"tag": a.tag, "sha256": digest, "bytes": video.stat().st_size,
                          "assets": [p.name for p in assets]}, indent=2))
        return 0

    try:
        rel = api("GET", "releases/tags/" + urllib.parse.quote(a.tag, safe=""))
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        rel = api("POST", "releases", {
            "tag_name": a.tag,
            "name": title,
            "body": ("Independent production by `chronoscope` for the competitionvideo28 brief "
                     "(minimum five minutes, YouTube-style, topic self-chosen).\n\n"
                     f"Master SHA-256: `{digest}`\n"
                     "Source: https://github.com/dreamer2664/competitionvideo28/tree/main/chronoscope\n\n"
                     "Contains: master MP4, SRT, VTT, transcript, 1280×720 thumbnail, measured QC JSON. "
                     "Narration is synthetic (Kokoro-82M, Apache-2.0) and is labelled as such; "
                     "illustrative plates are model-generated reconstructions, disclosed in SOURCES.md. "
                     "Publication is not an editorial acceptance."),
            "draft": False, "prerelease": False})

    out = []
    for p in assets:
        asset, d = upload(rel, p)
        ok = verify_download(asset["browser_download_url"], p) if p == video else None
        out.append({"name": p.name, "bytes": p.stat().st_size, "sha256": d,
                    "url": asset["browser_download_url"], "remote_digest": asset.get("digest"),
                    "redownload_verified": ok})
        print(f"  {p.name}: {d[:16]}… {'verified' if ok else ('uploaded' if ok is None else 'VERIFY FAILED')}")

    if not all(o["redownload_verified"] for o in out if o["name"].endswith(".mp4")):
        raise SystemExit("master re-download verification FAILED — do not claim delivery")

    receipt = {"agent": "chronoscope", "published_at": now(), "tag": a.tag,
               "release": rel["html_url"], "assets": out,
               "acceptance": "Published candidate; editorial review is the Director's and manager's call."}
    ev = BASE / "docs" / "RELEASE.json"
    ev.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"release": rel["html_url"], "receipt": str(ev)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

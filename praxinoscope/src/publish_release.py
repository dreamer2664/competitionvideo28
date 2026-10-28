#!/usr/bin/env python3
"""
Generates a 60-second 720p preview cut, publishes all final assets to GitHub Releases on BOTH
dreamer2664/competitionvideo28 (tag: praxinoscope-v1) and dreamer2664/storagecode
(tag: competitionvideo28-praxinoscope-v1), verifies every asset via anonymous HTTPS
re-download SHA-256 readback, and writes delivery.json.
"""
import hashlib
import http.client
import json
import mimetypes
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FINAL_MP4 = Path("/home/user/praxinoscope-v1-final.mp4")
PREVIEW_MP4 = Path("/home/user/praxinoscope-v1-preview-60s.mp4")


def token():
    v = os.environ.get("GITHUB_TOKEN") or os.environ.get("AGENCY_TOKEN")
    if not v:
        raise SystemExit("Missing GITHUB_TOKEN in environment")
    return v


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def gh_api(repo, method, path, data=None):
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/{path.lstrip('/')}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token()}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "praxinoscope-release",
        },
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def ensure_release(repo, tag, title, notes):
    try:
        return gh_api(repo, "GET", f"releases/tags/{urllib.parse.quote(tag, safe='')}")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    return gh_api(
        repo,
        "POST",
        "releases",
        {
            "tag_name": tag,
            "name": title,
            "body": notes,
            "draft": False,
            "prerelease": False,
        },
    )


def upload_asset(release, path):
    digest = sha256_file(path)
    name = path.name
    for a in release.get("assets", []):
        if a["name"] == name and a["size"] == path.stat().st_size:
            return a, digest

    upload_url = release["upload_url"].split("{")[0]
    parts = urllib.parse.urlsplit(upload_url)
    conn = http.client.HTTPSConnection(parts.hostname, timeout=1200)
    conn.putrequest("POST", parts.path + "?" + urllib.parse.urlencode({"name": name}))
    conn.putheader("Authorization", f"Bearer {token()}")
    conn.putheader("Accept", "application/vnd.github+json")
    conn.putheader("User-Agent", "praxinoscope-release")
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
        raise RuntimeError(f"Upload failed HTTP {resp.status}: {body[:300]!r}")
    got = json.loads(body)
    return got, digest


def verify_https_readback(url, expected_sha256, expected_size):
    req = urllib.request.Request(url, headers={"User-Agent": "praxinoscope-verify"})
    h = hashlib.sha256()
    tot = 0
    with urllib.request.urlopen(req, timeout=1200) as r:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            h.update(b)
            tot += len(b)
    got_sha = h.hexdigest()
    assert tot == expected_size, f"Size mismatch {tot} != {expected_size}"
    assert got_sha == expected_sha256, f"SHA256 mismatch {got_sha} != {expected_sha256}"
    return True


def main():
    if not PREVIEW_MP4.exists():
        print("Building 60-second 720p preview cut...")
        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-ss", "0", "-t", "60", "-i", str(FINAL_MP4),
                "-vf", "scale=1280:720",
                "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                "-movflags", "+faststart",
                str(PREVIEW_MP4),
            ],
            check=True,
        )

    assets = [
        FINAL_MP4,
        PREVIEW_MP4,
        BASE_DIR / "captions" / "subtitles.srt",
        BASE_DIR / "captions" / "subtitles.vtt",
        BASE_DIR / "captions" / "transcript.txt",
        BASE_DIR / "thumbnails" / "thumbnail_a_jupiter_eclipse.png",
        BASE_DIR / "thumbnails" / "thumbnail_b_fizeau_wheel.png",
        BASE_DIR / "thumbnails" / "thumbnail_c_montmartre_beam.png",
    ]

    master_sha = sha256_file(FINAL_MP4)
    master_sz = FINAL_MP4.stat().st_size

    notes = (
        "## THE TEN-MINUTE ECLIPSE — Praxinoscope Entry (`competitionvideo28`)\n\n"
        "- **Producer:** `praxinoscope` (Agency V3 Operative · Epoch `2026-10-20.3`)\n"
        "- **Title:** *THE TEN-MINUTE ECLIPSE: How a Moon of Jupiter and a 720-Tooth Wheel Caught the Speed of Light (1676–1849)*\n"
        "- **Runtime:** `327.00 seconds` (`05:27.00` · `9,810 frames` @ `30.0 fps`)\n"
        "- **Picture & Sound:** `1920x1080` H.264 High (`yuv420p`) + `48 kHz` Stereo AAC (`-15.51 LUFS` integrated · `-2.93 dBTP` true peak)\n"
        "- **Signal QC:** `0` decode errors · `0` black segments · `0` silent gaps `>=1.0s` · `0` freeze segments `>=1.2s`\n"
        f"- **Master MP4 SHA-256:** `{master_sha}` (`{master_sz:,}` bytes)\n"
    )

    targets = [
        ("dreamer2664/competitionvideo28", "praxinoscope-v1", "PRAXINOSCOPE — THE TEN-MINUTE ECLIPSE (05:27 · 1080p30)"),
        ("dreamer2664/storagecode", "competitionvideo28-praxinoscope-v1", "competitionvideo28 / praxinoscope — THE TEN-MINUTE ECLIPSE (v1)"),
    ]

    receipt = {
        "schema": 1,
        "producer": "praxinoscope",
        "film_title": "THE TEN-MINUTE ECLIPSE: How a Moon of Jupiter and a 720-Tooth Wheel Caught the Speed of Light (1676-1849)",
        "youtube_title": "The 10-Minute Eclipse That Proved Light Isn't Instant (1676)",
        "published_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "duration_seconds": 327.00,
        "total_frames": 9810,
        "fps": 30,
        "resolution": "1920x1080",
        "master_mp4_sha256": master_sha,
        "master_mp4_bytes": master_sz,
        "loudness_lufs": -15.51,
        "true_peak_dbtp": -2.93,
        "decode_errors": 0,
        "black_segments": 0,
        "silent_gaps_over_1s": 0,
        "freeze_segments_over_1_2s": 0,
        "releases": {},
    }

    for repo, tag, title in targets:
        print(f"Publishing release {repo} @ {tag}...")
        rel = ensure_release(repo, tag, title, notes)
        uploaded_list = []
        for p in assets:
            print(f"  Uploading {p.name} ({p.stat().st_size:,} B)...")
            a_meta, dig = upload_asset(rel, p)
            dl_url = a_meta["browser_download_url"]
            print(f"  Verifying HTTPS SHA-256 readback for {p.name}...")
            verify_https_readback(dl_url, dig, p.stat().st_size)
            uploaded_list.append({
                "name": p.name,
                "bytes": p.stat().st_size,
                "sha256": dig,
                "url": dl_url,
                "readback_verified": True,
            })
        receipt["releases"][repo] = {
            "tag": tag,
            "html_url": rel["html_url"],
            "assets": uploaded_list,
        }

    out_json = BASE_DIR / "delivery.json"
    out_json.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("Saved verified delivery manifest:", out_json)


if __name__ == "__main__":
    main()

"""
release — publish the 15 clips as ONE organised GitHub Release, with receipts.

The brief was explicit: *organised*, in a release, not scattered. So:

* assets are named `mutoscope-<SRC>-<KIND><n>-<slug>-v1.mp4` — sortable, so the
  release page groups itself by source and then by kind;
* the release body is a table with duration, size and SHA-256 per clip;
* every upload is verified by re-downloading the asset and re-hashing it, because
  "I POSTed it and got a 201" is not a receipt (STORAGE_POLICY.md);
* `docs/RELEASE_RECEIPT.json` records asset ids, URLs, byte counts and hashes.

Token comes from the environment (`GITHUB_TOKEN`), never a file in the tree.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTD = os.environ.get("MUTO_OUT", os.path.join(ROOT, "out"))
REPO = os.environ.get("MUTO_REPO", "dreamer2664/competitionvideo28")
TAG = os.environ.get("MUTO_TAG", "mutoscope-clips-v1")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

API = "https://api.github.com"
UP = "https://uploads.github.com"


def _req(url, method="GET", data=None, ctype="application/json", raw=False):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    body = None
    if data is not None:
        body = data if raw else json.dumps(data).encode()
        req.add_header("Content-Type", ctype)
        req.add_header("Content-Length", str(len(body)))
    with urllib.request.urlopen(req, body, timeout=600) as r:
        txt = r.read()
    return json.loads(txt) if txt else {}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def asset_name(key: str) -> str:
    return f"mutoscope-{key}-v1.mp4"


def build_body(manifest: dict) -> str:
    clips = [c for c in manifest["clips"] if c["status"] == "ok"]
    by_src: dict[str, list] = {}
    for c in clips:
        by_src.setdefault(c["source_video_id"], []).append(c)

    total = sum(c["size_bytes"] for c in clips)
    secs = sum(c["duration"] for c in clips)
    lines = [
        "# MUTOSCOPE — 15 vertical shorts from `clippingvids`",
        "",
        f"**{len(clips)} clips · {secs/60:.1f} min total · {total/1e6:.0f} MB · "
        "1080x1920 · 30 fps · H.264 high / AAC 192k · normalised to −14 LUFS**",
        "",
        "Two styles, per the brief and its reference links:",
        "",
        "* **normal** (`N1`, `N2`) — one moment, full-bleed, face-tracked 9:16 reframe, "
        "1–3 word karaoke captions, emoji stabs, punch-in + flash + sub-bass on each beat.",
        "* **leaderboard** (`LB`) — five moments counting **#5 → #1** behind a title bar, "
        "with a ranking that fills in as it plays, a `#N` stamp per entry and a "
        "drum-roll into number one.",
        "",
        "Sound effects are **synthesised from scratch** (`src/sfx.py`, 13 effects, numpy) — "
        "no sample packs. Captions come from each source's word-level `json3` track.",
        "",
        "---",
        "",
    ]
    for vid, group in by_src.items():
        group.sort(key=lambda c: c["key"])
        head = group[0]
        lines += [
            f"### {head['source_title']}",
            f"`{vid}` · <{head['source_url']}>",
            "",
            "| clip | style | length | size | SHA-256 |",
            "|---|---|---|---|---|",
        ]
        for c in group:
            lines.append(
                f"| [`{asset_name(c['key'])}`](https://github.com/{REPO}/releases/"
                f"download/{TAG}/{asset_name(c['key'])}) | {c['kind']} | "
                f"{c['duration']:.1f}s | {c['size_bytes']/1e6:.1f} MB | "
                f"`{c['sha256'][:16]}…` |")
        lines.append("")
    lines += [
        "---",
        "",
        "### Source 1 of 6 is missing, on purpose",
        "",
        "`https://youtu.be/FDRUMXwb4mg` is **age-restricted** — every yt-dlp player "
        "client (`tv_embedded`, `web_embedded`, `mweb`, `tv`, `android_vr`, `ios`) "
        "answers *“Sign in to confirm your age.”* It needs a signed-in account's "
        "cookies, which are a credential and do not go in a sandbox or a repo "
        "(`ORDERS.md` R3). Nothing was substituted and the count was not padded: "
        "5 sources × 3 = 15. Full reproduction, both unblock routes and the three "
        "commands that finish it are in "
        f"[`mutoscope/docs/BLOCKED.md`](https://github.com/{REPO}/blob/main/mutoscope/docs/BLOCKED.md).",
        "",
        f"Build, cut list and receipts: "
        f"[`mutoscope/`](https://github.com/{REPO}/tree/main/mutoscope) · "
        f"per-clip hashes in "
        f"[`docs/MANIFEST.json`](https://github.com/{REPO}/blob/main/mutoscope/docs/MANIFEST.json).",
    ]
    return "\n".join(lines)


def ensure_release(body: str) -> dict:
    try:
        rel = _req(f"{API}/repos/{REPO}/releases/tags/{TAG}")
        print(f"  release exists id={rel['id']}")
        rel = _req(f"{API}/repos/{REPO}/releases/{rel['id']}", "PATCH",
                   {"body": body, "name": "MUTOSCOPE — 15 vertical shorts (v1)"})
        return rel
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    rel = _req(f"{API}/repos/{REPO}/releases", "POST", {
        "tag_name": TAG, "name": "MUTOSCOPE — 15 vertical shorts (v1)",
        "body": body, "draft": False, "prerelease": False,
    })
    print(f"  release created id={rel['id']}")
    return rel


def upload(rel: dict, path: str, name: str, existing: dict) -> dict:
    if name in existing:
        print(f"    - {name} already uploaded (id={existing[name]['id']})")
        return existing[name]
    with open(path, "rb") as fh:
        data = fh.read()
    url = f"{UP}/repos/{REPO}/releases/{rel['id']}/assets?name={name}"
    for attempt in range(3):
        try:
            a = _req(url, "POST", data, "application/octet-stream", raw=True)
            print(f"    + {name} ({len(data)/1e6:.1f} MB) id={a['id']}")
            return a
        except urllib.error.HTTPError as e:
            print(f"    ! {name} attempt {attempt+1}: HTTP {e.code}")
            time.sleep(4)
    raise RuntimeError(f"upload failed: {name}")


def verify(asset_url: str, expect_sha: str, expect_bytes: int) -> dict:
    """Download the published asset back and re-hash it. A URL is not a receipt."""
    req = urllib.request.Request(asset_url)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Accept", "application/octet-stream")
    h = hashlib.sha256()
    n = 0
    with urllib.request.urlopen(req, timeout=600) as r:
        while True:
            c = r.read(1 << 20)
            if not c:
                break
            h.update(c)
            n += len(c)
    return {"downloaded_bytes": n, "sha256": h.hexdigest(),
            "match": h.hexdigest() == expect_sha and n == expect_bytes}


def main():
    if not TOKEN:
        print("GITHUB_TOKEN not set", file=sys.stderr)
        return 2
    man = json.load(open(os.path.join(ROOT, "docs", "MANIFEST.json"), encoding="utf-8"))
    clips = [c for c in man["clips"] if c["status"] == "ok"]
    if not clips:
        print("nothing to publish")
        return 1
    body = build_body(man)
    rel = ensure_release(body)
    existing = {a["name"]: a for a in rel.get("assets", [])}

    receipts = []
    for c in sorted(clips, key=lambda x: x["key"]):
        path = os.path.join(OUTD, f"{c['key']}.mp4")
        name = asset_name(c["key"])
        a = upload(rel, path, name, existing)
        v = verify(a["url"], c["sha256"], c["size_bytes"])
        status = "VERIFIED" if v["match"] else "MISMATCH"
        print(f"      {status} {v['downloaded_bytes']} bytes {v['sha256'][:16]}…")
        receipts.append({
            "key": c["key"], "asset": name, "asset_id": a["id"],
            "browser_download_url":
                f"https://github.com/{REPO}/releases/download/{TAG}/{name}",
            "size_bytes": c["size_bytes"], "sha256_local": c["sha256"],
            "sha256_readback": v["sha256"], "verified": v["match"],
            "duration_s": c["duration"],
        })

    out = os.path.join(ROOT, "docs", "RELEASE_RECEIPT.json")
    json.dump({"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "agent": "mutoscope", "repo": REPO, "tag": TAG,
               "release_url": rel["html_url"],
               "verified": sum(1 for r in receipts if r["verified"]),
               "total": len(receipts), "assets": receipts},
              open(out, "w"), indent=2)
    ok = sum(1 for r in receipts if r["verified"])
    print(f"\n{ok}/{len(receipts)} assets verified by read-back")
    print(f"release: {rel['html_url']}")
    print(f"receipt: {out}")
    return 0 if ok == len(receipts) else 1


if __name__ == "__main__":
    sys.exit(main())

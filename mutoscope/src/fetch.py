"""
fetch — pull the clippingvids sources and their word-level captions.

Reads ../clippingvids (the Director's list), downloads each at <=1080p with the
json3 auto-captions beside it, and writes a receipt recording exactly what came
down and what refused.

`json3` is requested specifically: it is the only caption export that keeps
per-word offsets, which is what the karaoke captions are built from.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIST = os.path.join(os.path.dirname(ROOT), "clippingvids")
OUT = os.environ.get("MUTO_SRC", "/home/user/work/src")

ID_RE = re.compile(r"(?:youtu\.be/|v=|shorts/)([A-Za-z0-9_-]{11})")


def ids_from_list(path: str = LIST) -> list[tuple[str, str]]:
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            m = ID_RE.search(line)
            if m:
                out.append((m.group(1), line))
    return out


def fetch(vid: str, url: str) -> dict:
    os.makedirs(OUT, exist_ok=True)
    mp4 = os.path.join(OUT, f"{vid}.mp4")
    rec = {"video_id": vid, "url": url}
    if os.path.exists(mp4) and os.path.getsize(mp4) > 1_000_000:
        rec["status"] = "cached"
        return rec
    cmd = [
        "yt-dlp", "--no-warnings", "--no-progress",
        "-f", "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/bv*[height<=1080]+ba/b[height<=1080]",
        "--merge-output-format", "mp4",
        "--write-auto-subs", "--write-subs", "--sub-langs", "en-orig,en",
        "--sub-format", "json3", "--write-info-json",
        "-o", os.path.join(OUT, f"{vid}.%(ext)s"), url,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(mp4):
        err = (r.stderr or r.stdout).strip().splitlines()
        rec["status"] = "FAILED"
        rec["error"] = err[-1][:400] if err else f"rc={r.returncode}"
        return rec
    rec["status"] = "ok"
    rec["bytes"] = os.path.getsize(mp4)
    return rec


def main():
    items = ids_from_list()
    print(f"{len(items)} links in clippingvids")
    recs = []
    for vid, url in items:
        print(f"  {vid} ...", flush=True)
        rec = fetch(vid, url)
        print(f"    {rec['status']} {rec.get('error','')}")
        recs.append(rec)
    out = os.path.join(ROOT, "docs", "FETCH_RECEIPT.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "sources": recs}, open(out, "w"), indent=2)
    bad = [r for r in recs if r["status"] == "FAILED"]
    print(f"receipt -> {out}  ({len(recs)-len(bad)} ok, {len(bad)} failed)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

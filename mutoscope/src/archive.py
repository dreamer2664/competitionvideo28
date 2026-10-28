"""
archive — mirror the receipts into storagecode, per STORAGE_POLICY.md.

The policy is specific: research/receipts/quality reports go to
`data/<project>/<date>-<agent>/` with a row in `data/INDEX.md`, every push gets one
factual row in `PUSHES.md`, and **large media never enters ordinary git** — it lives
in Releases and the archive keeps the URL, hash, byte count and duration.

So this copies the small, high-value stuff: cut list, manifest, release receipt,
blocked report, handoff, and a README that lets a stranger rebuild everything.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT = "mutoscope"
DATE = time.strftime("%Y-%m-%d", time.gmtime())
PROJECT = "competitionvideo28"
REL_DIR = f"data/{PROJECT}/{DATE}-{AGENT}"


def run(cmd, cwd, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return r


def main(storage_repo: str):
    dest = os.path.join(storage_repo, REL_DIR)
    os.makedirs(dest, exist_ok=True)

    copies = [
        ("cutlist/cutlist.json", "cutlist.json"),
        ("cutlist/plans.json", "crop-plans.json"),
        ("docs/MANIFEST.json", "MANIFEST.json"),
        ("docs/RELEASE_RECEIPT.json", "RELEASE_RECEIPT.json"),
        ("docs/BLOCKED.md", "BLOCKED.md"),
        ("docs/FETCH_RECEIPT.json", "FETCH_RECEIPT.json"),
        ("HANDOFF.md", "HANDOFF.md"),
        ("README.md", "PRODUCER_README.md"),
    ]
    copied = []
    for src, name in copies:
        p = os.path.join(ROOT, src)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(dest, name))
            copied.append(name)

    man = {}
    mp = os.path.join(ROOT, "docs", "MANIFEST.json")
    if os.path.exists(mp):
        man = json.load(open(mp, encoding="utf-8"))
    rec = {}
    rp = os.path.join(ROOT, "docs", "RELEASE_RECEIPT.json")
    if os.path.exists(rp):
        rec = json.load(open(rp, encoding="utf-8"))

    clips = [c for c in man.get("clips", []) if c.get("status") == "ok"]
    secs = sum(c["duration"] for c in clips)
    byts = sum(c["size_bytes"] for c in clips)

    lines = [
        f"# {PROJECT} · {AGENT} · {DATE}",
        "",
        "Short-form clipping lane: the six YouTube links in "
        f"[`{PROJECT}/clippingvids`](https://github.com/dreamer2664/{PROJECT}/blob/main/clippingvids) "
        "cut into vertical shorts — 2 normal-style + 1 leaderboard-style per source.",
        "",
        f"**Delivered: {len(clips)} clips · {secs/60:.1f} min · {byts/1e6:.0f} MB · "
        "1080x1920 30fps H.264/AAC · −14 LUFS**",
        "",
        f"* Release (media lives here, not in git): {rec.get('release_url','pending')}",
        f"* Verified by read-back: {rec.get('verified','-')}/{rec.get('total','-')} assets",
        f"* Build + cut list: https://github.com/dreamer2664/{PROJECT}/tree/main/mutoscope",
        "",
        "## Clips",
        "",
        "| clip | kind | length | SHA-256 | source |",
        "|---|---|---|---|---|",
    ]
    for c in sorted(clips, key=lambda x: x["key"]):
        lines.append(f"| `{c['key']}` | {c['kind']} | {c['duration']:.1f}s | "
                     f"`{c['sha256'][:16]}…` | `{c['source_video_id']}` |")
    lines += [
        "",
        "## Not delivered, and why",
        "",
        "`FDRUMXwb4mg` (link 1 of 6) is age-restricted; every yt-dlp player client "
        "returns *Sign in to confirm your age*. Cookies are a credential and do not "
        "go in a sandbox or a repo (ORDERS.md R3). 5 sources x 3 = 15 clips, not 18, "
        "and the count was not padded. See `BLOCKED.md` here for reproduction and the "
        "two routes that finish it.",
        "",
        "## Files in this deposit",
        "",
    ] + [f"* `{n}`" for n in copied] + [
        "",
        "*No source footage and no MP4s are stored here — STORAGE_POLICY.md: large "
        "media goes to Releases, the archive keeps the URL, hash, bytes and duration.*",
    ]
    open(os.path.join(dest, "README.md"), "w").write("\n".join(lines))

    # data/INDEX.md — append, never overwrite a stranger
    idx = os.path.join(storage_repo, "data", "INDEX.md")
    row = (f"| {DATE} | {PROJECT} | {AGENT} | `{REL_DIR}/` | "
           f"{len(clips)} vertical shorts from clippingvids (2 normal + 1 leaderboard "
           f"per source); 1 of 6 sources age-gated, documented | "
           f"{rec.get('release_url','pending')} |\n")
    with open(idx, "a", encoding="utf-8") as fh:
        fh.write(row)

    # PUSHES.md — one factual row
    pushes = os.path.join(storage_repo, "PUSHES.md")
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                          cwd=os.path.dirname(ROOT), capture_output=True,
                          text=True).stdout.strip()
    prow = (f"| {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} | {AGENT} | "
            f"{PROJECT} | `{head}` | {len(clips)} shorts rendered + released "
            f"({secs/60:.1f} min, {byts/1e6:.0f} MB); receipts in `{REL_DIR}/` | "
            f"{rec.get('release_url','pending')} |\n")
    with open(pushes, "a", encoding="utf-8") as fh:
        fh.write(prow)

    print(f"deposited {len(copied)} files -> {REL_DIR}")
    return dest


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/home/user/repos/storagecode")

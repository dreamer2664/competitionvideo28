"""
build_all — cutlist.json in, 15 delivery MP4s + receipts out.

Run it as:
    python3 src/build_all.py plan            # face/crop plans for every segment
    python3 src/build_all.py render [IDS...] # render clips (skips finished ones)
    python3 src/build_all.py manifest        # hashes + ffprobe receipts

Planning and rendering are separate commands on purpose. Planning imports OpenCV
and holds the detector; rendering wants that 200 MB back, and on a 2 GB box you do
not get to be sentimental. Plans are cached to cutlist/plans.json so a sandbox
reset costs minutes, not the whole job.

Every clip is rendered in its own subprocess (`render-one`) so one failure cannot
take the batch with it and peak memory is whatever a single clip needs.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

SRCD = os.environ.get("MUTO_SRC", "/home/user/work/src")
OUTD = os.environ.get("MUTO_OUT", os.path.join(ROOT, "out"))
CUTLIST = os.path.join(ROOT, "cutlist", "cutlist.json")
PLANS = os.path.join(ROOT, "cutlist", "plans.json")

os.makedirs(OUTD, exist_ok=True)


def load_cutlist() -> dict:
    with open(CUTLIST, encoding="utf-8") as fh:
        return json.load(fh)


def src_mp4(vid: str) -> str:
    return os.path.join(SRCD, f"{vid}.mp4")


def src_caps(vid: str) -> str:
    for suffix in (".en-orig.json3", ".en.json3"):
        p = os.path.join(SRCD, f"{vid}{suffix}")
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"no captions for {vid}")


def clip_jobs(cl: dict) -> list[dict]:
    """Flatten the cut list into one job per delivered file."""
    jobs = []
    for s in cl["sources"]:
        for i, n in enumerate(s["normal"], start=1):
            jobs.append({
                "key": f"{s['id']}-N{i}-{n['slug']}",
                "kind": "normal", "source": s, "spec": n,
                "segments": [(n["t0"], n["t1"])],
            })
        lb = s["leaderboard"]
        jobs.append({
            "key": f"{s['id']}-LB-{lb['slug']}",
            "kind": "leaderboard", "source": s, "spec": lb,
            "segments": [(e["t0"], e["t1"]) for e in lb["entries"]],
        })
    return jobs


# --------------------------------------------------------------------------- #
# plan
# --------------------------------------------------------------------------- #

def cmd_plan():
    from analyze import crop_plan
    cl = load_cutlist()
    plans = {}
    if os.path.exists(PLANS):
        plans = json.load(open(PLANS, encoding="utf-8"))
    for job in clip_jobs(cl):
        mp4 = src_mp4(job["source"]["video_id"])
        for si, (a, b) in enumerate(job["segments"]):
            pk = f"{job['key']}#{si}"
            if pk in plans:
                print(f"  cached {pk}")
                continue
            t = time.time()
            p = crop_plan(mp4, a, b - a)
            plans[pk] = p.to_json()
            print(f"  {pk:42s} {p.mode:5s} faces={p.face_hits:.2f} "
                  f"keys={len(p.keys)} ({time.time()-t:.1f}s)")
            json.dump(plans, open(PLANS, "w"), indent=1)
    json.dump(plans, open(PLANS, "w"), indent=1)
    print(f"plans: {len(plans)} segments -> {PLANS}")


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #

def _entry_emoji(label: str) -> str:
    from vidkit import split_emoji
    runs = [c for k, c in split_emoji(label) if k == "emoji"]
    return runs[-1] if runs else ""


def render_one(key: str):
    from analyze import CropPlan
    from render import build_base, composite, ffprobe_report
    from styles import leaderboard_track, normal_track
    from vidkit import INK, RED
    from ytcaps import group_cues, load_words, words_in

    cl = load_cutlist()
    plans = json.load(open(PLANS, encoding="utf-8"))
    job = next(j for j in clip_jobs(cl) if j["key"] == key)
    s = job["source"]
    mp4 = src_mp4(s["video_id"])
    words = load_words(src_caps(s["video_id"]))

    def plan_for(i):
        d = plans[f"{key}#{i}"]
        return CropPlan(d["mode"], [tuple(k) for k in d["keys"]], d["face_hits"],
                        d.get("note", ""))

    tmp_base = os.path.join(os.environ.get("MUTO_TMP", "/home/user/work/tmp"),
                            f"base_{key}.mp4")
    out = os.path.join(OUTD, f"{key}.mp4")

    if job["kind"] == "normal":
        n = job["spec"]
        plan = plan_for(0)
        segs = [{"src": mp4, "t0": n["t0"], "t1": n["t1"], "plan": plan,
                 "zooms": [(b, 0.13) for b in n["beats"]]}]
        dur = build_base(segs, tmp_base)
        cues = group_cues(words_in(words, n["t0"], n["t1"]))
        tr, sx = normal_track(
            dur, cues, n["hook"], n["hook_emoji"], n["beats"], plan.mode,
            [(t, e) for t, e in n["emoji"]], n.get("end_card"),
            seed=abs(hash(key)) % 9999, cap_dy=s.get("caption_dy", 0))
    else:
        lb = job["spec"]
        entries, cues_by, segs, cur = [], [], [], 0.0
        for i, e in enumerate(lb["entries"]):
            plan = plan_for(i)
            ln = e["t1"] - e["t0"]
            segs.append({"src": mp4, "t0": e["t0"], "t1": e["t1"], "plan": plan,
                         "zooms": [(1.1, 0.11)]})
            entries.append({"rank": e["rank"], "label": e["label"],
                            "t0": cur, "t1": cur + ln,
                            "beats": [cur + ln * 0.55],
                            "emoji": _entry_emoji(e["label"])})
            cues_by.append([(c[0] + cur, c[1] + cur, c[2])
                            for c in group_cues(words_in(words, e["t0"], e["t1"]))])
            cur += ln
        dur = build_base(segs, tmp_base)
        # rescale entry windows onto the real concatenated duration
        if abs(dur - cur) > 0.05 and cur > 0:
            k = dur / cur
            for en, cs in zip(entries, cues_by):
                en["t0"] *= k
                en["t1"] *= k
                en["beats"] = [b * k for b in en["beats"]]
            cues_by = [[(a * k, b * k, t) for a, b, t in cs] for cs in cues_by]
        mode = plan_for(0).mode
        tr, sx = leaderboard_track(
            dur, entries,
            [(lb["title_lead"], INK), (s["subject"], RED), (lb["title_tail"], INK)],
            lb["sub"], cues_by, mode, seed=abs(hash(key)) % 9999,
            cap_dy=s.get("caption_dy", 0))

    composite(tmp_base, tr, sx, out, quiet=False)
    if os.path.exists(tmp_base):
        os.remove(tmp_base)
    rep = ffprobe_report(out)
    print(f"DONE {key}: {rep}")
    return out


def cmd_render(only: list[str]):
    cl = load_cutlist()
    jobs = clip_jobs(cl)
    if only:
        jobs = [j for j in jobs if any(o in j["key"] for o in only)]
    for j in jobs:
        out = os.path.join(OUTD, f"{j['key']}.mp4")
        if os.path.exists(out) and os.path.getsize(out) > 200_000:
            print(f"skip (exists) {j['key']}")
            continue
        print(f"\n=== {j['key']} ===", flush=True)
        t = time.time()
        r = subprocess.run([sys.executable, __file__, "render-one", j["key"]])
        if r.returncode != 0:
            print(f"!! FAILED {j['key']} rc={r.returncode}", flush=True)
        else:
            print(f"   {j['key']} in {time.time()-t:.0f}s", flush=True)


# --------------------------------------------------------------------------- #
# manifest
# --------------------------------------------------------------------------- #

def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_manifest():
    from render import ffprobe_report
    cl = load_cutlist()
    rows = []
    for j in clip_jobs(cl):
        p = os.path.join(OUTD, f"{j['key']}.mp4")
        if not os.path.exists(p):
            rows.append({"key": j["key"], "status": "MISSING"})
            continue
        rep = ffprobe_report(p)
        rows.append({
            "key": j["key"], "status": "ok", "file": os.path.basename(p),
            "kind": j["kind"], "source_video_id": j["source"]["video_id"],
            "source_url": j["source"]["url"], "source_title": j["source"]["title"],
            "segments": [[a, b] for a, b in j["segments"]],
            "sha256": sha256(p), **rep,
        })
    out = os.path.join(ROOT, "docs", "MANIFEST.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "agent": "mutoscope", "clips": rows}, open(out, "w"), indent=2)
    ok = sum(1 for r in rows if r["status"] == "ok")
    print(f"manifest: {ok}/{len(rows)} clips -> {out}")
    for r in rows:
        if r["status"] == "ok":
            print(f"  {r['key']:34s} {r['duration']:6.2f}s "
                  f"{r['size_bytes']/1e6:6.2f}MB {r['sha256'][:12]}")
        else:
            print(f"  {r['key']:34s} MISSING")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "render"
    if cmd == "plan":
        cmd_plan()
    elif cmd == "render":
        cmd_render(sys.argv[2:])
    elif cmd == "render-one":
        render_one(sys.argv[2])
    elif cmd == "manifest":
        cmd_manifest()
    else:
        print(__doc__)

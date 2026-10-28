#!/usr/bin/env python3
"""
render.py — frame renderer.

  python3 render.py --start 0 --end 3000 --out work/seg0.mp4
  python3 render.py --frame 1240 --png /tmp/preview.png     # single-frame QC
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

import scenes1
import scenes2
import scenes3
from render_kit import FPS, H, W

BASE = Path(__file__).resolve().parent.parent
REGISTRY = {}
REGISTRY.update(scenes1.REGISTRY)
REGISTRY.update(scenes2.REGISTRY)
REGISTRY.update(scenes3.REGISTRY)

_tl = None


def timeline():
    global _tl
    if _tl is None:
        _tl = json.loads((BASE / "work" / "timeline.json").read_text())
    return _tl


def shot_for_frame(f, tl):
    for s in tl["shots"]:
        if s["frame_start"] <= f < s["frame_end"]:
            return s
    return tl["shots"][-1] if f >= tl["shots"][-1]["frame_end"] else tl["shots"][0]


def render_frame(f, tl):
    s = shot_for_frame(f, tl)
    t = (f - s["frame_start"]) / float(FPS)
    t = min(max(t, 0.0), s["duration"] - 1e-4)
    u = t / max(s["duration"], 1e-6)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    fn = REGISTRY[s["scene_kind"]]
    img = fn(img, s, u, t, tl)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--frame", type=int, default=None)
    ap.add_argument("--png", default=None)
    ap.add_argument("--crf", type=int, default=17)
    ap.add_argument("--preset", default="veryfast")
    args = ap.parse_args()

    tl = timeline()
    total = int(tl["total_frames"])

    if args.frame is not None:
        img = render_frame(args.frame, tl)
        out = args.png or f"/tmp/frame_{args.frame:05d}.png"
        img.save(out)
        s = shot_for_frame(args.frame, tl)
        print(json.dumps({"frame": args.frame, "shot": s["id"], "scene": s["scene_kind"], "png": out}))
        return

    start = args.start
    end = total if args.end is None else min(args.end, total)
    out = args.out or str(BASE / "work" / f"seg_{start}_{end}.mp4")

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
        "-an",
        "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
        "-pix_fmt", "yuv420p", "-g", "60", "-keyint_min", "30",
        "-x264-params", "aq-mode=3:deblock=-1,-1",
        out,
    ]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    t0 = time.time()
    n = end - start
    for i, f in enumerate(range(start, end)):
        img = render_frame(f, tl)
        try:
            p.stdin.write(img.tobytes())
        except BrokenPipeError:
            print("ffmpeg closed the pipe early:", p.stderr.read().decode()[:800], file=sys.stderr)
            return 1
        if i % 150 == 0:
            el = time.time() - t0
            rate = (i + 1) / max(el, 1e-6)
            eta = (n - i - 1) / max(rate, 1e-6)
            print(f"[{Path(out).name}] {i + 1}/{n} frames · {rate:5.2f} fps · eta {eta / 60:4.1f} min", flush=True)
    p.stdin.close()
    rc = p.wait()
    print(f"[{Path(out).name}] done in {(time.time() - t0) / 60:.2f} min · rc={rc}", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())

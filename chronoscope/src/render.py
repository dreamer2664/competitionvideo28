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

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

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


# ---------------------------------------------------------------- living layer
# Every frame gets three continuous, low-amplitude motions: a breathing camera,
# animated film grain and a drifting light band. Without them a diagram shot can
# sit pixel-identical for seconds and the film reads as a slideshow (measured:
# 45 freeze segments over 1.2 s in master r01, longest 16.0 s).
_GRAIN = None
_LIGHT = None


def _grain_bank():
    """Six mid-grey noise fields, cycled every two frames and blended at ~4%.
    Low amplitude on purpose: enough to keep the encoder awake and the picture
    alive, never enough to read as snow over the diagrams."""
    global _GRAIN
    if _GRAIN is None:
        rng = np.random.default_rng(4242)
        bank = []
        for i in range(6):
            n = rng.normal(0, 15.0, (270, 480)).astype(np.float32)
            g = Image.fromarray(np.clip(128 + n, 0, 255).astype(np.uint8), "L").convert("RGB")
            bank.append(g)
        _GRAIN = bank
    return _GRAIN


def _light_layer():
    global _LIGHT
    if _LIGHT is None:
        small = Image.new("RGBA", (240, 135), (0, 0, 0, 0))
        d = ImageDraw.Draw(small)
        d.ellipse((60, 30, 180, 105), fill=(255, 238, 206, 70))
        _LIGHT = small.filter(ImageFilter.GaussianBlur(26))
    return _LIGHT


def living_layer(img, f, shot):
    """breathing camera + animated grain + drifting warm light band."""
    # 1. breathing camera: scale 1.006 -> 1.020, slow lissajous drift
    ph = shot["index"] * 1.7
    s = 1.008 + 0.006 * math.sin(2 * math.pi * f / 780.0 + ph)
    dx = 2.4 * math.sin(2 * math.pi * f / 690.0 + ph * 0.7)
    dy = 1.8 * math.cos(2 * math.pi * f / 910.0 + ph * 1.3)
    inv = 1.0 / s
    a = inv
    c = -(inv - 1.0) * W / 2 + dx
    e = inv
    fff = -(inv - 1.0) * H / 2 + dy
    img = img.transform((W, H), Image.AFFINE, (a, 0, c, 0, e, fff), resample=Image.BILINEAR)

    # 2. drifting light band (quarter-res sprite, upscaled)
    sp = _light_layer()
    lx = (f * 1.9) % (W + 900) - 450
    light = sp.resize((520, 420), Image.BILINEAR).convert("RGBA")
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halo.alpha_composite(light, (int(max(-260, min(W + 260, lx))), int(H * 0.18)))
    img = Image.alpha_composite(img.convert("RGBA"), halo)

    # 3. animated grain, blended at low amplitude
    g = _grain_bank()[(f // 2) % 6].resize((W, H), Image.BILINEAR)
    return Image.blend(img.convert("RGB"), g, 0.045)


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
    return living_layer(img, f, s)


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

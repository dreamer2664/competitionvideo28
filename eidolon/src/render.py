"""The engine: timeline + shots + captions + grain → H.264.

Rendering is split into N contiguous chunks, each rendered by its own process and
encoded by its own ffmpeg, then concatenated losslessly. On a two-core box that
roughly halves wall time without sharing a single frame in memory.

    python3 render.py                # full film
    python3 render.py --from 200 --to 260   # seconds, for tests
"""
import argparse
import json
import math
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenes1
import scenes2
from canvas import (AMBER, DIM, FONTS, H, PAPER, W, act_card, add_grain, clamp,
                    draw_text, ease_in_out, ease_out, prog, rule, text_len)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "out")
TL = json.load(open(os.path.join(OUT, "timeline.json")))
FPS = TL["fps"]
TOTAL = TL["total"]

SCENES = {}
for mod in (scenes1, scenes2):
    for name in dir(mod):
        fn = getattr(mod, name)
        if callable(fn) and getattr(fn, "__module__", "") == mod.__name__ and not name.startswith("_"):
            SCENES.setdefault(name, fn)

ACTS = TL["acts"]
BEATS = TL["beats"]
CAPS = TL["captions"]


# ------------------------------------------------------------------ overlays
def draw_captions(img, t):
    """Bottom caption: one line, up to two rows, the spoken word lit."""
    for c in CAPS:
        if c["start"] <= t <= c["end"]:
            break
    else:
        return
    words = c["words"]
    font = FONTS("sans", 31, 500, opsz=30)
    tracking = 0.2
    # wrap to at most two lines of ~54 characters
    lines, cur = [], []
    for w in words:
        trial = " ".join(x["w"] for x in cur + [w])
        if text_len(trial, font) > 1080 and cur:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    y = 928 if len(lines) == 1 else 900
    # a soft plate behind the type so bright footage never eats it
    for li, ln in enumerate(lines):
        total = text_len(" ".join(x["w"] for x in ln), font, tracking)
        x = W / 2 - total / 2
        yy = y + li * 46
        platte = ImageDraw.Draw(img, "RGBA")
        platte.rounded_rectangle([x - 22, yy - 34, x + total + 22, yy + 18],
                                 radius=10, fill=(4, 5, 8, 128))
        for w in ln:
            active = w["t"] <= t <= w["t"] + max(w["d"], 0.12)
            col = AMBER if active else PAPER
            a = 255 if active else 224
            draw_text(img, (x, yy + 2), w["w"], font, (0, 0, 0), int(a * 0.55), "ls", tracking)
            draw_text(img, (x, yy), w["w"], font, col, int(a), "ls", tracking)
            x += text_len(w["w"], font, tracking) + font.getlength(" ")


def act_stamp(img, t):
    """Chapter transitions: a numeral and a title over a softened frame, 2.8 s."""
    for i, a in enumerate(ACTS):
        if i == 0:
            continue
        p = (t - a["start"]) / 2.8
        if 0 <= p <= 1:
            return act_card(img, a["numeral"], a["title"], p)
    return img


def frame_at(t):
    beat = BEATS[0]
    for b in BEATS:
        if b["start"] <= t < b["end"]:
            beat = b
            break
    dur = beat["end"] - beat["start"]
    img = SCENES[beat["visual"]](min(t - beat["start"], dur - 0.001), dur)
    img = act_stamp(img, t)
    draw_captions(img, t)
    img = add_grain(img, int(t * FPS))
    return img


# ------------------------------------------------------------------ chunked encode
def render_chunk(args):
    idx, f0, f1 = args
    raw = os.path.join(OUT, f"seg{idx:02d}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "faster", "-crf", "21",
           "-pix_fmt", "yuv420p", "-x264-params", "keyint=60:min-keyint=30",
           raw]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        img = frame_at(f / FPS)
        p.stdin.write(img.tobytes())
    p.stdin.close()
    p.wait()
    return raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=TOTAL)
    ap.add_argument("--chunks", type=int, default=2)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default=os.path.join(OUT, "picture.mp4"))
    ap.add_argument("--still", type=float, default=None)
    a = ap.parse_args()

    if a.still is not None:
        frame_at(a.still).save(os.path.join(OUT, f"still_{a.still:06.1f}.png"))
        return

    f_start, f_end = int(a.t0 * FPS), int(a.t1 * FPS)
    n = f_end - f_start
    per = math.ceil(n / a.chunks)
    jobs = [(i, f_start + i * per, min(f_start + (i + 1) * per, f_end))
            for i in range(a.chunks)]
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        segs = list(ex.map(render_chunk, jobs))
    lst = os.path.join(OUT, "segs.txt")
    with open(lst, "w") as fh:
        for s in segs:
            fh.write(f"file '{s}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", a.out], check=True)
    for s in segs:
        os.remove(s)
    print(f"picture: {a.out}  {n} frames  {n/FPS:.1f}s")


if __name__ == "__main__":
    main()

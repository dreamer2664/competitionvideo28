"""Render single stills from any shot, so composition can be checked in seconds.

    python3 preview.py b09 3 8 12      # beat id + local times
    python3 preview.py all             # one frame from the middle of every shot
"""
import json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenes1  # noqa: F401
import scenes2  # noqa: F401
from canvas import add_grain

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "out", "preview")
TL = json.load(open(os.path.join(ROOT, "out", "timeline.json")))
BEATS = {b["id"]: b for b in TL["beats"]}

SCENES = {}
for mod in (scenes1, scenes2):
    for name in dir(mod):
        fn = getattr(mod, name)
        if callable(fn) and getattr(fn, "__module__", "") == mod.__name__ and not name.startswith("_"):
            SCENES.setdefault(name, fn)


def render(beat_id, t):
    b = BEATS[beat_id]
    dur = b["end"] - b["start"]
    fn = SCENES[b["visual"]]
    img = fn(min(t, dur - 0.01), dur)
    return add_grain(img, int(t * 30))


def main():
    os.makedirs(OUT, exist_ok=True)
    args = sys.argv[1:]
    if not args or args[0] == "all":
        for bid, b in BEATS.items():
            t = (b["end"] - b["start"]) * 0.62
            p = os.path.join(OUT, f"{bid}_{b['visual']}_{t:05.1f}.png")
            render(bid, t).save(p)
            print(p)
        return
    bid = args[0]
    for s in args[1:]:
        t = float(s)
        p = os.path.join(OUT, f"{bid}_{t:05.1f}.png")
        render(bid, t).save(p)
        print(p)


if __name__ == "__main__":
    main()

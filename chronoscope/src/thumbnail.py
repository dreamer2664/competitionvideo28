#!/usr/bin/env python3
"""thumbnail.py — the 1280x720 YouTube thumbnail, drawn from the film's own plates."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_kit import BRONZE, BRONZE_LIGHT, GOLD, PARCHMENT, font, plate  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "assets" / "thumbnail"
TW, TH = 1280, 720


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    bg = plate("plate_02_fragment_a.jpg").resize((TW, TH), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(1.2))
    dark = Image.new("RGB", (TW, TH), (6, 9, 14))
    bg = Image.blend(bg, dark, 0.45).convert("RGB")

    img = bg.convert("RGBA")

    # left-to-right scrim so the type sits on darkness while the bronze stays visible
    scrim = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    for x in range(TW):
        a = int(235 * max(0.0, 1.0 - x / (TW * 0.78)) ** 0.85)
        sd.line([(x, 0), (x, TH)], fill=(5, 8, 13, a))
    img.alpha_composite(scrim)
    d = ImageDraw.Draw(img, "RGBA")

    # amber rule + kicker
    d.rectangle((64, 96, 68, 300), fill=BRONZE)
    d.text((94, 92), "2,000 YEARS OLD · 30 BRONZE GEARS", font=font("mono_md", 22), fill=GOLD)

    d.text((90, 168), "THIRTY", font=font("display", 118), fill=PARCHMENT,
           stroke_width=0, spacing=8)
    d.text((90, 300), "BRONZE", font=font("display", 118), fill=PARCHMENT, spacing=8)
    d.text((90, 432), "WHEELS", font=font("display", 118), fill=GOLD, spacing=8)

    d.text((96, 602), "the Antikythera Mechanism, decoded", font=font("sans_md", 34),
           fill=(214, 226, 236))

    # scale legibility check: 120 px wide
    small = img.convert("RGB").resize((120, 68), Image.LANCZOS)
    small.save(OUT / "thumb_120px_check.png")

    out = OUT / "thumb_1280x720.jpg"
    img.convert("RGB").save(out, quality=92, subsampling=0, optimize=True)
    print(out, out.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Delivery stills: the YouTube thumbnail (1280×720) and the poster frame.

    python3 thumb.py     # writes out/thumb.png and out/poster.png
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenes1
import scenes2
from canvas import (AMBER, CYAN, DIM, FONTS, GREY, H, PAPER, RED, W, add_grain,
                    draw_text, ease_out, prog, text_len)
from scenes2 import hand_ellipse, write_text

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "out"))


def thumbnail():
    """A thumbnail is not a still: one idea, three words, readable at 320 px."""
    from canvas import base_plate, INK, disc
    img = base_plate((9, 10, 14), (3, 4, 6), scrim=False)
    d = ImageDraw.Draw(img, "RGBA")
    from canvas import stars, draw_stars
    draw_stars(img, stars(160, seed=77), 3.0, alpha_scale=0.5, size_scale=0.9)

    # a wide glow behind the characters
    from canvas import radial_glow
    g = radial_glow(1400, (227, 162, 75), 26, 2.4)
    img.paste(g, (200, -120), g)

    draw_text(img, (140, 300), "6EQUJ5", FONTS("mono", 300, 700), PAPER, 255, "ls", 12)
    hand_ellipse(img, (700, 232), 600, 168, 1.0, RED, 9, seed=9, alpha=255)
    d.line([(144, 430), (1180, 430)], fill=AMBER + (120,), width=2)
    draw_text(img, (144, 528), "THE SIGNAL THAT", FONTS("serif", 122, 500), PAPER, 250, "ls", 2)
    draw_text(img, (144, 672), "NEVER CAME TWICE", FONTS("serif", 122, 500), PAPER, 250, "ls", 2)
    write_text(img, (1290, 690), "Wow!", FONTS("hand", 240, 700), RED, 1.0, angle=-7.0, alpha=255)
    draw_text(img, (150, 790), "15 AUGUST 1977 · 72 SECONDS · ONE PAGE", FONTS("cond", 32, 500),
              AMBER, 230, "ls", 5.0)
    draw_text(img, (150, 900), "A FILM MADE IN CODE · EIDOLON", FONTS("cond", 26, 400),
              GREY, 170, "ls", 4.0)
    img = add_grain(img, 7)
    img.save(os.path.join(OUT, "thumb.png"))
    img.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, "thumb_1280.png"))
    return img


def poster():
    img = scenes2.coda(46.0, 50.0)
    img.save(os.path.join(OUT, "poster.png"))
    return img


if __name__ == "__main__":
    thumbnail()
    poster()
    print("thumb.png + poster.png written")

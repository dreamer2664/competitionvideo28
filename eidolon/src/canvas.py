"""The drawing kit: palette, type, easing, texture, captions.

Everything the film is made of. Scenes import this and draw; the engine in
render.py only decides *which* frame of *which* shot to ask for.
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "assets", "fonts")

INK = (7, 8, 11)
INK2 = (12, 14, 19)
PAPER = (239, 233, 220)
AMBER = (227, 162, 75)
CYAN = (143, 214, 223)
RED = (192, 57, 43)
GREY = (138, 142, 150)
DIM = (86, 90, 98)


# ------------------------------------------------------------------ easing / time
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def prog(t, t0, dur):
    """0..1 progress of a thing that starts at t0 and takes dur seconds."""
    if dur <= 0:
        return 1.0 if t >= t0 else 0.0
    return clamp((t - t0) / dur)


def ease_in_out(x):
    x = clamp(x)
    return 4 * x * x * x if x < 0.5 else 1 - pow(-2 * x + 2, 3) / 2


def ease_out(x):
    x = clamp(x)
    return 1 - pow(1 - x, 3)


def ease_in(x):
    x = clamp(x)
    return x * x * x


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def pulse(t, period=2.0, sharp=6.0):
    """0..1 pulse, peaks once per period."""
    return pow(0.5 + 0.5 * math.cos(2 * math.pi * t / period), sharp)


def fade_window(t, dur, fin=0.5, fout=0.5):
    return min(clamp(t / fin), clamp((dur - t) / fout))


# ------------------------------------------------------------------ type
class FontBook:
    def __init__(self):
        self.paths = {
            "serif": os.path.join(FONT_DIR, "cormorant.ttf"),
            "sans": os.path.join(FONT_DIR, "inter.ttf"),
            "cond": os.path.join(FONT_DIR, "oswald.ttf"),
            "hand": os.path.join(FONT_DIR, "caveat.ttf"),
            "mono": os.path.join(FONT_DIR, "jetbrains.ttf"),
        }
        self.cache = {}

    def __call__(self, name, size, weight=None, opsz=None):
        key = (name, size, weight, opsz)
        if key in self.cache:
            return self.cache[key]
        f = ImageFont.truetype(self.paths[name], size)
        try:
            axes = {a["name"]: a for a in f.get_variation_axes()}
            vals = []
            for key_name, a in axes.items():
                nm = key_name.decode() if isinstance(key_name, bytes) else key_name
                if nm == "Weight":
                    vals.append(weight or a["default"])
                elif nm.lower().startswith("optical"):
                    vals.append(opsz or a["default"])
                else:
                    vals.append(a["default"])
            f.set_variation_by_axes(vals)
        except Exception:
            pass
        self.cache[key] = f
        return f


FONTS = FontBook()


def text_len(s, font, tracking=0.0):
    if not s:
        return 0.0
    return sum(font.getlength(c) for c in s) + tracking * (len(s) - 1)


def draw_text(img, xy, s, font, fill, alpha=255, anchor="ls", tracking=0.0):
    """Draw with letter-spacing and vertical-centre anchors. anchor: l|c|r + a|m|s
    (a = ascender top, m = middle, s = baseline)."""
    if not s or alpha <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    col = tuple(fill) + (int(alpha),) if len(fill) == 3 else tuple(fill)
    hx, va = anchor[0], anchor[1] if len(anchor) > 1 else "s"
    total = text_len(s, font, tracking)
    x = xy[0]
    if hx == "c":
        x -= total / 2
    elif hx == "r":
        x -= total
    asc, desc = font.getmetrics()[:2]
    y = xy[1]
    # xy is always the *baseline*-style reference, never the top of the box:
    # "s" = baseline, "m" = optical middle, "a" = ascender top.
    if va == "m":
        y += asc * 0.52
    elif va == "a":
        y += asc
    if tracking == 0:
        d.text((x, y), s, font=font, fill=col, anchor="ls")
    else:
        for ch in s:
            d.text((x, y), ch, font=font, fill=col, anchor="ls")
            x += font.getlength(ch) + tracking


def wrap(s, font, max_w):
    words, lines, cur = s.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if text_len(test, font) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_block(img, xy, s, font, fill, max_w, leading=1.32, alpha=255, align="l"):
    lines = wrap(s, font, max_w)
    lh = font.size * leading
    for i, ln in enumerate(lines):
        anchor = {"l": "la", "c": "ca", "r": "ra"}[align]
        draw_text(img, (xy[0], xy[1] + i * lh), ln, font, fill, alpha, anchor)


def typewrite(img, xy, s, font, fill, t, cps=34, alpha=255, anchor="ls",
              tracking=0.0, caret=True):
    n = int(clamp(t * cps, 0, len(s)))
    shown = s[:n]
    draw_text(img, xy, shown, font, fill, alpha, anchor, tracking)
    if caret and n < len(s) and int(t * 3) % 2 == 0:
        x0 = xy[0] - (text_len(s, font, tracking) / 2 if anchor[0] == "c" else 0)
        cx = x0 + text_len(shown, font, tracking) + (2 if shown else 0)
        d = ImageDraw.Draw(img, "RGBA")
        asc = font.getmetrics()[0]
        d.rectangle([cx, xy[1] - asc * 0.92, cx + max(2, font.size * 0.05),
                     xy[1] - asc * 0.08], fill=tuple(fill) + (int(alpha * 0.8),))


# ------------------------------------------------------------------ geometry
def line(d, p0, p1, fill, width=2, alpha=255):
    if alpha <= 0:
        return
    d.line([p0, p1], fill=tuple(fill) + (int(alpha),) if len(fill) == 3 else fill,
           width=width)


def polyline(img, pts, fill, width=2, alpha=255, progress=1.0):
    """Draw a polyline up to `progress` of its length (for stroke-on animations)."""
    if len(pts) < 2 or alpha <= 0 or progress <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    col = tuple(fill) + (int(alpha),) if len(fill) == 3 else tuple(fill)
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seg) or 1.0
    want = total * clamp(progress)
    acc = 0.0
    for i, L in enumerate(seg):
        if acc >= want:
            break
        take = min(L, want - acc)
        if take <= 0:
            break
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        f = take / L if L else 0
        d.line([(x0, y0), (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)], fill=col, width=width)
        acc += take


def dashed(d, p0, p1, fill, width=1, dash=6, gap=6, alpha=255):
    if alpha <= 0:
        return
    col = tuple(fill) + (int(alpha),) if len(fill) == 3 else fill
    x0, y0 = p0
    x1, y1 = p1
    L = math.dist(p0, p1)
    if L == 0:
        return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    s = 0.0
    while s < L:
        e = min(s + dash, L)
        d.line([(x0 + ux * s, y0 + uy * s), (x0 + ux * e, y0 + uy * e)], fill=col, width=width)
        s += dash + gap


def ring(img, center, r, fill, width=2, alpha=255, start=0.0, end=1.0):
    if alpha <= 0 or r <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    col = tuple(fill) + (int(alpha),) if len(fill) == 3 else fill
    box = [center[0] - r, center[1] - r, center[0] + r, center[1] + r]
    d.arc(box, start=-90 + start * 360, end=-90 + end * 360, fill=col, width=width)


def disc(img, center, r, fill, alpha=255):
    if alpha <= 0 or r <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    col = tuple(fill) + (int(alpha),) if len(fill) == 3 else fill
    d.ellipse([center[0] - r, center[1] - r, center[0] + r, center[1] + r], fill=col)


def box(img, xy, fill=None, outline=None, width=1, alpha=255, radius=0):
    d = ImageDraw.Draw(img, "RGBA")
    def c(v):
        if v is None:
            return None
        return tuple(v) + (int(alpha),) if len(v) == 3 else v
    d.rounded_rectangle(xy, radius=radius, fill=c(fill), outline=c(outline), width=width)


# ------------------------------------------------------------------ texture
_VIG = None
_GRAIN = []


def vignette_mask(strength=0.46, floor=0.52):
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        nx = (xx - W / 2) / (W / 2)
        ny = (yy - H / 2) / (H / 2)
        r = np.sqrt(nx ** 2 * 0.82 + ny ** 2)
        _VIG = np.clip(1 - strength * np.clip(r - 0.30, 0, None) ** 1.7,
                       floor, 1).astype(np.float32)
    return _VIG


_GLOW = None


def _key_glow():
    """A very wide, very faint warm key at 38% height: the plate is dark, not black."""
    global _GLOW
    if _GLOW is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W * 0.5) / (W * 0.62)) ** 2 + ((yy - H * 0.38) / (H * 0.55)) ** 2)
        g = np.clip(1 - d, 0, 1) ** 2.1
        _GLOW = (g * 15.0).astype(np.float32)
    return _GLOW


def base_plate(top=(30, 34, 44), bottom=(10, 12, 17), scrim=True):
    """A vertical gradient with vignette, a faint key and the caption scrim baked in,
    so every frame starts from a finished plate and only draws the motion.
    Calibrated for a phone screen: the film is dark, but it is never black."""
    t = np.linspace(0, 1, H, dtype=np.float32)[:, None, None] ** 0.85
    a = np.array(top, dtype=np.float32)[None, None, :]
    b = np.array(bottom, dtype=np.float32)[None, None, :]
    arr = (a * (1 - t) + b * t)
    arr = np.repeat(arr, W, axis=1)
    arr += _key_glow()[..., None] * np.array([1.0, 0.82, 0.62], dtype=np.float32)
    arr *= vignette_mask()[..., None]
    if scrim:
        g = np.clip((np.arange(H) - H * 0.76) / (H * 0.24), 0, 1)[:, None, None] ** 1.4
        arr = arr * (1 - 0.38 * g)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


_LUT = None


def shadow_lift():
    """One grade over everything: lift the toe so shadows read on a phone, leave the
    highlights where the type needs them."""
    global _LUT
    if _LUT is None:
        i = np.arange(256, dtype=np.float32)
        out = i + 14.0 * (1 - i / 255.0) ** 2.2
        _LUT = np.clip(out, 0, 255).astype(np.uint8)
    return _LUT


def make_grain(n=6, amount=5.0):
    global _GRAIN
    if _GRAIN:
        return _GRAIN
    rng = np.random.default_rng(4242)
    for _ in range(n):
        small = rng.normal(0, amount, (H // 3, W // 3)).astype(np.float32)
        plate = np.array(Image.fromarray(np.clip(128 + small, 0, 255).astype(np.uint8))
                         .resize((W, H), Image.BILINEAR), dtype=np.int16) - 128
        _GRAIN.append(plate)
    return _GRAIN


def add_grain(img, frame_idx):
    plates = make_grain()
    p = plates[frame_idx % len(plates)]
    arr = np.asarray(img).astype(np.int16)
    arr = np.clip(arr + p[..., None], 0, 255).astype(np.uint8)
    arr = shadow_lift()[arr]
    return Image.fromarray(arr)


def bloom(img, amount=0.55, radius=18, threshold=170):
    """Cheap bloom: quarter-res bright pass, blur, add back."""
    small = img.resize((W // 4, H // 4), Image.BILINEAR)
    a = np.asarray(small).astype(np.float32)
    bright = np.clip(a - threshold, 0, None)
    b = Image.fromarray(np.clip(bright * 3.2, 0, 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(radius / 4))
    b = b.resize((W, H), Image.BILINEAR)
    base = np.asarray(img).astype(np.float32)
    out = np.clip(base + np.asarray(b).astype(np.float32) * amount, 0, 255)
    return Image.fromarray(out.astype(np.uint8))


def radial_glow(size, color, alpha=60, falloff=2.2):
    s = size
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    r = np.sqrt((xx - s / 2) ** 2 + (yy - s / 2) ** 2) / (s / 2)
    f = np.clip(1 - r, 0, 1) ** falloff
    arr = np.zeros((s, s, 4), dtype=np.uint8)
    for i in range(3):
        arr[..., i] = color[i]
    arr[..., 3] = (f * alpha).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


# ------------------------------------------------------------------ data-ish visuals
def scanlines(img, alpha=10, step=3, color=(0, 0, 0)):
    d = ImageDraw.Draw(img, "RGBA")
    for y in range(0, H, step):
        d.line([(0, y), (W, y)], fill=tuple(color) + (alpha,))


def hgrid(img, ys, x0=0, x1=W, color=DIM, alpha=26, width=1):
    d = ImageDraw.Draw(img, "RGBA")
    for y in ys:
        d.line([(x0, y), (x1, y)], fill=tuple(color) + (alpha,), width=width)


def vgrid(img, xs, y0=0, y1=H, color=DIM, alpha=26, width=1):
    d = ImageDraw.Draw(img, "RGBA")
    for x in xs:
        d.line([(x, y0), (x, y1)], fill=tuple(color) + (alpha,), width=width)


def stars(n=240, seed=77):
    rng = random.Random(seed)
    return [(rng.uniform(0, W), rng.uniform(0, H * 0.92), rng.uniform(0.3, 1.0),
             rng.uniform(0, 6.28)) for _ in range(n)]


def draw_stars(img, st, t, alpha_scale=1.0, drift=0.0, size_scale=1.0):
    d = ImageDraw.Draw(img, "RGBA")
    for x, y, b, ph in st:
        tw = 0.55 + 0.45 * math.sin(t * 0.9 + ph)
        a = int(clamp(b * tw * 190 * alpha_scale, 0, 255))
        if a <= 2:
            continue
        px = (x - drift * 6) % W
        r = (0.6 + b * 0.9) * size_scale
        d.ellipse([px - r, y - r, px + r, y + r], fill=(222, 228, 238, a))


def label(img, xy, s, alpha=200, color=AMBER, size=17, anchor="ls", tracking=2.4):
    draw_text(img, xy, s.upper(), FONTS("cond", size, weight=400), color,
              alpha, anchor, tracking)


def leader(img, start, end, alpha=120, color=DIM, width=1, text=None, text_alpha=190,
           text_size=17, text_color=PAPER, side="r"):
    """A thin leader line from a feature to a label, with a small dot at the feature."""
    dashed(ImageDraw.Draw(img, "RGBA"), start, end, color, width=1, dash=4, gap=5, alpha=alpha)
    disc(img, start, 2.4, color, alpha + 40)
    if text:
        anchor = "ls" if side == "r" else "rs"
        draw_text(img, (end[0] + (8 if side == "r" else -8), end[1] + 6), text,
                  FONTS("cond", text_size, 400), text_color, text_alpha, anchor, 1.8)


# ------------------------------------------------------------------ frame chrome
def chrome(img, left, right="", alpha=70, y=58):
    """Quiet frame furniture: an act stamp top-left, a technical tag top-right, and
    four corner ticks. Sits above the plate, below everything that matters."""
    d = ImageDraw.Draw(img, "RGBA")
    if left:
        draw_text(img, (96, y), left.upper(), FONTS("cond", 14, 400), PAPER, alpha, "ls", 3.2)
    if right:
        draw_text(img, (W - 96, y), right.upper(), FONTS("cond", 14, 400), AMBER, alpha, "rs", 3.2)
    tick = 22
    c = tuple(DIM) + (alpha + 30,)
    for (x, y0, dx, dy) in ((72, 40, 1, 1), (W - 72, 40, -1, 1), (72, H - 72, 1, -1),
                            (W - 72, H - 72, -1, -1)):
        d.line([(x, y0), (x + tick * dx, y0)], fill=c, width=1)
        d.line([(x, y0), (x, y0 + tick * dy)], fill=c, width=1)


def rule(img, x0, x1, y, color=AMBER, alpha=120, width=1):
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(x0, y), (x1, y)], fill=tuple(color) + (int(alpha),), width=width)


def act_card(img, numeral, title, p):
    """Full-frame act card overlay, p = 0..1 lifecycle (in, hold, out)."""
    if p <= 0:
        return img
    a = min(clamp(p / 0.22), clamp((1 - p) / 0.22))
    veil = Image.new("RGBA", (W, H), (5, 6, 8, int(235 * a)))
    img = Image.alpha_composite(img.convert("RGBA"), veil).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    grow = ease_out(clamp(p / 0.5))
    cx, cy = W / 2, H / 2 - 30
    d.line([(cx - 180 * grow, cy + 66), (cx + 180 * grow, cy + 66)],
           fill=AMBER + (int(170 * a),), width=1)
    draw_text(img, (cx, cy - 30), numeral, FONTS("serif", 96, 400), AMBER, int(230 * a), "cs", 6)
    draw_text(img, (cx, cy + 34), title, FONTS("cond", 24, 400), PAPER, int(220 * a), "cs", 12)
    return img


def title_block(img, kicker, headline, t, t0=0.4, y=96, x=96, max_w=1180, accent=AMBER):
    """Kicker + serif headline + rule, the explainer scenes' top-left signature.
    Appears as a unit; nothing else is painted above y=240 in those scenes."""
    pk = ease_out(prog(t, t0, 0.9))
    ph = ease_out(prog(t, t0 + 0.18, 1.1))
    if pk <= 0:
        return
    draw_text(img, (x - 26 * (1 - pk), y), kicker.upper(), FONTS("cond", 15, 400),
              accent, int(210 * pk), "ls", 3.4)
    lines = wrap(headline, FONTS("serif", 46, 400), max_w)
    for i, ln in enumerate(lines):
        draw_text(img, (x, y + 52 + i * 54), ln, FONTS("serif", 46, 400), PAPER,
                  int(236 * ph), "ls", 0.6)
    if ph > 0:
        rule(img, x, x + 120 * ph, y + 52 + len(lines) * 54 + 6, accent, 130)

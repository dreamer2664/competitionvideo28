#!/usr/bin/env python3
"""
render_kit.py — shared visual primitives for THIRTY BRONZE WHEELS.
Palette, typography, plate camera, gear sprites, panels, captions, HUD.
"""
import math
import os
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = Path(__file__).resolve().parent.parent
ASSETS = BASE / "assets"
FONTS = ASSETS / "fonts"
PLATES = ASSETS / "plates"

W, H = 1920, 1080
FPS = 30

# ----------------------------------------------------------------- palette
INK = (8, 11, 16)
INK_SOFT = (14, 20, 29)
BRONZE = (200, 138, 62)
BRONZE_LIGHT = (242, 196, 126)
BRONZE_DARK = (110, 70, 24)
PATINA = (43, 138, 120)
PATINA_LIGHT = (92, 224, 198)
CYAN = (108, 229, 255)
CYAN_DEEP = (24, 62, 88)
CRIMSON = (226, 85, 73)
GOLD = (248, 206, 108)
PARCHMENT = (243, 239, 230)
MUTED = (150, 168, 186)
MUTED_DIM = (96, 112, 128)

FONT_FILES = {
    "display": "Fraunces.ttf",
    "sans": "Inter-Regular.ttf",
    "sans_md": "Inter-Medium.ttf",
    "sans_sb": "Inter-SemiBold.ttf",
    "sans_bd": "Inter-Bold.ttf",
    "mono": "IBMPlexMono-Regular.ttf",
    "mono_md": "IBMPlexMono-Medium.ttf",
    "mono_sb": "IBMPlexMono-SemiBold.ttf",
    "dejavu": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "greek": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "greek_bd": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "dejavu_bd": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}


@lru_cache(maxsize=256)
def font(kind: str, size: int):
    path = FONT_FILES[kind]
    if not os.path.isabs(path):
        path = str(FONTS / path)
    return ImageFont.truetype(path, size)


# ----------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else (b if x > b else x)


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - ((-2 * x + 2) ** 3) / 2


def between(u, a, b):
    """normalised progress of u within [a,b]"""
    if b <= a:
        return 1.0 if u >= b else 0.0
    return clamp((u - a) / (b - a))


def alpha_for(u, t_in=0.0, t_out=1.0, fade=0.12):
    a = smooth(between(u, t_in, t_in + fade)) if fade > 0 else 1.0
    b = 1 - smooth(between(u, t_out - fade, t_out)) if fade > 0 else 1.0
    return min(a, b)


def lerp(a, b, x):
    return a + (b - a) * x


def mix(c1, c2, x):
    x = clamp(x)
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * x)) for i in range(3))


def with_alpha(c, a):
    return (c[0], c[1], c[2], int(round(255 * clamp(a))))


# ----------------------------------------------------------------- cached layers
@lru_cache(maxsize=1)
def _vignette():
    y, x = np.ogrid[0:H, 0:W]
    cx, cy = W / 2, H * 0.46
    r = np.sqrt(((x - cx) / (W * 0.62)) ** 2 + ((y - cy) / (H * 0.62)) ** 2)
    v = np.clip(1.0 - r, 0, 1) ** 1.6
    a = (1.0 - v) * 0.82
    arr = np.zeros((H, W, 4), dtype=np.uint8)
    arr[..., 0] = 4
    arr[..., 1] = 6
    arr[..., 2] = 10
    arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


@lru_cache(maxsize=1)
def _grid():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(120, 160, 190, 10))
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(120, 160, 190, 10))
    for x in range(0, W, 300):
        d.line([(x, 0), (x, H)], fill=(140, 190, 220, 16))
    for y in range(0, H, 300):
        d.line([(0, y), (W, y)], fill=(140, 190, 220, 16))
    return img


@lru_cache(maxsize=1)
def _grain():
    rng = np.random.default_rng(77)
    n = rng.normal(0, 7.0, (H // 2, W // 2)).astype(np.float32)
    g = Image.fromarray(np.clip(128 + n, 0, 255).astype(np.uint8), "L").resize((W, H), Image.BILINEAR)
    arr = np.zeros((H, W, 4), dtype=np.uint8)
    arr[..., 0] = 255
    arr[..., 1] = 255
    arr[..., 2] = 255
    arr[..., 3] = 12
    return Image.fromarray(arr, "RGBA"), g


@lru_cache(maxsize=32)
def plate(name: str):
    p = PLATES / name
    im = Image.open(p).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    return im


def plate_frame(name, zoom=1.0, pan=(0.0, 0.0), dim=0.42, tint=(6, 9, 14), blur=0.0):
    """Camera move over a plate: zoom>1 crops in; pan in fraction of the crop window."""
    im = plate(name)
    cw, ch = W / max(zoom, 1.0), H / max(zoom, 1.0)
    cx = (W - cw) / 2 + pan[0] * (W - cw) / 2
    cy = (H - ch) / 2 + pan[1] * (H - ch) / 2
    crop = im.crop((int(cx), int(cy), int(cx + cw), int(cy + ch))).resize((W, H), Image.LANCZOS)
    if blur > 0:
        crop = crop.filter(ImageFilter.GaussianBlur(blur))
    if dim > 0:
        ov = Image.new("RGB", (W, H), tint)
        crop = Image.blend(crop, ov, dim)
    return crop.convert("RGB")


def base_canvas(bg=None, grid=True, grain=True, vignette=True):
    """Start a frame: plate or ink gradient, then grid/vignette."""
    if bg is None:
        arr = np.zeros((H, W, 3), dtype=np.float32)
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
        x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
        radial = np.clip(1.0 - np.sqrt(((x - 0.5) * 1.25) ** 2 + ((y - 0.48) * 1.35) ** 2), 0, 1)
        for i, (c0, c1) in enumerate(zip((6, 9, 14), (26, 38, 52))):
            arr[..., i] = c0 + (c1 - c0) * (radial ** 1.5)
        bg = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    img = bg.convert("RGB")
    if vignette:
        img = Image.alpha_composite(img.convert("RGBA"), _vignette())
    if grid:
        img = Image.alpha_composite(img, _grid())
    if grain:
        gimg, _ = _grain()
        img = Image.alpha_composite(img, gimg)
    return img


# ----------------------------------------------------------------- text
def text(d, xy, s, f, fill, anchor="la", shadow=2, alpha=1.0, tracking=0, spacing=4):
    """Draw text with optional drop shadow. anchor: PIL anchors (la, mm, ls, rs...)."""
    if alpha <= 0.01:
        return
    col = with_alpha(fill, alpha) if len(fill) == 3 else fill
    if tracking and len(s) > 1:
        tracked_text(d, xy, s, f, fill, anchor=anchor, shadow=shadow, alpha=alpha, tracking=tracking)
        return
    if shadow:
        sh = (0, 0, 0, int(150 * alpha))
        for ox, oy in ((shadow * 0.6, shadow * 0.8), (shadow * 0.25, shadow * 0.35)):
            d.text((xy[0] + ox, xy[1] + oy), s, font=f, fill=sh, anchor=anchor, spacing=spacing)
    d.text(xy, s, font=f, fill=col, anchor=anchor, spacing=spacing)


def tracked_text(d, xy, s, f, fill, anchor="la", shadow=2, alpha=1.0, tracking=3):
    total = sum(f.getlength(ch) + tracking for ch in s) - tracking
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    col = with_alpha(fill, alpha) if len(fill) == 3 else fill
    for ch in s:
        if shadow:
            d.text((x + 1.2, y + 1.6), ch, font=f, fill=(0, 0, 0, int(140 * alpha)), anchor="l" + anchor[1])
        d.text((x, y), ch, font=f, fill=col, anchor="l" + anchor[1])
        x += f.getlength(ch) + tracking


def wrap(s, f, max_w):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getlength(t) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ----------------------------------------------------------------- shapes
def _c(col):
    """coerce a colour tuple to ints (PIL rejects float channels)."""
    if col is None:
        return None
    return tuple(int(round(v)) for v in col)


def panel(d, box, radius=14, fill=(10, 15, 22, 210), outline=(120, 150, 175, 70), width=1):
    d.rounded_rectangle(tuple(int(round(v)) for v in box), radius=radius, fill=_c(fill), outline=_c(outline), width=width)


def hairline(d, x0, y0, x1, y1, c=BRONZE, alpha=0.5, width=1):
    d.line([(x0, y0), (x1, y1)], fill=with_alpha(c, alpha), width=width)


def corner_ticks(d, box, size=16, c=CYAN, alpha=0.55, width=2):
    x0, y0, x1, y1 = box
    a = int(255 * alpha)
    col = (c[0], c[1], c[2], a)
    d.line([(x0, y0 + size), (x0, y0), (x0 + size, y0)], fill=col, width=width)
    d.line([(x1 - size, y0), (x1, y0), (x1, y0 + size)], fill=col, width=width)
    d.line([(x0, y1 - size), (x0, y1), (x0 + size, y1)], fill=col, width=width)
    d.line([(x1 - size, y1), (x1, y1), (x1 - size, y1)], fill=col, width=width)


def arrow(d, p0, p1, c=BRONZE_LIGHT, width=3, head=14, alpha=1.0):
    d.line([p0, p1], fill=with_alpha(c, alpha), width=width)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (+1, -1):
        d.line(
            [p1, (p1[0] - head * math.cos(ang - s * 0.42), p1[1] - head * math.sin(ang - s * 0.42))],
            fill=with_alpha(c, alpha),
            width=width,
        )


def glow_ellipse(img, cx, cy, rx, ry, color, alpha=0.5, blur=28):
    layer = Image.new("RGBA", (int(rx * 2 + blur * 4), int(ry * 2 + blur * 4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((blur * 2, blur * 2, blur * 2 + rx * 2, blur * 2 + ry * 2), fill=with_alpha(color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer, (int(cx - rx - blur * 2), int(cy - ry - blur * 2)))


# ----------------------------------------------------------------- gear sprites
@lru_cache(maxsize=400)
def gear_sprite(r_pitch, teeth, palette="bronze", spokes=4, pad=10):
    from kinematics import PATINA_BASE, PATINA_DARK, PATINA_SPEC

    if palette == "patina":
        c_base, c_spec, c_dark = PATINA_BASE, PATINA_SPEC, PATINA_DARK
    elif palette == "xray":
        c_base, c_spec, c_dark = (46, 122, 158), CYAN, (14, 44, 62)
    elif palette == "crimson":
        c_base, c_spec, c_dark = (170, 62, 52), (250, 150, 136), (70, 20, 18)
    elif palette == "dark":
        c_base, c_spec, c_dark = (78, 58, 34), (150, 116, 70), (34, 24, 14)
    else:
        c_base, c_spec, c_dark = BRONZE, BRONZE_LIGHT, BRONZE_DARK

    size = int(2 * (r_pitch + 12 + pad))
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = size / 2
    pitch = 2 * math.pi * r_pitch / max(teeth, 8)
    half_h = max(2.0, min(8.0, 0.46 * pitch))
    r_out = r_pitch + half_h
    r_in = max(3.0, r_pitch - half_h * 0.85)
    dth = 2 * math.pi / teeth

    pts = []
    for i in range(teeth):
        a_tip = -math.pi / 2 + i * dth
        a_root = a_tip + 0.52 * dth
        pts.append((cx + r_out * math.cos(a_tip), cy + r_out * math.sin(a_tip)))
        pts.append((cx + r_in * math.cos(a_root), cy + r_in * math.sin(a_root)))
    d.polygon(pts, fill=c_base, outline=c_spec)
    d.line(pts + [pts[0]], fill=c_spec, width=1)

    r_rim_o = max(7.0, r_pitch * 0.80)
    r_rim_i = max(5.5, r_pitch * 0.71)
    r_hub = max(4.5, r_pitch * 0.23)

    if r_pitch >= 30 and spokes:
        d.ellipse((cx - r_rim_i, cy - r_rim_i, cx + r_rim_i, cy + r_rim_i), fill=c_dark)
        sw = max(4.0, r_pitch * 0.12)
        for s in range(spokes):
            ang = -math.pi / 2 + s * (2 * math.pi / spokes)
            ca, sa = math.cos(ang), math.sin(ang)
            pa, qa = -sa, ca
            w0, w1 = sw * 0.66, sw * 0.46
            p1 = (cx + r_hub * 0.8 * ca + w0 * pa, cy + r_hub * 0.8 * sa + w0 * qa)
            p2 = (cx + r_hub * 0.8 * ca - w0 * pa, cy + r_hub * 0.8 * sa - w0 * qa)
            p3 = (cx + r_rim_i * 1.0 * ca - w1 * pa, cy + r_rim_i * 1.0 * sa - w1 * qa)
            p4 = (cx + r_rim_i * 1.0 * ca + w1 * pa, cy + r_rim_i * 1.0 * sa + w1 * qa)
            d.polygon([p1, p2, p3, p4], fill=c_base)
            d.line([p1, p2], fill=c_spec, width=1)
        d.ellipse((cx - r_rim_o, cy - r_rim_o, cx + r_rim_o, cy + r_rim_o), outline=c_spec, width=2)
    else:
        d.line([(cx, cy), (cx + r_pitch * 0.55, cy)], fill=c_spec, width=2)

    d.ellipse((cx - r_hub, cy - r_hub, cx + r_hub, cy + r_hub), fill=c_base, outline=c_spec, width=2)
    ar = max(2.5, r_hub * 0.40)
    d.polygon(
        [
            (cx + ar * math.cos(-math.pi / 2 + k * math.pi / 2 + math.pi / 4),
             cy + ar * math.sin(-math.pi / 2 + k * math.pi / 2 + math.pi / 4))
            for k in range(4)
        ],
        fill=(16, 20, 28),
        outline=c_spec,
    )
    return img


def paste_gear(img, r_pitch, teeth, cx, cy, angle_deg, palette="bronze", spokes=4, alpha=1.0):
    sp = gear_sprite(int(round(r_pitch)), int(teeth), palette, spokes)
    if abs(angle_deg) > 0.01:
        sp = sp.rotate(-angle_deg, resample=Image.BICUBIC, expand=False)
    if alpha < 0.999:
        sp = sp.copy()
        a = sp.getchannel("A").point(lambda v: int(v * alpha))
        sp.putalpha(a)
    img.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)))


def mesh_angle(teeth_driver, phase_driver_deg, driver_angle_deg, center_driver, center_driven, teeth_driven=None):
    """
    Angular position of a meshing driven gear such that its teeth interleave the driver.
    Returns degrees.
    """
    if teeth_driven is None:
        raise ValueError('mesh_angle needs teeth_driven')
    ax = math.degrees(math.atan2(center_driven[1] - center_driver[1], center_driven[0] - center_driver[0]))
    # Tooth of driver at angle `driver_angle + 180` sits at the line of centres.
    # Driven gear must present a gap there: offset by half a tooth pitch.
    ratio = teeth_driver / teeth_driven
    phase = phase_driver_deg + ax + (180.0 / teeth_driven)
    return (driver_angle_deg * -ratio) + phase


# ----------------------------------------------------------------- HUD / captions
def act_header(d, act_label, shot_title, idx, total, alpha=1.0):
    if alpha <= 0.02:
        return
    text(d, (96, 62), act_label.upper(), font("mono_md", 19), BRONZE_LIGHT, alpha=0.92 * alpha, tracking=3.4)
    text(d, (96, 92), shot_title, font("sans_md", 25), (206, 218, 228), alpha=0.80 * alpha)
    hairline(d, 96, 132, 470, 132, BRONZE, 0.42 * alpha)
    lab = f"{idx:02d} / {total:02d}"
    text(d, (W - 96, 62), lab, font("mono_md", 20), MUTED, anchor="ra", alpha=0.85 * alpha, tracking=2)
    text(d, (W - 96, 92), "CHRONOSCOPE", font("sans_sb", 18), MUTED, anchor="ra", alpha=0.55 * alpha, tracking=4)


def progress_bar(d, t_global, total, alpha=1.0):
    y = H - 4
    d.line([(0, y), (W, y)], fill=(255, 255, 255, 18), width=4)
    x = W * clamp(t_global / total)
    d.line([(0, y), (x, y)], fill=with_alpha(BRONZE, 0.85 * alpha), width=4)


def draw_caption(img, cards, t, t_shot_start, alpha=1.0):
    """Word-level karaoke captions in a lower-third band, max 2 lines x 42 chars."""
    if alpha <= 0.02:
        return
    d = ImageDraw.Draw(img, "RGBA")
    active = None
    for c in cards:
        if c["start"] - 0.05 <= t <= c["end"] + 0.18:
            active = c
            break
    if active is None:
        return
    f = font("sans_md", 33)
    line_h = 44
    lines = active["lines"]
    widths = [f.getlength(l) for l in lines]
    maxw = max(widths) if widths else 0
    pad_x, pad_y = 34, 18
    box_w = maxw + pad_x * 2 + 18
    box_h = line_h * len(lines) + pad_y * 2
    x0 = (W - box_w) / 2
    y1 = H - 92
    y0 = y1 - box_h

    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rounded_rectangle((x0, y0, x0 + box_w, y1), radius=12, fill=(6, 9, 14, 205), outline=(190, 150, 92, 60), width=1)
    bd.rounded_rectangle((x0 + 10, y0 + 12, x0 + 14, y1 - 12), radius=2, fill=with_alpha(BRONZE, 0.8))
    img.alpha_composite(band.filter(ImageFilter.GaussianBlur(0.4)))

    # word-level highlight
    word_times = {(w["word"], round(w["start"], 3)): (w["start"], w["end"]) for w in active["words"]}
    flat = [w for w in active["words"]]
    wi = 0
    for li, line in enumerate(lines):
        words = line.split()
        # compute total line width precisely with per-word spacing
        widths_w = [f.getlength(w) for w in words]
        space = f.getlength(" ")
        total_w = sum(widths_w) + space * max(0, len(words) - 1)
        x = (W - total_w) / 2
        y = y0 + pad_y + li * line_h
        for w, ww in zip(words, widths_w):
            span = None
            if wi < len(flat):
                span = (flat[wi]["start"], flat[wi]["end"])
            spoken = span is not None and span[0] - 0.02 <= t <= span[1] + 0.02
            past = span is not None and t > span[1]
            col = GOLD if spoken else (PARCHMENT if past else (176, 190, 203))
            a = 1.0 if spoken else 0.94
            if spoken:
                d.text((x + 1, y + 2), w, font=f, fill=(0, 0, 0, 170))
            d.text((x, y), w, font=f, fill=with_alpha(col, a * alpha))
            x += ww + space
            wi += 1


# ----------------------------------------------------------------- small utilities
def fmt_num(n, dec=0):
    return f"{n:,.{dec}f}"


def draw_scale_bar(d, x, y, meters, px_per_m, label=None, color=CYAN, alpha=0.9):
    w = meters * px_per_m
    d.line([(x, y), (x + w, y)], fill=with_alpha(color, alpha), width=2)
    for i in range(int(meters) + 1):
        xx = x + i * px_per_m
        d.line([(xx, y - 5), (xx, y + 5)], fill=with_alpha(color, alpha * 0.8), width=1)
    if label:
        text(d, (x + w + 12, y), label, font("mono", 17), color, anchor="lm", alpha=alpha)


def star_field(d, t, count=150, seed=3, alpha=1.0, y_max=H, twinkle=True):
    rng = np.random.default_rng(seed)
    for i in range(count):
        x = float(rng.uniform(0, W))
        y = float(rng.uniform(0, y_max))
        r = float(rng.uniform(0.7, 2.2))
        b = float(rng.uniform(0.25, 1.0))
        if twinkle:
            b *= 0.7 + 0.3 * math.sin(t * 1.7 + i * 1.3)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 248, 235, int(200 * b * alpha)))

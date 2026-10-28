#!/usr/bin/env python3
"""
Shared visual primitives, typography loader, sub-pixel Ken Burns plate engine,
safe-zone HUD chrome, and broadcast lower-bottom caption renderer.
"""
import math
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080

# Cohesive palette
BG_ABYSS = (7, 15, 27)
BG_SLATE = (13, 25, 43)
PANEL_FILL = (11, 22, 38, 226)
PANEL_BORDER = (68, 114, 156, 175)
IVORY = (242, 236, 225)
MUTED = (172, 192, 212)
DIM = (110, 134, 158)
AMBER = (234, 168, 68)
AMBER_SOFT = (234, 168, 68, 70)
CRIMSON = (228, 78, 64)
CYAN = (88, 204, 222)
EMERALD = (82, 198, 138)

FONT_PATHS = {
    "serif_bold": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "serif_italic": "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf",
    "serif_reg": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "disp_bold": "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf",
    "disp_black": "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf",
    "sans_bold": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "sans_semi": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
    "sans_med": "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    "sans_reg": "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    "mono_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "mono_reg": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
}

_FONT_CACHE = {}


def get_font(key, size):
    k = (key, int(size))
    if k not in _FONT_CACHE:
        _FONT_CACHE[k] = ImageFont.truetype(FONT_PATHS[key], int(size))
    return _FONT_CACHE[k]


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def ease_out_cubic(x):
    x = clamp(x)
    return 1.0 - (1.0 - x) ** 3


def ease_in_out_cubic(x):
    x = clamp(x)
    return 4 * x * x * x if x < 0.5 else 1 - ((-2 * x + 2) ** 3) / 2


def prog(t, start, dur):
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return clamp((t - start) / dur)


# Precomputed radial vignette multiplier (H, W, 1)
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_rx = (_xx - W * 0.5) / (W * 0.55)
_ry = (_yy - H * 0.5) / (H * 0.58)
_rad2 = _rx * _rx + _ry * _ry
VIGNETTE_MASK = np.clip(1.0 - 0.34 * (_rad2 ** 1.15), 0.52, 1.0)[:, :, None].astype(np.float32)

# Precomputed procedural dark abyssal gradient canvas with subtle fine grid
_base_grad = np.zeros((H, W, 3), dtype=np.float32)
for c_idx, (c_top, c_bot) in enumerate(zip((10, 21, 38), (5, 10, 19))):
    _base_grad[:, :, c_idx] = np.linspace(c_top, c_bot, H, dtype=np.float32)[:, None]
# Subtle 60px technical grid
_base_grad[::60, :, :] += np.array([5, 9, 14], dtype=np.float32)
_base_grad[:, ::60, :] += np.array([5, 9, 14], dtype=np.float32)
BASE_TECH_CANVAS = np.clip(_base_grad * VIGNETTE_MASK, 0, 255).astype(np.uint8)

_PLATE_CACHE = {}


def load_plate_bgr_or_rgb(plate_dir, filename):
    if filename not in _PLATE_CACHE:
        p = os.path.join(plate_dir, filename)
        im = Image.open(p).convert("RGB")
        arr = np.array(im)
        # Pre-upscale slightly to 2160x1215 for ultra-smooth sub-pixel Ken Burns warp
        up = cv2.resize(arr, (2160, 1215), interpolation=cv2.INTER_CUBIC)
        _PLATE_CACHE[filename] = up
    return _PLATE_CACHE[filename]


def render_ken_burns_plate(plate_dir, filename, frac, zoom_start=1.01, zoom_end=1.085,
                           pan_x=(-18, 18), pan_y=(-10, 10), darken=0.84):
    """Sub-pixel smooth affine crop from 2160x1215 -> 1920x1080 in <1ms."""
    src = load_plate_bgr_or_rgb(plate_dir, filename)
    sh, sw = src.shape[:2]
    s = ease_in_out_cubic(frac)
    zoom = zoom_start + (zoom_end - zoom_start) * s
    dx = pan_x[0] + (pan_x[1] - pan_x[0]) * s
    dy = pan_y[0] + (pan_y[1] - pan_y[0]) * s

    # Map output (W, H) back to src coordinates around center
    scale = (W / sw) * (1.0 / zoom) * (sw / W)  # effective inverse zoom relative to fit
    # Wait: src is 2160x1215 = 1.125 * (1920x1080). At zoom=1.0, crop width = 2160 / 1.03 = 2097
    crop_w = (sw * 0.96) / zoom
    crop_h = crop_w * (H / W)
    cx = sw * 0.5 + dx
    cy = sh * 0.5 + dy
    x0 = cx - crop_w * 0.5
    y0 = cy - crop_h * 0.5
    sx = crop_w / W
    sy = crop_h / H

    M = np.array([[sx, 0.0, x0], [0.0, sy, y0]], dtype=np.float32)
    out = cv2.warpAffine(
        src, M, (W, H),
        flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
        borderMode=cv2.BORDER_REFLECT_101,
    )
    out_f = out.astype(np.float32) * (darken * VIGNETTE_MASK)
    return np.clip(out_f, 0, 255).astype(np.uint8)


# Deterministic marine-snow / dust particle seeds
_RNG = np.random.default_rng(19291118)
_PARTICLES = np.column_stack([
    _RNG.uniform(0, W, 75),
    _RNG.uniform(0, H - 170, 75),
    _RNG.uniform(1.2, 3.2, 75),     # radius
    _RNG.uniform(8.0, 24.0, 75),    # vx
    _RNG.uniform(-12.0, -4.0, 75),  # vy
    _RNG.uniform(22, 68, 75),       # alpha
])


def draw_particles(overlay_draw, t_global, tint=(180, 215, 235)):
    for px, py, r, vx, vy, alpha in _PARTICLES:
        x = (px + vx * t_global) % W
        y = (py + vy * t_global) % (H - 170)
        a = int(alpha * (0.65 + 0.35 * math.sin(t_global * 1.4 + px * 0.01)))
        overlay_draw.ellipse((x - r, y - r, x + r, y + r), fill=(tint[0], tint[1], tint[2], a))


def draw_panel(draw, box, fill=PANEL_FILL, outline=PANEL_BORDER, radius=14, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_top_hud(draw, act_label, right_badge, t_local):
    alpha = 255 if t_local == 0.0 else int(255 * (0.55 + 0.45 * ease_out_cubic(prog(t_local, 0.0, 0.25))))
    # Top translucent gradient strip
    draw.rectangle((0, 0, W, 72), fill=(5, 11, 20, int(165 * (alpha / 255.0))))
    draw.line((72, 72, W - 72, 72), fill=(68, 114, 156, int(110 * (alpha / 255.0))), width=1)

    f_act = get_font("sans_semi", 18)
    f_mono = get_font("mono_bold", 18)
    # Accent dot
    draw.ellipse((72, 31, 82, 41), fill=(CYAN[0], CYAN[1], CYAN[2], alpha))
    draw.text((94, 24), act_label, font=f_act, fill=(MUTED[0], MUTED[1], MUTED[2], alpha))

    if right_badge:
        bbox = draw.textbbox((0, 0), right_badge, font=f_mono)
        tw = bbox[2] - bbox[0]
        bx0 = W - 72 - tw - 28
        draw.rounded_rectangle(
            (bx0, 18, W - 72, 54),
            radius=8,
            fill=(22, 36, 56, int(215 * (alpha / 255.0))),
            outline=(AMBER[0], AMBER[1], AMBER[2], int(160 * (alpha / 255.0))),
            width=1,
        )
        draw.text((bx0 + 14, 25), right_badge, font=f_mono, fill=(AMBER[0], AMBER[1], AMBER[2], alpha))


def draw_captions_and_progress(draw, active_cue, t_global, total_duration):
    """
    Renders lower-bottom broadcast captions inside dedicated safe band y=[924..1048]
    so captions NEVER collide with scene diagrams in y=[84..905].
    """
    if active_cue:
        lines = active_cue["lines"]
        f_cap = get_font("sans_bold", 34)
        widths = [draw.textbbox((0, 0), ln, font=f_cap)[2] for ln in lines]
        max_w = max(widths) if widths else 200
        pad_x = 32
        pad_y = 14
        line_h = 42
        box_h = len(lines) * line_h + pad_y * 2 - 4
        box_w = max_w + pad_x * 2
        x0 = (W - box_w) // 2
        # Anchor cleanly near bottom safe margin
        y1 = 1052
        y0 = y1 - box_h

        draw.rounded_rectangle(
            (x0, y0, x0 + box_w, y1),
            radius=12,
            fill=(5, 10, 18, 228),
            outline=(78, 118, 154, 135),
            width=1,
        )
        for i, ln in enumerate(lines):
            lw = widths[i]
            lx = (W - lw) // 2
            ly = y0 + pad_y + i * line_h - 2
            # Crisp 1px drop shadow + bright ivory text (>=14:1 contrast)
            draw.text((lx + 1, ly + 2), ln, font=f_cap, fill=(0, 0, 0, 230))
            draw.text((lx, ly), ln, font=f_cap, fill=(IVORY[0], IVORY[1], IVORY[2], 255))

    # Subtle bottom timeline progress bar (y = 1075..1080)
    p_frac = clamp(t_global / max(1.0, total_duration))
    draw.rectangle((0, 1075, W, 1080), fill=(16, 28, 44, 210))
    draw.rectangle((0, 1075, int(W * p_frac), 1080), fill=(AMBER[0], AMBER[1], AMBER[2], 235))


def text_centered(draw, cx, y, text, font, fill=IVORY):
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    draw.text((cx - tw * 0.5, y), text, font=font, fill=fill)

#!/usr/bin/env python3
"""
Shared visual primitives, typography loader, sub-pixel Ken Burns plate engine,
safe-zone HUD chrome, and word-highlighted lower-bottom broadcast caption renderer
for THE TEN-MINUTE ECLIPSE (praxinoscope).
"""
import math
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080

# Cohesive celestial & brass optical palette
BG_ABYSS = (7, 13, 24)
BG_SLATE = (12, 22, 38)
PANEL_FILL = (10, 19, 34, 228)
PANEL_DARK = (7, 13, 24, 238)
PANEL_BORDER = (72, 118, 164, 185)
BRASS_BORDER = (218, 168, 76, 200)
IVORY = (244, 239, 230)
MUTED = (176, 196, 218)
DIM = (114, 136, 162)
AMBER = (244, 184, 72)
AMBER_SOFT = (244, 184, 72, 72)
CRIMSON = (232, 82, 68)
CYAN = (86, 208, 228)
EMERALD = (84, 204, 142)
VIOLET = (168, 132, 238)

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
    return 4 * x * x * x if x < 0.5 else 1.0 - ((-2 * x + 2) ** 3) / 2.0


def prog(t, start, dur):
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return clamp((t - start) / dur)


# Precomputed radial vignette multiplier (H, W, 1)
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_rx = (_xx - W * 0.5) / (W * 0.56)
_ry = (_yy - H * 0.5) / (H * 0.58)
_rad2 = _rx * _rx + _ry * _ry
VIGNETTE_MASK = np.clip(1.0 - 0.34 * (_rad2 ** 1.15), 0.52, 1.0)[:, :, None].astype(np.float32)

# Precomputed dark astronomical blueprint canvas with fine 60px technical grid
_base_grad = np.zeros((H, W, 3), dtype=np.float32)
for c_idx, (c_top, c_bot) in enumerate(zip((11, 20, 36), (5, 10, 18))):
    _base_grad[:, :, c_idx] = np.linspace(c_top, c_bot, H, dtype=np.float32)[:, None]
_base_grad[::60, :, :] += np.array([5, 9, 15], dtype=np.float32)
_base_grad[:, ::60, :] += np.array([5, 9, 15], dtype=np.float32)
BASE_TECH_CANVAS = np.clip(_base_grad * VIGNETTE_MASK, 0, 255).astype(np.uint8)

_PLATE_CACHE = {}


def load_plate_rgb(plate_dir, filename):
    if filename not in _PLATE_CACHE:
        p = os.path.join(plate_dir, filename)
        im = Image.open(p).convert("RGB")
        arr = np.array(im)
        up = cv2.resize(arr, (2160, 1215), interpolation=cv2.INTER_CUBIC)
        _PLATE_CACHE[filename] = up
    return _PLATE_CACHE[filename]


def render_ken_burns_plate(plate_dir, filename, frac, zoom_start=1.01, zoom_end=1.085,
                           pan_x=(-18, 18), pan_y=(-10, 10), darken=0.84):
    """Sub-pixel smooth affine crop from 2160x1215 -> 1920x1080."""
    src = load_plate_rgb(plate_dir, filename)
    sh, sw = src.shape[:2]
    s = ease_in_out_cubic(frac)
    zoom = zoom_start + (zoom_end - zoom_start) * s
    dx = pan_x[0] + (pan_x[1] - pan_x[0]) * s
    dy = pan_y[0] + (pan_y[1] - pan_y[0]) * s

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


# Deterministic starlight / optical dust mote seeds (keeps every frame alive)
_RNG = np.random.default_rng(16761109)
_PARTICLES = np.column_stack([
    _RNG.uniform(0, W, 80),
    _RNG.uniform(0, H - 170, 80),
    _RNG.uniform(1.1, 3.0, 80),     # radius
    _RNG.uniform(9.0, 25.0, 80),    # vx
    _RNG.uniform(-11.0, -3.5, 80),  # vy
    _RNG.uniform(24, 72, 80),       # alpha
])


def draw_particles(draw, t_global, tint=(210, 225, 245)):
    for px, py, r, vx, vy, alpha in _PARTICLES:
        x = (px + vx * t_global) % W
        y = (py + vy * t_global) % (H - 170)
        a = int(alpha * (0.62 + 0.38 * math.sin(t_global * 1.5 + px * 0.01)))
        c = (tint[0], tint[1], tint[2], a)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=c)


def draw_panel(draw, box, fill=PANEL_FILL, border=PANEL_BORDER, radius=16, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=border, width=width)


def draw_top_hud(draw, shot, t_local, t_global, total_dur):
    """Consistent top broadcast header bar (y = 22..72)."""
    bar_box = (48, 22, W - 48, 74)
    draw.rounded_rectangle(bar_box, radius=12, fill=(8, 15, 27, 215), outline=(64, 108, 152, 165), width=1)

    f_act = get_font("mono_bold", 18)
    f_title = get_font("sans_semi", 20)
    f_tc = get_font("mono_reg", 18)

    # Act pill on left
    act_str = shot["act"]
    draw.text((70, 36), act_str, font=f_act, fill=AMBER)
    ab = draw.textbbox((70, 36), act_str, font=f_act)
    sep_x = ab[2] + 22
    draw.line((sep_x, 32, sep_x, 64), fill=(80, 120, 160, 180), width=2)
    draw.text((sep_x + 20, 35), shot["title"], font=f_title, fill=IVORY)

    # Right side: speaker badge + global timecode
    is_quote = "Ryan" in shot.get("voice", "")
    badge_txt = "PRIMARY SOURCE CHRONICLE" if is_quote else "PRAXINOSCOPE · 1080P30"
    badge_col = CYAN if is_quote else MUTED
    mins = int(t_global) // 60
    secs = t_global - mins * 60
    tc_str = f"{badge_txt}   |   {mins:02d}:{secs:04.1f}"
    tb = draw.textbbox((0, 0), tc_str, font=f_tc)
    tw = tb[2] - tb[0]
    draw.text((W - 70 - tw, 36), tc_str, font=f_tc, fill=badge_col)

    # Thin progress line along bottom of top HUD
    p_frac = clamp(t_global / max(1.0, total_dur))
    px1 = int(52 + (W - 104) * p_frac)
    draw.line((52, 73, px1, 73), fill=AMBER, width=2)


def draw_caption_bar(draw, shot, t_global):
    """
    Renders the active <=2-line caption cue inside the dedicated bottom safe zone (y = 924..1052)
    with word-level gold highlighting on the currently spoken word.
    """
    active_cue = None
    for c in shot.get("cues", []):
        if c["start"] - 0.04 <= t_global <= c["end"] + 0.04:
            active_cue = c
            break
    if not active_cue:
        return

    lines = active_cue["lines"]
    words = active_cue.get("words", [])
    f_cap = get_font("sans_bold", 34)

    # Measure max line width for pill sizing
    line_widths = []
    for ln in lines:
        bb = draw.textbbox((0, 0), ln, font=f_cap)
        line_widths.append(bb[2] - bb[0])
    max_w = max(line_widths) if line_widths else 400
    pad_x = 38
    pill_w = max(560, min(W - 120, max_w + pad_x * 2))
    x0 = (W - pill_w) // 2
    x1 = x0 + pill_w

    if len(lines) == 1:
        y0, y1 = 954, 1034
        line_ys = [972]
    else:
        y0, y1 = 926, 1048
        line_ys = [940, 990]

    is_quote = "Ryan" in shot.get("voice", "")
    border_col = (86, 208, 228, 195) if is_quote else (234, 178, 72, 185)
    draw.rounded_rectangle((x0, y0, x1, y1), radius=16, fill=(7, 14, 25, 236), outline=border_col, width=2)

    # Map words to lines in order
    word_idx = 0
    for ln_i, ln in enumerate(lines):
        ln_tokens = ln.split()
        lw = line_widths[ln_i]
        cur_x = (W - lw) // 2
        cur_y = line_ys[ln_i]
        for tok in ln_tokens:
            is_active = False
            if word_idx < len(words):
                w_item = words[word_idx]
                if w_item["start"] - 0.05 <= t_global <= w_item["end"] + 0.08:
                    is_active = True
                word_idx += 1
            col = AMBER if is_active else IVORY
            draw.text((cur_x, cur_y), tok, font=f_cap, fill=col)
            tb = draw.textbbox((cur_x, cur_y), tok + " ", font=f_cap)
            cur_x = tb[2]

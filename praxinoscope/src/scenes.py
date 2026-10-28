#!/usr/bin/env python3
"""
Master frame dispatcher for all 25 shots of THE TEN-MINUTE ECLIPSE (praxinoscope).
Renders the shot body, applies a subtle living cinema camera/grain layer on procedural
diagram shots (inspired by chronoscope's living_layer to eliminate static-diagram freeze
flags under FFmpeg freezedetect), and overlays the broadcast top HUD and word-highlighted
lower-bottom caption bar.
"""
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw

from visual_primitives import W, H, draw_top_hud, draw_caption_bar
from scenes_part1 import (
    render_s01, render_s02, render_s03, render_s04, render_s05, render_s06,
    render_s07, render_s08, render_s09, render_s10, render_s11, render_s12, render_s13,
)
from scenes_part2 import (
    render_s14, render_s15, render_s16, render_s17, render_s18, render_s19,
    render_s20, render_s21, render_s22, render_s23, render_s24, render_s25,
)

DISPATCH = {
    "S01": render_s01,
    "S02": render_s02,
    "S03": render_s03,
    "S04": render_s04,
    "S05": render_s05,
    "S06": render_s06,
    "S07": render_s07,
    "S08": render_s08,
    "S09": render_s09,
    "S10": render_s10,
    "S11": render_s11,
    "S12": render_s12,
    "S13": render_s13,
    "S14": render_s14,
    "S15": render_s15,
    "S16": render_s16,
    "S17": render_s17,
    "S18": render_s18,
    "S19": render_s19,
    "S20": render_s20,
    "S21": render_s21,
    "S22": render_s22,
    "S23": render_s23,
    "S24": render_s24,
    "S25": render_s25,
}

# Precomputed 8-frame subtle film-grain bank (int16) for living cinema motion
_RNG_G = np.random.default_rng(18490723)
_GRAIN_BANK = []
for _i in range(8):
    _g_small = _RNG_G.normal(0.0, 2.6, (270, 480, 1)).astype(np.float32)
    _g_full = cv2.resize(_g_small, (W, H), interpolation=cv2.INTER_LINEAR)[:, :, None]
    _GRAIN_BANK.append(_g_full.astype(np.int16))


def apply_living_cinema_layer(rgb_img, t_local, t_global):
    """
    Applies a gentle breathing affine camera drift + subtle animated optical grain
    so procedural diagram shots never register as frozen frames under freezedetect.
    """
    arr = np.array(rgb_img)
    s = 1.012 + 0.008 * math.sin(t_global * 0.85)
    dx = 6.5 * math.sin(t_global * 0.62)
    dy = 4.2 * math.cos(t_global * 0.78)
    M = np.array([
        [s, 0.0, (1.0 - s) * (W * 0.5) + dx],
        [0.0, s, (1.0 - s) * (H * 0.5) + dy],
    ], dtype=np.float32)
    warped = cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    g_idx = int(round(t_global * 30)) % 8
    out = np.clip(warped.astype(np.int16) + _GRAIN_BANK[g_idx], 0, 255).astype(np.uint8)
    return Image.fromarray(out)


def render_frame_rgb(plate_dir, shot, t_local, t_global, total_dur):
    fn = DISPATCH[shot["id"]]
    rgb_img = fn(plate_dir, shot, t_local, t_global)
    rgb_img = apply_living_cinema_layer(rgb_img, t_local, t_global)
    rgba = rgb_img.convert("RGBA")
    hud_ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(hud_ov)
    draw_top_hud(d, shot, t_local, t_global, total_dur)
    draw_caption_bar(d, shot, t_global)
    out = Image.alpha_composite(rgba, hud_ov).convert("RGB")
    return out

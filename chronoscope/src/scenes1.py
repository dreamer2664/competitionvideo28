#!/usr/bin/env python3
"""Scenes S01–S08: the wreck, the museum, the title, the calendar problem, the train."""
import math

from PIL import Image, ImageDraw, ImageFilter

from render_kit import (
    BASE, BRONZE, BRONZE_DARK, BRONZE_LIGHT, CRIMSON, CYAN, CYAN_DEEP, GOLD, H,
    INK, INK_SOFT, MUTED, MUTED_DIM, PARCHMENT, PATINA, PATINA_LIGHT, W,
    arrow, act_header, alpha_for, base_canvas, between, clamp, corner_ticks,
    draw_caption, ease_in_out, ease_out, font, glow_ellipse, hairline, lerp,
    mesh_angle, mix, panel, paste_gear, plate, plate_frame, progress_bar,
    smooth, star_field, text, tracked_text, with_alpha,
)
from kinematics import CORINTHIAN_MONTHS, gear_tooth_polygon


# ------------------------------------------------------------------ S01
def bathymetry_dive(img, shot, u, t, tl):
    pan_x = lerp(0.10, -0.10, ease_in_out(u))
    bg = plate_frame(shot["plate"], zoom=lerp(1.16, 1.04, ease_out(u)), pan=(pan_x, 0.02), dim=0.30, tint=(4, 16, 24))
    img.paste(bg)

    d = ImageDraw.Draw(img, "RGBA")

    # sonar sweep
    cx, cy = 1560, 300
    for i in range(3):
        r = 120 + 150 * ((u * 1.4 + i * 0.33) % 1.0)
        a = 0.22 * (1.0 - ((u * 1.4 + i * 0.33) % 1.0))
        d.arc((cx - r, cy - r, cx + r, cy + r), 200, 340, fill=with_alpha(CYAN, a), width=2)

    # depth ruler on the left
    rx, top, bot = 74, 190, 900
    d.line([(rx, top), (rx, bot)], fill=with_alpha(CYAN, 0.45), width=2)
    max_depth = 50.0
    for m in range(0, 51, 5):
        y = top + (m / max_depth) * (bot - top)
        long = m % 10 == 0
        d.line([(rx - (16 if long else 9), y), (rx, y)], fill=with_alpha(CYAN, 0.55 if long else 0.3), width=1)
        if long:
            text(d, (rx - 24, y), f"{m}", font("mono", 17), CYAN, anchor="rm", alpha=0.6)

    depth = lerp(0.0, 42.0, ease_out(between(u, 0.02, 0.48)))
    dy = top + (depth / max_depth) * (bot - top)
    d.line([(rx, top), (rx, dy)], fill=with_alpha(BRONZE_LIGHT, 0.95), width=3)
    # diver marker
    d.polygon([(rx - 13, dy - 9), (rx + 3, dy), (rx - 13, dy + 9)], fill=GOLD)
    glow_ellipse(img, rx, dy, 22, 22, GOLD, alpha=0.30, blur=16)
    d = ImageDraw.Draw(img, "RGBA")

    panel(d, (108, dy - 26, 372, dy + 26), radius=8, fill=(6, 12, 18, 220), outline=(190, 150, 92, 90))
    text(d, (126, dy), "DEPTH", font("mono_md", 17), MUTED, anchor="lm", alpha=0.8, tracking=2)
    text(d, (214, dy), f"{depth:05.1f} m", font("mono_sb", 30), GOLD, anchor="lm")

    # site plate
    panel(d, (1340, 856, 1824, 962), radius=10, fill=(5, 10, 16, 205), outline=(120, 160, 190, 70))
    text(d, (1364, 882), "CAPE GLYFADIA · ANTIKYTHERA", font("mono_md", 19), CYAN, alpha=0.9, tracking=2)
    text(d, (1364, 912), "35° 51′ N   23° 18′ E   ·   ELIAS STADIATIS DIVE", font("mono", 17), MUTED, alpha=0.82)
    corner_ticks(d, (1340, 856, 1824, 962), size=14, c=CYAN, alpha=0.35)

    # date stamp
    a = alpha_for(u, 0.16, 0.62, 0.06)
    text(d, (96, 196), "SPRING 1900", font("display", 58), PARCHMENT, alpha=0.95 * a, tracking=2)
    text(d, (98, 268), "A sponge diver, a cliff, and a ship that sank around 70 BC",
         font("sans_md", 25), BRONZE_LIGHT, alpha=0.85 * a)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0.0, 0.9, 0.1))
    progress_bar(d, tl["shots"][shot["index"]]["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"], alpha=1.0)
    return img


# ------------------------------------------------------------------ S02
def museum_discovery(img, shot, u, t, tl):
    bg = plate_frame(shot["plate"], zoom=lerp(1.10, 1.02, ease_in_out(u)), pan=(-0.06, -0.02), dim=0.52, tint=(10, 9, 8))
    img.paste(bg)
    d = ImageDraw.Draw(img, "RGBA")

    # magnifier: circular lens that drifts onto the lump
    lens_r = 210
    lx = lerp(1180, 1010, ease_in_out(between(u, 0.02, 0.42)))
    ly = lerp(700, 640, ease_in_out(between(u, 0.02, 0.42)))

    zoom_src = plate("plate_02_fragment_a.jpg")
    zf = 1.05
    crop_w = int(W / zf)
    cx0 = int(760 - crop_w / 2)
    cy0 = int(430 - crop_w / 2)
    crop = zoom_src.crop((cx0, cy0, cx0 + crop_w, cy0 + crop_w)).resize((lens_r * 2, lens_r * 2), Image.LANCZOS)

    mask = Image.new("L", (lens_r * 2, lens_r * 2), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, lens_r * 2 - 1, lens_r * 2 - 1), fill=255)
    img.paste(crop, (int(lx - lens_r), int(ly - lens_r)), mask)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((lx - lens_r, ly - lens_r, lx + lens_r, ly + lens_r), outline=with_alpha(GOLD, 0.85), width=3)
    d.ellipse((lx - lens_r - 8, ly - lens_r - 8, lx + lens_r + 8, ly + lens_r + 8), outline=with_alpha(GOLD, 0.22), width=1)
    # crosshair
    d.line([(lx - lens_r, ly), (lx - lens_r + 26, ly)], fill=with_alpha(GOLD, 0.8), width=2)
    d.line([(lx + lens_r - 26, ly), (lx + lens_r, ly)], fill=with_alpha(GOLD, 0.8), width=2)
    d.line([(lx, ly - lens_r), (lx, ly - lens_r + 26)], fill=with_alpha(GOLD, 0.8), width=2)
    d.line([(lx, ly + lens_r - 26), (lx, ly + lens_r)], fill=with_alpha(GOLD, 0.8), width=2)

    # annotation with a leader line to the lens
    ax, ay = lx + lens_r + 40, ly - 120
    d.line([(lx + lens_r * 0.72, ly - lens_r * 0.72), (ax, ay)], fill=with_alpha(BRONZE_LIGHT, 0.5), width=1)
    text(d, (ax + 10, ay - 20), "FRAGMENT A", font("mono_sb", 21), GOLD, alpha=0.95, tracking=2)
    text(d, (ax + 10, ay + 8), "180 × 150 mm · 1.5 mm triangular teeth", font("mono", 16), MUTED, alpha=0.8)

    # crack animation over the lump (a drawn fracture line)
    crack = ease_out(between(u, 0.30, 0.62))
    if crack > 0:
        pts = [(560, 700), (700, 660), (820, 700), (930, 640), (1040, 676)]
        n = max(2, int(len(pts) * crack))
        sub = pts[:n]
        d.line(sub, fill=with_alpha(GOLD, 0.5), width=3, joint="curve")

    # date stamp with typewriter reveal
    stamp = "17 MAY 1902"
    a = alpha_for(u, 0.1, 0.8, 0.06)
    text(d, (96, 190), "ATHENS · NATIONAL ARCHAEOLOGICAL MUSEUM", font("mono_md", 18), CYAN, alpha=0.85 * a, tracking=3)
    chars = int(clamp((u - 0.10) / 0.28) * len(stamp))
    text(d, (94, 226), stamp[:chars], font("display", 72), PARCHMENT, alpha=0.96 * a, tracking=2)
    text(d, (96, 318), "Valerios Stais sees gear teeth in a calcified lump",
         font("sans_md", 26), BRONZE_LIGHT, alpha=0.88 * a)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0.0, 0.88, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S03
def title_lockup(img, shot, u, t, tl):
    bg = plate_frame("plate_06_clockwork_cosmos.jpg", zoom=lerp(1.28, 1.12, ease_out(u)), dim=0.58, blur=3.0)
    img.paste(bg)
    d = ImageDraw.Draw(img, "RGBA")
    star_field(d, t, count=90, seed=11, alpha=0.5, y_max=H)

    # giant slow gear behind the type
    ang = t * 2.2
    paste_gear(img, 300, 223, 1430, 520, ang, palette="dark", spokes=6, alpha=0.55)
    paste_gear(img, 190, 127, 1290, 640, -ang * 1.76, palette="dark", spokes=5, alpha=0.45)
    d = ImageDraw.Draw(img, "RGBA")

    # light sweep
    sweep = -400 + 3200 * ease_in_out(between(u, 0.12, 0.72))
    for i in range(26):
        x = sweep + i * 7
        d.line([(x, 0), (x + 210, H)], fill=(255, 226, 176, 4), width=9)

    kit = "A CHRONOSCOPE DOCUMENTARY"
    a = alpha_for(u, 0.02, 0.85, 0.10)
    text(d, (W / 2, 322), kit, font("mono_md", 24), BRONZE_LIGHT, anchor="mm", alpha=0.95 * a, tracking=8)
    hairline(d, W / 2 - 160, 360, W / 2 + 160, 360, BRONZE, 0.5 * a)

    t1 = "THIRTY"
    t2 = "BRONZE WHEELS"
    s1 = smooth(between(u, 0.06, 0.26))
    s2 = smooth(between(u, 0.16, 0.42))
    text(d, (W / 2, 470), t1, font("display", 132), PARCHMENT, anchor="mm", alpha=s1, tracking=6)
    text(d, (W / 2, 606), t2, font("display", 116), GOLD, anchor="mm", alpha=s2, tracking=3)

    sub = "Decoding the Antikythera Mechanism · 100 BCE — 2021"
    text(d, (W / 2, 716), sub, font("sans_md", 31), (214, 224, 232), anchor="mm", alpha=alpha_for(u, 0.30, 0.95, 0.08))

    # 30 wheel ticks along the bottom
    n = 30
    for i in range(n):
        x = 660 + i * 20
        hgt = 10 + 16 * (0.5 + 0.5 * math.sin(t * 2.0 + i * 0.55))
        a2 = clamp((u - 0.34 - i * 0.006) / 0.2) * 0.7
        d.line([(x, 830), (x, 830 + hgt)], fill=with_alpha(BRONZE_LIGHT, a2), width=2)
    text(d, (W / 2, 880), "30 SURVIVING WHEELS · 82 FRAGMENTS · ONE HAND-CRANKED SKY",
         font("mono", 17), MUTED, anchor="mm", alpha=0.7 * smooth(between(u, 0.45, 0.7)), tracking=2)

    progress_bar(d, shot["start"] + t, tl["total_duration"])
    # no captions on the title card (deliberate)
    return img


# ------------------------------------------------------------------ S04
def calendar_drift(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img, "RGBA")

    # left: solar year ring
    sx, sy, sr = 470, 520, 196
    d.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), outline=with_alpha(BRONZE, 0.55), width=2)
    for i in range(365):
        a = -math.pi / 2 + i * (2 * math.pi / 365)
        r0 = sr - (12 if i % 30 == 0 else 6)
        d.line([(sx + r0 * math.cos(a), sy + r0 * math.sin(a)), (sx + sr * math.cos(a), sy + sr * math.sin(a))],
               fill=with_alpha(BRONZE, 0.30 if i % 30 else 0.7), width=1)
    sa = -math.pi / 2 + u * 2 * math.pi * 1.0
    glow_ellipse(img, sx + sr * math.cos(sa), sy + sr * math.sin(sa), 26, 26, GOLD, 0.5, 18)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((sx + sr * math.cos(sa) - 16, sy + sr * math.sin(sa) - 16,
               sx + sr * math.cos(sa) + 16, sy + sr * math.sin(sa) + 16), fill=GOLD)
    text(d, (sx, sy - 30), "365.2422", font("mono_sb", 44), PARCHMENT, anchor="mm")
    text(d, (sx, sy + 22), "DAYS · TROPICAL YEAR", font("mono", 17), MUTED, anchor="mm", tracking=3)
    text(d, (sx, sy + sr + 44), "ONE SOLAR YEAR", font("sans_sb", 21), BRONZE_LIGHT, anchor="mm", tracking=3)

    # right: lunar month ring
    lx0, ly0, lr = 1450, 520, 150
    d.ellipse((lx0 - lr, ly0 - lr, lx0 + lr, ly0 + lr), outline=with_alpha(CYAN, 0.45), width=2)
    steps = 12
    for i in range(steps):
        a = -math.pi / 2 + i * 2 * math.pi / steps
        mx, my = lx0 + (lr - 30) * math.cos(a), ly0 + (lr - 30) * math.sin(a)
        phase = (i / steps + u * 0.6) % 1.0
        # moon phase disc
        rr = 17
        d.ellipse((mx - rr, my - rr, mx + rr, my + rr), fill=(232, 236, 240, 235))
        if phase > 0.05:
            cut = int(rr * 2 * min(phase, 1.0))
            d.ellipse((mx - rr + cut - rr * 2, my - rr, mx - rr + cut + rr, my + rr),
                      fill=(18, 26, 36, 255))
    text(d, (lx0, ly0 - 30), "29.5306", font("mono_sb", 44), PARCHMENT, anchor="mm")
    text(d, (lx0, ly0 + 22), "DAYS · SYNODIC MONTH", font("mono", 17), MUTED, anchor="mm", tracking=3)
    text(d, (lx0, ly0 + lr + 44), "TWELVE LUNATIONS = 354.37 DAYS", font("sans_sb", 21), PATINA_LIGHT, anchor="mm", tracking=2)

    # centre drift meter
    gap = 10.875
    bar_x0, bar_y = 760, 700
    bar_w = 400
    d.rounded_rectangle((bar_x0, bar_y, bar_x0 + bar_w, bar_y + 46), radius=8, outline=with_alpha(BRONZE, 0.5), width=1)
    filled = fill = clamp(ease_out(between(u, 0.18, 0.9)))
    d.rounded_rectangle((bar_x0 + 3, bar_y + 3, bar_x0 + 3 + (bar_w - 6) * filled, bar_y + 43), radius=6,
                        fill=with_alpha(CRIMSON, 0.75))
    text(d, (bar_x0, bar_y - 34), "ANNUAL GAP", font("mono_md", 17), MUTED, tracking=3)
    text(d, (bar_x0 + bar_w, bar_y - 34), f"{gap * filled:5.3f} d", font("mono_sb", 26), CRIMSON, anchor="ra")
    text(d, (bar_x0, bar_y + 66), "twelve lunar months fall short of one solar year",
         font("sans", 19), MUTED, alpha=0.85)

    # equation strip
    a = smooth(between(u, 0.42, 0.72))
    text(d, (W / 2, 250), "12 × 29.53059 = 354.37", font("mono_md", 30), (198, 212, 224), anchor="mm", alpha=0.85 * a)
    text(d, (W / 2, 300), "365.2422 − 354.3671 = 10.8751 days every year", font("mono_md", 30), CRIMSON, anchor="mm", alpha=0.9 * a)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0.0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S05
def metonic_grid(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img, "RGBA")

    cols, rows = 19, 13
    x0, y0 = 300, 330
    cw, chh = 68, 40
    total = 235
    reveal = ease_out(between(u, 0.05, 0.62))

    idx = 0
    for r in range(rows):
        for c in range(cols):
            if idx >= total:
                break
            x = x0 + c * cw
            y = y0 + r * chh
            on = idx < total * reveal
            if on:
                age = clamp((total * reveal - idx) / 24.0)
                col = mix(PATINA, GOLD, age)
                d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=with_alpha(col, 0.35 + 0.6 * age))
            else:
                d.ellipse((x - 2.2, y - 2.2, x + 2.2, y + 2.2), fill=(120, 140, 160, 55))
            idx += 1

    # the 19-year row markers on the left
    for r in range(rows):
        text(d, (x0 - 34, y0 + r * chh), f"{r + 1}", font("mono", 14), MUTED, anchor="rm", alpha=0.45)

    # counters
    counted = int(round(total * reveal))
    panel(d, (1440, 300, 1830, 470), radius=12, fill=(8, 13, 20, 200), outline=(190, 150, 92, 80))
    text(d, (1470, 328), "LUNAR MONTHS COUNTED", font("mono", 16), MUTED, tracking=3, alpha=0.8)
    text(d, (1470, 356), f"{counted:03d}", font("mono_sb", 76), GOLD)
    text(d, (1680, 400), "/ 235", font("mono_md", 28), MUTED, alpha=0.8)

    panel(d, (1440, 500, 1830, 640), radius=12, fill=(8, 13, 20, 200), outline=(120, 180, 200, 70))
    text(d, (1470, 526), "SOLAR YEARS", font("mono", 16), MUTED, tracking=3, alpha=0.8)
    text(d, (1470, 552), "19", font("mono_sb", 62), CYAN)
    text(d, (1620, 588), "× 365.2422 d", font("mono", 20), MUTED, alpha=0.75)

    a = smooth(between(u, 0.55, 0.85))
    text(d, (W / 2 - 160, 906), "19 YEARS  =  235 MONTHS", font("mono_sb", 46), PARCHMENT, anchor="mm", alpha=a)
    text(d, (W / 2 - 160, 962), "6,939.60 d  vs  6,939.69 d   →   drift under 2 hours in 19 years",
         font("mono", 21), PATINA_LIGHT, anchor="mm", alpha=0.9 * a)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0.0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S06
def sidereal_vector(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img, "RGBA")

    sun = (700, 560)
    # sun
    glow_ellipse(img, sun[0], sun[1], 46, 46, GOLD, 0.55, 34)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((sun[0] - 34, sun[1] - 34, sun[0] + 34, sun[1] + 34), fill=(252, 214, 128))
    text(d, (sun[0], sun[1] + 62), "SUN", font("mono", 17), GOLD, anchor="mm", tracking=3)

    # earth orbit
    orb_r = 300
    d.ellipse((sun[0] - orb_r, sun[1] - orb_r, sun[0] + orb_r, sun[1] + orb_r), outline=with_alpha(CYAN, 0.35), width=1)
    ea = -math.pi / 2 + u * 2 * math.pi
    ex, ey = sun[0] + orb_r * math.cos(ea), sun[1] + orb_r * math.sin(ea)
    d.ellipse((ex - 13, ey - 13, ex + 13, ey + 13), fill=(96, 168, 214), outline=(190, 230, 250))

    # moon orbit around earth
    mr = 74
    d.ellipse((ex - mr, ey - mr, ex + mr, ey + mr), outline=with_alpha(PARCHMENT, 0.28), width=1)
    ma = -math.pi / 2 + u * 2 * math.pi * 12.0
    mx, my = ex + mr * math.cos(ma), ey + mr * math.sin(ma)
    d.ellipse((mx - 7, my - 7, mx + 7, my + 7), fill=(238, 240, 244))
    text(d, (ex, ey + 34), "EARTH", font("mono", 14), CYAN, anchor="mm", tracking=2)

    # star field reference marks (fixed)
    for i in range(16):
        ang = i * (2 * math.pi / 16)
        rr = 442
        x, y = sun[0] + rr * math.cos(ang), sun[1] + rr * math.sin(ang)
        d.line([(x - 4, y), (x + 4, y)], fill=(255, 250, 230, 90), width=1)
        d.line([(x, y - 4), (x, y + 4)], fill=(255, 250, 230, 90), width=1)

    # right panel: the two counts
    panel(d, (1250, 300, 1830, 700), radius=14, fill=(8, 13, 20, 214), outline=(190, 150, 92, 80))
    text(d, (1290, 330), "IN ONE 19-YEAR METONIC CYCLE", font("mono_md", 17), MUTED, tracking=3, alpha=0.85)

    rows2 = [
        ("PHASE CYCLES AGAINST THE SUN", "235", PATINA_LIGHT, 0.10),
        ("EARTH'S OWN ORBITS", "+ 19", CYAN, 0.30),
        ("ORBITS AGAINST THE FIXED STARS", "254", GOLD, 0.50),
    ]
    for i, (lab, val, col, t0) in enumerate(rows2):
        a = smooth(between(u, t0, t0 + 0.18))
        y = 386 + i * 96
        text(d, (1290, y), lab, font("sans", 20), MUTED, alpha=0.85 * a)
        text(d, (1790, y - 4), val, font("mono_sb", 46), col, anchor="ra", alpha=a)
        hairline(d, 1290, y + 52, 1790, y + 52, BRONZE, 0.22 * a)

    a = smooth(between(u, 0.60, 0.82))
    panel(d, (1250, 726, 1830, 800), radius=10, fill=(16, 28, 22, 200), outline=(120, 200, 160, 70))
    text(d, (1290, 754), "235 + 19  =  254   →   RATIO 254 / 19", font("mono_sb", 25), GOLD, alpha=a)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0.0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S07
def prime_factorization(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img, "RGBA")

    # left: the fraction
    fx = 330
    text(d, (fx, 320), "254", font("mono_sb", 108), GOLD, anchor="mm")
    d.line([(fx - 96, 384), (fx + 96, 384)], fill=with_alpha(PARCHMENT, 0.8), width=4)
    text(d, (fx, 450), "19", font("mono_sb", 108), PARCHMENT, anchor="mm")
    text(d, (fx, 560), "THE TARGET RATIO", font("mono", 16), MUTED, anchor="mm", tracking=4)

    # factor tree
    a1 = smooth(between(u, 0.10, 0.28))
    d.line([(fx + 96, 340), (fx + 210, 300)], fill=with_alpha(BRONZE_LIGHT, 0.6 * a1), width=2)
    d.line([(fx + 96, 340), (fx + 210, 390)], fill=with_alpha(BRONZE_LIGHT, 0.6 * a1), width=2)
    text(d, (fx + 226, 300), "2", font("mono_sb", 52), PATINA_LIGHT, anchor="lm", alpha=a1)
    text(d, (fx + 226, 390), "127", font("mono_sb", 52), GOLD, anchor="lm", alpha=smooth(between(u, 0.16, 0.34)))
    text(d, (fx + 330, 390), "PRIME", font("mono", 15), CRIMSON, anchor="lm", tracking=2, alpha=smooth(between(u, 0.20, 0.38)))

    a2 = smooth(between(u, 0.24, 0.42))
    text(d, (fx + 226, 520), "19 is already prime", font("mono_md", 22), MUTED, alpha=0.85 * a2)

    # the buildable chain
    chain = [
        ("64", "38", "b2 → c1", 0.34),
        ("48", "24", "c2 → d1", 0.46),
        ("127", "32", "d2 → e2", 0.58),
    ]
    bx = 640
    for i, (n1, n2, lab, t0) in enumerate(chain):
        a = smooth(between(u, t0, t0 + 0.14))
        x = bx + i * 400
        y = 470
        panel(d, (x - 120, y - 90, x + 120, y + 90), radius=14, fill=(9, 14, 21, int(210 * a)),
              outline=(190, 150, 92, int(90 * a)))
        paste_gear(img, 54, int(n1), x - 50, y - 16, t * 12 * (1 if i % 2 == 0 else -1), "bronze", 4, alpha=a)
        paste_gear(img, 42, int(n2), x + 52, y + 34, -t * 12, "patina", 4, alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        text(d, (x, y + 62), lab, font("mono_md", 17), MUTED, anchor="mm", alpha=a, tracking=2)
        text(d, (x, y - 60), f"{n1}/{n2}", font("mono_sb", 22), GOLD, anchor="mm", alpha=a)
        if i < 2:
            arrow(d, (x + 132, y), (x + 262, y), c=BRONZE_LIGHT, width=2, head=11, alpha=0.6 * a)

    # product line
    a3 = smooth(between(u, 0.66, 0.86))
    text(d, (W / 2, 720), "64/38  ×  48/24  ×  127/32", font("mono_sb", 40), PARCHMENT, anchor="mm", alpha=a3)
    text(d, (W / 2, 786), "= (64 × 48 × 127) / (38 × 24 × 32)  =  389,376 / 29,184  =  254 / 19",
         font("mono", 22), MUTED, anchor="mm", alpha=0.9 * a3)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0.0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S08
def live_gear_train(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img, "RGBA")

    # ---- exact train geometry
    b2 = dict(cx=336, cy=600, r=112, n=64)
    c1 = dict(cx=336 + 112 + 68, cy=600, r=68, n=38)
    c2 = dict(cx=c1["cx"], cy=600, r=86, n=48)
    d1 = dict(cx=c1["cx"] + 86 + 40, cy=520, r=40, n=24)
    d2 = dict(cx=d1["cx"], cy=520, r=150, n=127)
    e2 = dict(cx=d1["cx"] + 150 + 52, cy=560, r=52, n=32)

    speed = 9.0  # deg/s of b2 -> deliberately slow so the train is legible
    th_b2 = -90 + t * speed
    th_c1 = mesh_angle(b2["n"], 0, th_b2, (b2["cx"], b2["cy"]), (c1["cx"], c1["cy"]), c1["n"])
    th_c2 = th_c1  # coaxial pair: same axle
    th_d1 = mesh_angle(c2["n"], 0, th_c2, (c2["cx"], c2["cy"]), (d1["cx"], d1["cy"]), d1["n"])
    th_d2 = th_d1
    th_e2 = mesh_angle(d2["n"], 0, th_d2, (d2["cx"], d2["cy"]), (e2["cx"], e2["cy"]), e2["n"])

    for g, th, pal in ((b2, th_b2, "bronze"), (c2, th_c2, "dark"), (c1, th_c1, "bronze"),
                       (d2, th_d2, "patina"), (d1, th_d1, "bronze"), (e2, th_e2, "bronze")):
        paste_gear(img, g["r"], g["n"], g["cx"], g["cy"], th, pal, 4)
    d = ImageDraw.Draw(img, "RGBA")

    # axle lines + labels
    labels = [
        (b2, "b2", "64"), (c1, "c1", "38"), (c2, "c2", "48"),
        (d1, "d1", "24"), (d2, "d2", "127"), (e2, "e2", "32"),
    ]
    for g, name, n in labels:
        d.ellipse((g["cx"] - 5, g["cy"] - 5, g["cx"] + 5, g["cy"] + 5), fill=(255, 255, 255, 120))
        text(d, (g["cx"], g["cy"] + g["r"] + 30), name, font("mono_sb", 22), GOLD, anchor="mm")
        text(d, (g["cx"], g["cy"] + g["r"] + 56), f"{n} teeth", font("mono", 15), MUTED, anchor="mm", alpha=0.8)

    # coaxial brace for c1/c2 and d1/d2
    for g in (c1, c2):
        pass
    d.arc((c1["cx"] - 96, c1["cy"] - 96, c1["cx"] + 96, c1["cy"] + 96), 200, 340,
          fill=with_alpha(CYAN, 0.35), width=1)
    d.arc((d1["cx"] - 160, d1["cy"] - 160, d1["cx"] + 160, d1["cy"] + 160), 200, 340,
          fill=with_alpha(CYAN, 0.30), width=1)
    text(d, (c1["cx"] + 92, c1["cy"] - 108), "coaxial pair", font("mono", 14), CYAN, alpha=0.65)
    text(d, (d1["cx"] + 158, d1["cy"] - 174), "coaxial pair", font("mono", 14), CYAN, alpha=0.65)

    # live ratio readout
    ratio = 254.0 / 19.0
    panel(d, (96, 830, 760, 962), radius=12, fill=(8, 13, 20, 214), outline=(190, 150, 92, 80))
    text(d, (124, 858), "OUTPUT / INPUT", font("mono", 15), MUTED, tracking=3, alpha=0.8)
    text(d, (124, 880), "254 / 19", font("mono_sb", 40), GOLD)
    text(d, (390, 892), f"= {ratio:.6f}", font("mono_md", 30), PATINA_LIGHT)
    text(d, (124, 936), f"e2 sweeps {ratio * 1.0:.2f} revolutions per single crank turn",
         font("sans", 17), MUTED, alpha=0.82)

    panel(d, (1180, 830, 1824, 962), radius=12, fill=(8, 13, 20, 200), outline=(120, 180, 200, 60))
    text(d, (1208, 858), "FRAGMENT A · REAR PLATE · SCHEMATIC", font("mono", 15), CYAN, tracking=2, alpha=0.85)
    text(d, (1208, 886), "(64/38) × (48/24) × (127/32) = 254/19", font("mono_md", 21), PARCHMENT, alpha=0.9)
    text(d, (1208, 918), "Freeth et al., Nature 444 (2006), Fig. 2", font("mono", 15), MUTED, alpha=0.7)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0.0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


REGISTRY = {
    "bathymetry_dive": bathymetry_dive,
    "museum_discovery": museum_discovery,
    "title_lockup": title_lockup,
    "calendar_drift": calendar_drift,
    "metonic_grid": metonic_grid,
    "sidereal_vector": sidereal_vector,
    "prime_factorization": prime_factorization,
    "live_gear_train": live_gear_train,
}

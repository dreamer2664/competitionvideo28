#!/usr/bin/env python3
"""Scenes S17–S24: the lunar anomaly, the pin-and-slot, and the closing cosmos."""
import math

from PIL import Image, ImageDraw, ImageFilter

from kinematics import solve_pin_and_slot
from render_kit import (
    BRONZE, BRONZE_DARK, BRONZE_LIGHT, CRIMSON, CYAN, CYAN_DEEP, GOLD, H,
    MUTED, MUTED_DIM, PARCHMENT, PATINA, PATINA_LIGHT, W,
    act_header, alpha_for, between, clamp, corner_ticks, base_canvas, draw_caption,
    ease_in_out,
    ease_out, font, glow_ellipse, hairline, lerp, mix, panel, paste_gear,
    plate, plate_frame, progress_bar, smooth, star_field, text, with_alpha,
)


# ------------------------------------------------------------------ S17
def lunar_ellipse_anomaly(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    cx, cy = 760, 540
    a_ax, b_ax = 400, 300
    # ellipse
    d.ellipse((cx - a_ax, cy - b_ax, cx + a_ax, cy + b_ax), outline=with_alpha(BRONZE, 0.45), width=2)
    # earth at focus
    c = math.sqrt(a_ax ** 2 - b_ax ** 2)
    ex, ey = cx + c, cy
    glow_ellipse(img, ex, ey, 30, 30, CYAN, 0.45, 22)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")
    d.ellipse((ex - 18, ey - 18, ex + 18, ey + 18), fill=(74, 148, 196), outline=(180, 226, 248))
    text(d, (ex + 28, ey + 30), "EARTH", font("mono", 14), CYAN, tracking=2, alpha=0.8)

    # perigee / apogee
    d.ellipse((cx - a_ax - 9, cy - 9, cx - a_ax + 9, cy + 9), fill=CRIMSON)
    text(d, (cx - a_ax - 16, cy + 26), "PERIGEE", font("mono_md", 15), CRIMSON, anchor="mm", tracking=2)
    text(d, (cx - a_ax - 16, cy + 48), "363,300 km", font("mono", 14), MUTED, anchor="mm", alpha=0.8)
    d.ellipse((cx + a_ax - 9, cy - 9, cx + a_ax + 9, cy + 9), fill=PATINA_LIGHT)
    text(d, (cx + a_ax + 16, cy + 26), "APOGEE", font("mono_md", 15), PATINA_LIGHT, anchor="mm", tracking=2)
    text(d, (cx + a_ax + 16, cy + 48), "405,500 km", font("mono", 14), MUTED, anchor="mm", alpha=0.8)

    # true-anomaly sweep: moon moves faster near perigee (Kepler II)
    n_steps = 720
    pts = []
    for i in range(n_steps):
        M = 2 * math.pi * (i / n_steps)  # mean anomaly
        # solve Kepler's equation E - e sinE = M, e ~ 0.0549
        e = 0.0549
        E = M
        for _ in range(6):
            E = E - (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
        nu = 2 * math.atan2(math.sqrt(1 + e) * math.sin(E / 2), math.sqrt(1 - e) * math.cos(E / 2))
        r = a_ax * (1 - e * math.cos(E))
        x = cx + r * math.cos(nu)
        y = cy + r * (b_ax / a_ax) * math.sin(nu)
        pts.append((x, y))
    d.line(pts, fill=with_alpha(GOLD, 0.30), width=1)

    # walk the moon along its true anomaly
    prog = ease_in_out(between(u, 0.02, 0.95)) * n_steps
    idx = int(prog) % n_steps
    mx, my = pts[idx]
    trail_start = max(0, idx - 60)
    d.line(pts[trail_start:idx + 1], fill=with_alpha(GOLD, 0.95), width=4)
    glow_ellipse(img, mx, my, 22, 22, GOLD, 0.4, 16)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")
    d.ellipse((mx - 12, my - 12, mx + 12, my + 12), fill=(242, 240, 232))

    # live angular speed readout
    e = 0.0549
    E = 0.0
    M = 2 * math.pi * (idx / n_steps)
    for _ in range(8):
        E = E - (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
    dnu_dM = math.sqrt(1 - e * e) / (1 - e * math.cos(E)) ** 2 if (1 - e * math.cos(E)) else 1
    mean_rate = 13.176358
    rate = mean_rate * dnu_dM
    near = "PERIGEE" if math.cos(E) > 0.6 else ("APOGEE" if math.cos(E) < -0.6 else "MID-ORBIT")

    panel(d, (1270, 300, 1824, 560), radius=14, fill=(8, 13, 20, 218), outline=(190, 150, 92, 80))
    text(d, (1300, 326), "LUNAR ANGULAR SPEED", font("mono", 15), MUTED, tracking=3, alpha=0.85)
    text(d, (1300, 352), f"{rate:5.2f}°/day", font("mono_sb", 58), GOLD)
    text(d, (1300, 424), f"mean 13.176°/day  ·  near {near}", font("mono", 17), PATINA_LIGHT, alpha=0.85)

    # bar
    bx0, bx1, byy = 1300, 1794, 470
    d.line([(bx0, byy), (bx1, byy)], fill=(255, 255, 255, 40), width=10)
    frac = clamp((rate - 11.6) / (14.5 - 11.6))
    d.line([(bx0, byy), (bx0 + (bx1 - bx0) * frac, byy)], fill=with_alpha(GOLD, 0.9), width=10)
    text(d, (bx0, byy + 24), "11.6", font("mono", 13), MUTED, alpha=0.7)
    text(d, (bx1, byy + 24), "14.5", font("mono", 13), MUTED, anchor="ra", alpha=0.7)

    text(d, (1300, 596), "Kepler's second law, executed\nby a pin sliding in a slot.",
         font("sans_md", 20), (212, 224, 234), alpha=0.9 * smooth(between(u, 0.4, 0.72)))

    # distance scale
    text(d, (1300, 686), "ORBITAL ECCENTRICITY  e = 0.0549", font("mono", 15), CYAN, alpha=0.7, tracking=2)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S18
def pin_and_slot_sim(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    cx, cy = 700, 560
    r_k1, r_k2 = 250, 210
    ecc_px = 52  # exaggerated ~1.1 mm for legibility; labelled as exaggerated

    theta1 = math.radians(-90 + t * 24.0)
    theta2, omega_ratio, deg_day = solve_pin_and_slot(theta1, ecc_ratio=0.21)

    # gear k2 (upper, slotted) behind
    paste_gear(img, r_k2, 50, cx, cy, math.degrees(theta2), "patina", 5)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    # the radial slot cut into k2
    slot_len = r_k2 * 0.92
    d.line([(cx, cy), (cx + slot_len * math.cos(theta2), cy + slot_len * math.sin(theta2))],
           fill=(6, 12, 14, 235), width=18)
    d.line([(cx, cy), (cx + slot_len * math.cos(theta2), cy + slot_len * math.sin(theta2))],
           fill=with_alpha(PATINA_LIGHT, 0.35), width=2)

    # gear k1 (lower, eccentric axle) — drawn semi transparent so the offset reads
    k1cx, k1cy = cx + ecc_px, cy
    paste_gear(img, r_k1, 50, k1cx, k1cy, math.degrees(theta1), "bronze", 5, alpha=0.34)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    # the two axles, and the offset between them
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=(240, 240, 235))
    d.ellipse((k1cx - 6, k1cy - 6, k1cx + 6, k1cy + 6), fill=GOLD)
    d.line([(cx, cy), (k1cx, k1cy)], fill=with_alpha(CRIMSON, 0.95), width=4)
    d.line([(cx, cy - 16), (cx, cy + 16)], fill=with_alpha(CRIMSON, 0.9), width=2)
    d.line([(k1cx, cy - 16), (k1cx, cy + 16)], fill=with_alpha(CRIMSON, 0.9), width=2)
    text(d, ((cx + k1cx) / 2, cy + 30), "e = 1.1 mm", font("mono_sb", 18), CRIMSON, anchor="ma")

    # the pin (on k1) and its position inside the slot
    pin_r = 0.90 * r_k1
    px = k1cx + pin_r * math.cos(theta1)
    py = k1cy + pin_r * math.sin(theta1)
    glow_ellipse(img, px, py, 16, 16, GOLD, 0.6, 14)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")
    d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=GOLD, outline=(255, 255, 240), width=2)

    # highlight the engaged radius along the slot
    d.line([(cx, cy), (px, py)], fill=with_alpha(GOLD, 0.45), width=2)

    # labels
    panel(d, (k1cx - 190, k1cy + r_k1 + 12, k1cx + 190, k1cy + r_k1 + 52), radius=8, fill=(6, 10, 16, 215), outline=(190, 150, 92, 70))
    text(d, (k1cx, k1cy + r_k1 + 32), "k1 · 50 teeth · DRIVER", font("mono_md", 16), GOLD, anchor="mm", tracking=2)
    panel(d, (cx - 190, cy - r_k2 - 56, cx + 190, cy - r_k2 - 16), radius=8, fill=(6, 10, 16, 215), outline=(120, 200, 180, 70))
    text(d, (cx, cy - r_k2 - 36), "k2 · 50 teeth · SLOTTED", font("mono_md", 16), PATINA_LIGHT, anchor="mm", tracking=2)

    # readouts
    panel(d, (1180, 300, 1824, 620), radius=14, fill=(8, 13, 20, 218), outline=(190, 150, 92, 80))
    text(d, (1210, 326), "PIN-AND-SLOT DIFFERENTIAL", font("mono", 15), MUTED, tracking=3, alpha=0.85)
    text(d, (1210, 352), "HIPPARCHUS · c. 130 BCE", font("sans_sb", 21), BRONZE_LIGHT, tracking=2)

    rows = [
        ("INPUT ANGLE  θ1", f"{math.degrees(theta1) % 360:6.1f}°"),
        ("OUTPUT ANGLE θ2", f"{math.degrees(theta2) % 360:6.1f}°"),
        ("SPEED RATIO ω2/ω1", f"{omega_ratio:5.3f}"),
        ("LUNAR RATE", f"{deg_day:5.2f}°/day"),
    ]
    for i, (lab, val) in enumerate(rows):
        y = 400 + i * 52
        text(d, (1210, y), lab, font("greek", 16) if ("θ" in lab or "ω" in lab) else font("mono", 15), MUTED, tracking=1 if ("θ" in lab or "ω" in lab) else 2, alpha=0.8)
        text(d, (1790, y - 4), val, font("mono_sb", 26), PARCHMENT, anchor="ra")

    text(d, (1210, 636), "Two equal wheels, one pin, one slot:\nthe output is forced to breathe.",
         font("sans_md", 19), (208, 220, 230), alpha=0.88 * smooth(between(u, 0.35, 0.7)))

    # small honesty note about exaggeration
    text(d, (1206, 906), "eccentricity in this diagram is exaggerated ×4 for legibility",
         font("mono", 13), MUTED_DIM, alpha=0.75)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S19
def pin_slot_oscilloscope(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    # scope panel
    ox, oy, ow, oh = 200, 260, 1120, 460
    d.rectangle((ox, oy, ox + ow, oy + oh), fill=(6, 12, 16, 235), outline=with_alpha(CYAN, 0.4), width=1)
    for gx in range(ox, ox + ow, 40):
        d.line([(gx, oy), (gx, oy + oh)], fill=(110, 190, 210, 8))
    for gy in range(oy, oy + oh, 40):
        d.line([(ox, gy), (ox + ow, gy)], fill=(110, 190, 210, 8))
    d.line([(ox, oy + oh / 2), (ox + ow, oy + oh / 2)], fill=(200, 230, 240, 26), width=1)

    # waveform of the ratio over one full k1 turn, drawn up to the current time
    n = 480
    span = 360.0  # degrees of k1
    cur = (t * 24.0) % 360.0
    pts = []
    for i in range(n + 1):
        frac = i / n
        th1 = math.radians(frac * span)
        _, ratio, _ = solve_pin_and_slot(th1, ecc_ratio=0.21)
        y = oy + oh / 2 - (ratio - 1.0) * 620
        x = ox + frac * ow
        pts.append((x, y))
    d.line(pts, fill=with_alpha(CYAN, 0.22), width=2)
    upto = int(n * (cur / span))
    d.line(pts[: max(2, upto)], fill=with_alpha(GOLD, 0.95), width=4)

    # playhead
    phx = ox + (cur / span) * ow
    d.line([(phx, oy), (phx, oy + oh)], fill=with_alpha(GOLD, 0.5), width=1)
    _, r_now, deg = solve_pin_and_slot(math.radians(cur), ecc_ratio=0.21)
    phy = oy + oh / 2 - (r_now - 1.0) * 620
    glow_ellipse(img, phx, phy, 14, 14, GOLD, 0.5, 12)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")
    d.ellipse((phx - 7, phy - 7, phx + 7, phy + 7), fill=GOLD)

    text(d, (ox + 14, oy + 12), "ω2 / ω1   ·   ONE TURN OF k1", font("greek", 16), CYAN, tracking=2, alpha=0.8)
    text(d, (ox + ow - 14, oy + 12), "CALCULATED, NOT MEASURED FROM FRAGMENTS",
         font("mono", 12), MUTED_DIM, anchor="ra", alpha=0.7)
    text(d, (ox - 6, oy + oh / 2), "ratio 1.00", font("mono", 13), MUTED, anchor="rm", alpha=0.7)

    # explanation column
    panel(d, (1380, 260, 1824, 700), radius=14, fill=(8, 13, 20, 214), outline=(120, 180, 200, 60))
    text(d, (1410, 286), "WHY A SLOT?", font("mono_md", 17), BRONZE_LIGHT, tracking=3)
    body = ("A gear tooth drives at a fixed\nradius, so it gives a constant\nspeed.\n\n"
            "A pin in a slot does not. Its\neffective radius grows and\nshrinks, so the driven wheel\n"
            "accelerates and hesitates —\nthe shape of an elliptical orbit.")
    y = 322
    for ln in body.split("\n"):
        text(d, (1410, y), ln, font("sans", 19), (208, 220, 230), alpha=0.9)
        y += 27

    panel(d, (1380, 724, 1824, 812), radius=12, fill=(14, 24, 20, 205), outline=(120, 200, 160, 70))
    text(d, (1410, 750), f"INSTANT ω2/ω1 = {r_now:.4f}", font("greek_bd", 20), GOLD)
    text(d, (1410, 782), f"lunar rate {deg:.2f}°/day at θ1 = {cur:.1f}°", font("greek", 15), PATINA_LIGHT, alpha=0.85)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S20
def epicyclic_turntable(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    cx, cy = 760, 560
    # the great e3 turntable
    paste_gear(img, 330, 223, cx, cy, t * 4.0, "dark", 6, alpha=0.9)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")
    d.ellipse((cx - 250, cy - 250, cx + 250, cy + 250), outline=with_alpha(BRONZE, 0.25), width=1)

    # the k-pair riding on the turntable, off centre
    ti = math.radians(t * 4.0)
    kx = cx + 168 * math.cos(ti)
    ky = cy + 168 * math.sin(ti)

    theta1 = math.radians(-90 + t * 60.0)
    theta2, _, _ = solve_pin_and_slot(theta1, 0.21)
    paste_gear(img, 86, 50, kx, ky, math.degrees(theta1), "bronze", 4, alpha=0.95)
    paste_gear(img, 74, 50, kx + 16, ky, math.degrees(theta2), "patina", 4, alpha=0.92)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")
    d.ellipse((kx - 5, ky - 5, kx + 5, ky + 5), fill=(240, 240, 235))

    panel(d, (kx - 58, ky + 96, kx + 58, ky + 130), radius=7, fill=(6, 10, 16, 220), outline=(190, 150, 92, 80))
    text(d, (kx, ky + 113), "k1 / k2", font("mono_md", 15), GOLD, anchor="mm", tracking=2)

    # line of apsides
    apogee_ang = ti
    ax1 = cx + 300 * math.cos(apogee_ang)
    ay1 = cy + 300 * math.sin(apogee_ang)
    ax2 = cx - 300 * math.cos(apogee_ang)
    ay2 = cy - 300 * math.sin(apogee_ang)
    d.line([(ax2, ay2), (ax1, ay1)], fill=with_alpha(CRIMSON, 0.55), width=2)
    d.ellipse((ax1 - 9, ay1 - 9, ax1 + 9, ay1 + 9), fill=CRIMSON)
    text(d, (ax1, ay1 - 26), "APOGEE", font("mono", 14), CRIMSON, anchor="mm", tracking=2, alpha=0.9)
    text(d, (cx, cy - 268), "e3 · 223 TEETH · ONE TURN = 18.6 YEARS", font("mono_md", 15), MUTED,
         anchor="mm", tracking=2, alpha=0.8)

    # precession arc
    for k in range(3):
        d.arc((cx - 350, cy - 350, cx + 350, cy + 350),
              math.degrees(ti) - 150 - k * 30, math.degrees(ti) - 20 - k * 30,
              fill=with_alpha(GOLD, 0.12 - k * 0.03), width=3)

    # right column
    panel(d, (1240, 280, 1824, 640), radius=14, fill=(8, 13, 20, 218), outline=(190, 150, 92, 80))
    text(d, (1270, 306), "THE TURNTABLE TRICK", font("mono_md", 17), BRONZE_LIGHT, tracking=3)
    body = ("The pin-and-slot pair does not\nsit still. It rides on the great\nSaros wheel e3.\n\n"
            "That slow rotation carries the\nline of apsides all the way round\nthe sky every 8.85 years.")
    y = 344
    for ln in body.split("\n"):
        text(d, (1270, y), ln, font("sans", 20), (208, 220, 230), alpha=0.92)
        y += 29

    text(d, (1270, 596), "ANOMALISTIC MONTH 27.5545 d  ·  8.85 yr", font("mono", 15), PATINA_LIGHT,
         alpha=0.85, tracking=1)

    # rotation counters
    panel(d, (1240, 668, 1824, 792), radius=12, fill=(10, 16, 24, 210), outline=(120, 180, 200, 60))
    text(d, (1270, 692), "TURNTABLE ANGLE", font("mono", 14), MUTED, tracking=2, alpha=0.8)
    text(d, (1270, 714), f"{(math.degrees(ti) % 360):6.1f}°", font("mono_sb", 30), CYAN)
    text(d, (1560, 714), "APSIDAL CYCLE", font("mono", 14), MUTED, tracking=2, alpha=0.8)
    text(d, (1560, 736), "8.85 yr", font("mono_sb", 30), GOLD)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S21
def ucl_venus_saturn(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    text(d, (W / 2, 236), "THE FRONT PLATE · DECODED 2021", font("mono_md", 19), CYAN, anchor="mm", tracking=4, alpha=0.9)
    hairline(d, W / 2 - 260, 268, W / 2 + 260, 268, CYAN, 0.35)

    cards = [
        ("VENUS", "289 / 462", "289 synodic cycles\nin 462 tropical years", 0.10, GOLD),
        ("SATURN", "427 / 442", "427 synodic cycles\nin 442 tropical years", 0.26, PATINA_LIGHT),
    ]
    for i, (name, frac, desc, t0, col) in enumerate(cards):
        a = smooth(between(u, t0, t0 + 0.16))
        x = 300 + i * 640
        y = 340
        panel(d, (x, y, x + 560, y + 380), radius=18, fill=(9, 14, 21, int(215 * a)), outline=(190, 150, 92, int(90 * a)))
        text(d, (x + 34, y + 26), name, font("sans_sb", 24), MUTED, tracking=6, alpha=0.9 * a)
        text(d, (x + 34, y + 66), frac, font("mono_sb", 76), col, alpha=a)
        yy = y + 190
        for ln in desc.split("\n"):
            text(d, (x + 34, yy), ln, font("sans", 22), (206, 218, 228), alpha=0.9 * a)
            yy += 34
        # tiny ring diagram
        rcx, rcy, rr = x + 470, y + 300, 44
        d.ellipse((rcx - rr, rcy - rr, rcx + rr, rcy + rr), outline=with_alpha(col, 0.5 * a), width=1)
        d.ellipse((rcx - 7, rcy - 7, rcx + 7, rcy + 7), fill=with_alpha(col, a))
        d.line([(rcx, rcy), (rcx + rr * math.cos(t * 0.6 + i), rcy + rr * math.sin(t * 0.6 + i))],
               fill=with_alpha(col, 0.6 * a), width=2)

    # factorisation strip
    a = smooth(between(u, 0.44, 0.66))
    panel(d, (300, 760, 1500, 880), radius=14, fill=(8, 13, 20, 205), outline=(120, 180, 200, int(60 * a)))
    text(d, (330, 786), "462 = 6 × 7 × 11", font("mono_sb", 30), GOLD, alpha=a)
    text(d, (760, 786), "442 = 2 × 13 × 17", font("mono_sb", 30), PATINA_LIGHT, alpha=a)
    text(d, (330, 832), "these are the whole-number handles the front gearing had to turn",
         font("sans", 19), MUTED, alpha=0.85 * a)

    # citation
    text(d, (1540, 800), "Freeth et al.,\nScientific Reports 11:5821 (2021)", font("mono", 14), MUTED, alpha=0.7 * a)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S22
def planetary_ring_cosmos(img, shot, u, t, tl):
    bg = plate_frame("plate_08_planetary_rings.jpg", zoom=lerp(1.22, 1.05, ease_out(u)), dim=0.52, blur=1.4)
    img.paste(bg)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    cx, cy = 760, 560
    planets = [
        ("MOON", 1.00, 0.72, (226, 230, 236), 0.30),
        ("SUN", 0.92, 0.95, (252, 214, 128), 0.22),
        ("MERCURY", 0.98, 0.78, (206, 184, 160), 0.26),
        ("VENUS", 0.96, 0.85, (246, 226, 190), 0.30),
        ("MARS", 0.94, 0.86, (222, 122, 96), 0.34),
        ("JUPITER", 0.92, 0.90, (226, 200, 164), 0.38),
        ("SATURN", 0.90, 0.94, (232, 214, 168), 0.42),
    ]
    for i, (name, r0, r1, col, speed) in enumerate(planets):
        rr = 150 + i * 44
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=with_alpha(col, 0.18), width=1)
        ang = -math.pi / 2 + t * speed + i * 0.9
        # slow, clearly non-uniform: outer planets almost crawl
        ang = -math.pi / 2 + t * speed * (1.0 / (1 + i * 0.9)) + i * 1.3
        x = cx + rr * math.cos(ang)
        y = cy + rr * math.sin(ang) * 0.42
        rad = 7 if i < 3 else 9
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=col, outline=(255, 255, 255, 110))
        if i == 6:  # saturn ring
            d.ellipse((x - rad - 12, y - 5, x + rad + 12, y + 5), outline=with_alpha(col, 0.6), width=1)

    # zodiac ring with Greek signs
    zr = 470
    d.ellipse((cx - zr, cy - zr, cx + zr, cy + zr), outline=with_alpha(GOLD, 0.22), width=1)
    signs = "Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω".split()
    for i, s in enumerate(signs):
        a = -math.pi / 2 + i * 2 * math.pi / 12
        x = cx + (zr - 26) * math.cos(a)
        y = cy + (zr - 26) * math.sin(a)
        text(d, (x, y), s, font("sans_md", 26), PARCHMENT, anchor="mm", alpha=0.30)

    # labelling panel
    panel(d, (1350, 300, 1824, 640), radius=14, fill=(8, 13, 20, 216), outline=(190, 150, 92, 80))
    text(d, (1380, 326), "SEVEN WANDERERS · ONE HANDLE", font("mono_md", 16), BRONZE_LIGHT, tracking=2)
    body = ("Each planet rides a concentric\nbronze ring. A pearl or a small\nsphere marks its place against\nthe zodiac.\n\n"
            "The user did not read a screen.\nThey watched a model of the sky\nturn in their hands.")
    y = 366
    for ln in body.split("\n"):
        text(d, (1380, y), ln, font("sans", 19), (208, 220, 230), alpha=0.9)
        y += 28

    # fragment D note
    panel(d, (1350, 664, 1824, 748), radius=12, fill=(18, 16, 10, 200), outline=(190, 150, 92, 70))
    text(d, (1380, 688), "FRAGMENT D · ORPHANED 63-TOOTH WHEEL", font("mono", 14), GOLD, alpha=0.9, tracking=1)
    text(d, (1380, 712), "the gear that had no home until 2021", font("sans", 17), MUTED, alpha=0.85)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S23
def historical_lineage(img, shot, u, t, tl):
    bg = plate_frame(shot["plate"], zoom=lerp(1.18, 1.06, ease_out(u)), dim=0.66, tint=(6, 14, 22), blur=1.2)
    img.paste(bg)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(band, "RGBA").rectangle((150, 470, 1770, 760), fill=(4, 8, 13, 190))
    band = band.filter(ImageFilter.GaussianBlur(46))
    img.paste(band, (0, 0), band)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    x0, x1, y = 200, 1720, 640
    d.line([(x0, y), (x1, y)], fill=with_alpha(PARCHMENT, 0.35), width=2)

    events = [
        ("c. 100 BCE", "the mechanism is built", 0.00, BRONZE_LIGHT),
        ("c. 70 BCE", "shipwreck off Antikythera", 0.12, BRONZE_LIGHT),
        ("1900", "sponge divers raise the cargo", 0.26, CYAN),
        ("1902", "Stais sees the teeth", 0.34, CYAN),
        ("1974", "Price's radiographs", 0.46, CYAN),
        ("2005", "BladeRunner CT scan", 0.60, GOLD),
        ("2006-08", "gearing, Saros, Olympiad published", 0.74, GOLD),
        ("2021", "the front cosmos reconstructed", 0.86, PATINA_LIGHT),
    ]
    prog = ease_in_out(between(u, 0.04, 0.82))
    for i, (date, label, pos, col) in enumerate(events):
        a = smooth(clamp((prog - pos) / 0.14)) if prog >= pos else 0.0
        x = x0 + pos * (x1 - x0)
        d.line([(x, y - 14), (x, y + 14)], fill=with_alpha(col, 0.9 * a), width=2)
        d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=with_alpha(col, a))
        up = i % 2 == 0
        ty = y - 40 if up else y + 34
        text(d, (x, ty), date, font("mono_sb", 22), col, anchor="mb" if up else "mt", alpha=a)
        text(d, (x, ty - 30 if up else ty + 30), label, font("sans", 17), (206, 218, 228),
             anchor="mb" if up else "mt", alpha=0.85 * a)

    # the two candidate workshops
    panel(d, (200, 790, 940, 940), radius=12, fill=(8, 13, 20, 216), outline=(190, 150, 92, 70))
    text(d, (230, 814), "WHERE WAS IT MADE?", font("mono_md", 16), BRONZE_LIGHT, tracking=3)
    text(d, (230, 846), "Rhodes — Hipparchus's tradition", font("sans", 20), PARCHMENT, alpha=0.9)
    text(d, (230, 880), "Syracuse — the school of Archimedes", font("sans", 20), PARCHMENT, alpha=0.9)
    text(d, (230, 910), "the Corinthian month names hint at Corinth or Syracuse", font("mono", 13), MUTED, alpha=0.8)

    panel(d, (990, 790, 1730, 940), radius=12, fill=(8, 13, 20, 216), outline=(120, 180, 200, 60))
    text(d, (1020, 814), "WHAT THE SILENCE LEFT US", font("mono_md", 16), CYAN, tracking=3)
    text(d, (1020, 846), "no Greek author describes this machine", font("sans", 20), (208, 220, 230), alpha=0.9)
    text(d, (1020, 880), "Cicero mentions Archimedes-built spheres — not this one", font("sans", 20), (208, 220, 230), alpha=0.9)
    text(d, (1020, 910), "geared astrolabes carry the idea into Islam and Byzantium", font("mono", 13), MUTED, alpha=0.8)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S24
def coda_blueprint(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")
    star_field(d, t, count=120, seed=21, alpha=0.55)

    # 30 wheels assembling out of the dark
    rng_teeth = [223, 188, 127, 120, 96, 88, 64, 60, 54, 53, 50, 50, 48, 48, 40, 38, 32, 32,
                 30, 27, 24, 24, 20, 16, 16, 12, 12, 10, 8, 8]
    cx, cy = 960, 618
    build = ease_out(between(u, 0.02, 0.55))
    for i, teeth in enumerate(rng_teeth):
        ang = i * 2.399963  # golden angle
        rad = 40 + 26 * math.sqrt(i) * 3.1
        spread = lerp(2.6, 1.0, build)
        x = cx + rad * spread * math.cos(ang)
        y = cy + rad * spread * math.sin(ang) * 0.72
        size = lerp(14, 18 + 150 / (2 + i * 0.5), build)
        a = clamp(build * 1.4 - i * 0.014)
        paste_gear(img, size, teeth, x, y, t * (8 + i % 5) * (1 if i % 2 == 0 else -1), "bronze", 4, alpha=a * 0.9)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    # luminous core
    glow_ellipse(img, cx, cy, 90, 90, GOLD, 0.16 * build, 60)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    # scrim so the type never fights the wheel cluster
    scrim = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    sd.ellipse((240, 150, 1680, 430), fill=(4, 7, 11, 206))
    scrim = scrim.filter(ImageFilter.GaussianBlur(70))
    img.paste(scrim, (0, 0), scrim)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    # closing card
    a1 = smooth(between(u, 0.56, 0.76))
    a2 = smooth(between(u, 0.66, 0.86))
    text(d, (W / 2, 250), "THIRTY BRONZE WHEELS", font("display", 62), PARCHMENT, anchor="mm", alpha=a1, tracking=3)
    text(d, (W / 2, 310), "a machine built to make the sky legible", font("sans_md", 24), BRONZE_LIGHT, anchor="mm", alpha=a2)

    a3 = smooth(between(u, 0.62, 0.80))
    if a3 > 0.02:
        panel(d, (470, 900, 1450, 992), radius=12,
              fill=(6, 10, 15, int(248 * a3)), outline=(190, 150, 92, int(70 * a3)))
    text(d, (W / 2, 932), "CHRONOSCOPE  ·  2026", font("mono_md", 20), GOLD, anchor="mm", tracking=5, alpha=a3)
    text(d, (W / 2, 966), "written, drawn and scored by code  ·  sources in SOURCES.md", font("mono", 15),
         MUTED, anchor="mm", alpha=0.8 * a3)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.55, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


REGISTRY = {
    "lunar_ellipse_anomaly": lunar_ellipse_anomaly,
    "pin_and_slot_sim": pin_and_slot_sim,
    "pin_slot_oscilloscope": pin_slot_oscilloscope,
    "epicyclic_turntable": epicyclic_turntable,
    "ucl_venus_saturn": ucl_venus_saturn,
    "planetary_ring_cosmos": planetary_ring_cosmos,
    "historical_lineage": historical_lineage,
    "coda_blueprint": coda_blueprint,
}

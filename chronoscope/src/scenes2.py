#!/usr/bin/env python3
"""Scenes S09–S16: radiography, tomography, epigraphy, the two spiral dials."""
import math

from PIL import Image, ImageDraw, ImageFilter

from render_kit import (
    BRONZE, BRONZE_DARK, BRONZE_LIGHT, CRIMSON, CYAN, CYAN_DEEP, GOLD, H,
    MUTED, MUTED_DIM, PARCHMENT, PATINA, PATINA_LIGHT, W,
    act_header, alpha_for, between, clamp, corner_ticks, base_canvas, draw_caption,
    ease_in_out,
    ease_out, font, glow_ellipse, hairline, lerp, mix, panel, paste_gear,
    plate, plate_frame, progress_bar, smooth, star_field, text, with_alpha,
)
from kinematics import (
    CORINTHIAN_MONTHS, SAROS_ECLIPSE_CELLS, gear_tooth_polygon, spiral_point,
)


# ------------------------------------------------------------------ S09
def price_radiograph(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    # radiographic plate rectangle
    px0, py0, px1, py1 = 300, 250, 1240, 900
    d.rectangle((px0, py0, px1, py1), fill=(9, 22, 26, 235), outline=with_alpha(CYAN, 0.45), width=2)

    # stacked translucent gears (the ambiguity the flat radiograph could not resolve)
    stack = [
        (620, 560, 178, 127, 0.20, 0.0),
        (700, 600, 150, 96, 0.26, 40.0),
        (660, 640, 132, 64, 0.30, -30.0),
        (730, 540, 108, 38, 0.34, 15.0),
    ]
    for i, (cx, cy, r, n, alpha, ph) in enumerate(stack):
        sp = gear_tooth_polygon(cx, cy, r, n, math.radians(ph + t * (6 + i * 2)))
        d.polygon(sp, fill=None, outline=with_alpha(CYAN, alpha * 2.2))
        d.line(sp + [sp[0]], fill=with_alpha(CYAN, alpha * 1.4), width=1)

    # bloom / scanlines to sell the radiograph
    for y in range(py0, py1, 6):
        d.line([(px0, y), (px1, y)], fill=(140, 230, 255, 4))
    glow_ellipse(img, 660, 580, 200, 200, CYAN, 0.10, 60)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    # overlap ambiguity callout
    a1 = smooth(between(u, 0.22, 0.44))
    bx, by = 742, 672
    d.ellipse((bx - 12, by - 12, bx + 12, by + 12), outline=with_alpha(CRIMSON, 0.9 * a1), width=2)
    d.line([(bx + 12, by + 12), (960, 810)], fill=with_alpha(CRIMSON, 0.55 * a1), width=1)
    panel(d, (966, 786, 1224, 852), radius=8, fill=(30, 10, 10, 210), outline=(226, 85, 73, int(120 * a1)))
    text(d, (984, 800), "TWO WHEELS, ONE SHADOW", font("mono_md", 15), CRIMSON, alpha=a1, tracking=1)
    text(d, (984, 822), "±1 tooth destroys the ratio", font("sans", 15), (232, 170, 160), alpha=0.9 * a1)

    # corner marks + caption
    corner_ticks(d, (px0, py0, px1, py1), size=26, c=CYAN, alpha=0.55)
    text(d, (px0 + 18, py1 - 30), "FLAT PROJECTION · 2D", font("mono", 15), CYAN, alpha=0.7, tracking=2)

    # right column: what Price got right and wrong
    panel(d, (1300, 300, 1824, 620), radius=12, fill=(8, 13, 20, 210), outline=(190, 150, 92, 70))
    text(d, (1330, 326), "DEREK J. DE SOLLA PRICE · 1974", font("mono_md", 17), BRONZE_LIGHT, tracking=2, alpha=0.95)
    lines = [
        ("✓", "recognised a gear-driven calendar computer", PATINA_LIGHT, 0.16),
        ("✓", "counted 27 wheels in the surviving fragments", PATINA_LIGHT, 0.26),
        ("✗", "mis-read the tooth counts through overlap", CRIMSON, 0.34),
        ("✗", "placed the lunar anomaly in the wrong train", CRIMSON, 0.42),
    ]
    for mark, lab, col, t0 in lines:
        a = smooth(between(u, t0, t0 + 0.14))
        y = 372 + lines.index((mark, lab, col, t0)) * 58
        text(d, (1332, y), mark, font("dejavu_bd", 26), col, alpha=a)
        text(d, (1372, y + 3), lab, font("sans", 19), (208, 220, 230), alpha=0.9 * a)

    text(d, (1330, 648), "Charalambos Karakalos exposed the first\nradiographs in 1971. The plates were\nreadable — the geometry was not.",
         font("sans", 18), MUTED, alpha=0.8 * smooth(between(u, 0.5, 0.72)), spacing=8)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S10
def bladerunner_rig(img, shot, u, t, tl):
    bg = plate_frame(shot["plate"], zoom=lerp(1.14, 1.03, ease_out(u)), pan=(0.05, 0.0), dim=0.44, tint=(6, 14, 16))
    img.paste(bg)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    # scanning beam across the specimen
    sx = 470 + 620 * ease_in_out(between(u, 0.05, 0.72))
    for i in range(10):
        d.line([(sx - i * 3, 190), (sx - i * 3, 900)], fill=(140, 235, 255, 10 - i))
    d.line([(sx, 190), (sx, 900)], fill=with_alpha(CYAN, 0.55), width=2)

    # measurement brackets
    d.line([(430, 900), (430, 940), (1140, 940), (1140, 900)], fill=with_alpha(CYAN, 0.4), width=1)
    text(d, (785, 952), "SPECIMEN STAGE", font("mono", 14), CYAN, anchor="mm", tracking=3, alpha=0.6)

    # spec readout panel
    panel(d, (1260, 232, 1824, 700), radius=12, fill=(6, 11, 17, 222), outline=(120, 190, 210, 80))
    text(d, (1290, 258), "XT H 450 · “BLADERUNNER”", font("mono_sb", 21), CYAN, tracking=1, alpha=0.95)
    text(d, (1290, 290), "X-TEK INDUSTRIAL MICRO-FOCUS CT", font("mono", 14), MUTED, tracking=2, alpha=0.7)
    hairline(d, 1290, 316, 1794, 316, CYAN, 0.3)

    specs = [
        ("BEAM ENERGY", "450", "kV"),
        ("MASS OF THE RIG", "8", "tonnes"),
        ("VOXEL SIZE", "50", "µm"),
        ("FRAGMENTS SCANNED", "82", "pieces"),
        ("NEW GREEK CHARACTERS", "2,000+", "legible"),
    ]
    for i, (lab, val, unit) in enumerate(specs):
        a = smooth(between(u, 0.08 + i * 0.07, 0.24 + i * 0.07))
        y = 350 + i * 66
        text(d, (1290, y), lab, font("mono", 15), MUTED, tracking=2, alpha=0.8 * a)
        text(d, (1794, y - 8), val, font("mono_sb", 34), GOLD, anchor="ra", alpha=a)
        text(d, (1794, y + 26), unit, font("mono", 13), MUTED, anchor="ra", alpha=0.7 * a)

    text(d, (1266, 726), "The fragments could not travel. So the laboratory did.",
         font("sans_md", 19), BRONZE_LIGHT, alpha=0.9 * smooth(between(u, 0.5, 0.8)))

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S11
def ct_slice_scanner(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    # left: a stack of reconstructed slices in isometric offset
    ox, oy = 240, 300
    n_slices = 22
    z = lerp(0.0, 1.0, ease_in_out(between(u, 0.02, 0.9)))

    for i in range(n_slices):
        depth = i / (n_slices - 1)
        x = ox + i * 20
        y = oy + i * 12
        alpha = 0.10 + 0.22 * (1 - abs(depth - z))
        col = mix(CYAN_DEEP, CYAN, 1 - abs(depth - z))
        d.polygon([(x, y), (x + 300, y), (x + 340, y + 90), (x + 40, y + 90)],
                  fill=with_alpha((10, 26, 34), 0.55), outline=with_alpha(col, alpha + 0.15))
        # faint gear ghost on each slice
        cx, cy = x + 170, y + 45
        for k in range(24):
            ang = k * math.pi / 12
            d.line([(cx + 34 * math.cos(ang), cy + 34 * 0.4 * math.sin(ang)),
                    (cx + 44 * math.cos(ang), cy + 44 * 0.4 * math.sin(ang))],
                   fill=with_alpha(col, alpha * 0.8), width=1)

    # active slice highlighted
    az = int(round(z * (n_slices - 1)))
    ax0, ay0 = ox + az * 20, oy + az * 12
    d.polygon([(ax0, ay0), (ax0 + 300, ay0), (ax0 + 340, ay0 + 90), (ax0 + 40, ay0 + 90)],
              outline=with_alpha(GOLD, 0.95), width=3)

    # right: the volume viewer with a real gear cross-section emerging
    vx0, vy0, vx1, vy1 = 1000, 250, 1660, 820
    d.rectangle((vx0, vy0, vx1, vy1), fill=(4, 9, 13, 235), outline=with_alpha(CYAN, 0.35), width=1)
    cx, cy = (vx0 + vx1) / 2, (vy0 + vy1) / 2

    # voxel grid
    for gx in range(int(vx0), int(vx1), 44):
        d.line([(gx, vy0), (gx, vy1)], fill=(120, 200, 220, 9))
    for gy in range(int(vy0), int(vy1), 44):
        d.line([(vx0, gy), (vx1, gy)], fill=(120, 200, 220, 9))

    # cross-section: a 127-tooth gear seen in section, teeth revealed progressively
    reveal = ease_out(between(u, 0.15, 0.85))
    n = 127
    r_out, r_in = 168, 152
    for i in range(n):
        if i / n > reveal:
            break
        a0 = -math.pi / 2 + i * 2 * math.pi / n
        a1 = a0 + 2 * math.pi / n * 0.55
        a2 = a0 + 2 * math.pi / n * 0.95
        d.polygon([
            (cx + r_out * math.cos(a0), cy + r_out * math.sin(a0)),
            (cx + r_in * math.cos(a1), cy + r_in * math.sin(a1)),
            (cx + r_in * math.cos(a2), cy + r_in * math.sin(a2)),
        ], fill=with_alpha(CYAN, 0.55), outline=with_alpha((200, 245, 255), 0.7))
    d.ellipse((cx - r_in, cy - r_in, cx + r_in, cy + r_in), outline=with_alpha(CYAN, 0.55), width=2)
    d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), outline=with_alpha(CYAN, 0.6), width=2)

    text(d, (vx0 + 20, vy1 - 34), "RECONSTRUCTED VOXEL VOLUME · FRAGMENT A", font("mono", 14), CYAN, alpha=0.65, tracking=2)

    # depth readout
    panel(d, (1000, 846, 1660, 940), radius=10, fill=(6, 12, 18, 220), outline=(190, 150, 92, 70))
    text(d, (1026, 866), "SLICE DEPTH", font("mono", 15), MUTED, tracking=3, alpha=0.8)
    zmm = lerp(4.2, 18.7, z)
    text(d, (1026, 890), f"Z = {zmm:05.2f} mm", font("mono_sb", 34), GOLD)
    # slider
    sx0, sx1, sy = 1300, 1630, 905
    d.line([(sx0, sy), (sx1, sy)], fill=(255, 255, 255, 40), width=3)
    d.line([(sx0, sy), (sx0 + (sx1 - sx0) * z, sy)], fill=with_alpha(CYAN, 0.9), width=3)
    d.ellipse((sx0 + (sx1 - sx0) * z - 8, sy - 8, sx0 + (sx1 - sx0) * z + 8, sy + 8), fill=PARCHMENT)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S12
def ptm_epigraphy(img, shot, u, t, tl):
    img.paste(base_canvas(tint=None) if False else base_canvas())
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    # bronze plate
    px0, py0, px1, py1 = 190, 230, 1300, 900
    plate_img = plate("plate_02_fragment_a.jpg").crop((260, 120, 1160, 700)).resize((px1 - px0, py1 - py0), Image.LANCZOS)
    plate_img = plate_img.filter(ImageFilter.GaussianBlur(0.6))
    img.paste(plate_img, (px0, py0))
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")
    d.rectangle((px0, py0, px1, py1), outline=with_alpha(BRONZE, 0.6), width=2)

    # raking light: a moving bright band from the left
    band_x = px0 + (px1 - px0) * (0.15 + 0.7 * ease_in_out(between(u, 0.05, 0.85)))
    for i in range(34):
        a = int(13 * (1 - i / 34))
        d.line([(band_x + i * 5, py0), (band_x + i * 5 - 150, py1)], fill=(255, 232, 190, a), width=7)
    d.line([(band_x, py0), (band_x - 60, py1)], fill=(255, 240, 210, 60), width=2)

    # inscribed Greek lines, revealed as the light passes
    lines = [
        ("ΤΟ ΕΛΙΚΙΟΝ ΕΙΣ ΜΟΙΡΑΣ", "the spiral into sections"),
        ("ΔΙΑΚΟΣΙΑΣ ΤΡΙΑΚΟΝΤΑ ΠΕΝΤΕ", "two hundred and thirty-five"),
        ("Η ΣΦΑΙΡΙΔΙΟΝ Η ΧΡΥΣΗ", "the golden little sphere"),
        ("ΤΟΝ ΗΛΙΟΝ ΣΗΜΑΙΝΕΙ", "marks the Sun"),
        ("ΕΣΠΕΡΙΑΣ ΠΛΕΙΑΣ", "in the evening, the Pleiades"),
        ("ΑΝΑΤΕΛΛΟΥΣΙΝ", "rise"),
    ]
    scrim = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(scrim, "RGBA").rectangle((px0 + 24, py0 + 40, px0 + 700, py0 + 470), fill=(4, 7, 11, 150))
    scrim = scrim.filter(ImageFilter.GaussianBlur(26))
    img.paste(scrim, (0, 0), scrim)
    d = ImageDraw.Draw(img, "RGBA")

    for i, (gr, en) in enumerate(lines):
        a = smooth(between(u, 0.12 + i * 0.055, 0.26 + i * 0.055))
        y = py0 + 70 + i * 66
        x = px0 + 54
        text(d, (x, y), gr, font("greek", 29), (255, 244, 222), alpha=0.95 * a, tracking=2)
        text(d, (x + 4, y + 34), en, font("sans", 15), (250, 214, 158), alpha=0.78 * a)

    # translation panel
    panel(d, (1350, 300, 1824, 640), radius=12, fill=(8, 13, 20, 214), outline=(190, 150, 92, 80))
    text(d, (1380, 326), "PARAPHRASE OF THE INSCRIBED MANUAL", font("mono_md", 15), BRONZE_LIGHT, tracking=2, alpha=0.9)
    hairline(d, 1380, 352, 1794, 352, BRONZE, 0.3)
    body = ("“The spiral is divided\ninto 235 sections.\nThe golden little sphere\nmarks the Sun.\n"
            "In the evening the\nPleiades rise, and the\nHyades set.”")
    a = smooth(between(u, 0.34, 0.6))
    y = 372
    for ln in body.split("\n"):
        text(d, (1380, y), ln, font("display", 24), PARCHMENT, alpha=0.95 * a)
        y += 33
    text(d, (1380, 600), "trans. Freeth, Jones,\nSteele & Bitsakis (2008)", font("mono", 13), MUTED, alpha=0.7 * a)

    # PTM light-dome indicator
    panel(d, (1350, 668, 1824, 742), radius=10, fill=(8, 13, 20, 200), outline=(120, 180, 200, 60))
    text(d, (1380, 692), "POLYNOMIAL TEXTURE MAPPING · 20 LIGHT DIRECTIONS", font("mono", 13), CYAN, alpha=0.8, tracking=1)

    text(d, (1350, 776), "A second voice reads\nthe instrument's own label.",
         font("sans", 18), MUTED, alpha=0.75 * smooth(between(u, 0.1, 0.3)))

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S13
def metonic_spiral_dial(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    cx, cy = 830, 570
    r_in, r_out, turns, total = 118, 300, 5, 235

    # spiral guide
    pts = [spiral_point(cx, cy, r_in, r_out, turns, total, i) for i in range(0, total * 2 + 1)]
    d.line([(p[0], p[1]) for p in pts], fill=with_alpha(BRONZE, 0.42), width=2)

    # month cells
    for i in range(total):
        x, y, r, th = spiral_point(cx, cy, r_in, r_out, turns, total, i)
        month_idx = i % 30 if i % 30 else 0
        rad = 3.1 if i % 30 == 0 else 1.5
        col = GOLD if i % 30 == 0 else BRONZE_LIGHT
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=with_alpha(col, 0.85 if i % 30 == 0 else 0.45))

    # pointer / runner
    pos = total * ease_in_out(between(u, 0.04, 0.92))
    px, py, pr, pth = spiral_point(cx, cy, r_in, r_out, turns, total, pos)
    d.line([(cx, cy), (px, py)], fill=with_alpha(GOLD, 0.55), width=2)
    glow_ellipse(img, px, py, 26, 26, GOLD, 0.42, 18)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")
    d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=GOLD, outline=(40, 28, 10))

    # month name at the pointer
    which = int(pos) % 12
    gr = CORINTHIAN_MONTHS[which][1]
    en = CORINTHIAN_MONTHS[which][2]
    panel(d, (150, 780, 560, 880), radius=10, fill=(8, 13, 20, 220), outline=(190, 150, 92, 80))
    text(d, (176, 804), gr, font("sans_sb", 32), PARCHMENT, tracking=4)
    text(d, (176, 846), f"{en} · month {which + 1} of 12", font("sans", 17), BRONZE_LIGHT, alpha=0.85)

    # Olympiad sub-dial
    ox, oy, orr = 1460, 430, 132
    d.ellipse((ox - orr, oy - orr, ox + orr, oy + orr), outline=with_alpha(CYAN, 0.4), width=2)
    games = [("ΟΛΥΜΠΙΑ", "Olympia"), ("ΝΕΜΕΑ", "Nemea"), ("ΙΣΘΜΙΑ", "Isthmia"), ("ΠΥΘΙΑ", "Pythia")]
    for i, (gr, en) in enumerate(games):
        a0 = -math.pi / 2 + i * math.pi / 2
        oa = -math.pi / 2 + (pos / 235.0) * 2 * math.pi * (235 / 4)
        active = int(((pos / 235.0) * 235 / 4) % 4) == i
        c = GOLD if active else MUTED
        x, y = ox + (orr + 34) * math.cos(a0 + math.pi / 4), oy + (orr + 34) * math.sin(a0 + math.pi / 4)
        text(d, (x, y), gr, font("sans_md", 18), c, anchor="mm", tracking=2, alpha=0.95 if active else 0.5)
        text(d, (x, y + 22), en, font("mono", 12), MUTED, anchor="mm", alpha=0.65)
    ang4 = -math.pi / 2 + ((pos / 235.0) * 235 / 4) * 2 * math.pi
    d.line([(ox, oy), (ox + (orr - 18) * math.cos(ang4), oy + (orr - 18) * math.sin(ang4))],
           fill=with_alpha(GOLD, 0.9), width=3)
    d.ellipse((ox - 7, oy - 7, ox + 7, oy + 7), fill=GOLD)
    text(d, (ox, oy + orr + 62), "PANHELLENIC GAMES · 4-YEAR DIAL", font("mono", 14), CYAN, anchor="mm", tracking=2, alpha=0.75)

    # counters
    panel(d, (1400, 660, 1824, 800), radius=12, fill=(8, 13, 20, 210), outline=(120, 180, 200, 60))
    text(d, (1430, 686), "MONTH ON THE SPIRAL", font("mono", 14), MUTED, tracking=2, alpha=0.8)
    text(d, (1430, 710), f"{int(pos):03d}", font("mono_sb", 52), GOLD)
    text(d, (1560, 744), "/ 235", font("mono_md", 24), MUTED, alpha=0.8)
    text(d, (1430, 772), "five turns · 19 solar years", font("sans", 16), MUTED, alpha=0.7)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S14
def saros_convergence(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    # three period traces normalised across 223 synodic months
    x0, x1 = 220, 1700
    bands = [
        ("SYNODIC · NEW / FULL MOON", 29.53059, 223, PATINA_LIGHT, 300),
        ("DRACONIC · NODE CROSSING", 27.21222, 223, CYAN, 450),
        ("ANOMALISTIC · APSIS", 27.55455, 223, GOLD, 600),
    ]
    months_total = 223
    for label, period, n, col, yc in bands:
        pts = []
        for i in range(0, 620):
            mx = (i / 619.0) * n
            phase = (mx * 29.53059 / period) % 1.0
            x = x0 + (i / 619.0) * (x1 - x0)
            y = yc - 48 * math.sin(phase * 2 * math.pi)
            pts.append((x, y))
        d.line(pts, fill=with_alpha(col, 0.85), width=2)
        text(d, (x0 - 8, yc - 74), label, font("mono", 14), col, anchor="la", tracking=2, alpha=0.85)
        # convergence marker at the right edge
        d.ellipse((x1 - 7, yc - 7, x1 + 7, yc + 7), outline=with_alpha(col, 0.8), width=2)

    # progress sweep
    sweep = x0 + (x1 - x0) * ease_in_out(between(u, 0.05, 0.85))
    d.line([(sweep, 262), (sweep, 660)], fill=with_alpha(PARCHMENT, 0.22), width=1)

    # month counter
    mcount = int(months_total * ease_in_out(between(u, 0.05, 0.85)))
    panel(d, (220, 690, 700, 800), radius=12, fill=(8, 13, 20, 214), outline=(190, 150, 92, 80))
    text(d, (248, 714), "SYNODIC MONTHS", font("mono", 14), MUTED, tracking=3, alpha=0.8)
    text(d, (248, 736), f"{mcount:03d}", font("mono_sb", 52), GOLD)
    text(d, (400, 770), "/ 223", font("mono_md", 24), MUTED, alpha=0.8)

    # the three periods table
    panel(d, (760, 690, 1700, 812), radius=12, fill=(8, 13, 20, 200), outline=(120, 180, 200, 55))
    rows = [("SYNODIC", "29.53059 d"), ("DRACONIC", "27.21222 d"), ("ANOMALISTIC", "27.55455 d")]
    for i, (a, b) in enumerate(rows):
        x = 790 + i * 310
        text(d, (x, 714), a, font("mono", 13), MUTED, tracking=2, alpha=0.75)
        text(d, (x, 736), b, font("mono_sb", 26), bands[i][3])

    a = smooth(between(u, 0.55, 0.8))
    text(d, (W / 2, 880), "223 SYNODIC MONTHS  ≈  242 DRACONIC  ≈  239 ANOMALISTIC",
         font("mono_md", 25), PARCHMENT, anchor="mm", alpha=a)
    text(d, (W / 2, 930), "18 years · 11 days · 8 hours", font("mono", 22), PATINA_LIGHT, anchor="mm", alpha=0.9 * a)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S15
def saros_spiral_dial(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    cx, cy = 720, 570
    r_in, r_out, turns, total = 96, 296, 4, 223

    pts = [spiral_point(cx, cy, r_in, r_out, turns, total, i) for i in range(0, total * 2 + 1)]
    d.line([(p[0], p[1]) for p in pts], fill=with_alpha(BRONZE, 0.40), width=2)

    for i in range(total):
        x, y, r, th = spiral_point(cx, cy, r_in, r_out, turns, total, i)
        if i in SAROS_ECLIPSE_CELLS:
            mark = SAROS_ECLIPSE_CELLS[i]
            col = CRIMSON if mark.startswith("Σ") else GOLD
            if "·" in mark:
                col = mix(CRIMSON, GOLD, 0.5)
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=with_alpha(col, 0.95), outline=(255, 255, 255, 90))
            text(d, (x + 12, y - 4), mark, font("sans_md", 16), col, anchor="lm", alpha=0.85)
        else:
            d.ellipse((x - 1.6, y - 1.6, x + 1.6, y + 1.6), fill=with_alpha(BRONZE_LIGHT, 0.35))

    pos = total * ease_in_out(between(u, 0.03, 0.9))
    px, py, pr, pth = spiral_point(cx, cy, r_in, r_out, turns, total, pos)
    d.line([(cx, cy), (px, py)], fill=with_alpha(GOLD, 0.5), width=2)
    glow_ellipse(img, px, py, 26, 26, CRIMSON, 0.35, 18)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")
    d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=GOLD)

    # gear e3 behind the dial (223 teeth, hand-drawn as a ring of teeth)
    for i in range(223):
        a0 = -math.pi / 2 + i * 2 * math.pi / 223
        x0g = cx + 330 * math.cos(a0)
        y0g = cy + 330 * math.sin(a0)
        x1g = cx + 344 * math.cos(a0)
        y1g = cy + 344 * math.sin(a0)
        d.line([(x0g, y0g), (x1g, y1g)], fill=with_alpha(BRONZE_DARK, 0.55), width=3)
    d.ellipse((cx - 330, cy - 330, cx + 330, cy + 330), outline=with_alpha(BRONZE_DARK, 0.5), width=2)
    text(d, (cx, cy + 372), "e3 · 223 TEETH", font("mono_md", 17), MUTED, anchor="mm", tracking=3, alpha=0.75)

    # Exeligmos dial
    ex, ey, er = 1470, 420, 140
    d.ellipse((ex - er, ey - er, ex + er, ey + er), fill=(10, 16, 24, 200), outline=with_alpha(GOLD, 0.45), width=2)
    LABELS = []
    for k in range(3):
        a0 = -math.pi / 2 + k * 2 * math.pi / 3
        a1 = a0 + 2 * math.pi / 3
        d.arc((ex - er, ey - er, ex + er, ey + er), math.degrees(a0) + 2, math.degrees(a1) - 2,
              fill=with_alpha(BRONZE_LIGHT, 0.5), width=1)
        mx = ex + (er * 0.60) * math.cos(a0 + math.pi / 3)
        my = ey + (er * 0.60) * math.sin(a0 + math.pi / 3)
        LABELS.append((mx, my, k))
    seg = int(((pos / total) * 223 / 3) % 3)
    ang = -math.pi / 2 + seg * 2 * math.pi / 3 + math.pi / 3
    d.line([(ex, ey), (ex + (er - 22) * math.cos(ang), ey + (er - 22) * math.sin(ang))],
           fill=with_alpha(GOLD, 0.95), width=3)
    d.ellipse((ex - 8, ey - 8, ex + 8, ey + 8), fill=GOLD)
    for mx, my, k in LABELS:
        d.ellipse((mx - 27, my - 16, mx + 27, my + 16), fill=(8, 12, 18, 235))
        text(d, (mx, my), ["0 h", "8 h", "16 h"][k], font("mono_sb", 23), PARCHMENT, anchor="mm")
    text(d, (ex, ey + er + 46), "EXELIGMOS · 3 TURNS = 54 YEARS", font("mono", 14), CYAN, anchor="mm", tracking=2, alpha=0.8)

    panel(d, (1250, 640, 1824, 800), radius=12, fill=(8, 13, 20, 214), outline=(190, 150, 92, 70))
    text(d, (1280, 666), "ECLIPSE GLYPHS ON THE SAROS SPIRAL", font("mono", 14), MUTED, tracking=2, alpha=0.8)
    text(d, (1280, 694), "Σ", font("sans_bd", 36), CRIMSON)
    text(d, (1310, 704), "Selene — lunar eclipse", font("sans", 19), (222, 232, 240), alpha=0.92)
    text(d, (1280, 744), "Η", font("sans_bd", 36), GOLD)
    text(d, (1310, 754), "Helios — solar eclipse", font("sans", 19), (222, 232, 240), alpha=0.92)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


# ------------------------------------------------------------------ S16
def eclipse_glyph_detail(img, shot, u, t, tl):
    img.paste(base_canvas())
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")

    # total eclipse disc (plate) on the right
    eclipse = plate("plate_05_saros_eclipse.jpg")
    cx, cy, r = 520, 540, 258
    crop = eclipse.crop((640, 60, 1290, 710)).resize((r * 2, r * 2), Image.LANCZOS)
    mask = Image.new("L", (r * 2, r * 2), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, r * 2 - 1, r * 2 - 1), fill=255)
    img.paste(crop, (int(cx - r), int(cy - r)), mask)
    d = ImageDraw.Draw(img.convert("RGB") if img.mode != "RGB" else img, "RGBA")
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=with_alpha(GOLD, 0.6), width=2)

    # corona ticks radiating
    for i in range(72):
        a = i * 2 * math.pi / 72 + t * 0.06
        r0 = r + 10
        r1 = r + 16 + 12 * (0.5 + 0.5 * math.sin(i * 0.9 + t * 2.0))
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
               fill=with_alpha(GOLD, 0.14), width=1)

    text(d, (cx, cy + r + 44), "TOTAL SOLAR ECLIPSE · THE CLOCK OF THE SAROS", font("mono", 15), MUTED,
         anchor="mm", tracking=2, alpha=0.8)

    # right: glyph cells, blown up
    gx, gy = 1080, 300
    cell_w, cell_h = 150, 150
    cells = [("Σ", CRIMSON, "lunar"), ("Η", GOLD, "solar"), ("Σ·Η", mix(CRIMSON, GOLD, 0.5), "both")]
    for i, (g, col, lab) in enumerate(cells):
        x = gx + i * (cell_w + 26)
        panel(d, (x, gy, x + cell_w, gy + cell_h), radius=10, fill=(10, 16, 24, 220), outline=(190, 150, 92, 70))
        text(d, (x + cell_w / 2, gy + cell_h / 2 - 8), g, font("sans_bd", 62), col, anchor="mm")
        text(d, (x + cell_w / 2, gy + cell_h + 26), lab.upper(), font("mono", 14), MUTED, anchor="mm", tracking=2)

    # back-cover inscription panel
    panel(d, (1080, 560, 1824, 812), radius=12, fill=(8, 13, 20, 214), outline=(120, 180, 200, 60))
    text(d, (1110, 586), "BACK COVER · ECLIPSE FORECAST NOTES", font("mono", 15), CYAN, tracking=2, alpha=0.85)
    body = ("“Lunar eclipse at the ninth hour.\n"
            "Solar eclipse: winds from the east,\n"
            "and a dark crimson light.”")
    a = smooth(between(u, 0.28, 0.55))
    y = 620
    for ln in body.split("\n"):
        text(d, (1110, y), ln, font("display", 26), PARCHMENT, alpha=0.94 * a)
        y += 42
    text(d, (1110, 762), "paraphrase of published translations (Freeth et al. 2006, 2008)",
         font("mono", 13), MUTED, alpha=0.65 * a)

    act_header(d, shot["act"], shot["title"], shot["index"] + 1, len(tl["shots"]), alpha_for(u, 0, 0.9, 0.1))
    progress_bar(d, shot["start"] + t, tl["total_duration"])
    draw_caption(img, shot["caption_cards"], t, shot["start"])
    return img


REGISTRY = {
    "price_radiograph": price_radiograph,
    "bladerunner_rig": bladerunner_rig,
    "ct_slice_scanner": ct_slice_scanner,
    "ptm_epigraphy": ptm_epigraphy,
    "metonic_spiral_dial": metonic_spiral_dial,
    "saros_convergence": saros_convergence,
    "saros_spiral_dial": saros_spiral_dial,
    "eclipse_glyph_detail": eclipse_glyph_detail,
}

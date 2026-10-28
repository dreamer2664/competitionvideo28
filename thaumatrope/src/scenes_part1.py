#!/usr/bin/env python3
"""
Scene choreography for Shots S01 through S12 (Acts I, II, III, IV).
All stage elements stay strictly inside x=[72..1848], y=[88..905].
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from visual_primitives import (
    W, H, IVORY, MUTED, DIM, AMBER, CRIMSON, CYAN, EMERALD,
    BASE_TECH_CANVAS, PANEL_FILL, PANEL_BORDER,
    get_font, clamp, ease_out_cubic, ease_in_out_cubic, prog,
    render_ken_burns_plate, draw_particles, draw_panel, draw_top_hud, text_centered,
)


def _draw_atlantic_coast_poly(draw, ox, oy, mw, mh):
    """Stylized geographic silhouettes of Newfoundland, Nova Scotia, and Cape Breton."""
    # Newfoundland (upper right-center)
    nfld = [
        (ox + mw * 0.56, oy + mh * 0.06),
        (ox + mw * 0.66, oy + mh * 0.04),
        (ox + mw * 0.75, oy + mh * 0.12),
        (ox + mw * 0.79, oy + mh * 0.21),
        (ox + mw * 0.69, oy + mh * 0.23),
        (ox + mw * 0.62, oy + mh * 0.19),
        (ox + mw * 0.53, oy + mh * 0.18),
    ]
    # Nova Scotia + Cape Breton (upper left)
    ns = [
        (ox + mw * 0.05, oy + mh * 0.27),
        (ox + mw * 0.22, oy + mh * 0.19),
        (ox + mw * 0.38, oy + mh * 0.15),
        (ox + mw * 0.43, oy + mh * 0.20),
        (ox + mw * 0.31, oy + mh * 0.29),
        (ox + mw * 0.14, oy + mh * 0.35),
        (ox + mw * 0.05, oy + mh * 0.34),
    ]
    # Bathymetric shelf contour (200m) & slope contour (2000m) & abyssal contour (4500m)
    shelf = [
        (ox + mw * 0.04, oy + mh * 0.43),
        (ox + mw * 0.34, oy + mh * 0.34),
        (ox + mw * 0.48, oy + mh * 0.27),
        (ox + mw * 0.58, oy + mh * 0.33),
        (ox + mw * 0.85, oy + mh * 0.37),
        (ox + mw * 0.96, oy + mh * 0.30),
    ]
    slope = [
        (ox + mw * 0.04, oy + mh * 0.54),
        (ox + mw * 0.38, oy + mh * 0.45),
        (ox + mw * 0.52, oy + mh * 0.39),
        (ox + mw * 0.64, oy + mh * 0.46),
        (ox + mw * 0.95, oy + mh * 0.49),
    ]
    abyss = [
        (ox + mw * 0.06, oy + mh * 0.72),
        (ox + mw * 0.46, oy + mh * 0.66),
        (ox + mw * 0.72, oy + mh * 0.69),
        (ox + mw * 0.95, oy + mh * 0.73),
    ]
    draw.line(shelf, fill=(88, 204, 222, 95), width=2)
    draw.line(slope, fill=(88, 204, 222, 65), width=2)
    draw.line(abyss, fill=(88, 204, 222, 45), width=2)

    draw.polygon(nfld, fill=(28, 46, 68, 235), outline=(120, 162, 198, 210))
    draw.polygon(ns, fill=(28, 46, 68, 235), outline=(120, 162, 198, 210))

    f_lbl = get_font("mono_bold", 15)
    draw.text((ox + mw * 0.59, oy + mh * 0.12), "NEWFOUNDLAND", font=f_lbl, fill=(195, 214, 232, 220))
    draw.text((ox + mw * 0.14, oy + mh * 0.24), "NOVA SCOTIA", font=f_lbl, fill=(195, 214, 232, 220))
    draw.text((ox + mw * 0.74, oy + mh * 0.31), "200m SHELF", font=f_lbl, fill=(88, 204, 222, 155))
    draw.text((ox + mw * 0.74, oy + mh * 0.43), "2,000m SLOPE", font=f_lbl, fill=(88, 204, 222, 130))
    draw.text((ox + mw * 0.66, oy + mh * 0.75), "SOHM ABYSSAL PLAIN (~5,000m)", font=f_lbl, fill=(140, 175, 205, 165))


def scene_s01(plate_dir, shot, t_local, t_global):
    """S01: Immediate Frame-1 Hook — 1929 telegraph room + 6 channels flatlining at 20:32 UTC."""
    frac = clamp(t_local / shot["duration"])
    bg = render_ken_burns_plate(plate_dir, shot["plate"], frac, zoom_start=1.02, zoom_end=1.09, pan_x=(-16, 12), darken=0.80)
    im = Image.fromarray(bg).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_particles(d, t_global, tint=(234, 185, 110))
    draw_top_hud(d, shot["act"], "18 NOV 1929 · 20:32 UTC", t_local)

    # Right-side live siphon-recorder telemetry card (starts active on Frame 1!)
    px0, py0, px1, py1 = 1050, 128, 1836, 790
    draw_panel(d, (px0, py0, px1, py1))
    d.text((px0 + 32, py0 + 26), "TRANSATLANTIC SIPHON RECORDER LOG", font=get_font("mono_bold", 19), fill=AMBER)
    d.text((px0 + 32, py0 + 56), "Six continental-slope circuits drop simultaneously", font=get_font("sans_reg", 20), fill=MUTED)

    cables = [
        ("CABLE A · NY–ST. JOHNS #1", "1,450 fm"),
        ("CABLE B · CANSO–FAYAL #4", "1,500 fm"),
        ("CABLE C · HALIFAX–HARBOR GRACE", "800 fm"),
        ("CABLE D · NY–ST. JOHNS #2", "1,820 fm"),
        ("CABLE E · CANSO–FAYAL #6", "1,780 fm"),
        ("CABLE F · WESTERN UNION #1", "1,800 fm"),
    ]
    snap_t = 1.65  # All 6 flatline simultaneously right as "went dead at the exact same instant" lands!
    is_dead = t_local >= snap_t

    for idx, (cname, depth) in enumerate(cables):
        ry = py0 + 112 + idx * 88
        d.rounded_rectangle((px0 + 28, ry, px1 - 28, ry + 72), radius=8, fill=(16, 30, 50, 210), outline=(55, 88, 122, 140))
        d.text((px0 + 44, ry + 12), cname, font=get_font("mono_bold", 16), fill=IVORY)
        d.text((px0 + 44, ry + 40), f"DEPTH: {depth}", font=get_font("mono_reg", 14), fill=DIM)

        # Animated siphon waveform on right side of row
        wx0, wx1 = px0 + 420, px1 - 165
        wy = ry + 36
        pts = []
        for step in range(44):
            u = step / 43.0
            x = wx0 + u * (wx1 - wx0)
            if is_dead and u > 0.35:
                y = wy
            else:
                sig = math.sin(u * 22.0 - t_local * 14.0 + idx * 1.7) * 11.0 * math.cos(u * 9.0 + idx)
                y = wy + sig
            pts.append((x, y))
        col = CRIMSON if is_dead else CYAN
        d.line(pts, fill=col + (240,), width=3)

        status_txt = "LOST 20:32" if is_dead else "ACTIVE"
        st_col = CRIMSON if is_dead else EMERALD
        d.text((px1 - 150, ry + 25), status_txt, font=get_font("mono_bold", 16), fill=st_col)

    # Bottom-left seismic alert badge
    if t_local > 3.2:
        a = ease_out_cubic(prog(t_local, 3.2, 0.5))
        bx0, by0 = 84, 710
        d.rounded_rectangle((bx0, by0, bx0 + 620, by0 + 128), radius=12,
                            fill=(26, 14, 20, int(230 * a)), outline=(CRIMSON[0], CRIMSON[1], CRIMSON[2], int(220 * a)), width=2)
        d.text((bx0 + 26, by0 + 20), "SEISMIC SHOCK DETECTED · Mw 7.2", font=get_font("disp_bold", 26),
               fill=(CRIMSON[0], CRIMSON[1], CRIMSON[2], int(255 * a)))
        d.text((bx0 + 26, by0 + 62), "Epicenter: 44.55°N, 55.95°W · Grand Banks Continental Slope",
               font=get_font("mono_reg", 17), fill=(IVORY[0], IVORY[1], IVORY[2], int(240 * a)))

    return Image.alpha_composite(im, ov)


def scene_s02(plate_dir, shot, t_local, t_global):
    """S02: Procedural North Atlantic Stopwatch Teaser — 00:59 -> 03:03 -> 13:17."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_particles(d, t_global)
    draw_top_hud(d, shot["act"], "THE 13h 17m ANOMALY", t_local)

    # Map viewport left-center
    mx, my, mw, mh = 84, 112, 1140, 760
    draw_panel(d, (mx, my, mx + mw, my + mh))
    _draw_atlantic_coast_poly(d, mx, my, mw, mh)

    # Epicenter star/ring
    ex, ey = mx + mw * 0.53, my + mh * 0.39
    pulse = 10 + 8 * (0.5 + 0.5 * math.sin(t_local * 5.0))
    d.ellipse((ex - pulse, ey - pulse, ex + pulse, ey + pulse), outline=AMBER + (190,), width=2)
    d.ellipse((ex - 6, ey - 6, ex + 6, ey + 6), fill=AMBER + (255,))
    d.text((ex + 16, ey - 10), "EPICENTER (T+00:00)", font=get_font("mono_bold", 15), fill=AMBER)

    # Progressive southward break markers timed to narration
    events = [
        (2.4, 0.54, 0.49, "+00h 59m · CABLE 7", "100 km S"),
        (5.6, 0.56, 0.60, "+03h 03m · CABLE 8", "240 km S"),
        (8.4, 0.59, 0.84, "+13h 17m · CABLE 12", "540+ km S"),
    ]
    prev = (ex, ey)
    elapsed_hours = 0.0
    for trig, rx, ry, label, dist_str in events:
        px, py = mx + mw * rx, my + mh * ry
        p = ease_out_cubic(prog(t_local, trig, 0.7))
        if p > 0:
            cx = prev[0] + (px - prev[0]) * p
            cy = prev[1] + (py - prev[1]) * p
            d.line((prev[0], prev[1], cx, cy), fill=CRIMSON + (220,), width=4)
            if p > 0.65:
                r = 9 + 6 * math.sin((t_local - trig) * 4.0)
                d.ellipse((px - r, py - r, px + r, py + r), outline=CRIMSON + (210,), width=2)
                d.ellipse((px - 6, py - 6, px + 6, py + 6), fill=CRIMSON + (255,))
                d.rounded_rectangle((px + 18, py - 18, px + 325, py + 20), radius=6, fill=(24, 12, 18, 230), outline=CRIMSON + (190,))
                d.text((px + 28, py - 9), f"{label} ({dist_str})", font=get_font("mono_bold", 15), fill=IVORY)
            prev = (px, py)

    # Right stopwatch panel
    sx0, sy0, sx1, sy1 = 1260, 112, 1836, 872
    draw_panel(d, (sx0, sy0, sx1, sy1))
    d.text((sx0 + 34, sy0 + 32), "ELAPSED AFTER QUAKE", font=get_font("mono_bold", 19), fill=CYAN)

    # Interpolate stopwatch readout across shot
    total_min = int(clamp((t_local - 1.2) / max(1.0, shot["duration"] - 3.2)) * (13 * 60 + 17))
    hh, mm = total_min // 60, total_min % 60
    d.text((sx0 + 34, sy0 + 82), f"+{hh:02d}h {mm:02d}m", font=get_font("disp_black", 82), fill=AMBER)

    d.line((sx0 + 34, sy0 + 205, sx1 - 34, sy0 + 205), fill=(68, 114, 156, 120), width=1)
    d.text((sx0 + 34, sy0 + 232), "WHY IT DEFIED PHYSICS", font=get_font("sans_bold", 22), fill=IVORY)
    bullets = [
        ("Seismic waves:", "arrive in < 2 minutes"),
        ("Surface tsunami:", "passes in < 1 hour"),
        ("Cable #12 break:", "13 hours 17 minutes later"),
        ("Maximum reach:", "> 500 km downslope"),
    ]
    for i, (k, v) in enumerate(bullets):
        by = sy0 + 292 + i * 108
        d.rounded_rectangle((sx0 + 34, by, sx1 - 34, by + 86), radius=10, fill=(16, 31, 52, 210), outline=(58, 96, 134, 140))
        d.text((sx0 + 52, by + 14), k, font=get_font("sans_semi", 19), fill=MUTED)
        d.text((sx0 + 52, by + 44), v, font=get_font("mono_bold", 21), fill=AMBER if i >= 2 else CYAN)

    return Image.alpha_composite(im, ov)


def scene_s03(plate_dir, shot, t_local, t_global):
    """S03: Deep abyssal cable plate + monumental Documentary Title Card."""
    frac = clamp(t_local / shot["duration"])
    bg = render_ken_burns_plate(plate_dir, shot["plate"], frac, zoom_start=1.01, zoom_end=1.08, pan_y=(10, -10), darken=0.72)
    im = Image.fromarray(bg).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_particles(d, t_global)

    a_title = ease_out_cubic(prog(t_local, 0.35, 0.9))
    a_sub = ease_out_cubic(prog(t_local, 1.25, 0.9))
    line_w = int(680 * ease_in_out_cubic(prog(t_local, 0.65, 1.1)))

    # Translucent backdrop behind title for guaranteed >=12:1 legibility
    d.rounded_rectangle((190, 255, W - 190, 610), radius=18,
                        fill=(5, 11, 21, int(185 * a_title)),
                        outline=(234, 168, 68, int(120 * a_title)), width=1)

    text_centered(d, W // 2, 295, "18 NOVEMBER 1929  ·  NORTH ATLANTIC ABYSS",
                  get_font("mono_bold", 20), fill=(CYAN[0], CYAN[1], CYAN[2], int(245 * a_title)))
    text_centered(d, W // 2, 352, "THE THIRTEEN-HOUR",
                  get_font("serif_bold", 72), fill=(IVORY[0], IVORY[1], IVORY[2], int(255 * a_title)))
    text_centered(d, W // 2, 434, "AVALANCHE",
                  get_font("serif_bold", 78), fill=(AMBER[0], AMBER[1], AMBER[2], int(255 * a_title)))

    if line_w > 4:
        d.line((W // 2 - line_w, 530, W // 2 + line_w, 530), fill=(AMBER[0], AMBER[1], AMBER[2], int(220 * a_title)), width=2)

    text_centered(d, W // 2, 552, "How Twelve Broken Telegraph Cables Revealed a Hidden Force of Earth",
                  get_font("sans_med", 25), fill=(MUTED[0], MUTED[1], MUTED[2], int(245 * a_sub)))

    return Image.alpha_composite(im, ov)


def scene_s04(plate_dir, shot, t_local, t_global):
    """S04: 1929 North Atlantic Transatlantic Cable Crossroads Map."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_particles(d, t_global)
    draw_top_hud(d, shot["act"], "GLOBAL NERVE CENTER · 1929", t_local)

    mx, my, mw, mh = 84, 110, 1752, 770
    draw_panel(d, (mx, my, mx + mw, my + mh))

    # Stylized North America (left) to Europe/Azores (right)
    na_pts = [(mx + 60, my + 120), (mx + 390, my + 90), (mx + 560, my + 210),
              (mx + 470, my + 310), (mx + 260, my + 430), (mx + 120, my + 580), (mx + 60, my + 580)]
    eu_pts = [(mx + 1480, my + 110), (mx + 1690, my + 110), (mx + 1690, my + 540),
              (mx + 1540, my + 510), (mx + 1460, my + 340), (mx + 1390, my + 210)]
    azores = (mx + 1260, my + 545)
    grand_banks_box = (mx + 455, my + 215, mx + 695, my + 435)

    d.polygon(na_pts, fill=(26, 44, 66, 235), outline=(112, 154, 190, 200))
    d.polygon(eu_pts, fill=(26, 44, 66, 235), outline=(112, 154, 190, 200))
    d.ellipse((azores[0] - 10, azores[1] - 10, azores[0] + 10, azores[1] + 10), fill=AMBER, outline=IVORY)

    # 16 curved transatlantic telegraph corridors all funneling past Grand Banks!
    rng = np.random.default_rng(42)
    reveal = ease_out_cubic(prog(t_local, 0.1, 2.2))
    for i in range(16):
        y_start = my + 245 + (i % 6) * 34
        x_start = mx + 240 + (i % 3) * 85
        dest_az = (i % 4 == 0)
        x_end = azores[0] if dest_az else mx + 1430 + (i % 3) * 45
        y_end = azores[1] if dest_az else my + 175 + (i % 5) * 48
        mid_x = mx + 575
        mid_y = my + 245 + i * 12

        pts = []
        steps = int(42 * reveal)
        for s in range(max(2, steps)):
            u = s / 41.0
            # Quadratic Bezier passing near Grand Banks bottleneck
            bx = (1 - u) ** 2 * x_start + 2 * (1 - u) * u * mid_x + u ** 2 * x_end
            by = (1 - u) ** 2 * y_start + 2 * (1 - u) * u * mid_y + u ** 2 * y_end
            pts.append((bx, by))
        d.line(pts, fill=(88, 204, 222, 145), width=2)
        # Moving Morse light pulse
        pu = (t_local * 0.28 + i * 0.13) % 1.0
        if pu <= reveal:
            px = (1 - pu) ** 2 * x_start + 2 * (1 - pu) * pu * mid_x + pu ** 2 * x_end
            py = (1 - pu) ** 2 * y_start + 2 * (1 - pu) * pu * mid_y + pu ** 2 * y_end
            d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=AMBER + (245,))

    # Highlight Grand Banks chokepoint box
    d.rounded_rectangle(grand_banks_box, radius=10, outline=AMBER + (235,), width=3)
    d.text((grand_banks_box[0] + 12, grand_banks_box[3] + 12),
           "CHOKEPOINT: GRAND BANKS CORRIDOR (21 CABLES)", font=get_font("mono_bold", 17), fill=AMBER)

    f_city = get_font("sans_bold", 19)
    d.text((mx + 125, my + 390), "NEW YORK / CAPE COD", font=f_city, fill=IVORY)
    d.text((mx + 255, my + 250), "NOVA SCOTIA", font=f_city, fill=IVORY)
    d.text((mx + 470, my + 168), "NEWFOUNDLAND", font=f_city, fill=IVORY)
    d.text((mx + 1445, my + 145), "IRELAND & UK", font=f_city, fill=IVORY)
    d.text((mx + 1495, my + 310), "BREST, FRANCE", font=f_city, fill=IVORY)
    d.text((azores[0] - 55, azores[1] + 18), "FAYAL (AZORES)", font=f_city, fill=AMBER)

    # Summary stat card bottom-left
    draw_panel(d, (mx + 48, my + 595, mx + 650, my + 725), fill=(8, 17, 30, 238))
    d.text((mx + 74, my + 616), "HIGHEST CABLE DENSITY ON EARTH (1929)", font=get_font("sans_bold", 22), fill=CYAN)
    d.text((mx + 74, my + 654), "Western Union · Commercial Cable · Imperial · French Cable Co.",
           font=get_font("sans_reg", 19), fill=MUTED)
    d.text((mx + 74, my + 684), "Source: Heezen & Ewing (1952), American Journal of Science",
           font=get_font("mono_reg", 15), fill=DIM)

    return Image.alpha_composite(im, ov)


def scene_s05(plate_dir, shot, t_local, t_global):
    """S05: Procedural Telescoping 4-Layer Submarine Telegraph Cable Cutaway."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "DEEP-SEA CABLE ANATOMY", t_local)
    draw_panel(d, (84, 110, W - 84, 875))

    text_centered(d, W // 2, 142, "1920s ARMORED SUBMARINE TELEGRAPH CABLE", get_font("disp_bold", 34), fill=IVORY)
    text_centered(d, W // 2, 186, "Engineered to withstand >300 atmospheres of abyssal pressure",
                  get_font("sans_reg", 21), fill=MUTED)

    # Draw telescoping cylindrical cutaway centered at cy = 465
    cy = 465
    layers = [
        # (x_left, x_right, half_height, fill_rgb, rim_rgb, title, subtitle, reveal_t, callout_y)
        (230, 760, 118, (88, 102, 118), (156, 176, 196), "4. GALVANIZED STEEL ARMOR",
         "Helical high-tensile wires resist seabed abrasion", 2.6, 705),
        (720, 1060, 88, (124, 92, 56), (178, 138, 88), "3. TANNED JUTE BEDDING",
         "Tarred fibrous cushion absorbs crushing pressure", 1.8, 255),
        (1020, 1340, 58, (54, 118, 126), (96, 198, 212), "2. GUTTA-PERCHA INSULATION",
         "Natural tropical latex prevents seawater short-circuits", 0.9, 705),
        (1300, 1640, 28, (218, 132, 58), (248, 184, 98), "1. STRANDED COPPER CORE",
         "7-wire pure copper conductor carries Morse current", 0.1, 255),
    ]

    for xl, xr, hh, col, rim, title, sub, trig, cy_card in layers:
        p = ease_out_cubic(prog(t_local, trig, 0.7))
        if p <= 0:
            continue
        cur_xr = int(xl + (xr - xl) * p)
        # Cylinder body with top/bottom shading bands
        d.rectangle((xl, cy - hh, cur_xr, cy + hh), fill=col + (245,), outline=rim + (245,), width=2)
        d.rectangle((xl, cy - hh + int(hh * 0.22), cur_xr, cy - hh + int(hh * 0.52)),
                    fill=(min(255, col[0] + 35), min(255, col[1] + 35), min(255, col[2] + 35), 115))
        # Texture stripes for steel armor & copper strands
        if hh == 118:
            for sx in range(xl + 20, cur_xr - 15, 28):
                d.line((sx, cy - hh, sx + 18, cy + hh), fill=(52, 64, 76, 190), width=3)
        elif hh == 28:
            for sy in (-12, 0, 12):
                d.line((xl, cy + sy, cur_xr, cy + sy), fill=(252, 204, 130, 180), width=2)

        # Elliptical end-cap
        ew = int(hh * 0.36)
        d.ellipse((cur_xr - ew, cy - hh, cur_xr + ew, cy + hh), fill=rim + (245,), outline=IVORY + (210,), width=2)

        # Callout card + leader line
        cx_mid = (xl + xr) // 2
        card_w = 390
        bx0 = clamp(cx_mid - card_w // 2, 115, W - 115 - card_w)
        by0 = cy_card
        anchor_y = cy - hh if cy_card < cy else cy + hh
        card_edge_y = by0 + 104 if cy_card < cy else by0
        alpha = int(255 * p)
        d.line((cx_mid, anchor_y, bx0 + card_w // 2, card_edge_y), fill=(rim[0], rim[1], rim[2], alpha), width=2)
        d.ellipse((cx_mid - 5, anchor_y - 5, cx_mid + 5, anchor_y + 5), fill=(AMBER[0], AMBER[1], AMBER[2], alpha))
        d.rounded_rectangle((bx0, by0, bx0 + card_w, by0 + 104), radius=10,
                            fill=(12, 24, 42, int(235 * p)), outline=(rim[0], rim[1], rim[2], int(200 * p)), width=2)
        d.text((bx0 + 18, by0 + 16), title, font=get_font("mono_bold", 17), fill=(rim[0], rim[1], rim[2], alpha))
        d.text((bx0 + 18, by0 + 48), sub, font=get_font("sans_reg", 17), fill=(IVORY[0], IVORY[1], IVORY[2], alpha))

    return Image.alpha_composite(im, ov)


def scene_s06(plate_dir, shot, t_local, t_global):
    """S06: Wheatstone Bridge Fault-Location Circuit — Converting Ohms into Nautical Miles."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "SHORE FAULT TELEMETRY · 1929", t_local)

    # Left panel: Shore Station Wheatstone Bridge diamond
    lx0, ly0, lx1, ly1 = 84, 112, 870, 870
    draw_panel(d, (lx0, ly0, lx1, ly1))
    d.text((lx0 + 34, ly0 + 28), "SHORE STATION · WHEATSTONE BRIDGE", font=get_font("mono_bold", 19), fill=CYAN)

    cx, cy = (lx0 + lx1) // 2, 465
    top_pt = (cx, cy - 185)
    bot_pt = (cx, cy + 185)
    left_pt = (cx - 210, cy)
    right_pt = (cx + 210, cy)

    # Diamond arms
    d.line([top_pt, left_pt, bot_pt, right_pt, top_pt], fill=CYAN + (225,), width=4)
    # Center galvanometer circle
    d.line((left_pt[0], left_pt[1], right_pt[0], right_pt[1]), fill=AMBER + (180,), width=2)
    d.ellipse((cx - 58, cy - 58, cx + 58, cy + 58), fill=(10, 20, 34, 250), outline=AMBER + (240,), width=3)

    # Galvanometer needle dampens to vertical balance (0 mA) as bridge balances!
    bal_p = ease_out_cubic(prog(t_local, 1.0, 3.2))
    angle = (1.0 - bal_p) * 0.72 * math.cos(t_local * 5.5)
    nx = cx + 44 * math.sin(angle)
    ny = cy - 44 * math.cos(angle)
    d.line((cx, cy + 10, nx, ny), fill=CRIMSON if bal_p < 0.85 else EMERALD, width=4)
    text_centered(d, cx, cy + 20, "G = 0", get_font("mono_bold", 15), fill=EMERALD if bal_p > 0.85 else MUTED)

    # Resistor labels on bridge arms
    for rx, ry, lbl in [
        (cx - 145, cy - 115, "R1 (Known)"),
        (cx + 45, cy - 115, "R2 (Known)"),
        (cx - 165, cy + 90, "R_var (Dial)"),
        (cx + 35, cy + 90, "R_cable (Sea)"),
    ]:
        d.rounded_rectangle((rx - 10, ry - 10, rx + 135, ry + 26), radius=6, fill=(16, 32, 54, 235), outline=CYAN + (150,))
        d.text((rx, ry - 3), lbl, font=get_font("mono_bold", 15), fill=IVORY)

    text_centered(d, cx, ly1 - 88, "Balanced when R_cable = (R2 / R1) × R_var",
                  get_font("mono_bold", 19), fill=AMBER)

    # Right panel: Underwater fault distance readout
    rx0, ry0, rx1, ry1 = 910, 112, 1836, 870
    draw_panel(d, (rx0, ry0, rx1, ry1))
    d.text((rx0 + 36, ry0 + 28), "RESISTANCE-TO-DISTANCE CONVERSION", font=get_font("mono_bold", 19), fill=AMBER)

    # Cable line extending from Shore (left) to Seafloor Rupture (right)
    cab_y = 355
    cab_x0, cab_x1 = rx0 + 65, rx1 - 95
    break_x = int(cab_x0 + (cab_x1 - cab_x0) * 0.72)

    # Seafloor silhouette
    d.polygon([(rx0 + 36, 430), (break_x, 455), (rx1 - 36, 515), (rx1 - 36, 545), (rx0 + 36, 545)],
              fill=(24, 40, 62, 220))
    d.line((cab_x0, cab_y, break_x, cab_y + 88), fill=AMBER + (245,), width=6)
    d.line((break_x + 34, cab_y + 96, cab_x1, cab_y + 135), fill=(95, 112, 130, 130), width=5)

    # Animated measurement pulse traveling out & reflecting back from break
    ping_u = (t_local * 0.55) % 2.0
    u_pos = ping_u if ping_u <= 1.0 else (2.0 - ping_u)
    px = cab_x0 + (break_x - cab_x0) * u_pos
    py = cab_y + 88 * u_pos
    d.ellipse((px - 8, py - 8, px + 8, py + 8), fill=CYAN + (255,))

    # Spark/rupture marker
    d.ellipse((break_x - 14, cab_y + 88 - 14, break_x + 14, cab_y + 88 + 14), outline=CRIMSON + (240,), width=3)
    d.text((break_x - 85, cab_y + 32), "RUPTURE POINT", font=get_font("mono_bold", 16), fill=CRIMSON)
    d.text((cab_x0, cab_y - 34), "SHORE HUT", font=get_font("mono_bold", 16), fill=EMERALD)

    # Live formula readout cards
    ohms = 553.8 * bal_p
    miles = 184.6 * bal_p
    d.rounded_rectangle((rx0 + 48, 585, rx0 + 435, 815), radius=12, fill=(14, 28, 48, 230), outline=CYAN + (160,))
    d.text((rx0 + 72, 608), "MEASURED RESISTANCE", font=get_font("mono_bold", 16), fill=MUTED)
    d.text((rx0 + 72, 652), f"{ohms:5.1f} Ω", font=get_font("disp_black", 58), fill=CYAN)
    d.text((rx0 + 72, 742), "Copper spec: ~3.00 Ω / nmi", font=get_font("mono_reg", 16), fill=DIM)

    d.rounded_rectangle((rx0 + 470, 585, rx1 - 48, 815), radius=12, fill=(14, 28, 48, 230), outline=AMBER + (190,))
    d.text((rx0 + 494, 608), "EXACT FAULT DISTANCE", font=get_font("mono_bold", 16), fill=MUTED)
    d.text((rx0 + 494, 652), f"{miles:5.1f} nmi", font=get_font("disp_black", 58), fill=AMBER)
    d.text((rx0 + 494, 742), "Pinpointed from dry land", font=get_font("sans_semi", 18), fill=EMERALD)

    return Image.alpha_composite(im, ov)


def scene_s07(plate_dir, shot, t_local, t_global):
    """S07: Newfoundland's Burin Peninsula Tsunami Tragedy (Mw 7.2, 28 lives lost)."""
    frac = clamp(t_local / shot["duration"])
    bg = render_ken_burns_plate(plate_dir, shot["plate"], frac, zoom_start=1.01, zoom_end=1.075, pan_x=(14, -14), darken=0.80)
    im = Image.fromarray(bg).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "BURIN PENINSULA · PLACENTIA BAY", t_local)

    a = ease_out_cubic(prog(t_local, 0.35, 0.8))
    bx0, by0, bx1, by1 = 84, 615, 920, 868
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=14,
                        fill=(9, 17, 30, int(232 * a)), outline=(AMBER[0], AMBER[1], AMBER[2], int(185 * a)), width=2)
    d.text((bx0 + 30, by0 + 24), "THE HUMAN COST ON LAND · 18 NOVEMBER 1929",
           font=get_font("mono_bold", 18), fill=(AMBER[0], AMBER[1], AMBER[2], int(255 * a)))
    d.text((bx0 + 30, by0 + 62), "Magnitude 7.2 Earthquake & Landslide Tsunami",
           font=get_font("disp_bold", 31), fill=(IVORY[0], IVORY[1], IVORY[2], int(255 * a)))
    d.text((bx0 + 30, by0 + 114), "• Struck Newfoundland's Burin Peninsula ~2.5 hours after the main shock",
           font=get_font("sans_reg", 20), fill=(MUTED[0], MUTED[1], MUTED[2], int(245 * a)))
    d.text((bx0 + 30, by0 + 148), "• 28 lives lost; fishing stages and coastal homes swept into Placentia Bay",
           font=get_font("sans_reg", 20), fill=(MUTED[0], MUTED[1], MUTED[2], int(245 * a)))
    d.text((bx0 + 30, by0 + 194), "Sources: Johnstone (1930) · Fine et al. (2005) · Ruffman & Hann (2006)",
           font=get_font("mono_reg", 15), fill=(DIM[0], DIM[1], DIM[2], int(235 * a)))

    return Image.alpha_composite(im, ov)


def scene_s08(plate_dir, shot, t_local, t_global):
    """S08: Atlantic Cable Repair Ships & Vladimir de Smitt's 28-Break Census."""
    frac = clamp(t_local / shot["duration"])
    bg = render_ken_burns_plate(plate_dir, shot["plate"], frac, zoom_start=1.02, zoom_end=1.09, pan_x=(-14, 14), darken=0.80)
    im = Image.fromarray(bg).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "WESTERN UNION HYDROGRAPHIC ARCHIVE", t_local)

    a = ease_out_cubic(prog(t_local, 0.35, 0.8))
    px0, py0, px1, py1 = 84, 130, 740, 560
    d.rounded_rectangle((px0, py0, px1, py1), radius=14,
                        fill=(8, 17, 30, int(228 * a)), outline=(CYAN[0], CYAN[1], CYAN[2], int(185 * a)), width=2)
    d.text((px0 + 30, py0 + 26), "DE SMITT (1932) REPAIR DOSSIER",
           font=get_font("mono_bold", 18), fill=(CYAN[0], CYAN[1], CYAN[2], int(255 * a)))

    stats = [
        ("12", "Transatlantic cables severed"),
        ("28", "Distinct seafloor rupture points"),
        (">3,050 m", "Recovery grappling depths"),
        ("~1 Year", "Required for Atlantic repair fleet"),
    ]
    for i, (num, desc) in enumerate(stats):
        ry = py0 + 78 + i * 86
        d.text((px0 + 30, ry), num, font=get_font("disp_black", 36), fill=(AMBER[0], AMBER[1], AMBER[2], int(255 * a)))
        d.text((px0 + 235, ry + 9), desc, font=get_font("sans_med", 21), fill=(IVORY[0], IVORY[1], IVORY[2], int(245 * a)))

    return Image.alpha_composite(im, ov)


def scene_s09(plate_dir, shot, t_local, t_global):
    """S09: Bathymetric Cross-Profile — Intact Shelf vs 6 Instantaneous Slope Breaks (A-F)."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "ZONE 1 & ZONE 2 · T + 00h 00m", t_local)
    bx0, by0, bx1, by1 = 84, 112, 1836, 872
    draw_panel(d, (bx0, by0, bx1, by1))

    d.text((bx0 + 36, by0 + 26), "NORTH-TO-SOUTH SEAFLOOR ELEVATION PROFILE (GRAND BANKS)",
           font=get_font("mono_bold", 20), fill=CYAN)

    # Ocean water fill & seafloor bathymetric polygon
    sea_top = 245
    profile = [
        (130, 310), (490, 322),     # Shallow Continental Shelf (<200m)
        (610, 375), (840, 520), (1080, 650),  # Steep Continental Slope (150-1800 fm)
        (1380, 745), (1790, 775),   # Continental Rise -> Abyssal Plain
    ]
    d.rectangle((130, sea_top, 1790, 815), fill=(12, 34, 62, 180))
    d.line((130, sea_top, 1790, sea_top), fill=CYAN + (190,), width=2)
    d.text((1560, sea_top - 26), "SEA LEVEL (0 m)", font=get_font("mono_reg", 15), fill=CYAN)

    earth_poly = profile + [(1790, 825), (130, 825)]
    d.polygon(earth_poly, fill=(36, 52, 68, 245), outline=AMBER + (200,))

    # Zone 1: Intact Continental Shelf cables (Emerald green)
    p1 = ease_out_cubic(prog(t_local, 0.15, 0.9))
    if p1 > 0:
        for sx in (210, 290, 370, 445):
            d.ellipse((sx - 9, 304, sx + 9, 322), fill=EMERALD + (int(255 * p1),), outline=IVORY + (int(220 * p1),), width=2)
        d.rounded_rectangle((155, 190, 520, 282), radius=10, fill=(10, 32, 28, int(235 * p1)), outline=EMERALD + (int(210 * p1),), width=2)
        d.text((175, 204), "CONTINENTAL SHELF (<200 m)", font=get_font("mono_bold", 16), fill=EMERALD)
        d.text((175, 236), "ALL CABLES 100% INTACT (0 BREAKS)", font=get_font("sans_bold", 19), fill=IVORY)

    # Zone 2: Steep Continental Slope Cables A-F snapping simultaneously at 20:32-20:33 UTC!
    p2 = ease_out_cubic(prog(t_local, 2.3, 0.8))
    if p2 > 0:
        slope_pts = [(650, 400, "A"), (725, 448, "B"), (800, 495, "C"),
                     (875, 540, "D"), (950, 582, "E"), (1025, 622, "F")]
        for sx, sy, cid in slope_pts:
            r = 12 + 4 * math.sin(t_local * 6.0)
            d.ellipse((sx - r, sy - r, sx + r, sy + r), outline=CRIMSON + (int(230 * p2),), width=2)
            d.ellipse((sx - 8, sy - 8, sx + 8, sy + 8), fill=CRIMSON + (int(255 * p2),))
            d.text((sx - 6, sy - 30), cid, font=get_font("mono_bold", 16), fill=AMBER)

        d.rounded_rectangle((685, 268, 1345, 396), radius=12, fill=(32, 12, 18, int(238 * p2)), outline=CRIMSON + (int(220 * p2),), width=2)
        d.text((712, 286), "EPICENTRAL CONTINENTAL SLOPE (150–1,800 FATHOMS)", font=get_font("mono_bold", 17), fill=CRIMSON)
        d.text((712, 318), "Cables A–F Severed Simultaneously at T + 00:00", font=get_font("sans_bold", 23), fill=IVORY)
        d.text((712, 354), "Cause: Direct earthquake shaking & immediate local slumps", font=get_font("sans_reg", 18), fill=MUTED)

    return Image.alpha_composite(im, ov)


def scene_s10(plate_dir, shot, t_local, t_global):
    """S10: Centerpiece Data Scene — Heezen & Ewing (1952) Table 1 Downslope Sequence (G to L)."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "HEEZEN & EWING (1952) · TABLE 1", t_local)

    # Left: North-to-South Canyon & Abyssal Map
    lx0, ly0, lx1, ly1 = 84, 110, 880, 875
    draw_panel(d, (lx0, ly0, lx1, ly1))
    _draw_atlantic_coast_poly(d, lx0, ly0, lx1 - lx0, ly1 - ly0)

    # Exact 6 delayed cables from Table 1 (Heezen & Ewing 1952, p. 853)
    # Trigger fractions spaced across shot duration (~16s) to match spoken timestamps!
    dur = shot["duration"]
    rows = [
        ("G", "French Cable · Cape Cod–St. Pierre", "44°20'N", "1,150 fm", "+00h 14m", 0.18, 0.44),
        ("H", "Imperial · Halifax–Fayal", "43°37'N", "2,200 fm", "+00h 59m", 0.27, 0.52),
        ("I", "French Cable · Cape Cod–Brest", "42°05'N", "2,500 fm", "+03h 03m", 0.37, 0.63),
        ("J", "French Cable · New York–Fayal", "40°30'N", "2,900 fm", "+09h 01m", 0.48, 0.74),
        ("K", "Western Union · NY–Bay Roberts #2", "40°00'N", "3,190 fm", "+10h 18m", 0.58, 0.81),
        ("L", "Western Union · NY–Horta #1", "39°29'N", "2,800 fm", "+13h 17m", 0.68, 0.90),
    ]

    # Right: Table 1 Ledger
    rx0, ry0, rx1, ry1 = 915, 110, 1836, 875
    draw_panel(d, (rx0, ry0, rx1, ry1))
    d.text((rx0 + 30, ry0 + 24), "DOWNSLOPE CABLE RUPTURE SEQUENCE (NORTH -> SOUTH)", font=get_font("mono_bold", 18), fill=AMBER)
    d.text((rx0 + 30, ry0 + 54), "Source: Doxsee (1948) / Heezen & Ewing (1952), Table 1", font=get_font("mono_reg", 15), fill=DIM)

    # Flowing amber turbidity plume down the Laurentian channel on map
    front_y_frac = 0.39
    for cid, name, lat, depth, dt_str, trig_f, map_yf in rows:
        if t_local >= trig_f * dur:
            front_y_frac = map_yf

    ep_x, ep_y = lx0 + (lx1 - lx0) * 0.53, ly0 + (ly1 - ly0) * 0.39
    plume_y = ly0 + (ly1 - ly0) * front_y_frac
    if plume_y > ep_y + 4:
        # Expanding fan polygon representing 150-mile-wide turbidity flow
        spread = (plume_y - ep_y) * 0.38
        fan = [(ep_x - 22, ep_y), (ep_x + 22, ep_y),
               (ep_x + spread + 35, plume_y), (ep_x - spread - 15, plume_y)]
        d.polygon(fan, fill=(234, 168, 68, 62), outline=(234, 168, 68, 175))

    for i, (cid, name, lat, depth, dt_str, trig_f, map_yf) in enumerate(rows):
        active = t_local >= trig_f * dur
        my_line = int(ly0 + (ly1 - ly0) * map_yf)
        # Cable line across map
        c_col = CRIMSON + (235,) if active else (88, 204, 222, 110)
        d.line((lx0 + 45, my_line, lx1 - 45, my_line), fill=c_col, width=3 if active else 2)
        if active:
            d.ellipse((ep_x - 7, my_line - 7, ep_x + 7, my_line + 7), fill=CRIMSON + (255,), outline=IVORY)
            d.text((lx0 + 54, my_line - 22), f"CABLE {cid} ({dt_str})", font=get_font("mono_bold", 14), fill=IVORY)

        # Right table row (spaced cleanly with generous breathing margin above bottom banner)
        ty = ry0 + 90 + i * 94
        bg_c = (34, 16, 22, 235) if active else (14, 27, 45, 185)
        bd_c = CRIMSON + (215,) if active else (52, 84, 116, 120)
        d.rounded_rectangle((rx0 + 26, ty, rx1 - 26, ty + 82), radius=10, fill=bg_c, outline=bd_c, width=2)
        d.text((rx0 + 44, ty + 12), f"CABLE {cid}  ·  {name}", font=get_font("sans_bold", 19), fill=IVORY if active else MUTED)
        d.text((rx0 + 44, ty + 45), f"LAT: {lat}   ·   DEPTH: {depth}", font=get_font("mono_reg", 16), fill=CYAN if active else DIM)
        d.text((rx1 - 215, ty + 22), dt_str, font=get_font("mono_bold", 26), fill=AMBER if active else DIM)

    # Bottom note on 200 miles buried
    if t_local >= 0.72 * dur:
        d.rounded_rectangle((rx0 + 26, ry1 - 68, rx1 - 26, ry1 - 18), radius=8, fill=(44, 28, 12, 235), outline=AMBER, width=2)
        text_centered(d, (rx0 + rx1) // 2, ry1 - 54,
                      "CABLE L (~5,100 m): 200 MILES OF ARMORED WIRE BURIED UNDER SAND",
                      get_font("mono_bold", 17), fill=AMBER)

    return Image.alpha_composite(im, ov)


def scene_s11(plate_dir, shot, t_local, t_global):
    """S11: Hypothesis #1 Refuted — J.W. Gregory (Nature, 1929) Parallel Rift Faults vs Seismographs."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "HYPOTHESIS #1 · J. W. GREGORY (1929)", t_local)

    # Left card: Gregory's Claim
    lx0, ly0, lx1, ly1 = 84, 115, 920, 868
    draw_panel(d, (lx0, ly0, lx1, ly1))
    d.text((lx0 + 34, ly0 + 28), "PROPOSED IN NATURE (DEC 21, 1929)", font=get_font("mono_bold", 18), fill=AMBER)
    d.text((lx0 + 34, ly0 + 64), "Progressive Seafloor Faulting", font=get_font("disp_bold", 34), fill=IVORY)
    d.text((lx0 + 34, ly0 + 114), "Claim: Two parallel faults unzipped 360 nmi south,", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((lx0 + 34, ly0 + 144), "dropping the Cabot Trench floor cable by cable.", font=get_font("sans_reg", 20), fill=MUTED)

    # Diagram of twin unzipping fault lines
    d.rounded_rectangle((lx0 + 48, 315, lx1 - 48, 760), radius=12, fill=(9, 18, 31, 230), outline=(58, 92, 126, 150))
    for fx in (lx0 + 245, lx1 - 245):
        d.line((fx, 355, fx + 45, 720), fill=AMBER + (210,), width=4)
    for row_y in range(390, 710, 62):
        d.line((lx0 + 110, row_y, lx1 - 110, row_y), fill=(110, 145, 178, 140), width=2)
        d.text((lx0 + 345, row_y - 22), "FAULT DROP?", font=get_font("mono_bold", 15), fill=AMBER)

    # Right card: Seismograph Refutation
    rx0, ry0, rx1, ry1 = 960, 115, 1836, 868
    draw_panel(d, (rx0, ry0, rx1, ry1))
    d.text((rx0 + 34, ry0 + 28), "GLOBAL SEISMOGRAPH RECORD (1929)", font=get_font("mono_bold", 18), fill=CYAN)
    d.text((rx0 + 34, ry0 + 64), "Why Seismology Ruled It Out", font=get_font("disp_bold", 34), fill=IVORY)

    # Draw 14-hour seismogram timeline showing mainshock at 20:32, tiny aftershocks at 23:01 & 02:01
    gx0, gx1, gy = rx0 + 48, rx1 - 48, 420
    d.rounded_rectangle((gx0 - 14, 300, gx1 + 14, 560), radius=10, fill=(8, 16, 28, 240), outline=(64, 108, 148, 160))
    pts = []
    for s in range(180):
        u = s / 179.0
        x = gx0 + u * (gx1 - gx0)
        amp = 2.0 * math.sin(s * 1.9)
        if abs(u - 0.05) < 0.03:
            amp = 82.0 * math.sin(s * 5.0) * math.exp(-abs(u - 0.05) * 45)
        elif abs(u - 0.22) < 0.02 or abs(u - 0.42) < 0.02:
            amp = 22.0 * math.sin(s * 5.0)
        pts.append((x, gy + amp))
    d.line(pts, fill=CYAN + (235,), width=2)
    d.text((gx0 + 8, 314), "20:32 MAINSHOCK", font=get_font("mono_bold", 14), fill=AMBER)
    d.text((gx0 + 135, 522), "ONLY 2 AFTERSHOCKS (BOTH AT ORIGINAL 44.5°N EPICENTER)", font=get_font("mono_bold", 15), fill=CYAN)

    # Verdict stamp at t_local > 5.0s
    vp = ease_out_cubic(prog(t_local, 4.6, 0.6))
    if vp > 0:
        d.rounded_rectangle((rx0 + 48, 605, rx1 - 48, 815), radius=12,
                            fill=(38, 12, 18, int(240 * vp)), outline=CRIMSON + (int(240 * vp),), width=3)
        d.text((rx0 + 76, 628), "VERDICT: REFUTED", font=get_font("disp_black", 36), fill=CRIMSON + (int(255 * vp),))
        d.text((rx0 + 76, 684), "• Six giant southern fault ruptures would trigger", font=get_font("sans_reg", 20), fill=IVORY)
        d.text((rx0 + 76, 716), "  six new earthquakes. Zero occurred at break times.", font=get_font("sans_reg", 20), fill=IVORY)
        d.text((rx0 + 76, 756), "• Aftershocks stayed 300 miles north of Cable L.", font=get_font("sans_reg", 20), fill=MUTED)

    return Image.alpha_composite(im, ov)


def scene_s12(plate_dir, shot, t_local, t_global):
    """S12: Hypotheses #2 & #3 Refuted — Silt Sagging (1930) & Surface Tsunami Speed Mismatch (1940)."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "WAVE SPEED MISMATCH · 1930–1951", t_local)
    bx0, by0, bx1, by1 = 84, 112, 1836, 872
    draw_panel(d, (bx0, by0, bx1, by1))

    d.text((bx0 + 42, by0 + 32), "WHY THE TSUNAMI HYPOTHESIS FAILED (BUCHER 1940 / KUENEN 1950)",
           font=get_font("mono_bold", 20), fill=AMBER)
    d.text((bx0 + 42, by0 + 70), "Tenfold Velocity Mismatch Across 500 Kilometers",
           font=get_font("disp_bold", 36), fill=IVORY)

    # Race comparison bars across 540 km
    bar_x0, bar_x1 = bx0 + 60, bx1 - 90
    bw = bar_x1 - bar_x0

    # Track 1: Surface Tsunami (~550 km/h in deep water -> finishes 540 km in ~59 min!)
    u_tsunami = clamp((t_local - 0.5) / 1.4)
    d.rounded_rectangle((bar_x0, 260, bar_x1, 415), radius=12, fill=(10, 24, 42, 230), outline=CYAN + (160,), width=2)
    d.text((bar_x0 + 26, 280), "SURFACE TSUNAMI WAVE (v ≈ 550–700 km/h in deep ocean)", font=get_font("sans_bold", 22), fill=CYAN)
    d.rounded_rectangle((bar_x0 + 26, 332, bar_x0 + 26 + int((bw - 52) * u_tsunami), 386), radius=8, fill=CYAN + (225,))
    d.text((bar_x1 - 310, 280), "CROSSES ZONE IN ~1 HOUR", font=get_font("mono_bold", 18), fill=IVORY)

    # Track 2: Actual 1929 Cable Break Wavefront (takes 13h 17m -> 10x slower!)
    u_cables = clamp((t_local - 0.5) / 14.0)
    d.rounded_rectangle((bar_x0, 465, bar_x1, 620), radius=12, fill=(24, 15, 22, 230), outline=CRIMSON + (190,), width=2)
    d.text((bar_x0 + 26, 485), "ACTUAL 1929 CABLE-BREAK FRONT (67–93 km/h peak, slowing to 22 km/h)",
           font=get_font("sans_bold", 22), fill=AMBER)
    d.rounded_rectangle((bar_x0 + 26, 537, bar_x0 + 26 + int((bw - 52) * max(0.06, u_cables)), 591), radius=8, fill=CRIMSON + (235,))
    d.text((bar_x1 - 365, 485), "TAKES 13 HOURS 17 MINUTES", font=get_font("mono_bold", 18), fill=CRIMSON)

    # Cold-case conclusion box
    p = ease_out_cubic(prog(t_local, 3.2, 0.8))
    if p > 0:
        d.rounded_rectangle((bar_x0, 668, bar_x1, 825), radius=12,
                            fill=(15, 28, 46, int(235 * p)), outline=AMBER + (int(190 * p),), width=2)
        d.text((bar_x0 + 30, 692), "23-YEAR SCIENTIFIC DEADLOCK (1929–1952)", font=get_font("mono_bold", 19), fill=AMBER)
        d.text((bar_x0 + 30, 730), "Faults were too static. Seismic waves and tsunamis were far too fast.",
               font=get_font("sans_semi", 23), fill=IVORY)
        d.text((bar_x0 + 30, 770), "What physical object travels 500 km across a 0.05% abyssal slope at highway speed?",
               font=get_font("sans_reg", 21), fill=CYAN)

    return Image.alpha_composite(im, ov)

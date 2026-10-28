#!/usr/bin/env python3
"""
Scene choreography for Shots S13 through S24 (Acts V, VI, VII).
All stage elements stay strictly inside x=[72..1848], y=[88..905].
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from visual_primitives import (
    W, H, IVORY, MUTED, DIM, AMBER, CRIMSON, CYAN, EMERALD,
    BASE_TECH_CANVAS,
    get_font, clamp, ease_out_cubic, ease_in_out_cubic, prog,
    render_ken_burns_plate, draw_particles, draw_panel, draw_top_hud, text_centered,
)


def scene_s13(plate_dir, shot, t_local, t_global):
    """S13: Philip Kuenen's Groningen Flume Tank + Gravity Density Physics Card."""
    frac = clamp(t_local / shot["duration"])
    bg = render_ken_burns_plate(plate_dir, shot["plate"], frac, zoom_start=1.01, zoom_end=1.085, pan_x=(-16, 16), darken=0.80)
    im = Image.fromarray(bg).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "GRONINGEN LAB · KUENEN (1937–1950)", t_local)

    a = ease_out_cubic(prog(t_local, 0.35, 0.8))
    px0, py0, px1, py1 = 1090, 130, 1836, 545
    d.rounded_rectangle((px0, py0, px1, py1), radius=14,
                        fill=(8, 18, 32, int(232 * a)), outline=(AMBER[0], AMBER[1], AMBER[2], int(195 * a)), width=2)
    d.text((px0 + 30, py0 + 26), "FLUME TANK PHYSICS · DENSITY CURRENT", font=get_font("mono_bold", 17), fill=AMBER)
    d.text((px0 + 30, py0 + 62), "Why Muddy Water Sinks & Accelerates", font=get_font("disp_bold", 28), fill=IVORY)

    d.rounded_rectangle((px0 + 30, py0 + 118, px1 - 30, py0 + 210), radius=10, fill=(14, 30, 52, int(225 * a)), outline=CYAN + (150,))
    d.text((px0 + 48, py0 + 132), "Clear Seawater Density:", font=get_font("sans_reg", 19), fill=MUTED)
    d.text((px1 - 245, py0 + 130), "1.028 g/cm³", font=get_font("mono_bold", 22), fill=CYAN)
    d.text((px0 + 48, py0 + 168), "Sediment Slurry Density:", font=get_font("sans_bold", 19), fill=IVORY)
    d.text((px1 - 245, py0 + 166), "1.10–1.20 g/cm³", font=get_font("mono_bold", 22), fill=AMBER)

    d.text((px0 + 30, py0 + 235), "Effective gravity pull along slope θ:", font=get_font("sans_reg", 19), fill=MUTED)
    d.text((px0 + 30, py0 + 272), "g' = g · (ρ_flow − ρ_water) / ρ_water · sin(θ)",
           font=get_font("mono_bold", 20), fill=EMERALD)
    d.text((px0 + 30, py0 + 322), "Reginald Daly (1936) · Philip H. Kuenen (1937, 1950)",
           font=get_font("mono_reg", 15), fill=DIM)

    return Image.alpha_composite(im, ov)


def scene_s14(plate_dir, shot, t_local, t_global):
    """S14: Lamont Geological Observatory (Dec 1952) — Heezen & Ewing Reopen the 1929 Logs."""
    frac = clamp(t_local / shot["duration"])
    bg = render_ken_burns_plate(plate_dir, shot["plate"], frac, zoom_start=1.02, zoom_end=1.08, pan_x=(14, -12), darken=0.78)
    im = Image.fromarray(bg).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "COLUMBIA UNIVERSITY · DECEMBER 1952", t_local)

    a = ease_out_cubic(prog(t_local, 0.35, 0.8))
    bx0, by0, bx1, by1 = 84, 590, 965, 868
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=14,
                        fill=(9, 18, 32, int(236 * a)), outline=(CYAN[0], CYAN[1], CYAN[2], int(195 * a)), width=2)
    d.text((bx0 + 30, by0 + 24), "LAMONT GEOLOGICAL OBSERVATORY CONTRIBUTION NO. 65",
           font=get_font("mono_bold", 16), fill=CYAN)
    d.text((bx0 + 30, by0 + 58), "Bruce C. Heezen & Maurice Ewing (1952)",
           font=get_font("serif_bold", 34), fill=IVORY)
    d.text((bx0 + 30, by0 + 108), "\"Turbidity Currents and Submarine Slumps, and the 1929 Grand Banks Earthquake\"",
           font=get_font("serif_italic", 21), fill=AMBER)
    d.text((bx0 + 30, by0 + 150), "Published in American Journal of Science, Vol. 250, pp. 849–873",
           font=get_font("sans_reg", 19), fill=MUTED)
    d.text((bx0 + 30, by0 + 190), "Key insight: Treat the 12 severed telegraph cables as a seafloor stopwatch.",
           font=get_font("sans_semi", 19), fill=EMERALD)

    return Image.alpha_composite(im, ov)


def scene_s15(plate_dir, shot, t_local, t_global):
    """S15: Cross-Dissolve Slump (plate_05) -> Towering Turbidity Head (plate_07) + Autosuspension Loop."""
    dur = shot["duration"]
    frac = clamp(t_local / dur)
    bg1 = render_ken_burns_plate(plate_dir, shot["plate"], frac, zoom_start=1.01, zoom_end=1.08, pan_y=(-8, 12), darken=0.82)
    bg2 = render_ken_burns_plate(plate_dir, shot["plate_secondary"], frac, zoom_start=1.02, zoom_end=1.09, pan_x=(-18, 14), darken=0.80)

    blend = ease_in_out_cubic(prog(t_local, dur * 0.42, 1.4))
    comp_arr = (bg1.astype(np.float32) * (1.0 - blend) + bg2.astype(np.float32) * blend).astype(np.uint8)
    im = Image.fromarray(comp_arr).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_particles(d, t_global, tint=(234, 185, 110))
    draw_top_hud(d, shot["act"], "200 km³ SUBMARINE AVALANCHE", t_local)

    # Bottom 4-step autosuspension chain
    steps = [
        ("1. SLOPE SLUMP", "200 km³ mud shakes loose"),
        ("2. WATER MIXING", "Forms dense turbulent plume"),
        ("3. CANYON SCOUR", "Erodes floor, adding mass"),
        ("4. ABYSSAL SURGE", "Hundreds of meters tall"),
    ]
    for i, (st_title, st_sub) in enumerate(steps):
        p = ease_out_cubic(prog(t_local, 0.3 + i * 1.4, 0.7))
        if p <= 0:
            continue
        sx0 = 84 + i * 444
        sy0 = 735
        d.rounded_rectangle((sx0, sy0, sx0 + 420, sy0 + 130), radius=12,
                            fill=(8, 17, 30, int(232 * p)),
                            outline=(AMBER[0], AMBER[1], AMBER[2], int(205 * p)), width=2)
        d.text((sx0 + 22, sy0 + 20), st_title, font=get_font("mono_bold", 18), fill=AMBER)
        d.text((sx0 + 22, sy0 + 58), st_sub, font=get_font("sans_semi", 20), fill=IVORY)

    return Image.alpha_composite(im, ov)


def scene_s16(plate_dir, shot, t_local, t_global):
    """S16: Animated Heezen & Ewing (1952) Fig. 2/3 Velocity Curve + Piper et al. (1988) Refinement."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "SPEEDOMETER ON THE SEAFLOOR", t_local)
    bx0, by0, bx1, by1 = 84, 110, 1836, 875
    draw_panel(d, (bx0, by0, bx1, by1))

    d.text((bx0 + 40, by0 + 26), "FLOW VELOCITY vs. DISTANCE DOWNSLOPE (1929 GRAND BANKS EVENT)",
           font=get_font("mono_bold", 20), fill=CYAN)
    d.text((bx0 + 40, by0 + 58), "Comparing Heezen & Ewing (1952) tangent estimate with Piper, Shor & Hughes Clarke (1988) reanalysis",
           font=get_font("sans_reg", 19), fill=MUTED)

    # Plot axes: x = 0..320 nautical miles (gx0..gx1), y = 0..100 km/h (gy1..gy0)
    gx0, gy0, gx1, gy1 = 210, 215, 1340, 775
    gw, gh = gx1 - gx0, gy1 - gy0

    # Gridlines
    for v_kmh in (0, 25, 50, 75, 100):
        yy = gy1 - int((v_kmh / 100.0) * gh)
        d.line((gx0, yy, gx1, yy), fill=(55, 88, 122, 110), width=1)
        d.text((gx0 - 95, yy - 11), f"{v_kmh:3d} km/h", font=get_font("mono_reg", 16), fill=MUTED)

    for dist_nm in (0, 80, 160, 240, 320):
        xx = gx0 + int((dist_nm / 320.0) * gw)
        d.line((xx, gy0, xx, gy1), fill=(55, 88, 122, 90), width=1)
        d.text((xx - 28, gy1 + 16), f"{dist_nm} nmi", font=get_font("mono_reg", 16), fill=MUTED)

    d.line((gx0, gy0, gx0, gy1), fill=IVORY + (210,), width=2)
    d.line((gx0, gy1, gx1, gy1), fill=IVORY + (210,), width=2)
    text_centered(d, (gx0 + gx1) // 2, gy1 + 48, "DISTANCE DOWNSLOPE SOUTH OF CABLE H (NAUTICAL MILES)",
                  get_font("mono_bold", 15), fill=CYAN)

    # Curve 1: Heezen & Ewing (1952) — ~50 knots (92.6 km/h) -> 40 kt -> 15 kt -> 12 kt (22.2 km/h)
    he_data = [(0, 92.6, "H (+0:59)"), (105, 74.0, "I (+3:03)"), (235, 34.0, "J (+9:01)"),
               (255, 27.8, "K (+10:18)"), (292, 22.2, "L (+13:17)")]
    p_he = ease_out_cubic(prog(t_local, 0.4, 2.8))
    if p_he > 0:
        he_pts = []
        for nm, kmh, _ in he_data:
            he_pts.append((gx0 + (nm / 320.0) * gw, gy1 - (kmh / 100.0) * gh))
        # Interpolate smooth polyline
        dense = []
        for idx in range(len(he_pts) - 1):
            for sub in range(20):
                u = sub / 20.0
                dense.append((he_pts[idx][0] * (1 - u) + he_pts[idx + 1][0] * u,
                              he_pts[idx][1] * (1 - u) + he_pts[idx + 1][1] * u))
        dense.append(he_pts[-1])
        cut = max(2, int(len(dense) * p_he))
        d.line(dense[:cut], fill=AMBER + (245,), width=5)
        for idx_pt, ((px, py), (_, kmh, lbl)) in enumerate(zip(he_pts, he_data)):
            if px <= dense[cut - 1][0] + 4:
                d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=AMBER, outline=IVORY, width=2)
                off_y = -32 if idx_pt != 3 else 14
                d.text((px - 10, py + off_y), lbl, font=get_font("mono_bold", 14), fill=AMBER)

    # Curve 2: Piper, Shor & Hughes Clarke (1988) refined maximum (~67 km/h = 18.6 m/s)
    p_pi = ease_out_cubic(prog(t_local, 4.8, 2.2))
    if p_pi > 0:
        pi_data = [(0, 67.0), (105, 58.0), (235, 33.0), (255, 27.0), (292, 22.0)]
        pi_pts = [(gx0 + (nm / 320.0) * gw, gy1 - (kmh / 100.0) * gh) for nm, kmh in pi_data]
        cut2 = max(2, int(len(pi_pts) * p_pi))
        d.line(pi_pts[:cut2], fill=CYAN + (245,), width=4)
        for px, py in pi_pts[:cut2]:
            d.ellipse((px - 6, py - 6, px + 6, py + 6), fill=CYAN, outline=IVORY, width=2)

    # Right legend & summary cards
    rx = 1385
    d.rounded_rectangle((rx, 225, 1795, 455), radius=12, fill=(28, 20, 12, 235), outline=AMBER, width=2)
    d.text((rx + 24, 248), "1952 ESTIMATE (HEEZEN & EWING)", font=get_font("mono_bold", 15), fill=AMBER)
    d.text((rx + 24, 286), "~50 kt (93 km/h)", font=get_font("disp_black", 42), fill=IVORY)
    d.text((rx + 24, 348), "Slowing to 12 kt (22 km/h)", font=get_font("sans_reg", 19), fill=MUTED)
    d.text((rx + 24, 378), "across 0.05% abyssal floor", font=get_font("sans_reg", 19), fill=MUTED)

    if p_pi > 0.1:
        d.rounded_rectangle((rx, 495, 1795, 745), radius=12, fill=(10, 28, 42, int(235 * p_pi)), outline=CYAN, width=2)
        d.text((rx + 24, 518), "1988 REANALYSIS (PIPER ET AL.)", font=get_font("mono_bold", 15), fill=CYAN)
        d.text((rx + 24, 556), "67 km/h (19 m/s)", font=get_font("disp_black", 42), fill=CYAN)
        d.text((rx + 24, 618), "Refined canyon routing—still", font=get_font("sans_reg", 19), fill=IVORY)
        d.text((rx + 24, 648), "highway speed in total darkness", font=get_font("sans_semi", 19), fill=EMERALD)

    return Image.alpha_composite(im, ov)


def scene_s17(plate_dir, shot, t_local, t_global):
    """S17: Lamont Research Ship Coring at Night + Testable Scientific Prediction."""
    frac = clamp(t_local / shot["duration"])
    bg = render_ken_burns_plate(plate_dir, shot["plate"], frac, zoom_start=1.01, zoom_end=1.08, pan_y=(12, -10), darken=0.80)
    im = Image.fromarray(bg).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "SOHM ABYSSAL PLAIN · TESTABLE PREDICTION", t_local)

    a = ease_out_cubic(prog(t_local, 0.3, 0.8))
    bx0, by0, bx1, by1 = 1045, 515, 1836, 855
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=14,
                        fill=(8, 17, 30, int(232 * a)), outline=(EMERALD[0], EMERALD[1], EMERALD[2], int(200 * a)), width=2)
    d.text((bx0 + 28, by0 + 24), "THE FALSIFIABLE PREDICTION (1952)", font=get_font("mono_bold", 17), fill=EMERALD)
    d.text((bx0 + 28, by0 + 62), "What Had to Lie South of Cable L?", font=get_font("disp_bold", 30), fill=IVORY)
    d.text((bx0 + 28, by0 + 114), "If the current passed Cable L at 12 knots, millions of tons", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((bx0 + 28, by0 + 144), "of coastal sand had to settle farther south across the", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((bx0 + 28, by0 + 174), "flat Sohm Abyssal Plain (~5,000 meters deep).", font=get_font("sans_semi", 20), fill=AMBER)
    d.text((bx0 + 28, by0 + 228), "Target: 36°N–39°N, 52°W–56°W · >400 miles offshore",
           font=get_font("mono_reg", 15), fill=CYAN)

    return Image.alpha_composite(im, ov)


def scene_s18(plate_dir, shot, t_local, t_global):
    """S18: Animated 5,000m Piston Corer Descent & Graded Turbidite Bed Stratigraphy."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "PISTON CORE VERIFICATION · 1952–1954", t_local)

    # Left panel: Piston Corer plunging 5,000m into seabed
    lx0, ly0, lx1, ly1 = 84, 112, 680, 872
    draw_panel(d, (lx0, ly0, lx1, ly1))
    d.text((lx0 + 30, ly0 + 26), "PISTON CORER (~5,100 m)", font=get_font("mono_bold", 19), fill=CYAN)

    cx = (lx0 + lx1) // 2
    drop = ease_out_cubic(prog(t_local, 0.2, 2.2))
    seabed_y = 665
    d.rectangle((lx0 + 28, seabed_y, lx1 - 28, ly1 - 28), fill=(52, 44, 36, 240))
    d.rectangle((lx0 + 28, seabed_y, lx1 - 28, seabed_y + 62), fill=(198, 156, 86, 225))
    d.line((lx0 + 28, seabed_y, lx1 - 28, seabed_y), fill=AMBER, width=2)

    corer_bot = int(260 + (seabed_y + 125 - 260) * drop)
    corer_top = corer_bot - 190
    # Winch cable
    d.line((cx, ly0 + 75, cx, corer_top), fill=MUTED + (220,), width=3)
    # Lead weight head + steel barrel
    d.rounded_rectangle((cx - 32, corer_top, cx + 32, corer_top + 48), radius=6, fill=(135, 152, 170, 250), outline=IVORY)
    d.rectangle((cx - 14, corer_top + 48, cx + 14, corer_bot), fill=(185, 200, 215, 250), outline=CYAN, width=2)
    d.text((lx0 + 42, seabed_y - 32), "SOHM ABYSSAL PLAIN FLOOR", font=get_font("mono_bold", 15), fill=AMBER)

    # Right panel: Magnified Graded Turbidite Core Column ("The Smoking Gun")
    rx0, ry0, rx1, ry1 = 720, 112, 1836, 872
    draw_panel(d, (rx0, ry0, rx1, ry1))
    d.text((rx0 + 36, ry0 + 26), "RECOVERED SEDIMENT CORE · GRADED TURBIDITE BED", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((rx0 + 36, ry0 + 58), "Heezen, Ericson & Ewing (1954), Deep-Sea Research", font=get_font("mono_reg", 15), fill=DIM)

    # Core cylinder column x = [785..1065], y = [205..815]
    col_x0, col_x1 = 785, 1065
    strata = [
        # (y0, y1, color, grain_count, grain_r, title, desc, accent)
        (205, 315, (148, 138, 122), 35, 1.5, "FINE SILT & MUD CAP", "Last fine particles to settle after current halted", MUTED),
        (315, 455, (186, 154, 98), 55, 3.0, "MEDIUM GRADED SAND", "Sorted upward from coarse to fine by settling speed", CYAN),
        (455, 625, (218, 168, 82), 75, 5.5, "COARSE SAND, PEBBLES & SHELLS",
         "Shallow-water Foraminifera carried 400+ miles!", AMBER),
        (625, 815, (74, 82, 94), 18, 1.2, "ANCIENT ABYSSAL PELAGIC CLAY",
         "Pre-1929 deep-sea floor beneath sharp erosional base", EMERALD),
    ]
    rng = np.random.default_rng(1954)
    p_rev = ease_out_cubic(prog(t_local, 1.6, 1.8))

    for idx, (sy0, sy1, rgb, g_cnt, g_r, title, desc, acc) in enumerate(strata):
        d.rectangle((col_x0, sy0, col_x1, sy1), fill=rgb + (245,), outline=IVORY + (160,), width=1)
        for _ in range(g_cnt):
            gx = rng.uniform(col_x0 + 12, col_x1 - 12)
            gy = rng.uniform(sy0 + 8, sy1 - 8)
            d.ellipse((gx - g_r, gy - g_r, gx + g_r, gy + g_r), fill=(248, 232, 195, 185))

        if p_rev > 0:
            mid_y = (sy0 + sy1) // 2
            d.line((col_x1 + 12, mid_y, 1125, mid_y), fill=acc + (int(235 * p_rev),), width=3)
            d.rounded_rectangle((1125, sy0 + 8, rx1 - 36, sy1 - 8), radius=10,
                                fill=(12, 24, 42, int(230 * p_rev)), outline=acc + (int(190 * p_rev),), width=2)
            d.text((1148, sy0 + 18), title, font=get_font("mono_bold", 17), fill=acc)
            d.text((1148, sy0 + 48), desc, font=get_font("sans_reg", 18), fill=IVORY)

    # Sharp 1929 erosional contact highlight line at y=625
    d.line((col_x0 - 16, 625, col_x1 + 16, 625), fill=CRIMSON, width=4)

    return Image.alpha_composite(im, ov)


def scene_s19(plate_dir, shot, t_local, t_global):
    """S19: Procedural 3D-Style Physiographic Panorama — Marie Tharp & Bruce Heezen's Living Seafloor."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "THARP & HEEZEN · FLOORS OF THE OCEANS (1957–1959)", t_local)
    bx0, by0, bx1, by1 = 84, 112, 1836, 872
    draw_panel(d, (bx0, by0, bx1, by1))

    d.text((bx0 + 40, by0 + 28), "PHYSIOGRAPHIC DIAGRAM OF THE NORTH ATLANTIC", font=get_font("mono_bold", 19), fill=AMBER)
    d.text((bx0 + 40, by0 + 62), "Marie Tharp & Bruce Heezen's New Vision of the Abyss", font=get_font("serif_bold", 36), fill=IVORY)

    # Stacked joy-plot / physiographic sonar horizon profiles showing Shelf -> Canyons -> Flat Abyssal Plain -> Mid-Atlantic Rift
    reveal = ease_out_cubic(prog(t_local, 0.1, 2.5))
    n_ridges = 18
    for r in range(n_ridges):
        rf = r / (n_ridges - 1)
        base_y = 265 + rf * 525
        pts = []
        max_x_idx = max(2, int(140 * reveal))
        for xi in range(max_x_idx):
            u = xi / 139.0
            x = 135 + u * 1650
            # Left: Continental shelf + incised submarine canyons
            if u < 0.18:
                canyon = 36.0 * math.exp(-((u - (0.11 + 0.02 * math.sin(r))) / 0.022) ** 2)
                elev = -95.0 + u * 320.0 + canyon
            # Center-left: Ultra-flat Sohm Abyssal Plain (slope < 1:1000!)
            elif u < 0.56:
                elev = 12.0 + 2.5 * math.sin(u * 25.0 + r)
            # Center-right: Mid-Atlantic Ridge with central Rift Valley!
            elif u < 0.84:
                ridge_env = math.exp(-((u - 0.70) / 0.095) ** 2)
                rift_notch = 48.0 * math.exp(-((u - 0.70) / 0.018) ** 2)
                elev = 12.0 - 115.0 * ridge_env + rift_notch + 8.0 * math.sin(u * 60.0 + r * 1.7)
            else:
                elev = 10.0 - (u - 0.84) * 420.0
            pts.append((x, base_y + elev * 0.65))

        if len(pts) >= 2:
            poly = pts + [(pts[-1][0], base_y + 42), (pts[0][0], base_y + 42)]
            d.polygon(poly, fill=(10, 22, 38, 220))
            col = CYAN if 0.20 < rf < 0.85 else AMBER
            d.line(pts, fill=(col[0], col[1], col[2], 195), width=2)

    # Feature callout badges along bottom of panorama
    badges = [
        (165, "SUBMARINE CANYONS", "Carved by turbidity flows"),
        (640, "ABYSSAL PLAINS (<1:1000)", "Buried smooth by turbidites"),
        (1170, "MID-ATLANTIC RIFT VALLEY", "Mapped by Marie Tharp (1952–57)"),
    ]
    for bx, b_t, b_s in badges:
        d.rounded_rectangle((bx, 765, bx + 445, 848), radius=10, fill=(12, 24, 42, 238), outline=AMBER + (180,))
        d.text((bx + 20, 779), b_t, font=get_font("mono_bold", 16), fill=AMBER)
        d.text((bx + 20, 810), b_s, font=get_font("sans_reg", 18), fill=IVORY)

    return Image.alpha_composite(im, ov)


def scene_s20(plate_dir, shot, t_local, t_global):
    """S20: Modern Subsea Fiber-Optic Infrastructure (>1.8M km, >99% Global Data)."""
    frac = clamp(t_local / shot["duration"])
    bg = render_ken_burns_plate(plate_dir, shot["plate"], frac, zoom_start=1.01, zoom_end=1.085, pan_x=(-15, 15), darken=0.78)
    im = Image.fromarray(bg).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "GLOBAL SUBSEA NETWORK · 2026", t_local)

    cards = [
        ("1.8M+ km", "Submarine fiber-optic cable length", CYAN),
        ("> 99%", "Of all intercontinental internet traffic", AMBER),
        ("~20 mm", "Deep-sea diameter (garden-hose thin)", EMERALD),
    ]
    for i, (big, sub, col) in enumerate(cards):
        p = ease_out_cubic(prog(t_local, 0.25 + i * 0.7, 0.7))
        if p <= 0:
            continue
        cx0 = 84
        cy0 = 138 + i * 198
        d.rounded_rectangle((cx0, cy0, cx0 + 685, cy0 + 168), radius=14,
                            fill=(8, 17, 30, int(232 * p)), outline=col + (int(205 * p),), width=2)
        d.text((cx0 + 30, cy0 + 22), big, font=get_font("disp_black", 56), fill=col)
        d.text((cx0 + 30, cy0 + 102), sub, font=get_font("sans_semi", 21), fill=IVORY)

    d.text((88, 742), "Sources: International Cable Protection Committee (ICPC, Nov 2025) · UN News (Feb 2026)",
           font=get_font("mono_reg", 15), fill=MUTED)

    return Image.alpha_composite(im, ov)


def scene_s21(plate_dir, shot, t_local, t_global):
    """S21: Hunga Tonga–Hunga Ha'apai (15 Jan 2022) — 122 km/h Submarine Density Currents."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "15 JANUARY 2022 · HUNGA TONGA ERUPTION", t_local)

    # Left: Radial Caldera Bathymetry & Expanding Volcaniclastic Density Current
    lx0, ly0, lx1, ly1 = 84, 112, 1040, 872
    draw_panel(d, (lx0, ly0, lx1, ly1))
    d.text((lx0 + 30, ly0 + 24), "SUBMARINE CALDERA & DENSITY FLOW FOOTPRINT", font=get_font("mono_bold", 18), fill=CRIMSON)

    vcx, vcy = (lx0 + lx1) // 2, 515
    # Radial submarine gully scours (>100m deep)
    for ang_deg in range(0, 360, 30):
        ang = math.radians(ang_deg + 12)
        d.line((vcx + 32 * math.cos(ang), vcy + 32 * math.sin(ang),
                vcx + 325 * math.cos(ang), vcy + 325 * math.sin(ang)),
               fill=(92, 134, 172, 70), width=2)
    # Bathymetric contour rings
    for rad, lbl in [(85, "1,000m"), (165, "1,800m"), (250, "2,400m"), (330, "100+ km RUNOUT")]:
        d.ellipse((vcx - rad, vcy - rad, vcx + rad, vcy + rad), outline=(68, 114, 156, 120), width=2)
        d.text((vcx + rad * 0.68, vcy - rad * 0.68), lbl, font=get_font("mono_reg", 13), fill=DIM)

    # Expanding crimson-amber volcaniclastic flow front
    surge_p = ease_out_cubic(prog(t_local, 0.3, 3.6))
    r_flow = int(38 + 285 * surge_p)
    d.ellipse((vcx - r_flow, vcy - r_flow, vcx + r_flow, vcy + r_flow),
              fill=(228, 78, 64, 58), outline=CRIMSON + (235,), width=3)
    # Caldera vent
    d.ellipse((vcx - 28, vcy - 28, vcx + 28, vcy + 28), fill=AMBER + (245,), outline=IVORY, width=2)
    text_centered(d, vcx, vcy + 36, "HUNGA CALDERA", get_font("mono_bold", 15), fill=AMBER)

    # Two subsea cables crossing south/east of caldera + glowing rupture markers
    dom_y = vcy + 95
    int_y = vcy + 205
    d.line((lx0 + 60, dom_y, lx1 - 60, dom_y), fill=CRIMSON if r_flow >= 95 else CYAN, width=3)
    d.text((lx0 + 75, dom_y - 24), "DOMESTIC CABLE (CUT 04:30)", font=get_font("mono_bold", 15), fill=IVORY)
    if r_flow >= 95:
        dx_hit = int(math.sqrt(max(0, r_flow * r_flow - 95 * 95)))
        for sgn in (-1, 1):
            d.ellipse((vcx + sgn * dx_hit - 7, dom_y - 7, vcx + sgn * dx_hit + 7, dom_y + 7), fill=AMBER, outline=CRIMSON, width=2)

    d.line((lx0 + 60, int_y, lx1 - 60, int_y), fill=CRIMSON if r_flow >= 205 else CYAN, width=3)
    d.text((lx0 + 75, int_y - 24), "TONGA–FIJI INTERNATIONAL CABLE (CUT 05:44)", font=get_font("mono_bold", 15), fill=IVORY)
    if r_flow >= 205:
        ix_hit = int(math.sqrt(max(0, r_flow * r_flow - 205 * 205)))
        for sgn in (-1, 1):
            d.ellipse((vcx + sgn * ix_hit - 7, int_y - 7, vcx + sgn * ix_hit + 7, int_y + 7), fill=AMBER, outline=CRIMSON, width=2)

    # Right: Speedometer & Science (2023) findings
    rx0, ry0, rx1, ry1 = 1075, 112, 1836, 872
    draw_panel(d, (rx0, ry0, rx1, ry1))
    d.text((rx0 + 34, ry0 + 28), "FASTEST SEAFLOOR FLOWS RECORDED", font=get_font("mono_bold", 18), fill=AMBER)

    spd = int(round(122 * surge_p))
    d.text((rx0 + 34, ry0 + 88), f"{spd} km/h", font=get_font("disp_black", 92), fill=CRIMSON)
    d.text((rx0 + 34, ry0 + 202), "Peak speed (33.8 m/s · 76 mph)", font=get_font("sans_semi", 23), fill=IVORY)

    d.line((rx0 + 34, ry0 + 258, rx1 - 34, ry0 + 258), fill=(68, 114, 156, 130), width=1)
    facts = [
        ("Trigger:", "Collapsed volcanic eruption plume plunging directly into ocean"),
        ("Seabed Scour:", "Gouged channels >100 meters deep into volcanic slopes"),
        ("Primary Study:", "Clare et al., Science, Vol. 381 (Sept 7, 2023)"),
    ]
    for i, (fk, fv) in enumerate(facts):
        fy = ry0 + 288 + i * 145
        d.rounded_rectangle((rx0 + 34, fy, rx1 - 34, fy + 122), radius=10, fill=(14, 27, 46, 225), outline=(64, 104, 142, 150))
        d.text((rx0 + 54, fy + 16), fk, font=get_font("mono_bold", 17), fill=CYAN)
        # Wrap fv into 2 lines cleanly
        words = fv.split()
        mid = len(words) // 2 + 1
        d.text((rx0 + 54, fy + 48), " ".join(words[:mid]), font=get_font("sans_reg", 19), fill=IVORY)
        d.text((rx0 + 54, fy + 76), " ".join(words[mid:]), font=get_font("sans_reg", 19), fill=IVORY)

    return Image.alpha_composite(im, ov)


def scene_s22(plate_dir, shot, t_local, t_global):
    """S22: 1929 Grand Banks vs. 2022 Hunga Tonga — Twin Cable Stopwatch Comparison."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "93 YEARS APART · IDENTICAL SIGNATURE", t_local)

    # Left Card: 1929 Grand Banks
    lx0, ly0, lx1, ly1 = 84, 115, 935, 868
    draw_panel(d, (lx0, ly0, lx1, ly1))
    d.text((lx0 + 34, ly0 + 28), "18 NOVEMBER 1929 · NORTH ATLANTIC", font=get_font("mono_bold", 18), fill=AMBER)
    d.text((lx0 + 34, ly0 + 64), "Grand Banks Telegraph Array", font=get_font("disp_bold", 34), fill=IVORY)
    rows_l = [
        ("Trigger", "Mw 7.2 Slope Earthquake"),
        ("Stopwatch Span", "13 hours 17 minutes (6 delayed lines)"),
        ("Peak Flow Speed", "67–93 km/h across >600 km"),
        ("Cable Damage", "12 cables broken; ~200 mi buried"),
        ("Repair Window", "Nearly 1 year by cable ships"),
    ]
    for i, (k, v) in enumerate(rows_l):
        ry = ly0 + 145 + i * 114
        d.rounded_rectangle((lx0 + 34, ry, lx1 - 34, ry + 94), radius=10, fill=(14, 28, 46, 220), outline=AMBER + (140,))
        d.text((lx0 + 54, ry + 14), k.upper(), font=get_font("mono_bold", 15), fill=AMBER)
        d.text((lx0 + 54, ry + 44), v, font=get_font("sans_semi", 21), fill=IVORY)

    # Right Card: 2022 Hunga Tonga
    rx0, ry0, rx1, ry1 = 985, 115, 1836, 868
    draw_panel(d, (rx0, ry0, rx1, ry1))
    d.text((rx0 + 34, ry0 + 28), "15 JANUARY 2022 · SOUTH PACIFIC", font=get_font("mono_bold", 18), fill=CYAN)
    d.text((rx0 + 34, ry0 + 64), "Kingdom of Tonga Fiber Links", font=get_font("disp_bold", 34), fill=IVORY)
    rows_r = [
        ("Trigger", "VEI 5–6 Volcanic Plume Collapse"),
        ("Stopwatch Span", "04:30 Domestic -> 05:44 Int'l (+74 min)"),
        ("Peak Flow Speed", "Up to 122 km/h across >100 km"),
        ("Cable Damage", "194 km of subsea fiber wrecked/buried"),
        ("Human Impact", "Nation digitally isolated ~5 weeks"),
    ]
    for i, (k, v) in enumerate(rows_r):
        ry = ry0 + 145 + i * 114
        d.rounded_rectangle((rx0 + 34, ry, rx1 - 34, ry + 94), radius=10, fill=(14, 28, 46, 220), outline=CYAN + (160,))
        d.text((rx0 + 54, ry + 14), k.upper(), font=get_font("mono_bold", 15), fill=CYAN)
        d.text((rx0 + 54, ry + 44), v, font=get_font("sans_semi", 21), fill=IVORY)

    return Image.alpha_composite(im, ov)


def scene_s23(plate_dir, shot, t_local, t_global):
    """S23: Modern Subsea Cable Protection Blueprint — Multibeam Sonar & Canyon Detour."""
    im = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    draw_top_hud(d, shot["act"], "ENGINEERING AGAINST THE AVALANCHE", t_local)
    bx0, by0, bx1, by1 = 84, 112, 1836, 872
    draw_panel(d, (bx0, by0, bx1, by1))

    d.text((bx0 + 40, by0 + 28), "MODERN SUBSEA ROUTE ENGINEERING (ICPC BEST PRACTICE)", font=get_font("mono_bold", 19), fill=EMERALD)
    d.text((bx0 + 40, by0 + 62), "Designing Around Submarine Canyons", font=get_font("disp_bold", 34), fill=IVORY)

    # Top-down bathymetric canyon chute + scanning sonar beam
    mx0, my0, mx1, my1 = 135, 215, 1180, 825
    d.rounded_rectangle((mx0, my0, mx1, my1), radius=12, fill=(7, 16, 28, 245), outline=(64, 108, 148, 170))

    # Submarine canyon chute down center of map
    canyon_poly = [(540, my0 + 10), (690, my0 + 10), (775, my1 - 10), (465, my1 - 10)]
    d.polygon(canyon_poly, fill=(28, 18, 24, 220), outline=CRIMSON + (150,))
    text_centered(d, 620, 505, "UNSTABLE CANYON CHUTE", get_font("mono_bold", 16), fill=CRIMSON)

    # Old direct route (dashed red X)
    d.line((mx0 + 50, 560, mx1 - 50, 560), fill=CRIMSON + (170,), width=3)
    d.text((mx0 + 65, 528), "LEGACY DIRECT ROUTE (HIGH RISK)", font=get_font("mono_bold", 15), fill=CRIMSON)

    # Modern safe ridge detour route (animated green curve)
    p = ease_out_cubic(prog(t_local, 0.3, 2.2))
    detour = []
    for s in range(60):
        u = s / 59.0
        x = mx0 + 50 + u * (mx1 - mx0 - 100)
        y = 560 - 245 * math.sin(math.pi * u) ** 1.3
        detour.append((x, y))
    cut = max(2, int(len(detour) * p))
    d.line(detour[:cut], fill=EMERALD + (250,), width=5)
    d.text((mx0 + 310, 265), "MODERN REROUTED RIDGE PATH (SAFE)", font=get_font("mono_bold", 16), fill=EMERALD)

    # Scanning multibeam sonar swath
    scan_x = mx0 + 80 + ((t_local * 145.0) % (mx1 - mx0 - 160))
    d.polygon([(scan_x, my0 + 25), (scan_x - 85, my1 - 25), (scan_x + 85, my1 - 25)],
              fill=(88, 204, 222, 36), outline=(88, 204, 222, 120))

    # Right 3 engineering pillars
    pillars = [
        ("1. MULTIBEAM SONAR", "Map landslide scars & canyon thalwegs before laying"),
        ("2. SLOPE DETOURS", "Route cables along stable inter-canyon ridges"),
        ("3. PLOW BURIAL & ARMOR", "Trench cables 1–3 m deep on shelves & add redundant paths"),
    ]
    for i, (pt, ps) in enumerate(pillars):
        py = 225 + i * 198
        d.rounded_rectangle((1225, py, 1790, py + 165), radius=12, fill=(14, 28, 46, 230), outline=EMERALD + (175,), width=2)
        d.text((1250, py + 24), pt, font=get_font("mono_bold", 18), fill=EMERALD)
        words = ps.split()
        m = len(words) // 2 + 1
        d.text((1250, py + 66), " ".join(words[:m]), font=get_font("sans_reg", 20), fill=IVORY)
        d.text((1250, py + 98), " ".join(words[m:]), font=get_font("sans_reg", 20), fill=IVORY)

    return Image.alpha_composite(im, ov)


def scene_s24(plate_dir, shot, t_local, t_global):
    """S24: Coda — Pre-Dawn Ocean Horizon & Luminous Subsea Optical Web + Subtle End Card."""
    # Procedural pre-dawn indigo sky + warm amber horizon + deep Atlantic abyssal threads
    arr = np.zeros((H, W, 3), dtype=np.float32)
    horizon_y = 435
    # Sky gradient (deep indigo -> warm dawn amber band at horizon)
    sky_y = np.linspace(0.0, 1.0, horizon_y, dtype=np.float32)[:, None]
    arr[:horizon_y, :, 0] = 8 + 75 * (sky_y ** 3.2)
    arr[:horizon_y, :, 1] = 14 + 52 * (sky_y ** 2.8)
    arr[:horizon_y, :, 2] = 32 + 34 * (sky_y ** 1.8)

    # Ocean gradient below horizon
    sea_y = np.linspace(0.0, 1.0, H - horizon_y, dtype=np.float32)[:, None]
    arr[horizon_y:, :, 0] = 28 * (1.0 - sea_y) + 5
    arr[horizon_y:, :, 1] = 44 * (1.0 - sea_y) + 11
    arr[horizon_y:, :, 2] = 68 * (1.0 - sea_y) + 22

    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    # Horizon warm amber glow line
    d.line((0, horizon_y, W, horizon_y), fill=(234, 168, 68, 175), width=2)
    draw_particles(d, t_global, tint=(160, 215, 235))

    # Luminous subsea optical filaments curving across the abyssal foreground into the horizon
    for idx in range(11):
        x_bot = -120 + idx * 215
        x_top = W * 0.5 + (idx - 5) * 62
        pts = []
        for s in range(36):
            u = s / 35.0
            xx = x_bot * (1 - u) + x_top * u + math.sin(u * 5.0 + idx) * 28.0 * (1 - u)
            yy = (H - 40) * (1 - u ** 0.72) + (horizon_y + 8) * (u ** 0.72)
            pts.append((xx, yy))
        col = CYAN if idx % 2 == 0 else AMBER
        d.line(pts, fill=(col[0], col[1], col[2], 125), width=2)
        # Light packet riding along glass fiber
        pu = (t_local * 0.24 + idx * 0.17) % 1.0
        pi = min(35, int(pu * 35))
        px, py = pts[pi]
        d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=(col[0], col[1], col[2], 235))

    # Center closing reflection card
    dur = shot["duration"]
    a = ease_out_cubic(prog(t_local, 0.3, 1.0))
    text_centered(d, W // 2, 165, "18 NOVEMBER 1929  —  2026",
                  get_font("mono_bold", 20), fill=(AMBER[0], AMBER[1], AMBER[2], int(240 * a)))
    text_centered(d, W // 2, 215, "THE THIRTEEN-HOUR AVALANCHE",
                  get_font("serif_bold", 58), fill=(IVORY[0], IVORY[1], IVORY[2], int(255 * a)))
    text_centered(d, W // 2, 292, "Twelve severed telegraph wires became humanity's first deep-ocean speedometer.",
                  get_font("sans_med", 24), fill=(MUTED[0], MUTED[1], MUTED[2], int(240 * a)))

    # Final 2.0s clean attribution card (well within <=10s intro/outro budget)
    if t_local >= dur - 2.1:
        ca = ease_out_cubic(prog(t_local, dur - 2.1, 0.5))
        d.rounded_rectangle((W // 2 - 430, 795, W // 2 + 430, 882), radius=10,
                            fill=(6, 12, 22, int(225 * ca)), outline=(AMBER[0], AMBER[1], AMBER[2], int(175 * ca)))
        text_centered(d, W // 2, 812, "PRODUCED BY THAUMATROPE  ·  AGENCY V3 COMPETITION ENTRY",
                      get_font("mono_bold", 16), fill=(AMBER[0], AMBER[1], AMBER[2], int(250 * ca)))
        text_centered(d, W // 2, 842, "Primary Sources: Heezen & Ewing (1952) · Piper et al. (1988) · Clare et al. (2023) · ICPC (2025)",
                      get_font("mono_reg", 14), fill=(MUTED[0], MUTED[1], MUTED[2], int(235 * ca)))

    return Image.alpha_composite(im, ov)

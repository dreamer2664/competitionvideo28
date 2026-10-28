#!/usr/bin/env python3
"""
Scene renderers for Shots S14 through S25 (Acts V - VII) of THE TEN-MINUTE ECLIPSE.
All scenes strictly respect the y = 0..910 visual zone so y = 924..1052 remains clear for captions.
"""
import math
from PIL import Image, ImageDraw
import numpy as np

from visual_primitives import (
    W, H, BG_ABYSS, BG_SLATE, PANEL_FILL, PANEL_DARK, PANEL_BORDER, BRASS_BORDER,
    IVORY, MUTED, DIM, AMBER, AMBER_SOFT, CRIMSON, CYAN, EMERALD, VIOLET,
    get_font, clamp, ease_out_cubic, ease_in_out_cubic, prog,
    BASE_TECH_CANVAS, render_ken_burns_plate, draw_particles, draw_panel,
)


def render_s14(plate_dir, shot, t_local, t_global):
    """Huygens' 1690 Traité de la Lumière first numerical speed of light derivation."""
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    draw_panel(d, (56, 100, W - 56, 888), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((92, 126), "CHRISTIAAN HUYGENS · TRAITÉ DE LA LUMIÈRE (LEIDEN, 1690 · CH. 1)", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((92, 164), "Converting Rømer's 22-Minute Orbital Delay Into the First Numerical Speed of Light", font=get_font("sans_bold", 25), fill=IVORY)

    # Three step cards across top-middle (y = 224..540)
    steps = [
        ("STEP 1 · RØMER'S LIGHT-TIME", "Δt (2 AU) = 22 minutes",
         "1,320 seconds across the full", "diameter of Earth's orbit around", "the Sun (Journal des Sçavans, 1676).", AMBER),
        ("STEP 2 · CASSINI'S SOLAR SCALE", "1 AU ≈ 12,000 Earth Diameters",
         "From Cassini's 1672 Mars parallax", "(9.5 arcseconds), 2 AU spans ~24,000", "Earth diameters (~282,000,000 km).", CYAN),
        ("STEP 3 · HUYGENS' QUOTIENT", "c ≈ 16.7 Earth Diameters / sec",
         "More than 600,000 × the speed of", "sound in air — equivalent in modern", "units to ~214,000 km / second!", EMERALD),
    ]
    cw = 552
    gap = 36
    sx = (W - (3 * cw + 2 * gap)) // 2
    for idx, (hdr, big, l1, l2, l3, col) in enumerate(steps):
        x0 = sx + idx * (cw + gap)
        draw_panel(d, (x0, 224, x0 + cw, 548), fill=(14, 26, 46, 235), border=col)
        d.text((x0 + 26, 250), hdr, font=get_font("mono_bold", 19), fill=col)
        d.text((x0 + 26, 294), big, font=get_font("sans_bold", 26), fill=IVORY)
        d.line((x0 + 26, 344, x0 + cw - 26, 344), fill=(80, 120, 160, 140), width=1)
        d.text((x0 + 26, 368), l1, font=get_font("sans_reg", 21), fill=MUTED)
        d.text((x0 + 26, 404), l2, font=get_font("sans_reg", 21), fill=MUTED)
        d.text((x0 + 26, 440), l3, font=get_font("sans_semi", 21), fill=IVORY)

    # Bottom visual scale comparison: Sound (0.343 km/s) vs Huygens Light (214,000 km/s)
    draw_panel(d, (92, 584, W - 92, 852), fill=(11, 20, 36, 240), border=PANEL_BORDER)
    d.text((124, 610), "SCALE COMPARISON: SOUND IN AIR (0.343 KM/S) VS. HUYGENS' 1690 SPEED OF LIGHT", font=get_font("mono_bold", 19), fill=AMBER)
    d.text((124, 658), "Speed of Sound (1 Mach):      0.343 km/s   [1 pixel]", font=get_font("mono_reg", 21), fill=MUTED)
    d.rounded_rectangle((975, 660, 982, 686), radius=2, fill=CRIMSON)

    bar_w = int(810 * ease_out_cubic(prog(t_local, 0.3, 3.0)))
    d.text((124, 718), "Huygens Light (1690):   214,000 km/s   [624,000 × Sound]", font=get_font("mono_bold", 21), fill=CYAN)
    if bar_w > 6:
        d.rounded_rectangle((975, 718, 975 + bar_w, 748), radius=6, fill=CYAN)
    d.text((124, 784), "Why 214,000 vs 299,792 km/s? Rømer's 22m (vs 16m38s) + 1672 solar parallax uncertainty.", font=get_font("sans_reg", 20), fill=IVORY)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s15(plate_dir, shot, t_local, t_global):
    frac = clamp(t_local / max(0.1, shot["shot_dur"]))
    base = render_ken_burns_plate(
        plate_dir, shot["plate"], frac,
        zoom_start=1.01, zoom_end=1.07, pan_x=(-14, 14), pan_y=(-6, 6), darken=0.84
    )
    canvas = Image.fromarray(base).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global, tint=(240, 215, 160))

    # Bottom split comparison: English Acceptance vs French Skepticism (y = 568..888)
    draw_panel(d, (64, 568, 930, 888), fill=PANEL_DARK, border=EMERALD)
    d.text((92, 594), "ENGLAND & HOLLAND · ACCEPTED IMMEDIATELY", font=get_font("mono_bold", 19), fill=EMERALD)
    d.text((92, 634), "• Isaac Newton (Principia, 1687 & Opticks, 1704)", font=get_font("sans_semi", 21), fill=IVORY)
    d.text((92, 672), "• Christiaan Huygens (Traité de la Lumière, 1690)", font=get_font("sans_semi", 21), fill=IVORY)
    d.text((92, 710), "• Edmond Halley & John Flamsteed (Greenwich, 1694)", font=get_font("sans_semi", 21), fill=IVORY)
    d.text((92, 764), "Adopted finite light-time corrections in all Jovian tables.", font=get_font("sans_reg", 20), fill=EMERALD)

    draw_panel(d, (966, 568, W - 64, 888), fill=PANEL_DARK, border=CRIMSON)
    d.text((994, 594), "PARIS ACADEMY · REJECTED FOR 52 YEARS (1676–1728)", font=get_font("mono_bold", 19), fill=CRIMSON)
    d.text((994, 634), "• Jean-Dominique Cassini & Giacomo Filippo Maraldi", font=get_font("sans_semi", 21), fill=IVORY)
    d.text((994, 672), "• Objection: Moons II, III & IV (Europa, Ganymede, Callisto)", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((994, 704), "  had inclined, Laplace-resonant orbits whose eclipses did", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((994, 736), "  not match a simple uniform delay table.", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((994, 784), "Stalemate persisted until an independent star proved Rømer right.", font=get_font("sans_bold", 20), fill=AMBER)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s16(plate_dir, shot, t_local, t_global):
    frac = clamp(t_local / max(0.1, shot["shot_dur"]))
    base = render_ken_burns_plate(
        plate_dir, shot["plate"], frac,
        zoom_start=1.02, zoom_end=1.08, pan_x=(12, -12), pan_y=(-8, 8), darken=0.85
    )
    canvas = Image.fromarray(base).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global, tint=(200, 225, 250))

    # Top-left Kew Gardens Zenith Sector Card
    draw_panel(d, (64, 102, 820, 468), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((92, 126), "KEW & WANSTEAD · JAMES BRADLEY (1725–1728)", font=get_font("mono_bold", 19), fill=AMBER)
    d.text((92, 164), "The Vertical Chimney Zenith Telescope on γ Draconis", font=get_font("sans_bold", 24), fill=IVORY)
    d.line((92, 204, 792, 204), fill=(80, 120, 160, 150), width=1)

    d.text((92, 224), "• Target Star:   Gamma Draconis (passes directly overhead)", font=get_font("mono_reg", 19), fill=CYAN)
    d.text((92, 262), "• Why Zenith?    Zero atmospheric refraction error", font=get_font("mono_reg", 19), fill=IVORY)
    d.text((92, 300), "• Expected:      Max parallax shift in June & December", font=get_font("mono_reg", 19), fill=MUTED)
    d.text((92, 338), "• Observed:      ±20.49\" shift in MARCH & SEPTEMBER!", font=get_font("mono_bold", 20), fill=CRIMSON)

    d.rounded_rectangle((92, 384, 792, 444), radius=10, fill=(16, 30, 50, 230), outline=CYAN, width=1)
    d.text((114, 402), "90° out of phase with distance — driven by Earth's VELOCITY!", font=get_font("sans_bold", 20), fill=CYAN)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s17(plate_dir, shot, t_local, t_global):
    """
    Procedural Stellar Aberration Vector Solver (James Bradley, Phil. Trans. 1728):
    tan(theta) = v_earth / c = 29.78 km/s / 299,792 km/s = 1 / 10,210 -> theta = 20.495".
    """
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    # Left: Animated Tilted Telescope & Falling Starlight Photons (x = 56..1020, y = 100..888)
    draw_panel(d, (56, 100, 1020, 888), fill=PANEL_DARK, border=CYAN)
    d.text((86, 126), "STELLAR ABERRATION VECTOR GEOMETRY (BRADLEY, 1728)", font=get_font("mono_bold", 19), fill=CYAN)
    d.text((86, 162), "Why a Moving Earth Must Tilt Its Telescope Forward by θ = 20.49\"", font=get_font("sans_bold", 22), fill=IVORY)

    # Starlight photons falling vertically at speed c while telescope moves right at v_earth
    cyc = (t_local * 0.55) % 1.0
    tx_base = int(310 + 360 * cyc)
    ty_bot = 740
    ty_top = 290
    dx_tilt = 140  # exaggerated tilt angle for visual clarity

    # Draw ghost vertical ray (true star direction)
    photon_x = 310 + dx_tilt
    photon_y = int(ty_top + (ty_bot - ty_top) * cyc)
    d.line((photon_x, 230, photon_x, ty_bot + 30), fill=(86, 208, 228, 120), width=2)
    d.text((photon_x - 120, 204), "TRUE STARLIGHT (VERTICAL, SPEED c)", font=get_font("mono_bold", 16), fill=CYAN)

    # Draw moving tilted telescope tube so photon stays centered down the bore!
    tube_x_bot = int(photon_x - dx_tilt * (1.0 - cyc))
    tube_x_top = tube_x_bot + dx_tilt
    d.line((tube_x_bot, ty_bot, tube_x_top, ty_top), fill=AMBER, width=22)
    d.line((tube_x_bot, ty_bot, tube_x_top, ty_top), fill=(24, 38, 58, 255), width=14)

    # Falling photon inside the moving tube
    d.ellipse((photon_x - 11, photon_y - 11, photon_x + 11, photon_y + 11), fill=IVORY, outline=CYAN, width=3)

    # Velocity vector arrows at bottom
    d.line((220, 790, 860, 790), fill=EMERALD, width=4)
    d.text((310, 806), "EARTH ORBITAL VELOCITY:  v = 29.78 km/s  --->", font=get_font("mono_bold", 19), fill=EMERALD)

    # Right: Vector Triangle & Primary-Source Receipt (x = 1048..1864, y = 100..888)
    draw_panel(d, (1048, 100, W - 56, 888), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((1080, 126), "PHILOSOPHICAL TRANSACTIONS · VOL. 35, NO. 406 (1728)", font=get_font("mono_bold", 19), fill=AMBER)
    d.text((1080, 164), "“A Letter from the Rev. Mr. James Bradley to Dr. Edmond Halley”", font=get_font("serif_italic", 23), fill=IVORY)
    d.line((1080, 204, W - 88, 204), fill=(80, 120, 160, 150), width=1)

    # Mathematical derivation box
    d.rounded_rectangle((1080, 228, W - 88, 520), radius=14, fill=(14, 26, 46, 235), outline=CYAN, width=2)
    d.text((1110, 252), "BRADLEY'S ABERRATION LAW:", font=get_font("mono_bold", 20), fill=CYAN)
    d.text((1110, 300), "tan(θ)  =  v_earth / c", font=get_font("mono_bold", 34), fill=IVORY)
    d.text((1110, 366), "• Measured Tilt Angle (θ):     20.495 arcseconds", font=get_font("mono_reg", 20), fill=AMBER)
    d.text((1110, 404), "• Speed Ratio (c / v_earth):   10,210  to  1", font=get_font("mono_bold", 20), fill=EMERALD)
    d.text((1110, 442), "• Solar Light-Time (1 AU):     8 minutes 12 seconds", font=get_font("mono_bold", 20), fill=CYAN)
    d.text((1110, 480), "• Implied Speed of Light:      ~301,000 km/s (<0.4% error!)", font=get_font("mono_bold", 20), fill=IVORY)

    # Historical impact box
    d.rounded_rectangle((1080, 554, W - 88, 852), radius=14, fill=(16, 30, 50, 235), outline=AMBER, width=1)
    d.text((1110, 580), "DOUBLE SCIENTIFIC TRIUMPH (1728):", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((1110, 624), "1. Confirmed Ole Rømer's finite speed of light", font=get_font("sans_semi", 21), fill=IVORY)
    d.text((1110, 658), "   from an independent star outside the solar system.", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((1110, 706), "2. Provided the first direct observational proof", font=get_font("sans_semi", 21), fill=IVORY)
    d.text((1110, 740), "   that Earth itself is moving through space around", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((1110, 774), "   the Sun at ~30 kilometers per second.", font=get_font("sans_bold", 20), fill=EMERALD)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s18(plate_dir, shot, t_local, t_global):
    frac = clamp(t_local / max(0.1, shot["shot_dur"]))
    base = render_ken_burns_plate(
        plate_dir, shot["plate"], frac,
        zoom_start=1.01, zoom_end=1.07, pan_x=(-14, 14), pan_y=(-6, 6), darken=0.86
    )
    canvas = Image.fromarray(base).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global, tint=(245, 205, 130))

    # Animated light pulse racing along the Suresnes -> Montmartre beam line
    x0, y0 = 905, 412
    x1, y1 = 1650, 312
    cyc = (t_local * 0.9) % 1.0
    u = cyc * 2.0 if cyc < 0.5 else (1.0 - (cyc - 0.5) * 2.0)
    px = x0 + (x1 - x0) * u
    py = y0 + (y1 - y0) * u
    d.ellipse((px - 10, py - 10, px + 10, py + 10), fill=IVORY, outline=AMBER, width=3)

    # Bottom-right Baseline Specification Card (y = 584..888)
    draw_panel(d, (860, 584, 1856, 888), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((890, 610), "FIRST TERRESTRIAL MEASUREMENT · HIPPOLYTE FIZEAU (JULY 1849)", font=get_font("mono_bold", 19), fill=AMBER)
    d.text((890, 648), "Suresnes Belvedere Cupola  <--->  Montmartre Collimator Mirror", font=get_font("sans_bold", 23), fill=IVORY)
    d.line((890, 688, 1826, 688), fill=(80, 120, 160, 150), width=1)
    d.text((890, 708), "• One-Way Baseline (L):       8,633 meters  (8.633 km across Paris)", font=get_font("mono_bold", 20), fill=CYAN)
    d.text((890, 748), "• Round-Trip Path (2L):      17,266 meters  (17.266 km total flight)", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((890, 788), "• Round-Trip Flight Time:     55.1 microseconds  (0.0000551 s)", font=get_font("mono_bold", 20), fill=EMERALD)
    d.text((890, 830), "Source: Fizeau, Comptes Rendus de l'Académie des Sciences, Vol. 29 (23 Juillet 1849)", font=get_font("sans_reg", 17), fill=DIM)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s19(plate_dir, shot, t_local, t_global):
    frac = clamp(t_local / max(0.1, shot["shot_dur"]))
    base = render_ken_burns_plate(
        plate_dir, shot["plate"], frac,
        zoom_start=1.02, zoom_end=1.08, pan_x=(14, -14), pan_y=(-6, 6), darken=0.85
    )
    canvas = Image.fromarray(base).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global, tint=(245, 210, 130))

    # Top-left Optical Chopper Engineering Card
    draw_panel(d, (64, 102, 830, 476), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((92, 126), "FIZEAU'S OPTICAL CHOPPER APPARATUS (1849)", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((92, 164), "How a Spinning Brass Cogwheel Slices a Beam of Light", font=get_font("sans_bold", 23), fill=IVORY)
    d.line((92, 204, 800, 204), fill=(80, 120, 160, 150), width=1)

    d.text((92, 224), "• Wheel Perimeter:    N = 720 square teeth + 720 gaps", font=get_font("mono_bold", 19), fill=CYAN)
    d.text((92, 262), "• Angular Pitch:      1 / 1,440 turn = 0.25° per tooth/gap", font=get_font("mono_reg", 19), fill=IVORY)
    d.text((92, 300), "• Maker:              Gustave Froment (Paris precision horologist)", font=get_font("mono_reg", 19), fill=MUTED)
    d.text((92, 338), "• Beam Splitter:      45° unsilvered glass plate sends lamp", font=get_font("mono_reg", 19), fill=IVORY)
    d.text((92, 370), "                      light out and lets observer look straight through.", font=get_font("sans_reg", 19), fill=IVORY)
    d.text((92, 416), "Each gap acts as a 55-microsecond mechanical camera shutter.", font=get_font("sans_bold", 20), fill=AMBER)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s20(plate_dir, shot, t_local, t_global):
    """
    Full-screen live simulation of Fizeau's 720-Tooth Brass Wheel accelerating from 0 -> 12.60 rps
    and eclipsing the returning Montmartre star-point at Δt = 55.1 microseconds.
    """
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    # Progress from low speed (2.0 rps) to first eclipse speed (12.60 rps)
    p_spin = ease_in_out_cubic(clamp(t_local / (shot["shot_dur"] * 0.68)))
    rps = 2.0 + (12.60 - 2.0) * p_spin
    # Relative intensity transmitted through wheel: cos^2(pi * rps / (2 * 12.60))
    trans = math.cos(math.pi * (rps - 0.0) / (2.0 * 12.60)) ** 2 if rps <= 12.60 else 0.0
    if p_spin > 0.94:
        rps = 12.60
        trans = 0.0

    # Left: Rotating Brass Toothed Wheel Rim & Beam Gate (x = 56..1120, y = 100..888)
    draw_panel(d, (56, 100, 1120, 888), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((86, 126), "LIVE SIMULATION · FIZEAU'S 720-TOOTH WHEEL (FIRST ECLIPSE @ 12.60 RPS)", font=get_font("mono_bold", 19), fill=AMBER)

    # Draw large zoomed brass wheel centered near bottom-left of panel so top rim passes through optical axis y = 470
    w_cx, w_cy, w_r = 460, 740, 270
    d.ellipse((w_cx - w_r + 26, w_cy - w_r + 26, w_cx + w_r - 26, w_cy + w_r - 26), fill=(155, 115, 45, 240), outline=AMBER, width=3)
    d.ellipse((w_cx - 70, w_cy - 70, w_cx + 70, w_cy + 70), fill=(30, 42, 60, 255), outline=IVORY, width=3)

    # Draw 72 representative macro teeth around rim rotating with rps
    rot_deg = t_local * rps * 12.0
    for k in range(72):
        a0 = math.radians(k * 5.0 + rot_deg)
        a1 = math.radians(k * 5.0 + 2.4 + rot_deg)
        p1 = (w_cx + (w_r - 28) * math.cos(a0), w_cy + (w_r - 28) * math.sin(a0))
        p2 = (w_cx + (w_r + 6) * math.cos(a0), w_cy + (w_r + 6) * math.sin(a0))
        p3 = (w_cx + (w_r + 6) * math.cos(a1), w_cy + (w_r + 6) * math.sin(a1))
        p4 = (w_cx + (w_r - 28) * math.cos(a1), w_cy + (w_r - 28) * math.sin(a1))
        d.polygon([p1, p2, p3, p4], fill=AMBER, outline=(90, 65, 20, 220))

    # Optical axis at y = 468 (top of wheel rim)
    gate_x, gate_y = w_cx, w_cy - w_r
    # Outgoing beam to Montmartre (right)
    d.line((120, gate_y - 12, 1040, gate_y - 12), fill=AMBER, width=4)
    d.text((640, gate_y - 44), "OUTBOUND PULSE -> MONTMARTRE (8,633 m)", font=get_font("mono_bold", 16), fill=AMBER)

    # Montmartre mirror at right edge of panel
    d.rectangle((1040, gate_y - 45, 1062, gate_y + 45), fill=CYAN, outline=IVORY, width=2)
    d.text((925, gate_y + 56), "MONTMARTRE MIRROR", font=get_font("mono_bold", 15), fill=CYAN)

    # Returning beam (gate_y + 12): passes through gate when trans > 0, blocked by tooth at 12.60 rps!
    d.line((1040, gate_y + 12, gate_x + 12, gate_y + 12), fill=CYAN, width=4)
    if trans > 0.08:
        alpha_ret = int(255 * trans)
        d.line((gate_x - 12, gate_y + 12, 120, gate_y + 12), fill=(86, 208, 228, alpha_ret), width=4)
    else:
        # Red X / blocked highlight at tooth + clean callout badge above optical axis
        d.ellipse((gate_x - 18, gate_y - 6, gate_x + 18, gate_y + 30), fill=(232, 82, 68, 220), outline=IVORY, width=2)
        d.rounded_rectangle((88, 210, 740, 266), radius=10, fill=(42, 14, 20, 235), outline=CRIMSON, width=2)
        d.text((112, 226), "BLOCKED BY ADJACENT TOOTH! (Δθ = 0.25° in 55.1 µs)", font=get_font("mono_bold", 18), fill=CRIMSON)

    # Right: Astronomer's Eyepiece View & Live Equation Solver (x = 1148..1864, y = 100..888)
    draw_panel(d, (1148, 100, W - 56, 888), fill=PANEL_DARK, border=PANEL_BORDER)
    d.text((1180, 126), "OBSERVER EYEPIECE VIEW (SURESNES)", font=get_font("mono_bold", 20), fill=AMBER)

    # Eyepiece circular field
    ecx, ecy, er = 1506, 330, 130
    d.ellipse((ecx - er, ecy - er, ecx + er, ecy + er), fill=(5, 9, 16, 255), outline=BRASS_BORDER, width=4)
    d.line((ecx - er, ecy, ecx + er, ecy), fill=(70, 100, 135, 130), width=1)
    d.line((ecx, ecy - er, ecx, ecy + er), fill=(70, 100, 135, 130), width=1)

    # Star-point brightness inside eyepiece
    star_r = int(4 + 26 * trans)
    if trans > 0.03:
        glow_a = int(245 * trans)
        d.ellipse((ecx - star_r*2, ecy - star_r*2, ecx + star_r*2, ecy + star_r*2), fill=(244, 184, 72, glow_a // 3))
        d.ellipse((ecx - star_r, ecy - star_r, ecx + star_r, ecy + star_r), fill=(255, 240, 190, glow_a))
    else:
        d.text((ecx - 108, ecy + 36), "1ST ECLIPSE (DARK)", font=get_font("mono_bold", 19), fill=CRIMSON)

    # Telemetry readout below eyepiece
    d.rounded_rectangle((1180, 500, W - 88, 854), radius=14, fill=(14, 26, 46, 235), outline=CYAN, width=2)
    d.text((1208, 524), f"WHEEL SPEED (f₁):      {rps:05.2f} rev / sec", font=get_font("mono_bold", 22), fill=AMBER)
    d.text((1208, 566), f"EYEPIECE BRIGHTNESS:   {int(round(trans * 100)):3d} %", font=get_font("mono_bold", 22), fill=CRIMSON if trans < 0.1 else CYAN)
    d.line((1208, 610, W - 116, 610), fill=(80, 120, 160, 140), width=1)
    d.text((1208, 630), "FIZEAU'S FORMULA:", font=get_font("mono_bold", 19), fill=CYAN)
    d.text((1208, 668), "c = 2L / Δt = 4 · N · L · f₁", font=get_font("mono_bold", 26), fill=IVORY)
    d.text((1208, 722), "c = 4 × 720 × 8,633 m × 12.6 s⁻¹", font=get_font("mono_reg", 20), fill=MUTED)
    d.text((1208, 766), "c ≈ 315,300 km / second", font=get_font("mono_bold", 25), fill=EMERALD)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s21(plate_dir, shot, t_local, t_global):
    """
    Harmonic verification curve: 12.6 rps (1st Eclipse), 25.2 rps (Full Brightening), 37.8 rps (2nd Eclipse).
    """
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    draw_panel(d, (56, 100, W - 56, 888), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((92, 126), "HARMONIC OPTICAL MODULATION · FIZEAU'S THREE SPEED THRESHOLDS (1849)", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((92, 162), "Intensity I(f) = cos²(π · f / 25.2) — Eclipsing at Odd Multiples, Shining at Even Multiples", font=get_font("sans_bold", 24), fill=IVORY)

    # Plot of Eyepiece Brightness vs Wheel Rotation Speed (0 to 42 rps)
    gx0, gy0, gx1, gy1 = 180, 560, 1760, 250
    d.line((gx0, gy0, gx1, gy0), fill=IVORY, width=2)
    d.line((gx0, gy0, gx0, gy1), fill=IVORY, width=2)
    d.text((92, gy1 - 6), "100%", font=get_font("mono_bold", 18), fill=CYAN)
    d.text((104, gy0 - 12), "0%", font=get_font("mono_bold", 18), fill=CRIMSON)

    frac = ease_in_out_cubic(clamp(t_local / (shot["shot_dur"] * 0.80)))
    max_f = 40.0 * frac
    pts = []
    for i in range(240):
        f_val = (i / 239.0) * max_f
        inten = math.cos(math.pi * f_val / (2.0 * 12.6)) ** 2
        px = int(gx0 + (f_val / 42.0) * (gx1 - gx0))
        py = int(gy0 - inten * (gy0 - gy1))
        pts.append((px, py))
    if len(pts) > 1:
        d.line(pts, fill=CYAN, width=5)

    # Highlight the 3 harmonic landmarks (12.6, 25.2, 37.8 rps)
    landmarks = [
        (12.6, 0.0, "f₁ = 12.6 rps", "1ST ECLIPSE", "Blocked by Tooth #1", CRIMSON),
        (25.2, 1.0, "2f₁ = 25.2 rps", "RE-BRIGHTENING", "Passes Through Gap #2", EMERALD),
        (37.8, 0.0, "3f₁ = 37.8 rps", "2ND ECLIPSE", "Blocked by Tooth #2", CRIMSON),
    ]
    for idx, (f_v, inten_v, f_str, state_str, desc_str, col) in enumerate(landmarks):
        lx = int(gx0 + (f_v / 42.0) * (gx1 - gx0))
        ly = int(gy0 - inten_v * (gy0 - gy1))
        d.line((lx, gy1, lx, gy0), fill=(90, 130, 175, 130), width=2)
        d.ellipse((lx - 9, ly - 9, lx + 9, ly + 9), fill=col, outline=IVORY, width=2)

        # Bottom summary card for each landmark
        cx0 = 92 + idx * 590
        draw_panel(d, (cx0, 614, cx0 + 556, 858), fill=(14, 26, 46, 235), border=col)
        d.text((cx0 + 26, 638), f"{f_str}  ·  {state_str}", font=get_font("mono_bold", 20), fill=col)
        d.text((cx0 + 26, 688), desc_str, font=get_font("sans_bold", 22), fill=IVORY)
        rot_str = f"Rotation in 55.1 µs: {idx + 1}/1,440 turn ({0.25*(idx+1):.2f}°)"
        d.text((cx0 + 26, 742), rot_str, font=get_font("mono_reg", 18), fill=MUTED)
        d.text((cx0 + 26, 788), f"c = {int(round(4*720*8.633*(f_v/(idx+1)))):,} km/s", font=get_font("mono_bold", 20), fill=EMERALD)
        # Mini eyepiece circle in upper-right of card
        ex, ey = cx0 + 494, 676
        d.ellipse((ex - 34, ey - 34, ex + 34, ey + 34), fill=(6, 10, 18, 255), outline=col, width=2)
        if inten_v > 0.5:
            d.ellipse((ex - 15, ey - 15, ex + 15, ey + 15), fill=AMBER, outline=IVORY, width=2)
        else:
            d.text((ex - 21, ey - 9), "DARK", font=get_font("mono_bold", 14), fill=CRIMSON)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s22(plate_dir, shot, t_local, t_global):
    """
    Foucault (1862) rotating mirror & Michelson's 1926 Mount Wilson to Mount San Antonio
    35.4 km 8-sided octagonal mirror measurement (299,796 ± 4 km/s).
    """
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    draw_panel(d, (56, 100, W - 56, 888), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((92, 126), "FROM TOOTHED WHEELS TO ROTATING MIRRORS · FOUCAULT (1862) & MICHELSON (1926)", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((92, 162), "Albert A. Michelson's 35.4 km Mount Wilson – Mount San Antonio Octagonal Mirror", font=get_font("sans_bold", 24), fill=IVORY)

    # Left: Animated 8-sided Rotating Octagonal Mirror + Mountain Baseline
    ocx, ocy, orad = 340, 490, 125
    rot = t_local * 2.2
    oct_pts = []
    for k in range(8):
        ang = rot + k * (math.pi / 4.0)
        oct_pts.append((ocx + orad * math.cos(ang), ocy + orad * math.sin(ang)))
    d.polygon(oct_pts, fill=(45, 72, 104, 240), outline=CYAN)
    d.ellipse((ocx - 24, ocy - 24, ocx + 24, ocy + 24), fill=AMBER, outline=IVORY, width=2)
    d.text((ocx - 135, ocy + 148), "OCTAGONAL STEEL MIRROR (528 RPS)", font=get_font("mono_bold", 17), fill=CYAN)

    # Distant Mount San Antonio (Old Baldy) retro-reflector at x = 1040, y = 490
    mx, my = 1020, 490
    d.polygon([(mx, my - 90), (mx + 90, my + 90), (mx - 90, my + 90)], fill=(28, 44, 68, 230), outline=AMBER)
    d.rectangle((mx - 14, my - 35, mx + 14, my + 35), fill=CYAN, outline=IVORY, width=2)
    d.text((mx - 130, my + 108), "MT. SAN ANTONIO MIRROR (35.4 KM)", font=get_font("mono_bold", 16), fill=AMBER)

    # Beam bouncing between octagon and distant mountain mirror
    d.line((ocx + orad - 12, ocy - 18, mx - 14, my - 18), fill=AMBER, width=4)
    d.line((mx - 14, my + 18, ocx + orad - 12, ocy + 18), fill=CYAN, width=4)
    p_u = (t_local * 1.1) % 1.0
    bx = (ocx + orad) + (mx - ocx - orad) * (p_u * 2.0 if p_u < 0.5 else 2.0 - p_u * 2.0)
    by = ocy - 18 if p_u < 0.5 else ocy + 18
    d.ellipse((bx - 9, by - 9, bx + 9, by + 9), fill=IVORY, outline=AMBER, width=2)
    d.text((530, 430), "ROUND TRIP: 70.8 KM (236.2 µs)", font=get_font("mono_bold", 18), fill=IVORY)

    # Right: Comparison cards for Foucault (1862) and Michelson (1926)
    draw_panel(d, (1180, 224, W - 92, 518), fill=(14, 26, 46, 235), border=CYAN)
    d.text((1208, 248), "LÉON FOUCAULT (PARIS, 1862)", font=get_font("mono_bold", 20), fill=CYAN)
    d.text((1208, 290), "c = 298,000 ± 500 km/s", font=get_font("mono_bold", 28), fill=IVORY)
    d.text((1208, 340), "• Replaced cogwheel with air-turbine", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((1208, 372), "  rotating mirror over a 20 m path", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((1208, 412), "• Error vs modern c:  0.60%", font=get_font("mono_bold", 20), fill=EMERALD)

    draw_panel(d, (1180, 548, W - 92, 852), fill=(14, 26, 46, 235), border=AMBER)
    d.text((1208, 572), "ALBERT A. MICHELSON (MT. WILSON, 1926)", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((1208, 614), "c = 299,796 ± 4 km/s", font=get_font("mono_bold", 28), fill=IVORY)
    d.text((1208, 664), "• 8-sided mirror at 528.0 rev/sec", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((1208, 696), "  rotates 1/8 turn during 70.8 km trip", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((1208, 736), "• Error vs modern c:  0.0012% (+3.5 km/s)", font=get_font("mono_bold", 20), fill=EMERALD)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s23(plate_dir, shot, t_local, t_global):
    """
    300-Year Convergence Ledger (1676 -> 1972): How measurement uncertainty shrank by 8 orders of magnitude
    until the Krypton-86 meter bar became the bottleneck.
    """
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    draw_panel(d, (56, 100, W - 56, 888), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((92, 126), "THREE CENTURIES OF CONVERGENCE · FROM JUPITER'S SHADOW TO STABILIZED LASERS", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((92, 162), "Relative Uncertainty (Δc / c) Shrank by 8 Orders of Magnitude (1676 – 1972)", font=get_font("sans_bold", 24), fill=IVORY)

    history = [
        ("1676 / 1690", "Rømer & Huygens", "Io Eclipses (2 AU)", "214,000 km/s", "±28%", 0.88, AMBER),
        ("1728", "James Bradley", "Stellar Aberration (γ Dra)", "301,000 km/s", "±0.4%", 0.62, CYAN),
        ("1849", "Hippolyte Fizeau", "720-Tooth Wheel (8.63 km)", "315,300 km/s", "±5.1%", 0.72, AMBER),
        ("1862", "Léon Foucault", "Rotating Mirror (20 m)", "298,000 km/s", "±0.17%", 0.50, CYAN),
        ("1926", "Albert A. Michelson", "Mt. Wilson Octagon (35.4 km)", "299,796 km/s", "±0.0013%", 0.28, EMERALD),
        ("1972", "Evenson et al. (NBS)", "He-Ne Laser Interferometer", "299,792.458 km/s", "±0.0000004% (±1.2 m/s)", 0.08, VIOLET),
    ]

    for idx, (yr, who, meth, val_s, unc_s, bar_frac, col) in enumerate(history):
        ry = 220 + idx * 104
        d.rounded_rectangle((92, ry, W - 92, ry + 88), radius=10, fill=(14, 26, 46, 230), outline=col, width=1)
        d.text((116, ry + 14), f"{yr}  ·  {who}", font=get_font("mono_bold", 20), fill=col)
        d.text((116, ry + 48), f"Method: {meth}", font=get_font("sans_reg", 19), fill=MUTED)
        d.text((680, ry + 26), val_s, font=get_font("mono_bold", 24), fill=IVORY)

        # Animated uncertainty bar shrinking toward right
        bx0 = 1060
        bw = int(680 * bar_frac * ease_out_cubic(prog(t_local, idx * 0.25, 1.8)))
        d.rounded_rectangle((bx0, ry + 18, bx0 + max(10, bw), ry + 46), radius=6, fill=col)
        d.text((bx0, ry + 52), f"Uncertainty: {unc_s}", font=get_font("mono_bold", 17), fill=IVORY)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s24(plate_dir, shot, t_local, t_global):
    """
    October 20, 1983 (17th CGPM Resolution 1): Fixing c = 299,792,458 m/s exact
    and redefining the meter from the speed of light.
    """
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    draw_panel(d, (56, 100, W - 56, 888), fill=PANEL_DARK, border=EMERALD)
    d.text((92, 126), "17TH CONFÉRENCE GÉNÉRALE DES POIDS ET MESURES · OCTOBER 20, 1983 (RESOLUTION 1)", font=get_font("mono_bold", 19), fill=EMERALD)
    d.text((92, 164), "When Humanity Stopped Measuring the Speed of Light — and Defined the Meter From It", font=get_font("sans_bold", 25), fill=IVORY)

    # Centerpiece Exact Constant Banner
    draw_panel(d, (120, 232, W - 120, 470), fill=(12, 26, 44, 245), border=AMBER, radius=18, width=3)
    s_lbl = "EXACT UNIVERSAL CONSTANT (ZERO UNCERTAINTY BY DEFINITION)"
    b_lbl = d.textbbox((0, 0), s_lbl, font=get_font("mono_bold", 20))
    d.text(((W - (b_lbl[2] - b_lbl[0])) // 2, 260), s_lbl, font=get_font("mono_bold", 20), fill=AMBER)

    s_val = "c  =  299,792,458  meters / second"
    b_val = d.textbbox((0, 0), s_val, font=get_font("disp_black", 62))
    d.text(((W - (b_val[2] - b_val[0])) // 2, 308), s_val, font=get_font("disp_black", 62), fill=IVORY)

    s_def = "“The metre is the length of the path travelled by light in vacuum during a time interval of 1 / 299,792,458 of a second.”"
    b_def = d.textbbox((0, 0), s_def, font=get_font("serif_italic", 25))
    d.text(((W - (b_def[2] - b_def[0])) // 2, 404), s_def, font=get_font("serif_italic", 25), fill=CYAN)

    # Animated laser interferometer standing wave & meter bar (y = 516..852)
    draw_panel(d, (120, 516, W - 120, 852), fill=(10, 18, 32, 240), border=CYAN)
    d.text((156, 544), "OPTICAL METER STANDARD · CESIUM-133 CLOCK + STABILIZED LASER CAVITY", font=get_font("mono_bold", 19), fill=CYAN)

    # Standing sinusoidal laser wave between two cavity mirrors (x = 220..1700)
    mx0, mx1, my = 240, 1680, 680
    d.rectangle((mx0 - 16, my - 65, mx0, my + 65), fill=CYAN, outline=IVORY, width=2)
    d.rectangle((mx1, my - 65, mx1 + 16, my + 65), fill=CYAN, outline=IVORY, width=2)

    wave_pts_1 = []
    wave_pts_2 = []
    for i in range(180):
        u = i / 179.0
        xx = int(mx0 + u * (mx1 - mx0))
        amp = 42.0 * math.sin(u * math.pi * 12.0 - t_global * 8.0)
        wave_pts_1.append((xx, int(my + amp)))
        wave_pts_2.append((xx, int(my - amp)))
    d.line(wave_pts_1, fill=CRIMSON, width=3)
    d.line(wave_pts_2, fill=AMBER, width=3)

    d.line((mx0, my + 90, mx1, my + 90), fill=EMERALD, width=3)
    d.text((590, my + 106), "1 METER  =  Δt = 3.33564095 nanoseconds of light travel in vacuum", font=get_font("mono_bold", 20), fill=EMERALD)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s25(plate_dir, shot, t_local, t_global):
    """
    Resonant Coda on Jupiter & Io's shadow cone: tying 1676 Paris to modern spacetime & GPS.
    """
    frac = clamp(t_local / max(0.1, shot["shot_dur"]))
    base = render_ken_burns_plate(
        plate_dir, shot["plate"], frac,
        zoom_start=1.06, zoom_end=1.01, pan_x=(12, -12), pan_y=(6, -6), darken=0.82
    )
    canvas = Image.fromarray(base).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global, tint=(240, 215, 160))

    # Highlight ring on Io
    ix, iy = 1548, 378
    pr = 42 + int(8 * math.sin(t_global * 3.5))
    d.ellipse((ix - pr, iy - pr, ix + pr, iy + pr), outline=AMBER, width=3)

    # Left Coda Synthesis Card (x = 64..980, y = 112..876)
    draw_panel(d, (64, 112, 980, 876), fill=(8, 15, 27, 232), border=BRASS_BORDER, radius=18)
    d.text((98, 142), "THE TEN-MINUTE ECLIPSE · LEGACY (1676 – PRESENT)", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((98, 184), "Every Modern Distance Is a Measurement of Light-Time", font=get_font("sans_bold", 27), fill=IVORY)
    d.line((98, 230, 946, 230), fill=(85, 125, 170, 150), width=1)

    milestones = [
        ("1676 · OLE RØMER (PARIS)", "Io emerges 10m 00s late (Nov 9, 1676); ~22m across 2 AU.", AMBER),
        ("1690 · CHRISTIAAN HUYGENS", "First numerical velocity: ~214,000 km/s (>600,000 × sound).", CYAN),
        ("1728 · JAMES BRADLEY (KEW)", "20.49\" stellar aberration on γ Draconis -> 8m 12s per AU.", EMERALD),
        ("1849 · HIPPOLYTE FIZEAU", "720-tooth brass wheel @ 12.60 rps over 8,633 m -> 315,300 km/s.", AMBER),
        ("1983 · 17TH CGPM (BIPM)", "Fixed c = 299,792,458 m/s exact; 1 ns of light = 29.98 cm.", CYAN),
    ]
    for idx, (hdr, desc, col) in enumerate(milestones):
        ry = 252 + idx * 104
        d.rounded_rectangle((98, ry, 946, ry + 88), radius=10, fill=(14, 26, 46, 225), outline=col, width=1)
        d.text((120, ry + 14), hdr, font=get_font("mono_bold", 19), fill=col)
        d.text((120, ry + 46), desc, font=get_font("sans_reg", 19), fill=IVORY)

    d.text((98, 796), "“Looking out into space is always looking back through time.”", font=get_font("serif_italic", 25), fill=AMBER)
    d.text((98, 834), "Directed & Engineered by PRAXINOSCOPE · Agency V3 · competitionvideo28", font=get_font("mono_reg", 17), fill=MUTED)

    return Image.alpha_composite(canvas, ov).convert("RGB")

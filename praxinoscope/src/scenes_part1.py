#!/usr/bin/env python3
"""
Scene renderers for Shots S01 through S13 (Acts I - IV) of THE TEN-MINUTE ECLIPSE.
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


def render_s01(plate_dir, shot, t_local, t_global):
    frac = clamp(t_local / max(0.1, shot["shot_dur"]))
    base = render_ken_burns_plate(
        plate_dir, shot["plate"], frac,
        zoom_start=1.01, zoom_end=1.07, pan_x=(-14, 12), pan_y=(-6, 6), darken=0.86
    )
    canvas = Image.fromarray(base).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global, tint=(240, 210, 150))

    # Top-left Paris Observatory Chronometer & Ephemeris Card
    draw_panel(d, (64, 102, 740, 418), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((92, 124), "OBSERVATOIRE DE PARIS · NOV 9, 1676", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((92, 158), "Cassini's Ephemeris Table (Immersion/Emersion of Io)", font=get_font("sans_med", 20), fill=MUTED)
    d.line((92, 194, 712, 194), fill=(90, 130, 170, 140), width=1)

    # Simulated ticking clock past 17:25:45
    sec_pass = int(t_local * 1.5)
    clock_str = f"17 : 25 : {45 + min(14, sec_pass):02d}  P.M."
    d.text((92, 210), "PREDICTED EMERSION:", font=get_font("mono_reg", 18), fill=DIM)
    d.text((340, 206), "17 : 25 : 45  P.M.", font=get_font("mono_bold", 24), fill=CYAN)

    d.text((92, 254), "REGULATOR CLOCK:", font=get_font("mono_reg", 18), fill=DIM)
    d.text((340, 248), clock_str, font=get_font("mono_bold", 28), fill=AMBER)

    # Status pill
    status_col = CRIMSON if t_local > 3.2 else AMBER
    status_txt = "JUPITER LIMB DARK — IO HAS NOT EMERGED" if t_local > 3.2 else "AWAITING FIRST SPARK OF IO (JUPITER I)..."
    d.rounded_rectangle((92, 304, 712, 356), radius=10, fill=(38, 16, 22, 220), outline=status_col, width=2)
    d.text((114, 318), status_txt, font=get_font("mono_bold", 19), fill=status_col)

    # Swinging pendulum indicator bar at bottom of card
    pend_x = int(402 + 190 * math.sin(t_global * math.pi))
    d.line((160, 386, 644, 386), fill=(80, 110, 140, 160), width=3)
    d.ellipse((pend_x - 10, 376, pend_x + 10, 396), fill=AMBER, outline=IVORY, width=2)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s02(plate_dir, shot, t_local, t_global):
    frac = clamp(t_local / max(0.1, shot["shot_dur"]))
    base = render_ken_burns_plate(
        plate_dir, shot["plate"], frac,
        zoom_start=1.02, zoom_end=1.08, pan_x=(-16, 14), pan_y=(-8, 8), darken=0.88
    )
    canvas = Image.fromarray(base).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global, tint=(210, 225, 250))

    # Left Stopwatch Card: 17:25:45 -> 17:35:45 (+10m 00s late)
    p_wait = clamp(t_local / (shot["shot_dur"] * 0.44))
    mins_late = 10.0 * ease_in_out_cubic(p_wait)
    tot_sec = int(round(mins_late * 60))
    mm = 25 + (45 + tot_sec) // 60
    ss = (45 + tot_sec) % 60
    emerged = p_wait >= 0.96

    draw_panel(d, (64, 102, 770, 440), fill=PANEL_DARK, border=AMBER if emerged else PANEL_BORDER)
    d.text((92, 124), "THE TEN-MINUTE ANOMALY · NOV 9, 1676", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((92, 162), f"PARIS LOCAL TIME:   17 : {mm:02d} : {ss:02d} P.M.", font=get_font("mono_bold", 28), fill=IVORY)

    delay_mm = tot_sec // 60
    delay_ss = tot_sec % 60
    col_del = EMERALD if emerged else CRIMSON
    d.text((92, 214), f"ACCUMULATED DELAY:  +{delay_mm:02d}m {delay_ss:02d}s LATE", font=get_font("mono_bold", 26), fill=col_del)

    # Progress bar of the 10-minute wait
    d.rounded_rectangle((92, 268, 740, 302), radius=8, fill=(18, 30, 48, 230), outline=(80, 120, 160, 180), width=1)
    bar_w = int(644 * ease_in_out_cubic(p_wait))
    if bar_w > 4:
        d.rounded_rectangle((94, 270, 94 + bar_w, 300), radius=7, fill=AMBER if emerged else CRIMSON)

    msg = "17:35:45 PM — IO EMERGES FROM JUPITER'S SHADOW!" if emerged else "JUPITER'S UMBRAL CONE STILL ECLIPSES IO..."
    d.text((92, 322), msg, font=get_font("sans_bold", 21), fill=AMBER if emerged else MUTED)
    d.text((92, 364), "Source: Rømer (1676), Journal des Sçavans; Bobis & Lequeux (2008)", font=get_font("sans_reg", 17), fill=DIM)

    # Highlight ring around Io on right when emerged
    if emerged:
        pulse_r = 46 + int(10 * math.sin(t_local * 5.0))
        ix, iy = 1548, 378
        d.ellipse((ix - pulse_r, iy - pulse_r, ix + pulse_r, iy + pulse_r), outline=AMBER, width=3)
        d.line((ix, iy + pulse_r, ix, iy + 110), fill=AMBER, width=2)
        draw_panel(d, (1240, 500, 1852, 620), fill=PANEL_DARK, border=AMBER)
        d.text((1266, 518), "IO EMERSION OBSERVED: 17:35:45 PM", font=get_font("mono_bold", 20), fill=AMBER)
        d.text((1266, 554), "Matches Ole Rømer's August 1676 prediction (+10m 00s)", font=get_font("sans_med", 19), fill=IVORY)

    # Bottom-left card: Rømer's August 1676 prediction
    if t_local > shot["shot_dur"] * 0.45:
        draw_panel(d, (64, 668, 920, 888), fill=PANEL_DARK, border=CYAN)
        d.text((92, 690), "ELEVEN WEEKS EARLIER · ROYAL ACADEMY OF SCIENCES (AUG 1676)", font=get_font("mono_bold", 19), fill=CYAN)
        d.text((92, 728), "Ole Rømer (age 32) publicly wagered against Cassini's instantaneous", font=get_font("sans_med", 22), fill=IVORY)
        d.text((92, 760), "tables — predicting the Nov 9 emersion would arrive 10 minutes late", font=get_font("sans_med", 22), fill=IVORY)
        d.text((92, 792), "solely because Earth had receded farther from Jupiter since August.", font=get_font("sans_med", 22), fill=AMBER)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s03(plate_dir, shot, t_local, t_global):
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    # Rotating decorative 720-tooth optical ring in background center
    cx, cy = W // 2, 330
    for r_ring, col_r in [(220, (50, 90, 135, 80)), (185, (234, 178, 72, 65))]:
        d.ellipse((cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring), outline=col_r, width=2)
    for k in range(72):
        ang = math.radians(k * 5.0 + t_global * 14.0)
        x0 = cx + 190 * math.cos(ang)
        y0 = cy + 190 * math.sin(ang)
        x1 = cx + 216 * math.cos(ang)
        y1 = cy + 216 * math.sin(ang)
        d.line((x0, y0, x1, y1), fill=(244, 184, 72, 95), width=2)

    # Central title banner
    draw_panel(d, (160, 118, W - 160, 430), fill=(9, 18, 33, 236), border=BRASS_BORDER, radius=20, width=2)
    f_sub = get_font("mono_bold", 21)
    f_main = get_font("disp_black", 64)
    f_tag = get_font("serif_italic", 30)

    s1 = "A PRAXINOSCOPE SCIENCE DOCUMENTARY · 1676 – 1849"
    b1 = d.textbbox((0, 0), s1, font=f_sub)
    d.text(((W - (b1[2] - b1[0])) // 2, 152), s1, font=f_sub, fill=AMBER)

    s2 = "THE TEN-MINUTE ECLIPSE"
    b2 = d.textbbox((0, 0), s2, font=f_main)
    d.text(((W - (b2[2] - b2[0])) // 2, 206), s2, font=f_main, fill=IVORY)

    s3 = "How a Moon of Jupiter, a Chimney Telescope & a 720-Tooth Wheel Caught the Speed of Light"
    b3 = d.textbbox((0, 0), s3, font=f_tag)
    d.text(((W - (b3[2] - b3[0])) // 2, 304), s3, font=f_tag, fill=CYAN)

    # Animated golden light pulse sweeping across the title card
    beam_x = int(200 + (W - 400) * ((t_local * 0.45) % 1.0))
    d.line((200, 382, W - 200, 382), fill=(70, 110, 150, 140), width=2)
    d.line((max(200, beam_x - 140), 382, min(W - 200, beam_x + 40), 382), fill=AMBER, width=5)
    d.ellipse((beam_x - 9, 373, beam_x + 9, 391), fill=IVORY, outline=AMBER, width=2)

    # Three pillar cards below (y = 472..884)
    pillars = [
        ("I · PARIS OBSERVATORY (1676)", "OLE RØMER & JUPITER'S MOON IO",
         "40 eclipses across Earth's orbit reveal a", "10-minute lag (Nov 9, 1676) & ~22-minute",
         "full-diameter light-travel delay.", AMBER),
        ("II · KEW GARDENS (1728)", "JAMES BRADLEY & GAMMA DRACONIS",
         "A vertical chimney zenith telescope measures", "20.49\" annual stellar aberration (v/c = 1/10,210),",
         "proving an 8m 12s solar light-time.", CYAN),
        ("III · SURESNES–MONTMARTRE (1849)", "HIPPOLYTE FIZEAU'S 720-TOOTH WHEEL",
         "An 8,633 m terrestrial beam chopped at", "12.60 rps eclipses returning light in 55.1 µs,",
         "clocking light on Earth at 315,300 km/s.", EMERALD),
    ]
    card_w = 548
    gap = 38
    start_x = (W - (3 * card_w + 2 * gap)) // 2
    for idx, (hdr, sub, l1, l2, l3, col) in enumerate(pillars):
        x0 = start_x + idx * (card_w + gap)
        draw_panel(d, (x0, 476, x0 + card_w, 882), fill=PANEL_DARK, border=col, radius=16)
        d.text((x0 + 28, 504), hdr, font=get_font("mono_bold", 19), fill=col)
        d.text((x0 + 28, 544), sub, font=get_font("sans_bold", 24), fill=IVORY)
        d.line((x0 + 28, 590, x0 + card_w - 28, 590), fill=(80, 120, 160, 140), width=1)
        d.text((x0 + 28, 618), l1, font=get_font("sans_reg", 21), fill=MUTED)
        d.text((x0 + 28, 654), l2, font=get_font("sans_reg", 21), fill=MUTED)
        d.text((x0 + 28, 690), l3, font=get_font("sans_semi", 21), fill=IVORY)
        # Mini equation badge at bottom of each pillar
        eqs = ["Δt = Δd / c = +10m 00s", "tan(20.49\") = v / c", "c = 4 · N · L · f₁"]
        d.rounded_rectangle((x0 + 28, 760, x0 + card_w - 28, 842), radius=10, fill=(14, 28, 48, 220), outline=col, width=1)
        d.text((x0 + 52, 786), eqs[idx], font=get_font("mono_bold", 24), fill=col)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s04(plate_dir, shot, t_local, t_global):
    frac = clamp(t_local / max(0.1, shot["shot_dur"]))
    base = render_ken_burns_plate(
        plate_dir, shot["plate"], frac,
        zoom_start=1.01, zoom_end=1.08, pan_x=(14, -14), pan_y=(-6, 8), darken=0.84
    )
    canvas = Image.fromarray(base).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global, tint=(245, 210, 140))

    # Primary-source archival quote card (Descartes letter to Isaac Beeckman, Aug 22, 1634)
    draw_panel(d, (64, 102, 1020, 468), fill=PANEL_DARK, border=CYAN, radius=16)
    d.text((92, 126), "PRIMARY SOURCE · RENÉ DESCARTES TO ISAAC BEECKMAN (AUG 22, 1634)", font=get_font("mono_bold", 19), fill=CYAN)
    d.line((92, 164, 990, 164), fill=(80, 130, 175, 160), width=1)

    q_lines = [
        "“Light reaches our eyes from the luminous object in an instant;",
        "and I declare that if the smallest time delay could ever be",
        "observed in the eclipses of the heavenly bodies, my entire",
        "philosophy of nature would be shaken to its foundations.”",
    ]
    for i, ln in enumerate(q_lines):
        d.text((92, 186 + i * 42), ln, font=get_font("serif_italic", 27), fill=IVORY)

    d.rounded_rectangle((92, 376, 990, 438), radius=10, fill=(24, 38, 62, 220), outline=AMBER, width=1)
    d.text((116, 394), "ORTHODOX ASSUMPTION (350 BCE – 1676 CE):   c = ∞  (Instantaneous Propagation)", font=get_font("mono_bold", 20), fill=AMBER)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s05(plate_dir, shot, t_local, t_global):
    frac = clamp(t_local / max(0.1, shot["shot_dur"]))
    base = render_ken_burns_plate(
        plate_dir, shot["plate"], frac,
        zoom_start=1.01, zoom_end=1.07, pan_x=(-12, 12), pan_y=(-5, 5), darken=0.86
    )
    canvas = Image.fromarray(base).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global, tint=(245, 200, 120))

    # Animated light pulse racing back and forth between the two Tuscan lanterns
    x_a, y_a = 650, 515
    x_b, y_b = 1545, 410
    cyc = (t_local * 0.85) % 1.0
    if cyc < 0.5:
        u = cyc * 2.0
        px = x_a + (x_b - x_a) * u
        py = y_a + (y_b - y_a) * u
        lbl = "OUTBOUND PULSE (OBSERVER A -> B)"
    else:
        u = (cyc - 0.5) * 2.0
        px = x_b + (x_a - x_b) * u
        py = y_b + (y_a - y_b) * u
        lbl = "RETURN PULSE (OBSERVER B -> A)"

    d.line((x_a, y_a, x_b, y_b), fill=(244, 184, 72, 130), width=3)
    d.ellipse((px - 12, py - 12, px + 12, py + 12), fill=AMBER, outline=IVORY, width=2)

    # Bottom-right experimental specification card
    draw_panel(d, (830, 610, 1856, 888), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((860, 634), "GALILEO GALILEI · DISCORSI (TWO NEW SCIENCES, 1638 · DAY 1)", font=get_font("mono_bold", 19), fill=AMBER)
    d.text((860, 674), "Method: Two shuttered lanterns across Tuscan hills (~1 mile / 1.61 km)", font=get_font("sans_semi", 22), fill=IVORY)
    d.text((860, 712), f"Live Beam Phase:  {lbl}", font=get_font("mono_bold", 20), fill=CYAN)
    d.text((860, 754), "Galileo's Verdict: “If not instantaneous, it is extraordinarily rapid.”", font=get_font("serif_italic", 23), fill=MUTED)
    d.text((860, 800), "Why it failed: Human neural reaction delay completely masked the 10.7 µs flight time.", font=get_font("sans_reg", 20), fill=CRIMSON)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s06(plate_dir, shot, t_local, t_global):
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    # Header card: Why Galileo's Hilltop Baseline Could Not Resolve c
    draw_panel(d, (64, 100, W - 64, 480), fill=PANEL_DARK, border=PANEL_BORDER)
    d.text((96, 126), "SIGNAL VS. NOISE: WHY TERRESTRIAL LANTERNS FAILED IN 1638", font=get_font("mono_bold", 21), fill=AMBER)
    d.text((96, 166), "Comparing a 2-Mile Optical Round-Trip Against Human Shutter Reaction Time", font=get_font("sans_bold", 28), fill=IVORY)

    # Track 1: Light round trip (3.22 km @ 299,792 km/s = 10.73 microseconds)
    d.text((96, 232), "1. LIGHT ROUND-TRIP (2 MILES = 3.22 KM)", font=get_font("mono_bold", 20), fill=CYAN)
    d.text((1350, 230), "Δt = 10.73 µs  (0.0000107 s)", font=get_font("mono_bold", 24), fill=CYAN)
    d.rounded_rectangle((96, 268, 1820, 310), radius=8, fill=(16, 28, 46, 230), outline=(70, 115, 160, 180), width=1)
    # Tiny sliver showing 10.7 us vs 200,000 us
    d.rounded_rectangle((98, 270, 112, 308), radius=4, fill=CYAN)
    d.text((130, 276), "<-- Completed 18,600 times before a human nerve impulse reaches the thumb", font=get_font("sans_med", 19), fill=IVORY)

    # Track 2: Human reaction time (200,000 microseconds = 0.20 s)
    d.text((96, 344), "2. HUMAN SHUTTER REACTION FLOOR (EYE -> CORTEX -> THUMB)", font=get_font("mono_bold", 20), fill=CRIMSON)
    d.text((1350, 342), "Δt = 200,000 µs  (0.200 s)", font=get_font("mono_bold", 24), fill=CRIMSON)
    d.rounded_rectangle((96, 380, 1820, 422), radius=8, fill=(16, 28, 46, 230), outline=(70, 115, 160, 180), width=1)
    bar_w = int(1720 * ease_out_cubic(prog(t_local, 0.2, 3.2)))
    if bar_w > 6:
        d.rounded_rectangle((98, 382, 98 + bar_w, 420), radius=6, fill=CRIMSON)
    d.text((116, 388), "18,630 × SLOWER THAN THE LIGHT BEAM", font=get_font("mono_bold", 20), fill=IVORY)

    # Bottom comparison: Terrestrial vs Planetary Baseline (y = 510..888)
    draw_panel(d, (64, 512, 920, 888), fill=PANEL_DARK, border=CRIMSON)
    d.text((96, 540), "TUSCAN HILLTOP BASELINE (1638)", font=get_font("mono_bold", 20), fill=CRIMSON)
    d.text((96, 588), "Distance (2L):     3.22 km", font=get_font("mono_reg", 24), fill=IVORY)
    d.text((96, 634), "Flight Time:       0.0000107 seconds", font=get_font("mono_bold", 24), fill=CRIMSON)
    d.text((96, 680), "Observer Error:   ±0.20 seconds", font=get_font("mono_reg", 24), fill=MUTED)
    d.text((96, 744), "Signal-to-Noise:   0.00005  (UNMEASURABLE)", font=get_font("mono_bold", 22), fill=CRIMSON)

    draw_panel(d, (960, 512, W - 64, 888), fill=PANEL_DARK, border=EMERALD)
    d.text((992, 540), "EARTH ORBITAL DIAMETER BASELINE (1676)", font=get_font("mono_bold", 20), fill=EMERALD)
    d.text((992, 588), "Distance (2 AU):   299,200,000 km", font=get_font("mono_reg", 24), fill=IVORY)
    d.text((992, 634), "Flight Time:       ~998.8 seconds (16m 38s)", font=get_font("mono_bold", 24), fill=EMERALD)
    d.text((992, 680), "Pendulum Error:   ±10 seconds", font=get_font("mono_reg", 24), fill=MUTED)
    d.text((992, 744), "Signal-to-Noise:   ~100 ×   (DECISIVE PROOF)", font=get_font("mono_bold", 22), fill=EMERALD)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s07(plate_dir, shot, t_local, t_global):
    frac = clamp(t_local / max(0.1, shot["shot_dur"]))
    base = render_ken_burns_plate(
        plate_dir, shot["plate"], frac,
        zoom_start=1.02, zoom_end=1.08, pan_x=(-15, 15), pan_y=(-8, 8), darken=0.84
    )
    canvas = Image.fromarray(base).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global, tint=(190, 220, 245))

    # Top-left Navigation & Longitude Card
    draw_panel(d, (64, 102, 860, 464), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((92, 126), "THE LONGITUDE PROBLEM · ROYAL ACADEMY MISSION (1666)", font=get_font("mono_bold", 19), fill=AMBER)
    d.text((92, 166), "Why King Louis XIV Funded the Paris Observatory", font=get_font("sans_bold", 25), fill=IVORY)
    d.line((92, 206, 830, 206), fill=(80, 120, 160, 150), width=1)

    d.text((92, 224), "• Earth Rotation Rate:   360° / 24h  =  15.0° per hour", font=get_font("mono_bold", 20), fill=CYAN)
    d.text((92, 264), "• 4 Minutes Clock Drift:  1.0° Longitude Error (~111 km)", font=get_font("mono_reg", 20), fill=IVORY)
    d.text((92, 304), "• Marine Pendulum Clocks: Pitching waves wreck gravity period", font=get_font("mono_reg", 20), fill=CRIMSON)

    d.rounded_rectangle((92, 354, 830, 434), radius=10, fill=(16, 32, 54, 225), outline=AMBER, width=1)
    d.text((114, 368), "SOLUTION: Use Jupiter's eclipsing moons as a master clock", font=get_font("sans_semi", 20), fill=AMBER)
    d.text((114, 398), "visible simultaneously from Paris and across the ocean.", font=get_font("sans_reg", 19), fill=IVORY)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s08(plate_dir, shot, t_local, t_global):
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    # Left: Orbital animation of Jupiter & the 4 Galilean moons with shadow cone
    draw_panel(d, (56, 100, 1140, 888), fill=PANEL_DARK, border=PANEL_BORDER)
    d.text((84, 124), "THE JOVIAN CELESTIAL CLOCK · 4 GALILEAN MOONS", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((84, 158), "Io's 42h 28m 35s Umbral Eclipse = Universal Reference Tick", font=get_font("sans_med", 20), fill=MUTED)

    jx, jy = 520, 520
    # Sunlight rays from left
    for ry in range(380, 661, 40):
        d.line((76, ry, 250, ry), fill=(244, 184, 72, 110), width=2)
    d.text((84, 344), "SUNLIGHT ->", font=get_font("mono_bold", 17), fill=AMBER)

    # Jupiter's dark umbral shadow cone extending right
    d.polygon([(jx, jy - 52), (1116, jy - 26), (1116, jy + 26), (jx, jy + 52)], fill=(4, 7, 14, 235), outline=(90, 110, 140, 120))
    d.text((840, jy - 12), "JUPITER UMBRAL SHADOW CONE", font=get_font("mono_bold", 16), fill=DIM)

    # 4 Galilean Moon orbits
    moons = [
        ("I · IO", 125, 1.769, AMBER, 9),
        ("II · EUROPA", 185, 3.551, CYAN, 7),
        ("III · GANYMEDE", 255, 7.155, EMERALD, 8),
        ("IV · CALLISTO", 330, 16.689, VIOLET, 7),
    ]
    for name, rad, period_d, col, mr in moons:
        d.ellipse((jx - rad, jy - rad, jx + rad, jy + rad), outline=(65, 100, 140, 110), width=1)
        omega = (2.0 * math.pi / period_d) * (t_local * 0.65)
        mx = jx + rad * math.cos(omega)
        my = jy + rad * math.sin(omega)
        in_shadow = (mx > jx) and (abs(my - jy) < 42)
        m_col = CRIMSON if in_shadow else col
        d.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=m_col, outline=IVORY, width=2)
        d.text((mx + 12, my - 10), f"{name}{' [ECLIPSED]' if in_shadow else ''}", font=get_font("mono_bold", 15), fill=m_col)

    # Jupiter body at center
    d.ellipse((jx - 52, jy - 52, jx + 52, jy + 52), fill=(216, 164, 104, 255), outline=AMBER, width=3)
    d.chord((jx - 52, jy - 52, jx + 52, jy + 52), start=-90, end=90, fill=(28, 36, 54, 235))
    d.text((jx - 38, jy + 62), "JUPITER", font=get_font("mono_bold", 17), fill=IVORY)

    # Right: Table of Galilean Periods & Longitude Formula
    draw_panel(d, (1168, 100, W - 56, 888), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((1198, 126), "CASSINI'S EPHEMERIDES (1668)", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((1198, 164), "Synodic Eclipse Periods", font=get_font("sans_bold", 25), fill=IVORY)

    rows = [
        ("Io (Jupiter I)", "1d 18h 28m 36s", "42.48 h", AMBER),
        ("Europa (II)", "3d 13h 17m 54s", "85.30 h", CYAN),
        ("Ganymede (III)", "7d 03h 59m 36s", "171.99 h", EMERALD),
        ("Callisto (IV)", "16d 18h 05m 07s", "402.08 h", VIOLET),
    ]
    for idx, (m_name, p_str, h_str, col) in enumerate(rows):
        ry = 224 + idx * 102
        d.rounded_rectangle((1198, ry, W - 86, ry + 86), radius=10, fill=(15, 28, 48, 220), outline=col, width=1)
        d.text((1220, ry + 14), m_name, font=get_font("sans_bold", 21), fill=col)
        d.text((1220, ry + 46), f"Period: {p_str}  ({h_str})", font=get_font("mono_reg", 18), fill=IVORY)

    d.rounded_rectangle((1198, 650, W - 86, 858), radius=12, fill=(18, 34, 58, 235), outline=AMBER, width=2)
    d.text((1222, 672), "WHY IO WAS THE PRIZE CLOCK:", font=get_font("mono_bold", 19), fill=AMBER)
    d.text((1222, 710), "Orbiting fastest and closest to", font=get_font("sans_reg", 20), fill=IVORY)
    d.text((1222, 740), "Jupiter's equator, Io enters shadow", font=get_font("sans_reg", 20), fill=IVORY)
    d.text((1222, 770), "every 42.5 hours with knife-edge", font=get_font("sans_reg", 20), fill=IVORY)
    d.text((1222, 800), "precision — 207 eclipses per year.", font=get_font("sans_bold", 20), fill=CYAN)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s09(plate_dir, shot, t_local, t_global):
    frac = clamp(t_local / max(0.1, shot["shot_dur"]))
    base = render_ken_burns_plate(
        plate_dir, shot["plate"], frac,
        zoom_start=1.01, zoom_end=1.08, pan_x=(12, -12), pan_y=(-6, 6), darken=0.85
    )
    canvas = Image.fromarray(base).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global, tint=(210, 225, 245))

    # Top-left Uraniborg Expedition Card
    draw_panel(d, (64, 102, 860, 412), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((92, 126), "URANIBORG EXPEDITION · ISLAND OF HVEN (1671)", font=get_font("mono_bold", 19), fill=AMBER)
    d.text((92, 164), "Jean Picard & Ole Rømer Synchronize With Cassini in Paris", font=get_font("sans_bold", 23), fill=IVORY)
    d.line((92, 204, 832, 204), fill=(80, 120, 160, 150), width=1)
    d.text((92, 224), "• Site A: Tycho Brahe's Uraniborg (55°54'N, 12°41'E)", font=get_font("mono_reg", 19), fill=CYAN)
    d.text((92, 260), "• Site B: Paris Observatory        (48°50'N, 02°20'E)", font=get_font("mono_reg", 19), fill=AMBER)
    d.text((92, 298), "• Measured Io Eclipse Time Offset:  Δt = 41m 22s", font=get_font("mono_bold", 20), fill=EMERALD)
    d.text((92, 338), "• Exact Longitude Difference:       Δλ = 10° 20' 30\" East", font=get_font("mono_bold", 20), fill=IVORY)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s10(plate_dir, shot, t_local, t_global):
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    # Left: The 1693 Carte de France Corrigée + Overview
    draw_panel(d, (56, 100, 860, 888), fill=PANEL_DARK, border=PANEL_BORDER)
    d.text((86, 126), "CARTE DE FRANCE CORRIGÉE (1671–1693)", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((86, 162), "Io Eclipse Timing Redraws the Kingdom", font=get_font("sans_bold", 24), fill=IVORY)

    # Stylized coastline comparison polygon (Old Sanson 1679 vs Corrected Academy Map)
    old_coast = [(340, 250), (220, 310), (160, 410), (240, 520), (210, 650), (350, 740), (580, 730), (650, 560), (620, 340)]
    new_coast = [(355, 260), (275, 320), (235, 410), (295, 515), (270, 640), (365, 725), (565, 715), (630, 555), (605, 345)]
    d.polygon(old_coast, fill=(232, 82, 68, 45), outline=CRIMSON)
    d.polygon(new_coast, fill=(86, 208, 228, 70), outline=CYAN)
    for i in range(len(old_coast)):
        d.line((old_coast[i][0], old_coast[i][1], new_coast[i][0], new_coast[i][1]), fill=AMBER, width=2)
    # Paris marker
    d.ellipse((430, 370, 446, 386), fill=AMBER, outline=IVORY, width=2)
    d.text((456, 366), "PARIS OBSERVATORY", font=get_font("mono_bold", 17), fill=AMBER)
    d.text((86, 780), "CRIMSON OUTLINE: 1679 Sanson Map (Overestimated West Coast)", font=get_font("mono_reg", 17), fill=CRIMSON)
    d.text((86, 814), "CYAN OUTLINE:    Io-Timed Academy Map (~20% Territory Trimmed)", font=get_font("mono_bold", 17), fill=CYAN)

    # Right: The 40-Eclipse Paris Observatory Ledger (1668–1676)
    draw_panel(d, (890, 100, W - 56, 888), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((922, 126), "PARIS OBSERVATORY LEDGER · 40 ECLIPSES OF IO (1668–1676)", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((922, 162), "Why Did the Celestial Clock Drift Early and Late Every Year?", font=get_font("sans_bold", 24), fill=IVORY)

    ledger_rows = [
        ("1671 Mar 19", "Immersion (G->H)", "Approaching Jupiter", "42h 28m 21s", "-14s / orbit (EARLY)", CYAN),
        ("1672 Apr 07", "Immersion (G->H)", "Approaching Jupiter", "42h 28m 22s", "-13s / orbit (EARLY)", CYAN),
        ("1672 Jul 29", "Emersion  (K->L)", "Receding from Jupiter", "42h 28m 50s", "+15s / orbit (LATE)", CRIMSON),
        ("1673 May 18", "Immersion (G->H)", "Approaching Jupiter", "42h 28m 20s", "-15s / orbit (EARLY)", CYAN),
        ("1675 Oct 14", "Emersion  (K->L)", "Receding from Jupiter", "42h 28m 49s", "+14s / orbit (LATE)", CRIMSON),
        ("1676 Aug 22", "Emersion  (K)",    "Post-Opposition Start", "17:09:10 PM", "Baseline Reference", AMBER),
        ("1676 Nov 09", "Emersion  (L)",    "40 Orbits Receding",    "17:35:45 PM", "+10m 00s CUMULATIVE!", CRIMSON),
    ]
    n_vis = min(len(ledger_rows), int(2 + t_local * 0.75))
    for idx in range(n_vis):
        dt_s, kind, earth_st, obs_t, resid, col = ledger_rows[idx]
        ry = 222 + idx * 88
        d.rounded_rectangle((922, ry, W - 88, ry + 74), radius=10, fill=(14, 26, 44, 225), outline=col, width=1)
        d.text((942, ry + 12), f"{dt_s}   ·   {kind}", font=get_font("mono_bold", 19), fill=IVORY)
        d.text((942, ry + 42), f"Earth State: {earth_st}   |   Measured: {obs_t}", font=get_font("sans_reg", 18), fill=MUTED)
        d.text((1490, ry + 24), resid, font=get_font("mono_bold", 19), fill=col)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s11(plate_dir, shot, t_local, t_global):
    """
    Reconstitution of Ole Rømer's famous Fig. 1 from Journal des Sçavans (Dec 7, 1676):
    Sun (A), Earth orbit (E-F-G-H-K-L), Jupiter (B), Io orbit & shadow cone (C-D).
    """
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    # Left: Geometric Orbital Diagram (x = 56..1180, y = 100..888)
    draw_panel(d, (56, 100, 1180, 888), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((86, 124), "RØMER'S GEOMETRIC DIAGRAM · JOURNAL DES SÇAVANS (DEC 7, 1676)", font=get_font("mono_bold", 19), fill=AMBER)

    # Sun A at center-bottom of diagram, Jupiter B at top-center
    ax, ay = 618, 608
    bx, by = 618, 278
    r_earth = 172

    # Jupiter shadow cone pointing straight up (away from Sun A)
    d.polygon([(bx - 26, by), (bx - 38, 168), (bx + 38, 168), (bx + 26, by)], fill=(4, 8, 15, 245), outline=(110, 140, 180, 160))
    # Io orbit around B
    r_io = 54
    d.ellipse((bx - r_io, by - r_io, bx + r_io, by + r_io), outline=(234, 178, 72, 170), width=2)
    # C (Immersion on left of shadow) & D (Emersion on right of shadow)
    cx_pt, cy_pt = bx - 28, by - 44
    dx_pt, dy_pt = bx + 28, by - 44
    d.ellipse((cx_pt - 7, cy_pt - 7, cx_pt + 7, cy_pt + 7), fill=CYAN, outline=IVORY, width=2)
    d.text((cx_pt - 165, cy_pt - 12), "C (IMMERSION)", font=get_font("mono_bold", 17), fill=CYAN)
    d.ellipse((dx_pt - 7, dy_pt - 7, dx_pt + 7, dy_pt + 7), fill=CRIMSON, outline=IVORY, width=2)
    d.text((dx_pt + 16, dy_pt - 12), "D (EMERSION)", font=get_font("mono_bold", 17), fill=CRIMSON)

    # Jupiter B
    d.ellipse((bx - 24, by - 24, bx + 24, by + 24), fill=(218, 166, 98, 255), outline=AMBER, width=2)
    d.text((bx - 8, by - 11), "B", font=get_font("mono_bold", 19), fill=BG_ABYSS)

    # Earth Orbit circle around Sun A (points E, F, G, H, K, L)
    d.ellipse((ax - r_earth, ay - r_earth, ax + r_earth, ay + r_earth), outline=(110, 160, 210, 190), width=3)
    # Approaching arc G->H (left side, cyan) & Receding arc K->L (right side, crimson)
    d.arc((ax - r_earth, ay - r_earth, ax + r_earth, ay + r_earth), start=195, end=250, fill=CYAN, width=7)
    d.arc((ax - r_earth, ay - r_earth, ax + r_earth, ay + r_earth), start=290, end=345, fill=CRIMSON, width=7)

    pts = [
        ("E (Conjunction)", 90, DIM),
        ("F", 165, MUTED),
        ("G", 200, CYAN),
        ("H", 248, CYAN),
        ("K", 292, CRIMSON),
        ("L", 342, CRIMSON),
    ]
    for lbl, deg, col in pts:
        rad_a = math.radians(deg)
        px = ax + r_earth * math.cos(rad_a)
        py = ay + r_earth * math.sin(rad_a)
        d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=col, outline=IVORY, width=2)
        if deg == 90:
            d.text((px + 14, py + 6), lbl, font=get_font("mono_bold", 17), fill=col)
        else:
            ox = -42 if math.cos(rad_a) < -0.2 else 16
            oy = 10 if math.sin(rad_a) > 0 else -24
            d.text((px + ox, py + oy), lbl, font=get_font("mono_bold", 18), fill=col)

    # Sun A at center
    d.ellipse((ax - 26, ay - 26, ax + 26, ay + 26), fill=AMBER, outline=IVORY, width=3)
    d.text((ax - 8, ay - 11), "A", font=get_font("mono_bold", 19), fill=BG_ABYSS)
    d.text((ax - 42, ay + 32), "SUN (A)", font=get_font("mono_bold", 17), fill=AMBER)

    # Animated Earth moving from G->H then K->L with sightline to C or D
    frac = clamp(t_local / max(0.1, shot["shot_dur"]))
    if frac < 0.5:
        u = frac * 2.0
        deg_e = 200 + 48 * u
        target_x, target_y = cx_pt, cy_pt
        beam_col = CYAN
        phase_lbl = "APPROACHING ARC (G -> H): SIGHTLINE TO IMMERSION C SHORTENS"
    else:
        u = (frac - 0.5) * 2.0
        deg_e = 292 + 50 * u
        target_x, target_y = dx_pt, dy_pt
        beam_col = CRIMSON
        phase_lbl = "RECEDING ARC (K -> L): SIGHTLINE TO EMERSION D LENGTHENS (+Δd)"

    ex = ax + r_earth * math.cos(math.radians(deg_e))
    ey = ay + r_earth * math.sin(math.radians(deg_e))
    d.line((target_x, target_y, ex, ey), fill=beam_col, width=3)
    d.ellipse((ex - 12, ey - 12, ex + 12, ey + 12), fill=beam_col, outline=IVORY, width=3)
    d.rounded_rectangle((84, 830, 1152, 872), radius=8, fill=(12, 22, 38, 235), outline=beam_col, width=1)
    d.text((104, 840), phase_lbl, font=get_font("mono_bold", 18), fill=beam_col)

    # Right Explanatory Card (x = 1206..1864, y = 100..888)
    draw_panel(d, (1206, 100, W - 56, 888), fill=PANEL_DARK, border=PANEL_BORDER)
    d.text((1236, 126), "THE DOPPLER-LIKE LIGHT TIME GEOMETRY", font=get_font("mono_bold", 19), fill=AMBER)
    d.text((1236, 168), "1. Approaching Arc (G -> H):", font=get_font("sans_bold", 23), fill=CYAN)
    d.text((1236, 204), "Earth moves toward Jupiter at 29.8 km/s.", font=get_font("sans_reg", 20), fill=IVORY)
    d.text((1236, 236), "We see Io vanish into shadow at C.", font=get_font("sans_reg", 20), fill=IVORY)
    d.text((1236, 268), "Each orbit's light travels a shorter", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((1236, 300), "distance -> eclipses arrive EARLY.", font=get_font("mono_bold", 19), fill=CYAN)

    d.line((1236, 350, W - 86, 350), fill=(80, 120, 160, 140), width=1)

    d.text((1236, 376), "2. Receding Arc (K -> L):", font=get_font("sans_bold", 23), fill=CRIMSON)
    d.text((1236, 412), "Earth moves away from Jupiter.", font=get_font("sans_reg", 20), fill=IVORY)
    d.text((1236, 444), "Jupiter's body hides C, so we see", font=get_font("sans_reg", 20), fill=IVORY)
    d.text((1236, 476), "Io emerge from shadow at D.", font=get_font("sans_reg", 20), fill=IVORY)
    d.text((1236, 508), "Each orbit's light must chase a", font=get_font("sans_reg", 20), fill=MUTED)
    d.text((1236, 540), "receding Earth -> eclipses arrive LATE.", font=get_font("mono_bold", 19), fill=CRIMSON)

    d.rounded_rectangle((1236, 610, W - 86, 854), radius=12, fill=(16, 30, 52, 235), outline=AMBER, width=2)
    d.text((1260, 634), "FUNDAMENTAL EQUATION:", font=get_font("mono_bold", 19), fill=AMBER)
    d.text((1260, 682), "T_obs = N · T_0  +  Δd / c", font=get_font("mono_bold", 26), fill=IVORY)
    d.text((1260, 738), "• Approaching:  Δd < 0  (Early)", font=get_font("mono_reg", 19), fill=CYAN)
    d.text((1260, 774), "• Receding:     Δd > 0  (Late)", font=get_font("mono_reg", 19), fill=CRIMSON)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s12(plate_dir, shot, t_local, t_global):
    """
    Live plot of cumulative time delay across 40 consecutive revolutions of Io (Aug -> Nov 9, 1676).
    """
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    draw_panel(d, (56, 100, W - 56, 888), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((92, 126), "COMPOUNDING THE SIGNAL · 40 CONSECUTIVE ORBITS OF IO (AUG – NOV 9, 1676)", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((92, 162), "Single-Orbit Lag (~15s) Is Small — Summing 40 Orbits Along Arc K -> L Builds a 10-Minute Signal", font=get_font("sans_bold", 24), fill=IVORY)

    # Chart axes: x = 180..1760 (Orbit 0 to Orbit 40), y = 780..250 (0 min to 10 min delay)
    gx0, gy0, gx1, gy1 = 190, 770, 1750, 250
    d.line((gx0, gy0, gx1, gy0), fill=IVORY, width=2)
    d.line((gx0, gy0, gx0, gy1), fill=IVORY, width=2)

    # Horizontal grid lines (0, 2, 4, 6, 8, 10 minutes)
    for m_val in range(0, 11, 2):
        yy = int(gy0 - (m_val / 10.0) * (gy0 - gy1))
        d.line((gx0, yy, gx1, yy), fill=(65, 100, 140, 110), width=1)
        d.text((100, yy - 12), f"+{m_val:02d} min", font=get_font("mono_bold", 18), fill=MUTED)

    # Vertical grid lines (Orbit 0, 10, 20, 30, 40)
    labels_x = [
        (0, "Orbit 0 (Aug 22)"),
        (10, "Orbit 10 (Sep 09)"),
        (20, "Orbit 20 (Sep 27)"),
        (30, "Orbit 30 (Oct 15)"),
        (40, "Orbit 40 (Nov 09)"),
    ]
    for orb_n, lbl in labels_x:
        xx = int(gx0 + (orb_n / 40.0) * (gx1 - gx0))
        d.line((xx, gy0, xx, gy1), fill=(65, 100, 140, 110), width=1)
        d.text((xx - 70, gy0 + 18), lbl, font=get_font("mono_reg", 17), fill=MUTED)

    # Zero-delay reference line (Cassini's Instantaneous Light Prediction)
    d.line((gx0, gy0, gx1, gy0), fill=CYAN, width=3)
    d.text((980, gy0 - 34), "CASSINI INSTANTANEOUS LIGHT TABLE (c = ∞ -> 0m 00s Delay)", font=get_font("mono_bold", 18), fill=CYAN)

    # Animated curve up to current orbit
    frac = ease_in_out_cubic(clamp(t_local / (shot["shot_dur"] * 0.82)))
    max_orb = int(round(40 * frac))
    pts = []
    for k in range(max_orb + 1):
        u = k / 40.0
        # Slight non-linear chord projection along Earth's receding arc K->L
        delay_m = 10.0 * (0.82 * u + 0.18 * (u ** 1.35))
        px = int(gx0 + u * (gx1 - gx0))
        py = int(gy0 - (delay_m / 10.0) * (gy0 - gy1))
        pts.append((px, py))

    if len(pts) > 1:
        d.line(pts, fill=AMBER, width=5)
    for idx_p, (px, py) in enumerate(pts):
        if idx_p % 2 == 0 or idx_p == len(pts) - 1:
            d.ellipse((px - 6, py - 6, px + 6, py + 6), fill=CRIMSON if idx_p == 40 else AMBER, outline=IVORY, width=2)

    # Live readout card in upper-left of plot
    cur_u = max_orb / 40.0
    cur_del_m = 10.0 * (0.82 * cur_u + 0.18 * (cur_u ** 1.35))
    cur_km = int(1.28e8 * cur_u)
    draw_panel(d, (230, 270, 880, 470), fill=(12, 22, 38, 240), border=AMBER)
    d.text((256, 292), f"IO REVOLUTION COUNT:   {max_orb:02d} / 40 ORBITS", font=get_font("mono_bold", 21), fill=AMBER)
    d.text((256, 332), f"ADDED LIGHT PATH (Δd): +{cur_km:,} km", font=get_font("mono_reg", 20), fill=IVORY)
    d.text((256, 372), f"CUMULATIVE ECLIPSE LAG: +{cur_del_m:04.1f} minutes ({int(cur_del_m*60)} s)", font=get_font("mono_bold", 21), fill=CRIMSON)
    d.text((256, 416), "Nov 9, 1676 Result: Predicted 17:25:45 -> Observed 17:35:45", font=get_font("sans_semi", 18), fill=EMERALD)

    return Image.alpha_composite(canvas, ov).convert("RGB")


def render_s13(plate_dir, shot, t_local, t_global):
    """
    Showcase of Rømer's Dec 7, 1676 Journal des Sçavans paper & comparison with modern 16m 38s (2 AU).
    """
    canvas = Image.fromarray(BASE_TECH_CANVAS).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_particles(d, t_global)

    # Left: Archival Facsimile Card of Journal des Sçavans (7 Décembre 1676, p. 233)
    draw_panel(d, (56, 100, 960, 888), fill=(22, 26, 36, 242), border=CYAN)
    d.text((88, 126), "PRIMARY SOURCE · JOURNAL DES SÇAVANS (7 DÉCEMBRE 1676)", font=get_font("mono_bold", 19), fill=CYAN)
    d.text((88, 166), "“Démonstration touchant le mouvement de la lumière”", font=get_font("serif_bold", 27), fill=AMBER)
    d.text((88, 204), "By M. Römer, Royal Academy of Sciences (Phil. Trans. June 25, 1677)", font=get_font("sans_reg", 19), fill=MUTED)
    d.line((88, 242, 928, 242), fill=(90, 130, 170, 150), width=1)

    quote_lines = [
        "“Wait until the Earth moves from K to L across forty",
        "revolutions of the first satellite: the delay of the",
        "eclipses becomes sensible, and demonstrates that light",
        "requires about eleven minutes for a distance equal to",
        "the half-diameter of the terrestrial orbit, or about",
        "twenty-two minutes for the entire diameter.”",
    ]
    for i, ln in enumerate(quote_lines):
        d.text((88, 268 + i * 44), ln, font=get_font("serif_italic", 26), fill=IVORY)

    d.rounded_rectangle((88, 560, 928, 852), radius=12, fill=(12, 22, 38, 235), outline=BRASS_BORDER, width=2)
    d.text((114, 586), "HISTORICAL MILESTONE:", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((114, 626), "• First quantitative proof in human history that c is finite", font=get_font("sans_med", 21), fill=IVORY)
    d.text((114, 668), "• Published in just 2.5 pages with 1 geometric woodcut", font=get_font("sans_med", 21), fill=IVORY)
    d.text((114, 710), "• Translated into English by the Royal Society within 6 months", font=get_font("sans_med", 21), fill=CYAN)
    d.text((114, 752), "• Surviving 60-eclipse folio preserved at Paris Observatory", font=get_font("sans_med", 21), fill=EMERALD)

    # Right: Rømer's 1676 Estimate vs Modern Relativistic Light-Time Across 1 AU and 2 AU
    draw_panel(d, (990, 100, W - 56, 888), fill=PANEL_DARK, border=BRASS_BORDER)
    d.text((1022, 126), "LIGHT-TIME ACROSS EARTH'S ORBIT (1 AU vs 2 AU)", font=get_font("mono_bold", 20), fill=AMBER)
    d.text((1022, 166), "Comparing Rømer (1676) With Modern Telemetry", font=get_font("sans_bold", 24), fill=IVORY)

    # Bar 1: 1 AU Radius (Sun to Earth)
    d.text((1022, 236), "1. ORBITAL RADIUS (1 AU = 149,597,871 KM)", font=get_font("mono_bold", 19), fill=CYAN)
    d.text((1022, 274), "Rømer (1676):      ~11m 00s  (660.0 s)", font=get_font("mono_bold", 21), fill=AMBER)
    d.rounded_rectangle((1022, 308, 1780, 342), radius=8, fill=AMBER)
    d.text((1022, 360), "Modern Exact Value: 08m 19s  (499.0 s)", font=get_font("mono_bold", 21), fill=EMERALD)
    d.rounded_rectangle((1022, 394, 1594, 428), radius=8, fill=EMERALD)

    # Bar 2: 2 AU Diameter (Full Orbit Chord)
    d.text((1022, 484), "2. ORBITAL DIAMETER (2 AU = 299,195,741 KM)", font=get_font("mono_bold", 19), fill=CYAN)
    d.text((1022, 522), "Rømer (1676):      ~22m 00s  (1,320.0 s)", font=get_font("mono_bold", 21), fill=AMBER)
    d.rounded_rectangle((1022, 556, 1810, 590), radius=8, fill=AMBER)
    d.text((1022, 608), "Modern Exact Value: 16m 38s  (998.0 s)", font=get_font("mono_bold", 21), fill=EMERALD)
    d.rounded_rectangle((1022, 642, 1618, 676), radius=8, fill=EMERALD)

    d.rounded_rectangle((1022, 720, W - 88, 852), radius=10, fill=(16, 30, 50, 235), outline=CYAN, width=1)
    d.text((1046, 742), "Order-of-magnitude triumph: From infinity (∞) down to", font=get_font("sans_semi", 20), fill=IVORY)
    d.text((1046, 774), "within 24% of the modern speed of light on the very", font=get_font("sans_semi", 20), fill=IVORY)
    d.text((1046, 806), "first attempt in human history.", font=get_font("sans_bold", 20), fill=AMBER)

    return Image.alpha_composite(canvas, ov).convert("RGB")

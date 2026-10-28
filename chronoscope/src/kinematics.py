#!/usr/bin/env python3
"""
Exact kinematic and geometric models of the Antikythera Mechanism:
- 60-degree triangular bronze gear tooth polygons & multi-spoke wheel renderer
- Exact Metonic/Sidereal gear train ratios: (64/38) * (48/24) * (127/32) = 254/19
- Exact Hipparchus pin-and-slot epicyclic differential (k1/k2 on e3 turntable)
- 5-turn Metonic (235-month) and 4-turn Saros (223-month) Archimedean spiral dials
"""
import math
from typing import List, Tuple

# Palette constants (RGBA / RGB)
BRONZE_BASE = (198, 138, 62)
BRONZE_SPEC = (244, 198, 126)
BRONZE_DARK = (98, 64, 24)
PATINA_BASE = (46, 138, 120)
PATINA_SPEC = (94, 224, 198)
PATINA_DARK = (22, 68, 60)
XRAY_CYAN = (108, 229, 255)
XRAY_DEEP = (24, 62, 88)
CRIMSON = (226, 85, 73)
GOLD_BRIGHT = (248, 206, 108)
PARCHMENT = (243, 239, 230)
SLATE_MUTED = (155, 174, 194)

# Corinthian Calendar Months inscribed on the 235-month Metonic spiral (Freeth et al. 2008)
CORINTHIAN_MONTHS = [
    ("1", "ΦΟΙΝΙΚΑΙΟΣ", "Phoinikaios"),
    ("2", "ΚΡΑΝΕΙΟΣ", "Kraneios"),
    ("3", "ΛΑΝΟΤΡΟΠΙΟΣ", "Lanotropios"),
    ("4", "ΜΑΧΑΝΕΥΣ", "Machaneus"),
    ("5", "ΔΩΔΕΚΑΤΕΥΣ", "Dodekateus"),
    ("6", "ΕΥΚΛΕΙΟΣ", "Eukleios"),
    ("7", "ΑΡΤΕΜΙΣΙΟΣ", "Artemisios"),
    ("8", "ΨΥΔΡΕΥΣ", "Psydreus"),
    ("9", "ΓΑΜΙΛΙΟΣ", "Gamilios"),
    ("10", "ΑΓΡΙΑΝΙΟΣ", "Agrianios"),
    ("11", "ΠΑΝΑΜΟΣ", "Panamos"),
    ("12", "ΑΠΕΛΛΑΙΟΣ", "Apellaios"),
]

# Attested Saros Eclipse Glyph cells (sample subset across the 223-month spiral)
# Sigma (Σ) = Selene (Lunar Eclipse), Eta (Η) = Helios (Solar Eclipse)
SAROS_ECLIPSE_CELLS = {
    8: "Σ",
    13: "Η·Σ",
    20: "Σ",
    25: "Σ·Η",
    32: "Σ",
    38: "Η",
    44: "Σ",
    55: "Σ·Η",
    61: "Σ",
    67: "Η·Σ",
    73: "Σ",
    79: "Η",
    91: "Σ·Η",
    97: "Σ",
    108: "Σ·Η",
    114: "Σ",
    120: "Η",
    126: "Σ",
    137: "Σ·Η",
    143: "Σ",
    149: "Η·Σ",
    155: "Σ",
    167: "Σ·Η",
    173: "Σ",
    179: "Η",
    190: "Σ·Η",
    196: "Σ",
    202: "Η·Σ",
    208: "Σ",
    220: "Σ·Η",
}


def gear_tooth_polygon(
    cx: float,
    cy: float,
    r_pitch: float,
    teeth: int,
    phase_rad: float = 0.0,
) -> List[Tuple[float, float]]:
    """
    Generate the 2*N vertex polygon for a Hellenistic 60-degree triangular-tooth bronze gear.
    To ensure visual clarity at 1080p even for 127- or 223-tooth gears, tooth height scales
    smoothly with pitch radius and tooth count.
    """
    pts = []
    # Circular pitch = 2 * pi * r_pitch / teeth
    pitch = (2.0 * math.pi * r_pitch) / max(teeth, 8)
    # 60-degree equilateral triangle height = (sqrt(3)/2) * pitch, clamped for crisp screen rendering
    half_h = max(2.2, min(7.5, 0.44 * pitch))
    r_outer = r_pitch + half_h
    r_inner = max(4.0, r_pitch - half_h)
    dtheta = (2.0 * math.pi) / teeth

    for i in range(teeth):
        a_tip = phase_rad + i * dtheta
        a_root = a_tip + 0.5 * dtheta
        pts.append((cx + r_outer * math.cos(a_tip), cy + r_outer * math.sin(a_tip)))
        pts.append((cx + r_inner * math.cos(a_root), cy + r_inner * math.sin(a_root)))
    return pts


def draw_bronze_gear(
    draw,
    cx: float,
    cy: float,
    r_pitch: float,
    teeth: int,
    phase_rad: float,
    palette: str = "bronze",
    spokes: int = 4,
    label: str = "",
    font_label=None,
    highlight_tooth: bool = False,
):
    """
    Render a rich multi-layered ancient bronze gear wheel with triangular teeth,
    cutout spokes, central hub, and rotational orientation markers.
    """
    if palette == "patina":
        c_base, c_spec, c_dark = PATINA_BASE, PATINA_SPEC, PATINA_DARK
    elif palette == "xray":
        c_base, c_spec, c_dark = (42, 128, 165), XRAY_CYAN, XRAY_DEEP
    elif palette == "crimson":
        c_base, c_spec, c_dark = (165, 58, 50), (245, 130, 118), (78, 24, 20)
    else:
        c_base, c_spec, c_dark = BRONZE_BASE, BRONZE_SPEC, BRONZE_DARK

    # 1. Soft drop shadow
    shadow_pts = gear_tooth_polygon(cx + 4, cy + 5, r_pitch, teeth, phase_rad)
    draw.polygon(shadow_pts, fill=(4, 6, 10))

    # 2. Outer tooth polygon
    poly_pts = gear_tooth_polygon(cx, cy, r_pitch, teeth, phase_rad)
    draw.polygon(poly_pts, fill=c_base, outline=c_spec)

    # 3. Inner rim ring
    r_rim_out = max(8.0, r_pitch * 0.80)
    r_rim_in = max(6.0, r_pitch * 0.70)
    r_hub = max(5.0, r_pitch * 0.24)

    draw.ellipse(
        (cx - r_rim_out, cy - r_rim_out, cx + r_rim_out, cy + r_rim_out),
        fill=c_dark,
        outline=c_spec,
        width=2,
    )

    # 4. Spokes or solid web with lightening holes
    if r_pitch >= 34 and spokes > 0:
        # Dark void behind spokes
        draw.ellipse(
            (cx - r_rim_in, cy - r_rim_in, cx + r_rim_in, cy + r_rim_in),
            fill=(11, 16, 23),
            outline=c_base,
            width=1,
        )
        spoke_w = max(5.0, r_pitch * 0.13)
        for s in range(spokes):
            ang = phase_rad + s * (2.0 * math.pi / spokes)
            ca, sa = math.cos(ang), math.sin(ang)
            pa, qa = -sa, ca
            w0 = spoke_w * 0.62
            w1 = spoke_w * 0.45
            p1 = (cx + r_hub * 0.7 * ca + w0 * pa, cy + r_hub * 0.7 * sa + w0 * qa)
            p2 = (cx + r_hub * 0.7 * ca - w0 * pa, cy + r_hub * 0.7 * sa - w0 * qa)
            p3 = (cx + r_rim_in * 1.02 * ca - w1 * pa, cy + r_rim_in * 1.02 * sa - w1 * qa)
            p4 = (cx + r_rim_in * 1.02 * ca + w1 * pa, cy + r_rim_in * 1.02 * sa + w1 * qa)
            draw.polygon([p1, p2, p3, p4], fill=c_base, outline=c_spec)
    else:
        # Rotating witness mark on solid small gear
        mx = cx + r_pitch * 0.52 * math.cos(phase_rad)
        my = cy + r_pitch * 0.52 * math.sin(phase_rad)
        draw.line([(cx, cy), (mx, my)], fill=c_spec, width=2)

    # 5. Central hub & square bronze arbor
    draw.ellipse(
        (cx - r_hub, cy - r_hub, cx + r_hub, cy + r_hub),
        fill=c_base,
        outline=c_spec,
        width=2,
    )
    arbor_r = max(3.0, r_hub * 0.42)
    arbor_pts = []
    for k in range(4):
        a = phase_rad + k * (math.pi / 2.0) + math.pi / 4.0
        arbor_pts.append((cx + arbor_r * math.cos(a), cy + arbor_r * math.sin(a)))
    draw.polygon(arbor_pts, fill=(18, 22, 30), outline=c_spec)

    # 6. Optional highlight marker on tooth #0
    if highlight_tooth:
        tx = cx + (r_pitch + 4) * math.cos(phase_rad)
        ty = cy + (r_pitch + 4) * math.sin(phase_rad)
        draw.ellipse((tx - 4, ty - 4, tx + 4, ty + 4), fill=GOLD_BRIGHT, outline=(20, 20, 20))

    # 7. Optional label
    if label and font_label is not None:
        bbox = draw.textbbox((0, 0), label, font=font_label)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        lx, ly = cx - tw / 2, cy + r_pitch + 12
        draw.rounded_rectangle(
            (lx - 8, ly - 3, lx + tw + 8, ly + th + 5),
            radius=5,
            fill=(10, 15, 22, 225),
            outline=c_spec,
            width=1,
        )
        draw.text((lx, ly), label, font=font_label, fill=PARCHMENT)


def solve_pin_and_slot(theta_k1: float, ecc_ratio: float = 0.145) -> Tuple[float, float, float]:
    """
    Solve the Hipparchus epicyclic pin-and-slot mechanism (gears k1 and k2):
    - theta_k1: input angle of uniform lower gear k1 (radians)
    - ecc_ratio: axle eccentricity e / pin radius R (physical ~0.115, visual ~0.145)
    Returns:
      (theta_k2, omega_ratio, deg_per_day)
    """
    sin1 = math.sin(theta_k1)
    cos1 = math.cos(theta_k1)
    theta_k2 = math.atan2(sin1, ecc_ratio + cos1)
    denom = 1.0 + 2.0 * ecc_ratio * cos1 + ecc_ratio * ecc_ratio
    omega_ratio = (1.0 + ecc_ratio * cos1) / max(1e-6, denom)
    # Mean sidereal lunar speed = 13.176358 deg/day
    deg_per_day = 13.176358 * omega_ratio
    return theta_k2, omega_ratio, deg_per_day


def spiral_point(
    cx: float,
    cy: float,
    r_inner: float,
    r_outer: float,
    turns: int,
    total_cells: int,
    cell_pos: float,
) -> Tuple[float, float, float, float]:
    """
    Compute (x, y, radius, angle_rad) along an Archimedean spiral dial (Metonic 235 or Saros 223).
    """
    u = max(0.0, min(1.0, cell_pos / float(total_cells)))
    theta = -math.pi / 2.0 + u * turns * 2.0 * math.pi
    r = r_inner + u * (r_outer - r_inner)
    x = cx + r * math.cos(theta)
    y = cy + r * math.sin(theta)
    return x, y, r, theta

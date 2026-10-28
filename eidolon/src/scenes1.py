"""Shots 0–7: cold open, the machine, the print.

Each shot is a pure function of local time: (t, duration) -> PIL Image. The engine
adds grain, captions, the act stamp and the act cards, so nothing here paints in
the caption band below y≈860 unless it is meant to sit under the type.
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter

from canvas import (AMBER, CYAN, DIM, FONTS, GREY, H, INK, INK2, PAPER, RED, W,
                    act_card, base_plate, chrome, clamp, dashed, disc, draw_stars,
                    draw_text, ease_in_out, ease_out, label, leader, lerp, polyline,
                    prog, pulse, ring, rule, smooth, stars, text_len, title_block,
                    typewrite)

_PLATE = {}


def plate(name, top=INK, bottom=(4, 5, 7), scrim=True):
    key = (name, top, bottom, scrim)
    if key not in _PLATE:
        _PLATE[key] = base_plate(top, bottom, scrim)
    return _PLATE[key].copy()


STARS = stars(260, seed=1977)
STARS2 = stars(120, seed=1978)


# ============================================================ S0 · the date
def black_lede(t, dur):
    img = plate("lede")
    d = ImageDraw.Draw(img, "RGBA")
    x = 300
    lines = [("15 AUGUST 1977", 0.7, AMBER, 27, 6.0),
             ("DELAWARE, OHIO", 1.9, PAPER, 27, 6.0),
             ("22:16 EASTERN", 3.1, PAPER, 27, 6.0)]
    out = ease_out(prog(t, 12.4, 1.6))
    a = 1 - out
    for i, (s, t0, col, size, tr) in enumerate(lines):
        p = ease_out(prog(t, t0, 1.1))
        draw_text(img, (x, 400 + i * 46), s, FONTS("cond", size, 400), col,
                  int(210 * p * a), "ls", tr)
        ln = prog(t, t0 - 0.25, 0.9)
        if ln > 0:
            d.line([(x - 66, 391 + i * 46), (x - 66 + 34 * ln, 391 + i * 46)],
                   fill=col + (int(160 * a),), width=1)

    # the waveform: a pen drawing one 72-second pass across the beam.
    # the clock runs 0 → 72 s; the sky is quiet, then it is not.
    base_y = 660
    x0, x1 = 300, W - 300
    t_draw0, t_draw1 = 9.6, 33.0
    pen = clamp((t - t_draw0) / (t_draw1 - t_draw0))
    line_a = ease_out(prog(t, 8.8, 1.0)) * (1 - ease_in_out(prog(t, 33.4, 2.2)))
    if line_a > 0:
        rng = random.Random(11)
        d.line([(x0, base_y + 60), (x1, base_y + 60)], fill=DIM + (int(55 * line_a),), width=1)
        n = 620
        pts = []
        for i in range(n + 1):
            u = i / n
            px = x0 + (x1 - x0) * u
            # the drift curve: a gaussian centred on the middle of the pass
            env = math.exp(-((u - 0.5) ** 2) / (2 * 0.085 ** 2))
            amp = 6.0 + 96 * env
            jitter = 0.45 + 0.55 * math.sin(i * 1.7 + t * 3.1)
            pts.append((px, base_y + rng.uniform(-1, 1) * amp * jitter))
        seg = pts[:max(2, int(pen * n))]
        polyline(img, seg, PAPER, width=2, alpha=int(175 * line_a))
        if 0 < pen < 1:
            disc(img, seg[-1], 3.6, AMBER, int(230 * line_a))
        # the clock
        tt = pen * 72
        clk = ease_out(prog(t, 8.8, 1.0))
        draw_text(img, (W / 2, base_y - 190), f"{int(tt):02d}", FONTS("serif", 108, 300),
                  AMBER, int(185 * clk * line_a), "cs")
        draw_text(img, (W / 2, base_y - 148), "SECONDS INTO THE PASS", FONTS("cond", 12, 400),
                  GREY, int(130 * clk * line_a), "cs", 2.8)
        # the peak, announced once it has happened
        if pen > 0.5:
            pa = ease_out(prog(t, t_draw0 + (t_draw1 - t_draw0) * 0.5, 0.8)) * line_a
            d.line([(W / 2, base_y - 96), (W / 2, base_y + 52)],
                   fill=AMBER + (int(150 * pa),), width=1)
            draw_text(img, (W / 2 + 12, base_y - 94), "×30 the noise", FONTS("cond", 15, 400),
                      AMBER, int(200 * pa), "ls", 1.8)
        draw_text(img, (x0, base_y + 84), "RECEIVED POWER · 1420 MHz", FONTS("cond", 13, 400),
                  GREY, int(115 * line_a), "ls", 2.4)
        draw_text(img, (x1, base_y + 84), "72 s", FONTS("cond", 13, 400), GREY,
                  int(130 * line_a), "rs", 2.0)
    return img


# ============================================================ S0 · the machine at night
def horizon(t, dur):
    img = plate("horizon")
    d = ImageDraw.Draw(img, "RGBA")
    draw_stars(img, STARS, t, alpha_scale=0.95, drift=t * 0.4)
    gy = 812

    stroke = ease_in_out(prog(t, 0.8, 5.0))
    ox = -20 * ease_in_out(prog(t, 0, dur))
    par = [(980 + 760 * (i / 60), 690 - 250 * math.sin(math.pi * (i / 60)) ** 0.75 + 60)
           for i in range(61)]
    par = [(x + ox, y) for x, y in par]

    # ground + mesh
    if stroke > 0.02:
        d.line([(0, gy), (W, gy)], fill=(30, 33, 40, 255), width=2)
        for i in range(60):
            xx = (i * 41) % W
            d.line([(xx, gy + 1), (xx + 24, gy + 1)], fill=(20, 22, 28, 150), width=2)
        for i in range(1, 40):
            u = i / 40
            if u > stroke:
                continue
            x, y = par[int(u * 60)]
            d.line([(x, y), (x, gy)], fill=PAPER + (34,), width=1)
    polyline(img, par, PAPER, width=2, alpha=160, progress=stroke)

    # flat reflector
    fl = [(300 + ox, 800), (392 + ox, 342), (452 + ox, 366), (368 + ox, 806)]
    pl = ease_in_out(prog(t, 2.6, 3.0))
    polyline(img, fl + [fl[0]], PAPER, width=2, alpha=160, progress=pl)
    if pl > 0.3:
        for i in range(1, 16):
            u = i / 16
            if u > pl:
                continue
            d.line([(300 + ox, lerp(800, 342, u)), (368 + ox, lerp(806, 366, u))],
                   fill=PAPER + (30,), width=1)

    # feed horn at the focus of the parabola
    if t > 4.6:
        p = ease_out(prog(t, 4.6, 1.6))
        fx, fy = 1180 + ox, 648
        d.line([(fx, fy + 20), (fx, gy + 2)], fill=PAPER + (int(120 * p),), width=2)
        d.polygon([(fx - 18, fy + 20), (fx + 18, fy + 20), (fx + 10, fy - 6), (fx - 10, fy - 6)],
                  outline=PAPER + (int(200 * p),))
        glow = pulse(t, 5.2, 2.0) * p
        disc(img, (fx, fy + 6), 26 + 6 * glow, AMBER, int(24 * glow))
        disc(img, (fx, fy + 6), 3.4, AMBER, int(230 * p))

    # the sky, turning: a slow arc of faint dots trailing behind the horizon line
    if t > 6.0:
        p = ease_out(prog(t, 6.0, 2.0))
        for k in range(3):
            arc = []
            for i in range(40):
                u = i / 39
                a = math.pi * (0.15 + 0.7 * u)
                arc.append((W / 2 + 1150 * math.cos(a), 980 - 780 * math.sin(a) * 0.42))
            polyline(img, arc, CYAN, width=1, alpha=int(26 * p / (k + 1)),
                     progress=p * (0.6 + 0.2 * k))

    # moon, for scale
    mx, my = 1660, 250
    disc(img, (mx, my), 24, (206, 208, 198), 22)
    ring(img, (mx, my), 24, PAPER, 1, 55)
    if t > 9.0:
        p = ease_out(prog(t, 9.0, 1.2))
        label(img, (mx, my + 52), "THE MOON · FOR SCALE", int(90 * p), GREY, 12, "cs", 2.0)
    return img


# ============================================================ S0 · title
def title(t, dur):
    img = plate("title", (6, 7, 10), (3, 4, 6))
    draw_stars(img, STARS2, t * 0.6, alpha_scale=0.75, size_scale=0.9)
    d = ImageDraw.Draw(img, "RGBA")

    p = ease_in_out(prog(t, 0.0, 3.4))
    cx, cy = W / 2, 520
    for k, r in enumerate((560, 700, 840)):
        ring(img, (cx, cy), r, AMBER if k == 0 else DIM, 1, int(24 * (1 - k * 0.25) * p),
             0.62 + 0.05 * math.sin(t * 0.3 + k), 0.98)

    a1 = ease_out(prog(t, 0.35, 1.0))
    draw_text(img, (W / 2, 268), "OHIO STATE UNIVERSITY RADIO OBSERVATORY · 1977",
              FONTS("cond", 18, 400), AMBER, int(190 * a1), "cs", 5.0)

    for i, line in enumerate(("SIX", "CHARACTERS")):
        p2 = ease_out(prog(t, 0.75 + i * 0.3, 1.5))
        tr = lerp(58, 16, p2)
        draw_text(img, (W / 2, 428 + i * 158), line, FONTS("serif", 158, 400),
                  PAPER, int(246 * p2), "cs", tr)

    pr = ease_in_out(prog(t, 2.1, 1.4))
    if pr > 0:
        d.line([(W / 2 - 300 * pr, 690), (W / 2 + 300 * pr, 690)],
               fill=AMBER + (int(180 * pr),), width=1)

    ps = ease_out(prog(t, 2.5, 1.4))
    draw_text(img, (W / 2, 748), "The Wow! signal — seventy-two seconds that never came twice",
              FONTS("sans", 30, 300, opsz=28), PAPER, int(196 * ps), "cs", 0.4)

    pc = ease_out(prog(t, 3.5, 1.4))
    draw_text(img, (W / 2, 960), "A FILM MADE IN CODE · EIDOLON",
              FONTS("cond", 15, 400), GREY, int(140 * pc), "cs", 4.4)
    return img


# ============================================================ S1 · the instrument
def schematic(t, dur):
    img = plate("schematic")
    d = ImageDraw.Draw(img, "RGBA")
    gy = 818
    title_block(img, "II · THE MACHINE", "A telescope that could not point", t, 0.4)
    rule(img, 96, W - 96, 250, DIM, 45)
    label(img, (W - 96, 236), "SIDE VIEW · NOT TO SCALE", 90, GREY, 12, "rs", 2.4)

    # ground
    d.line([(96, gy), (W - 96, gy)], fill=DIM + (70,), width=1)
    for x in range(96, W - 96, 26):
        d.line([(x, gy), (x, gy + 6)], fill=DIM + (36,), width=1)
    label(img, (96, gy + 40), "GROUND PLANE · 110 × 152 m", 110, GREY, 14)

    # --- paraboloid
    p_par = ease_in_out(prog(t, 2.4, 2.8))
    par = [(1000 + 740 * (i / 60), 720 - 250 * math.sin(math.pi * (i / 60)) ** 0.75)
           for i in range(61)]
    polyline(img, par, PAPER, width=2, alpha=200, progress=p_par)
    if p_par > 0.2:
        for i in range(1, 35):
            u = i / 35
            if u > p_par:
                continue
            x, y = par[int(u * 60)]
            d.line([(x, y), (x, gy)], fill=PAPER + (24,), width=1)
    pa = int(200 * ease_out(prog(t, 4.0, 1.0)))
    if pa > 0:
        label(img, (1700, 404), "FIXED PARABOLOID", pa, PAPER, 16, "rs")
        label(img, (1700, 428), "110 × 21 m", int(pa * 0.7), GREY, 14, "rs")
        leader(img, (1470, 470), (1698, 420), pa // 2, side="l")

    # --- flat reflector
    p_fl = ease_in_out(prog(t, 0.9, 2.2))
    fl = [(300, 812), (392, 342), (452, 366), (368, 818)]
    polyline(img, fl + [fl[0]], PAPER, width=2, alpha=200, progress=p_fl)
    if p_fl > 0.3:
        for i in range(1, 17):
            u = i / 17
            if u > p_fl:
                continue
            d.line([(300, lerp(812, 342, u)), (368, lerp(818, 366, u))],
                   fill=PAPER + (24,), width=1)
    fa = int(200 * ease_out(prog(t, 1.6, 1.0)))
    if fa > 0:
        label(img, (250, 300), "FLAT REFLECTOR", fa, PAPER, 16, "ls")
        label(img, (250, 324), "104 × 30 m · TILTABLE", int(fa * 0.7), GREY, 14, "ls")
        d.line([(258, 336), (300, 400)], fill=DIM + (int(90 * fa / 200),), width=1)

    # --- rays
    if t > 5.4:
        p = ease_out(prog(t, 5.4, 2.4))
        for k in range(6):
            sy = 300 + k * 62
            hit = (300 + (sy - 300) * 0.028 + 92 * (1 - (sy - 300) / 340),
                   lerp(812, 342, (sy - 300) / 340))
            src = (-40, sy + 30)
            polyline(img, [src, hit], CYAN, width=1, alpha=int(110 * p), progress=p)
            tx = 1150 + k * 24
            ty = 700 - k * 4
            polyline(img, [hit, (tx, ty)], CYAN, width=1, alpha=int(85 * p), progress=p)
            if p > 0.95:
                disc(img, hit, 2.2, CYAN, 140)

    # --- feed horns
    if t > 8.8:
        p = ease_out(prog(t, 8.8, 1.6))
        for i, hx in enumerate((1120, 1218)):
            d.line([(hx, 772), (hx, gy + 2)], fill=PAPER + (int(120 * p),), width=2)
            d.polygon([(hx - 22, 772), (hx + 22, 772), (hx + 12, 744), (hx - 12, 744)],
                      outline=PAPER + (int(190 * p),))
            disc(img, (hx, 758), 24 + 6 * pulse(t * 0.7 + i, 4.0, 2.0), AMBER,
                 int(18 * p * (0.6 + 0.4 * pulse(t + i, 4.0, 2.0))))
            disc(img, (hx, 758), 2.6, AMBER, int(220 * p))
        label(img, (1120, 900), "TWO FEED HORNS · OFFSET ≈ 1/3 BEAM", int(180 * p), AMBER, 15)

    # --- the collector note
    if t > 13.0:
        p = ease_out(prog(t, 13.0, 1.2))
        label(img, (W - 96, 300), "2 200 SQUARE METRES COLLECTING AREA", int(150 * p), GREY, 14, "rs", 2.4)
        label(img, (W - 96, 324), "≈ A 53 m DISH", int(150 * p), GREY, 14, "rs", 2.4)
    return img


# ============================================================ S1 · 72 seconds
def beam(t, dur):
    img = plate("beam")
    d = ImageDraw.Draw(img, "RGBA")
    title_block(img, "II · THE MACHINE", "Seventy-two seconds is geometry", t, 0.4)
    rule(img, 96, W - 96, 250, DIM, 45)

    # left: the beam vs the Moon
    cx, cy = 470, 520
    pm = ease_out(prog(t, 0.9, 1.4))
    disc(img, (cx, cy), 154, (206, 208, 198), int(18 * pm))
    ring(img, (cx, cy), 154, (206, 208, 198), 1, int(115 * pm))
    label(img, (cx, cy + 194), "FULL MOON · 31 ARCMIN", int(140 * pm), GREY, 14, "cs", 2.4)

    pb = ease_out(prog(t, 3.4, 1.6))
    bw, bh = 154 * (8 / 31), 154 * (40 / 31)
    if pb > 0:
        d.rectangle([cx - bw * pb, cy - bh * pb, cx + bw * pb, cy + bh * pb],
                    outline=AMBER + (int(220 * pb),), width=2)
        draw_text(img, (cx + 176, cy - 34), "BIG EAR BEAM", FONTS("cond", 17, 400), AMBER,
                  int(200 * pb), "ls", 2.4)
        draw_text(img, (cx + 176, cy - 6), "8 × 40 ARCMIN", FONTS("cond", 17, 400), AMBER,
                  int(200 * pb), "ls", 2.4)
        draw_text(img, (cx + 176, cy + 26), "the sky drifts through it", FONTS("sans", 15, 300, opsz=16),
                  GREY, int(150 * pb), "ls")

    # right: the drift scan, six samples of twelve seconds
    px0, py0, pw = 940, 360, 740
    pa = ease_out(prog(t, 1.4, 1.2))
    label(img, (px0, py0 - 40), "ONE PASS · SIX SAMPLES · 12 s EACH", int(170 * pa), GREY, 14)
    cells = 6
    cw = pw / cells
    for i in range(cells):
        p = ease_out(prog(t, 2.2 + i * 0.45, 0.7))
        x0 = px0 + i * cw
        d.rectangle([x0, py0, x0 + cw - 8, py0 + 110], outline=DIM + (int(150 * p),), width=1)
        draw_text(img, (x0 + cw / 2 - 4, py0 + 62), str(i + 1), FONTS("serif", 40, 400),
                  PAPER, int(100 * p), "cs")
        draw_text(img, (x0 + cw / 2 - 4, py0 + 140), "0:{:02d}".format(12 * (i + 1)),
                  FONTS("mono", 14, 400), GREY, int(95 * p), "cs")

    sweep = prog(t, 3.6, 12.0)
    if 0 < sweep < 1:
        sx = px0 + pw * sweep
        d.line([(sx, py0 - 14), (sx, py0 + 126)], fill=CYAN + (200,), width=2)
        disc(img, (sx, py0 - 16), 3, CYAN, 220)
    secs = int(clamp((t - 3.6) / 12.0, 0, 1) * 72)
    ct = ease_out(prog(t, 3.2, 1.0))
    if ct > 0:
        draw_text(img, (px0 + pw, py0 + 538), f"{secs:02d}", FONTS("serif", 128, 500),
                  AMBER, int(225 * ct), "rs")
        draw_text(img, (px0 + pw, py0 + 574), "SECONDS OF BEAM TIME", FONTS("cond", 14, 400),
                  GREY, int(150 * ct), "rs", 2.6)

    # the motor
    ex, ey = 470, 856
    eo = ease_out(prog(t, 9.4, 1.4))
    if eo > 0:
        r = 40
        ring(img, (ex, ey), r, PAPER, 1, int(110 * eo))
        ring(img, (ex, ey), r, CYAN, 2, int(150 * eo), 0.05, 0.05 + 0.9 * ((t * 0.25) % 1))
        d.line([(ex, ey - r - 24), (ex + 20, ey - r - 34)], fill=AMBER + (int(150 * eo),), width=1)
        label(img, (ex + 66, ey + 6), "THE EARTH IS THE MOTOR", int(130 * eo), GREY, 13)
    return img


# ============================================================ S1 · fifty channels
def channels(t, dur):
    img = plate("channels")
    d = ImageDraw.Draw(img, "RGBA")
    title_block(img, "II · THE MACHINE", "Fifty channels, and one atom", t, 0.4)
    rule(img, 96, W - 96, 250, DIM, 45)

    x0, x1 = 240, W - 240
    base, top = 760, 380
    n = 50
    bw = (x1 - x0) / n - 3

    pa = ease_out(prog(t, 0.8, 1.2))
    d.line([(x0, base), (x1, base)], fill=PAPER + (int(150 * pa),), width=1)

    rng = random.Random(6)
    heights = [rng.uniform(0.05, 0.22) for _ in range(n)]
    heights[2] = 0.02
    for i in range(n):
        p = ease_out(prog(t, 1.4 + i * 0.035, 0.7))
        amp = heights[i]
        if i == 2:
            amp = 0.02 + 0.92 * ease_out(prog(t, 9.6, 2.2))
        h = max(1.0, amp * (base - top) * p)
        col = DIM if i != 2 else AMBER
        d.rectangle([x0 + i * (bw + 3), base - h, x0 + i * (bw + 3) + bw, base - 1],
                    fill=tuple(col) + (150 if i != 2 else 215,))

    if t > 2.6:
        p = ease_out(prog(t, 2.6, 1.2))
        for frac, txt in [(0.0, "1420.30"), (0.5, "1420.40"), (1.0, "1420.50")]:
            xx = lerp(x0, x1, frac)
            d.line([(xx, base), (xx, base + 8)], fill=GREY + (int(120 * p),), width=1)
            draw_text(img, (xx, base + 36), txt, FONTS("mono", 14, 400), GREY,
                      int(140 * p), "cs")
        label(img, ((x0 + x1) / 2, base + 66), "MHz", int(110 * p), GREY, 13, "cs", 2.4)

    if t > 5.2:
        p = ease_out(prog(t, 5.2, 1.4))
        hx = lerp(x0, x1, (1420.4058 - 1420.30) / 0.20)
        dashed(d, (hx, top - 44), (hx, base), AMBER, 1, 5, 5, int(190 * p))
        draw_text(img, (hx - 12, top - 50), "H I · 1420.4058 MHz", FONTS("cond", 16, 400),
                  AMBER, int(200 * p), "rs", 1.8)
        draw_text(img, (hx + 12, base + 36), "THE HYDROGEN LINE", FONTS("cond", 14, 400),
                  GREY, int(150 * p), "ls", 2.2)

    if t > 9.4:
        p = ease_out(prog(t, 9.4, 1.4))
        cx = x0 + 2 * (bw + 3) + bw / 2
        yy = base + 112
        d.line([(cx, yy), (cx, base + 88)], fill=CYAN + (int(180 * p),), width=1)
        d.line([(cx - 60 * p, yy), (cx + 60 * p, yy)], fill=CYAN + (int(180 * p),), width=1)
        draw_text(img, (cx + 74, yy + 6), "CHANNEL 2 · 1420.4556 MHz", FONTS("cond", 16, 400),
                  CYAN, int(200 * p), "ls", 1.8)
        draw_text(img, (cx + 74, yy + 32), "the only channel that shouted", FONTS("sans", 14, 300, opsz=15),
                  GREY, int(140 * p), "ls")
    return img


# ============================================================ S2 · the printout
PAPER_W, PAPER_H = 1560, 1980
_print_cache = {}


def _printout_sheet():
    """A reconstruction of the fan-fold sheet: 50 channels per row, one row per
    12-second sample, the character scale 0–9 then A–Z. Channel 2 is blank here —
    the signal belongs to the next shot, not to the background sheet."""
    if "sheet" in _print_cache:
        return _print_cache["sheet"]
    import numpy as np
    from canvas import FONTS as _F
    rng = random.Random(1977)
    sheet = Image.new("RGB", (PAPER_W, PAPER_H), (230, 224, 209))
    arr = np.asarray(sheet).astype(np.int16)
    noise = np.random.default_rng(3).normal(0, 3.2, (PAPER_H // 2, PAPER_W // 2))
    noise = np.array(Image.fromarray((noise + 128).clip(0, 255).astype(np.uint8))
                     .resize((PAPER_W, PAPER_H), Image.BILINEAR), dtype=np.int16) - 128
    arr = np.clip(arr + noise[..., None], 0, 255).astype(np.uint8)
    sheet = Image.fromarray(arr)
    d = ImageDraw.Draw(sheet, "RGBA")
    mono = _F("mono", 21, 400)
    small = _F("mono", 15, 400)

    y = 90
    d.text((70, y), "OHIO STATE UNIVERSITY RADIO OBSERVATORY", font=small, fill=(60, 58, 52, 210))
    d.text((70, y + 22), "SETI SEARCH · 1420.4 MHz · 50 CHANNELS · 12 s INTEGRATION",
           font=small, fill=(90, 86, 76, 190))
    d.text((PAPER_W - 70, y + 22), "15 AUG 77", font=small, fill=(60, 58, 52, 210), anchor="rs")
    y += 70
    d.line([(70, y), (PAPER_W - 70, y)], fill=(120, 114, 100, 140), width=1)
    y += 34

    x0, step = 150, 23.5
    for c in range(50):
        if c % 5 == 0:
            d.text((x0 + c * step, y), f"{c}", font=small, fill=(120, 114, 100, 200))
    y += 30
    row_y = {}
    for r in range(34):
        d.text((70, y), f"{1016 + r:04d}.{r:02d}", font=small, fill=(110, 104, 92, 170))
        chars = [str(rng.randint(0, 6)) for _ in range(50)]
        chars[2] = " "                       # the quiet channel, until it isn't
        d.text((x0, y - 2), "".join(chars), font=mono, fill=(38, 40, 44, 235))
        row_y[r] = y
        y += 34
        if y > PAPER_H - 90:
            break
    d.line([(70, y + 10), (PAPER_W - 70, y + 10)], fill=(120, 114, 100, 120), width=1)
    d.text((70, y + 26), "CHANNEL 02 IS THE SECOND CHARACTER OF EACH ROW",
           font=small, fill=(120, 116, 104, 120))
    _print_cache["sheet"] = sheet
    _print_cache["meta"] = dict(x0=x0, step=step, row_y=row_y, cols=50)
    return sheet


def printout(t, dur):
    sheet = _printout_sheet()
    img = plate("printout", (10, 9, 8), (6, 5, 4))

    sw = 1440
    sh = int(PAPER_H * sw / PAPER_W)
    sc = sheet.resize((sw, sh), Image.LANCZOS)
    scroll = ease_in_out(prog(t, 6.0, 22.0)) * 190
    x = (W - sw) // 2
    y = int(200 - scroll)

    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([x - 10, y - 10, x + sw + 10, y + sh + 10], fill=(0, 0, 0, 130))
    img.paste(sc, (x, y))

    # the prime focus of the lamp
    lamp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lamp)
    lx = 900 + 120 * math.sin(t * 0.18)
    for r, a in ((760, 15), (520, 17), (320, 20)):
        ld.ellipse([lx - r, 300 - r * 0.7, lx + r, 300 + r * 0.7], fill=(255, 214, 150, a))
    lamp = lamp.filter(ImageFilter.GaussianBlur(90))
    img = Image.alpha_composite(img.convert("RGBA"), lamp).convert("RGB")

    # the sheet is revealed downward, like a printer feeding
    reveal = ease_out(prog(t, 0.8, 20.0))
    cutoff = y + 130 + (sh - 240) * reveal
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([x, cutoff, x + sw, y + sh], fill=(28, 24, 20, 255))
    d.rectangle([x, cutoff - 3, x + sw, cutoff], fill=(227, 162, 75, 38))
    if reveal < 0.995:
        d.rectangle([x + 40, cutoff - 28, x + sw - 40, cutoff - 20], fill=(214, 204, 184, 95))

    # scan pass
    sy = y + 110 + (sh - 220) * ((t * 0.11) % 1.0)
    if y < sy < min(cutoff, y + sh):
        d.rectangle([x, sy - 32, x + sw, sy], fill=(255, 246, 226, 12))
        d.line([(x, sy), (x + sw, sy)], fill=(227, 162, 75, 80), width=1)

    # channel-2 bracket: this column will matter
    if t > 9.0:
        p = ease_out(prog(t, 9.0, 1.4))
        cx = x + sc.width * (meta_x := _print_cache["meta"]["x0"] / PAPER_W)
        d.line([(cx, 330), (cx, 330 + 26 * p)], fill=CYAN + (int(120 * p),), width=1)
        draw_text(img, (cx + 8, 356), "CH 02", FONTS("cond", 12, 400), CYAN,
                  int(150 * p), "ls", 1.8)

    # title over the page, on its own scrim, so the type never sits on bare paper
    scrim = Image.new("RGBA", (W, H), (6, 7, 9, 0))
    sd = ImageDraw.Draw(scrim)
    for i in range(300):
        sd.line([(0, i), (W, i)], fill=(6, 7, 9, int(215 * (1 - i / 300) ** 1.5)))
    img = Image.alpha_composite(img.convert("RGBA"), scrim).convert("RGB")
    title_block(img, "III · THE PRINT", "The telescope wrote itself down", t, 0.5, y=96)

    label(img, (W - 96, 96), "RECONSTRUCTION · NOT THE ORIGINAL SHEET", 120, PAPER, 13, "rs", 2.4)
    return img


# ============================================================ S2 · the reader
def reader(t, dur):
    sheet = _printout_sheet()
    img = plate("reader", (12, 10, 9), (4, 4, 4), scrim=False)
    sw = 1280
    sh = int(PAPER_H * sw / PAPER_W)
    sc = sheet.resize((sw, sh), Image.LANCZOS).rotate(-3.5, expand=True, resample=Image.BICUBIC)
    x = (W - sc.width) // 2
    y = (H - sc.height) // 2 - 10
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([x - 12, y - 12, x + sc.width + 12, y + sc.height + 12], fill=(0, 0, 0, 170))
    img.paste(sc, (x, y))

    # someone's shadow, reading
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    hx = 1210 + 26 * math.sin(t * 0.25)
    sd.ellipse([hx - 180, 520 + 10 * math.sin(t * 0.31), hx + 180, 980], fill=(0, 0, 0, 215))
    sd.ellipse([hx - 400, 620, hx - 70, 1040], fill=(0, 0, 0, 150))
    shade = shade.filter(ImageFilter.GaussianBlur(70))
    img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")

    warm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(warm)
    for r, a in ((820, 24), (520, 28)):
        wd.ellipse([700 - r, 250 - r * 0.55, 700 + r, 250 + r * 0.55], fill=(255, 197, 120, a))
    warm = warm.filter(ImageFilter.GaussianBlur(110))
    img = Image.alpha_composite(img.convert("RGBA"), warm).convert("RGB")

    # left scrim for the date block
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sc = ImageDraw.Draw(scrim)
    for i in range(760):
        sc.line([(i, 0), (i, H)], fill=(5, 5, 7, int(210 * (1 - i / 760) ** 1.4)))
    for i in range(260):
        sc.line([(0, i), (W, i)], fill=(5, 5, 7, int(170 * (1 - i / 260) ** 1.5)))
    img = Image.alpha_composite(img.convert("RGBA"), scrim).convert("RGB")

    d = ImageDraw.Draw(img, "RGBA")
    pa = ease_out(prog(t, 0.6, 1.2))
    draw_text(img, (96, 120), "19 AUGUST 1977", FONTS("cond", 28, 400), AMBER,
              int(230 * pa), "ls", 5.0)
    draw_text(img, (96, 160), "THREE DAYS AFTER THE OBSERVATION", FONTS("cond", 17, 400),
              PAPER, int(180 * pa), "ls", 3.4)
    draw_text(img, (W - 96, 120), "J. R. EHMAN · VOLUNTEER", FONTS("cond", 15, 400), PAPER,
              int(120 * pa), "rs", 3.0)
    return img

"""Shots 8–16: the word, why it mattered, the silence, the coda."""
import math
import random

from PIL import Image, ImageDraw, ImageFilter

from canvas import (AMBER, CYAN, DIM, FONTS, GREY, H, INK, INK2, PAPER, RED, W,
                    act_card, base_plate, chrome, clamp, dashed, disc, draw_stars,
                    draw_text, ease_in_out, ease_out, label, leader, lerp, polyline,
                    prog, pulse, ring, rule, smooth, stars, text_len, title_block)

_PLATE = {}


def plate(name, top=INK, bottom=(4, 5, 7), scrim=True):
    key = (name, top, bottom, scrim)
    if key not in _PLATE:
        _PLATE[key] = base_plate(top, bottom, scrim)
    return _PLATE[key].copy()


STARS = stars(200, seed=2024)

SIG = ["6", "E", "Q", "U", "J", "5"]
VAL = ["6", "14", "26", "30", "19", "5"]

# geometry shared by the "column" and "mark" shots so the cut lands on the same page
COL_X, COL_Y0, COL_STEP, COL_SIZE = 800, 300, 96, 138


# ------------------------------------------------------------------ hand-drawn helpers
def hand_ellipse(img, center, rx, ry, progress, color=RED, width=4, seed=5, alpha=235):
    if progress <= 0:
        return
    rng = random.Random(seed)
    ph = [rng.uniform(0, 6.28) for _ in range(4)]
    dr = ImageDraw.Draw(img, "RGBA")
    pts = []
    stop = 2 * math.pi * (0.06 + 1.12 * clamp(progress))
    steps = 150
    for i in range(steps):
        a = -2.2 + stop * i / steps
        w = 1 + 0.035 * math.sin(3 * a + ph[0]) + 0.02 * math.sin(5 * a + ph[1])
        px = center[0] + rx * w * math.cos(a) * (1 + 0.05 * (i / steps))
        py = center[1] + ry * w * math.sin(a) * (1 + 0.03 * math.sin(2 * a + ph[2]))
        pts.append((px, py))
    if len(pts) > 1:
        dr.line(pts, fill=tuple(color) + (int(alpha),), width=width, joint="curve")


def write_text(img, xy, s, font, fill, progress, angle=-4.0, alpha=255):
    if progress <= 0:
        return
    w = int(text_len(s, font) + 80)
    asc, desc = font.getmetrics()
    layer = Image.new("RGBA", (w, int(asc + desc + 80)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((40, 40), s, font=font, fill=tuple(fill) + (int(alpha),))
    cut = int((w + 20) * clamp(progress * 1.1))
    mask = Image.new("L", layer.size, 0)
    ImageDraw.Draw(mask).rectangle([0, 0, cut, layer.size[1]], fill=255)
    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", layer.size, 0), mask))
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(layer, (int(xy[0]), int(xy[1])), layer)


# ============================================================ S3 · the column
COL_X, COL_Y0, COL_STEP, COL_SIZE = 1010, 306, 106, 96


def _chars(img, t, appear=0.0, alpha=250):
    font = FONTS("mono", COL_SIZE, 500)
    small = FONTS("serif", 36, 400)
    for i, ch in enumerate(SIG):
        y = COL_Y0 + i * COL_STEP
        a = int(alpha * ease_out(prog(t, appear + i * 0.12, 0.4)))
        if a <= 0:
            continue
        draw_text(img, (COL_X, y), ch, font, PAPER, a, "ls")
        draw_text(img, (COL_X + 104, y - 2), VAL[i], small, AMBER, int(a * 0.75), "ls")


def _minigrid(img, t, x=100, y=330, rows=11, cols=21, cw=25, rh=36, t0=1.0):
    """The page in miniature: one row per 12 s, one character per channel.
    Channel 2 is the amber thread down the page."""
    p = ease_out(prog(t, t0, 2.0))
    if p <= 0:
        return
    rng = random.Random(31)
    mono = FONTS("mono", 21, 400)
    d = ImageDraw.Draw(img, "RGBA")
    shown = int(rows * p)
    for r in range(rows):
        if r >= shown:
            continue
        a = int(230 * (1 if r < shown - 1 else p * rows - r))
        for c in range(cols):
            ch = str(rng.randint(0, 6))
            col = GREY if c != 2 else AMBER
            d.text((x + c * cw, y + r * rh), ch, font=mono,
                   fill=tuple(col) + (a if c != 2 else min(255, a + 20),), anchor="ls")
    label(img, (x, y - 34), "THE PAGE · CHANNEL 2", int(150 * p), GREY, 12, "ls", 2.4)


def column(t, dur):
    img = plate("column", (8, 9, 13), (3, 4, 6))
    d = ImageDraw.Draw(img, "RGBA")
    title_block(img, "IV · THE WORD", "One column that would not behave", t, 0.4)
    rule(img, 96, W - 96, 262, DIM, 45)

    _minigrid(img, t)

    # the magnified column, character by character, out of noise
    font = FONTS("mono", COL_SIZE, 500)
    small = FONTS("serif", 36, 400)
    for i, ch in enumerate(SIG):
        ta = 2.2 + i * 1.05
        if t < ta:
            continue
        y = COL_Y0 + i * COL_STEP
        p = prog(t, ta, 0.7)
        if p < 1:
            rng = random.Random(int(t * 24) + i)
            noise = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"[rng.randrange(36)]
            draw_text(img, (COL_X, y), noise, font, CYAN, int(80 + 130 * p), "ls")
        else:
            a = int(250 * ease_out(prog(t, ta + 0.7, 0.35)))
            draw_text(img, (COL_X, y), ch, font, PAPER, a, "ls")
            pv = ease_out(prog(t, ta + 1.0, 0.6))
            draw_text(img, (COL_X + 104, y - 2), VAL[i], small, AMBER, int(200 * pv), "ls")
            g = math.exp(-((t - ta - 0.75) ** 2) / 0.10)
            if g > 0.05:
                for k, (rr, aa) in enumerate(((60, 6), (40, 8), (24, 12))):
                    disc(img, (COL_X + 28, y - 44), rr * (0.7 + 0.3 * g), AMBER, int(aa * g))

    pb = ease_in_out(prog(t, 8.6, 2.2))
    if pb > 0:
        lx = COL_X - 74
        y0, y1 = COL_Y0 - 56, COL_Y0 + 5 * COL_STEP + 10
        d.line([(lx, y0), (lx, y0 + (y1 - y0) * pb)], fill=CYAN + (int(140 * pb),), width=1)
        for yy in (y0, y1):
            d.line([(lx, yy), (lx + 12, yy)], fill=CYAN + (int(140 * pb),), width=1)
        label(img, (lx - 14, y0 + 2), "CHANNEL 2", int(185 * pb), CYAN, 16, "rs", 3.0)
        label(img, (lx - 14, y0 + 24), "SIX SAMPLES · 12 s", int(140 * pb), GREY, 12, "rs", 2.2)

    if t > 11.0:
        p = ease_out(prog(t, 11.0, 1.2))
        label(img, (COL_X + 176, COL_Y0 - 40), "SIGNAL-TO-NOISE", int(130 * p), GREY, 12, "ls", 2.4)
        label(img, (COL_X + 176, COL_Y0 + 5 * COL_STEP + 40), "THE SAME COLUMN, SIX TIMES",
              int(140 * p), GREY, 12, "ls", 2.4)
    return img


# ============================================================ S3 · the mark
def mark(t, dur):
    img = plate("mark", (8, 9, 13), (3, 4, 6))
    d = ImageDraw.Draw(img, "RGBA")
    title_block(img, "IV · THE WORD", "Then a volunteer picked up a pen", t, 0.4)
    rule(img, 96, W - 96, 262, DIM, 45)

    # the drift curve: intensity against time, six samples, 36 s up and 36 s down
    cp = ease_in_out(prog(t, 1.2, 4.6))
    px0, px1 = 150, 700
    py_lo, py_hi = 720, 360
    if cp > 0:
        d.line([(px0, py_lo), (px1, py_lo)], fill=DIM + (int(80 * cp),), width=1)
        d.line([(px0, py_lo), (px0, py_hi)], fill=DIM + (int(80 * cp),), width=1)
        pts = []
        for i in range(100):
            u = i / 99
            v = math.exp(-((u - 0.5) ** 2) / (2 * 0.16 ** 2))
            pts.append((lerp(px0, px1, u), lerp(py_lo, py_hi, v)))
        polyline(img, pts, CYAN, width=2, alpha=int(200 * clamp(cp * 2)), progress=cp)
        for i in range(6):
            u = (i + 0.5) / 6
            v = math.exp(-((u - 0.5) ** 2) / (2 * 0.16 ** 2))
            if cp > u * 1.04:
                disc(img, (lerp(px0, px1, u), lerp(py_lo, py_hi, v)), 3.4, AMBER, 230)
        if cp > 0.97:
            label(img, (px0, py_hi - 26), "RECEIVED POWER · ONE PASS", 140, GREY, 12, "ls", 2.4)
            label(img, (px0, py_lo + 40), "0", 120, GREY, 12, "ls", 2.0)
            label(img, (px1, py_lo + 40), "72 s", 120, GREY, 12, "rs", 2.0)

    # the column, same place it was when the cut happened
    _chars(img, t, alpha=250)

    # red circle, then the word
    hand_ellipse(img, (COL_X + 34, COL_Y0 + 2.4 * COL_STEP), 104, 5 * COL_STEP * 0.60,
                 prog(t, 7.2, 1.4), RED, 4, seed=9)
    wp = prog(t, 9.0, 0.9)
    write_text(img, (300, 780), "Wow!", FONTS("hand", 200, 600), RED, wp, angle=-4.0, alpha=245)

    if t > 11.6:
        p = ease_out(prog(t, 11.6, 1.2))
        draw_text(img, (300, 830), "J. R. EHMAN · 19 AUGUST 1977", FONTS("cond", 15, 400),
                  GREY, int(170 * p), "ls", 2.8)
    return img


# ============================================================ S4 · three properties
def properties(t, dur):
    img = plate("properties", (8, 9, 12), (3, 4, 6))
    d = ImageDraw.Draw(img, "RGBA")
    title_block(img, "V · WHY IT MATTERED", "Three properties, and one problem", t, 0.4)
    rule(img, 96, W - 96, 250, DIM, 45)

    rows = [(318, "I", "FREQUENCY", 1.0), (548, "II", "WIDTH", 12.6),
            (778, "III", "SHAPE", 24.4)]
    for (y, num, name, t0) in rows:
        p = ease_out(prog(t, t0, 1.2))
        if p <= 0:
            continue
        draw_text(img, (96, y + 54), num, FONTS("serif", 46, 400), AMBER, int(170 * p), "ls")
        label(img, (150, y + 44), name, int(200 * p), PAPER, 19, "ls", 4.0)
        d.line([(96, y + 78), (96 + 420 * p, y + 78)], fill=DIM + (int(90 * p),), width=1)

    # ---- I: frequency
    p1 = ease_out(prog(t, 2.2, 1.4))
    if p1 > 0:
        x0, x1, y = 560, W - 130, 386
        d.line([(x0, y), (x0 + (x1 - x0) * p1, y)], fill=PAPER + (int(130 * p1),), width=1)
        for k in range(11):
            xx = lerp(x0, x1, k / 10)
            if (xx - x0) / (x1 - x0) > p1:
                continue
            d.line([(xx, y), (xx, y + 6)], fill=GREY + (int(110 * p1),), width=1)
            draw_text(img, (xx, y + 26), f"{1400 + k * 10}", FONTS("mono", 11, 400),
                      GREY, int(100 * p1), "cs")
        hi = lerp(x0, x1, (1420.4058 - 1400) / 100)
        pg = ease_out(prog(t, 3.6, 1.0))
        d.line([(hi, y - 56), (hi, y + 4)], fill=AMBER + (int(200 * pg),), width=1)
        draw_text(img, (hi - 8, y - 62), "H I · 1420.4058", FONTS("cond", 14, 400), AMBER,
                  int(190 * pg), "rs", 1.6)
        ps = ease_out(prog(t, 4.4, 1.2))
        sx = lerp(x0, x1, (1420.4556 - 1400) / 100)
        d.line([(sx, y - 104), (sx, y + 4)], fill=CYAN + (int(220 * ps),), width=2)
        disc(img, (sx, y - 106), 3.4, CYAN, int(230 * ps))
        draw_text(img, (sx + 12, y - 112), "THE SIGNAL · +50 kHz", FONTS("cond", 14, 400),
                  CYAN, int(210 * ps), "ls", 1.6)
        draw_text(img, (x1, y - 62), "THE WATER HOLE", FONTS("cond", 12, 400), GREY,
                  int(120 * ps), "rs", 2.2)

    # ---- II: width
    p2 = ease_out(prog(t, 13.6, 1.2))
    if p2 > 0:
        x0, x1, y = 560, W - 130, 620
        n = 50
        bw = (x1 - x0) / n - 4
        rng = random.Random(8)
        for i in range(n):
            h = 24 + rng.uniform(0, 14)
            xx = x0 + i * (bw + 4)
            if (xx - x0) / (x1 - x0) > p2:
                continue
            col = AMBER if i == 2 else DIM
            d.rectangle([xx, y - h, xx + bw, y], fill=tuple(col) + (185 if i == 2 else 85,))
        pg = ease_out(prog(t, 15.0, 1.0))
        if pg > 0:
            xx = x0 + 2 * (bw + 4) + bw / 2
            d.line([(xx, y + 14), (xx, y + 62)], fill=CYAN + (int(170 * pg),), width=1)
            draw_text(img, (xx + 12, y + 58), "< 10 kHz IN ONE CHANNEL OF FIFTY",
                      FONTS("cond", 15, 400), CYAN, int(200 * pg), "ls", 1.6)
            draw_text(img, (x1, y + 58), "NATURAL SOURCES: 10⁵–10⁸ Hz WIDE",
                      FONTS("cond", 13, 400), GREY, int(140 * pg), "rs", 1.6)

    # ---- III: shape
    p3 = ease_out(prog(t, 25.4, 1.2))
    if p3 > 0:
        x0, x1 = 560, W - 520
        y_lo, y_hi = 826, 716
        pts = []
        for i in range(90):
            u = i / 89
            v = math.exp(-((u - 0.5) ** 2) / (2 * 0.14 ** 2))
            pts.append((lerp(x0, x1, u), lerp(y_lo, y_hi, v)))
        polyline(img, pts, PAPER, width=2, alpha=int(180 * p3), progress=p3)
        for i in range(6):
            u = (i + 0.5) / 6
            v = math.exp(-((u - 0.5) ** 2) / (2 * 0.14 ** 2))
            if p3 > u * 1.04:
                disc(img, (lerp(x0, x1, u), lerp(y_lo, y_hi, v)), 3.0, AMBER, 220)
        pg = ease_out(prog(t, 26.8, 1.2))
        draw_text(img, (x1 + 34, 760), "RISE = FALL", FONTS("cond", 17, 400), AMBER,
                  int(200 * pg), "ls", 2.6)
        draw_text(img, (x1 + 34, 786), "36 s each side", FONTS("sans", 15, 300, opsz=16),
                  GREY, int(150 * pg), "ls")
        draw_text(img, (x1 + 34, 812), "a fixed source drifting", FONTS("sans", 15, 300, opsz=16),
                  GREY, int(120 * pg), "ls")
    return img


# ============================================================ S4 · the two horns
def horns(t, dur):
    img = plate("horns", (8, 9, 12), (3, 4, 6))
    d = ImageDraw.Draw(img, "RGBA")
    title_block(img, "V · WHY IT MATTERED", "And one thing that did not fit", t, 0.4)
    rule(img, 96, W - 96, 250, DIM, 45)

    gy = 742
    for i, (hx, name, ok) in enumerate([(600, "POSITIVE HORN", True),
                                        (1360, "NEGATIVE HORN", False)]):
        pa = ease_out(prog(t, 0.8 + i * 0.5, 1.2))
        d.line([(hx, gy), (hx, gy - 96)], fill=PAPER + (int(150 * pa),), width=2)
        d.polygon([(hx - 44, gy - 96), (hx + 44, gy - 96), (hx + 24, gy - 132),
                   (hx - 24, gy - 132)], outline=PAPER + (int(190 * pa),))
        cone = [(hx - 20, gy - 132), (hx - 260, 286), (hx + 260, 286), (hx + 20, gy - 132)]
        if ok:
            d.polygon(cone, fill=CYAN + (int(15 * pa),), outline=CYAN + (int(65 * pa),))
        else:
            for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
                dashed(d, cone[a], cone[b], DIM, 1, 6, 8, int(120 * pa))
        label(img, (hx, gy + 42), name, int(200 * pa), PAPER, 18, "cs", 3.2)

        pdot = ease_out(prog(t, 4.0 + i * 0.6, 1.0))
        sx, sy = hx + (0 if ok else 92), 330
        if pdot > 0:
            if ok:
                for k in range(3):
                    ring(img, (sx, sy), 10 + k * 12 * (0.6 + 0.4 * math.sin(t * 1.6 + k)),
                         CYAN, 1, int(110 * pdot / (k + 1)))
                disc(img, (sx, sy), 4.0, CYAN, int(240 * pdot))
            else:
                ring(img, (sx, sy), 9, GREY, 1, int(90 * pdot))
                disc(img, (sx, sy), 3.0, GREY, int(120 * pdot))

    po = ease_out(prog(t, 7.4, 1.4))
    if po > 0:
        dashed(d, (592, 330), (1350, 330), AMBER, 1, 5, 7, int(140 * po))
        dashed(d, (600, 296), (692, 296), AMBER, 1, 4, 4, int(120 * po))
        draw_text(img, (646, 274), "OFFSET ≈ ⅓ BEAM", FONTS("cond", 12, 400), AMBER,
                  int(150 * po), "cs", 1.6)

    p1 = ease_out(prog(t, 9.2, 1.2))
    if p1 > 0:
        draw_text(img, (600, 812), "DETECTED", FONTS("cond", 24, 400), AMBER,
                  int(220 * p1), "cs", 4.0)
        draw_text(img, (600, 840), "30σ · one channel · 72 s", FONTS("sans", 14, 300, opsz=15),
                  GREY, int(160 * p1), "cs")
    p2v = ease_out(prog(t, 10.6, 1.2))
    if p2v > 0:
        draw_text(img, (1360, 812), "NOTHING", FONTS("cond", 24, 400), GREY,
                  int(200 * p2v), "cs", 4.0)
        draw_text(img, (1360, 840), "same sky · same 72 s", FONTS("sans", 14, 300, opsz=15),
                  GREY, int(140 * p2v), "cs")
    return img


# ============================================================ S5 · the silence
EVENTS = [(1977, "THE SIGNAL", AMBER, 0),
          (1983, "RE-OBSERVATIONS", GREY, 1),
          (1998, "BIG EAR DISMANTLED", PAPER, 0),
          (2016, "COMET HYPOTHESIS", GREY, 1),
          (2020, "ARECIBO COLLAPSES", PAPER, 0),
          (2024, "MAGNETAR HYPOTHESIS", GREY, 1),
          (2026, "TODAY", AMBER, 0)]


def silence(t, dur):
    img = plate("silence", (8, 9, 12), (3, 4, 6))
    d = ImageDraw.Draw(img, "RGBA")
    title_block(img, "VI · THE SILENCE", "Everything after, in order", t, 0.4)
    rule(img, 96, W - 96, 250, DIM, 45)

    x0, x1, y = 180, 1120, 726
    y0, y1 = 1976, 2027
    p = ease_in_out(prog(t, 1.0, 4.0))
    d.line([(x0, y), (x0 + (x1 - x0) * p, y)], fill=PAPER + (int(140 * p),), width=1)

    def X(yr):
        return lerp(x0, x1, (yr - y0) / (y1 - y0))

    if p > 0:
        for yr in range(1976, 2028):
            xx = X(yr)
            if (xx - x0) / (x1 - x0) > p:
                continue
            h = 9 if yr % 5 == 0 else 4
            d.line([(xx, y), (xx, y + h)], fill=GREY + (80 if yr % 5 else 125,), width=1)
            if yr % 10 == 0:
                draw_text(img, (xx, y + 40), str(yr), FONTS("mono", 13, 400), GREY,
                          120, "cs")

    for i, (yr, name, col, tier) in enumerate(EVENTS):
        pe = ease_out(prog(t, 1.8 + i * 1.15, 0.9))
        if pe <= 0:
            continue
        xx = X(yr)
        top = y - (86 if tier == 0 else 172)
        d.line([(xx, y - 8), (xx, y - 8 - 26 * pe)], fill=tuple(col) + (int(150 * pe),), width=1)
        d.line([(xx, top + 44), (xx, top + 52 + 8 * pe)], fill=tuple(col) + (int(90 * pe),), width=1)
        draw_text(img, (xx, top + 40), str(yr), FONTS("serif", 32, 400), col,
                  int(228 * pe), "cs")
        label(img, (xx, top), name, int(155 * pe), col, 12.5, "cs", 2.0)

    # counters, right
    pa = ease_out(prog(t, 2.6, 1.4))
    if pa > 0:
        searches = int(clamp((t - 2.6) / 14, 0, 1) * 100)
        cx = 1250
        d.line([(cx, 500), (cx, 760)], fill=DIM + (int(70 * pa),), width=1)
        draw_text(img, (cx + 48, 590), f"{searches}", FONTS("serif", 92, 500), PAPER,
                  int(210 * pa), "ls")
        label(img, (cx + 52, 618), "SEARCHES AFTERWARDS", int(140 * pa), GREY, 12.5, "ls", 2.4)
        draw_text(img, (cx + 48, 726), "0", FONTS("serif", 92, 500), AMBER,
                  int(225 * pa), "ls")
        label(img, (cx + 52, 754), "DETECTIONS", int(160 * pa), AMBER, 12.5, "ls", 2.4)
    return img


# ============================================================ S5 · the others
def modern(t, dur):
    img = plate("modern", (7, 8, 11), (3, 4, 6))
    d = ImageDraw.Draw(img, "RGBA")
    title_block(img, "VI · THE SILENCE", "Every telescope that looked again", t, 0.4)
    rule(img, 96, W - 96, 250, DIM, 45)

    rows = 4
    for r in range(rows):
        depth = 1 - r / rows
        size = 26 + 30 * depth
        yy = 820 - r * 108
        alpha = int(85 + 55 * depth)
        n = 7 + r
        for c in range(n):
            xx = 240 + (c + 0.5) * (1440 / n) + (r % 2) * 22
            p = ease_out(prog(t, 0.8 + r * 0.35 + c * 0.04, 0.9))
            if p <= 0:
                continue
            arc = [(xx - size * p, yy - 4 * p)]
            for i in range(1, 13):
                u = i / 12
                arc.append((xx - size * p + 2 * size * p * u,
                            yy - 4 * p - size * 0.6 * p * math.sin(math.pi * u)))
            polyline(img, arc, PAPER, width=1, alpha=alpha)
            d.line([(xx, yy - 4), (xx, yy + 10)], fill=PAPER + (alpha,), width=1)

    # a faint sweep in the sky above the dishes: something is still searching
    for k in range(2):
        cy = 470 + k * 70
        ph = (t * 0.10 + k * 0.5) % 1.0
        x = lerp(-200, W + 200, ph)
        d.line([(x, cy), (x + 160, cy - 10)], fill=CYAN + (55,), width=1)
        d.line([(x - 160, cy + 10), (x, cy)], fill=CYAN + (30,), width=1)

    labels = [("ARECIBO · 1963–2020", 400, 330, 1.6), ("GREEN BANK", 900, 300, 4.2),
              ("VERY LARGE ARRAY", 1320, 286, 6.0), ("ALLEN TELESCOPE ARRAY", 700, 286, 8.0)]
    for (name, x, y, t0) in labels:
        p = ease_out(prog(t, t0, 1.1))
        if p <= 0:
            continue
        d.line([(x, y + 16), (x, y + 24 + 10 * p)], fill=AMBER + (int(80 * p),), width=1)
        label(img, (x, y), name, int(165 * p), PAPER, 14, "cs", 2.4)

    pa = ease_out(prog(t, 3.2, 1.4))
    if pa > 0:
        draw_text(img, (W - 100, 330), "0", FONTS("serif", 76, 500), AMBER,
                  int(225 * pa), "rs")
        label(img, (W - 100, 356), "DETECTIONS AT THE COORDINATES", int(140 * pa),
              AMBER, 11, "rs", 2.2)
        draw_text(img, (W - 100, 388), "1977 — 2026", FONTS("mono", 13, 400), GREY,
                  int(120 * pa), "rs")
    return img


# ============================================================ S5 · hypotheses
HYP = [("ORBITAL DEBRIS", "a reflection off something in orbit", "1980s", "NOT EXCLUDED", GREY, 0),
       ("INTERSTELLAR SCINTILLATION", "the galaxy, bending the signal like a lens", "1990s",
        "POSSIBLE", GREY, 0),
       ("COMET HYDROGEN CLOUDS", "ice, warmed by the Sun, glowing at 1420 MHz", "2016",
        "RULED OUT", RED, 1),
       ("MAGNETAR-LIT HYDROGEN", "a flare lighting up a cold cloud of gas", "2024",
        "PLAUSIBLE · UNCONFIRMED", AMBER, 0)]


def hypotheses(t, dur):
    img = plate("hypotheses", (8, 9, 12), (3, 4, 6))
    d = ImageDraw.Draw(img, "RGBA")
    title_block(img, "VI · THE SILENCE", "The explanations, and what survived", t, 0.4)
    rule(img, 96, W - 96, 250, DIM, 45)

    for i, (name, sub, year, verdict, col, strike) in enumerate(HYP):
        t0 = 1.0 + i * 8.6
        p = ease_out(prog(t, t0, 1.0))
        if p <= 0:
            continue
        yy = 300 + i * 152
        draw_text(img, (96, yy + 34), name, FONTS("serif", 42, 400), PAPER, int(225 * p), "ls")
        draw_text(img, (98, yy + 62), sub, FONTS("sans", 16, 300, opsz=17), GREY,
                  int(150 * p), "ls")
        draw_text(img, (W - 100, yy + 28), year, FONTS("mono", 15, 400), GREY,
                  int(165 * p), "rs")
        draw_text(img, (W - 100, yy + 58), verdict, FONTS("cond", 15, 400), col,
                  int(205 * p), "rs", 2.4)
        d.line([(96, yy + 96), (96 + (W - 196) * p, yy + 96)], fill=DIM + (int(60 * p),), width=1)
        if strike and t > t0 + 2.2:
            ps = ease_out(prog(t, t0 + 2.2, 0.8))
            d.line([(96, yy + 22), (96 + 560 * ps, yy + 22)], fill=RED + (int(200 * ps),), width=2)
        if i == 3 and t > 30.0:
            pb = ease_out(prog(t, 30.0, 1.2))
            d.rectangle([78, yy - 14, 78 + (W - 156) * pb, yy + 110],
                        outline=AMBER + (int(60 * pb),), width=1)
    return img


# ============================================================ S6 · coordinates
def coordinates(t, dur):
    img = plate("coordinates", (7, 8, 12), (3, 4, 6))
    d = ImageDraw.Draw(img, "RGBA")
    draw_stars(img, STARS, t * 0.5, alpha_scale=0.5, size_scale=0.85)
    title_block(img, "VII · CODA", "The coordinates are public", t, 0.4)
    rule(img, 96, W - 96, 250, DIM, 45)
    z = 1 + 0.09 * ease_in_out(prog(t, 0.5, 16.0))
    cx, cy = 1080, 560

    def P(x, y):
        return (cx + (x - cx) * z, cy + (y - cy) * z)

    pa = ease_out(prog(t, 1.0, 1.4))
    for i, hh in enumerate([19.0, 19.2, 19.4, 19.6]):
        x = 420 + i * 300
        d.line([P(x, 300), P(x, 860)], fill=DIM + (int(55 * pa),), width=1)
        draw_text(img, P(x, 892), f"{hh:.1f}h", FONTS("mono", 13, 400), GREY, int(110 * pa), "cs")
    for i, dec in enumerate([-26.0, -26.5, -27.0]):
        y = 380 + i * 200
        d.line([P(380, y), P(1560, y)], fill=DIM + (int(55 * pa),), width=1)
        draw_text(img, P(1560, y - 8), f"{dec:.1f}°", FONTS("mono", 13, 400), GREY,
                  int(110 * pa), "rs")

    px, py = P(1080, 560)
    pc = ease_out(prog(t, 3.2, 1.6))
    if pc > 0:
        for r in (18, 44, 78):
            ring(img, (px, py), r * z * 0.7, AMBER, 1, int(85 * pc / (1 + r / 60)))
        d.line([(px - 66 * z, py), (px + 66 * z, py)], fill=AMBER + (int(200 * pc),), width=1)
        d.line([(px, py - 66 * z), (px, py + 66 * z)], fill=AMBER + (int(200 * pc),), width=1)
        disc(img, (px, py), 2.4, AMBER, int(240 * pc))
    pt = ease_out(prog(t, 4.6, 1.4))
    if pt > 0:
        draw_text(img, (px + 96, py - 36), "RA 19h 25m 31s", FONTS("cond", 21, 400), PAPER,
                  int(215 * pt), "ls", 2.4)
        draw_text(img, (px + 96, py - 2), "DEC −26° 57′", FONTS("cond", 21, 400), PAPER,
                  int(215 * pt), "ls", 2.4)
        draw_text(img, (px + 96, py + 34), "SAGITTARIUS · +50 kHz FROM H I", FONTS("cond", 13, 400),
                  GREY, int(150 * pt), "ls", 2.0)
    return img


# ============================================================ S6 · coda
def coda(t, dur):
    img = plate("coda", (7, 8, 11), (3, 3, 4))
    d = ImageDraw.Draw(img, "RGBA")
    draw_stars(img, STARS, t * 0.4, alpha_scale=0.55, size_scale=0.8)

    x0, x1, base_y = 300, W - 300, 560
    a = ease_out(prog(t, 1.0, 2.0)) * (1 - ease_in_out(prog(t, 30.0, 2.6)))
    if a > 0:
        rng = random.Random(11)
        pts = []
        for i in range(0, 601):
            px = x0 + (x1 - x0) * i / 600
            env = math.exp(-((i - 300) ** 2) / (2 * 40.0 ** 2))
            amp = 2.0 + env * 96
            y = base_y + rng.uniform(-1, 1) * amp * (0.55 + 0.45 * math.sin(i * 1.7))
            pts.append((px, y))
        polyline(img, pts, PAPER, width=2, alpha=int(115 * a))

    p1 = ease_out(prog(t, 35.2, 1.6)) * (1 - ease_in_out(prog(t, 39.0, 1.2)))
    if p1 > 0:
        draw_text(img, (W / 2, 400), "For seventy-two seconds,", FONTS("serif", 74, 400),
                  PAPER, int(240 * p1), "cs", 1.0)
        draw_text(img, (W / 2, 496), "the sky was loud.", FONTS("serif", 74, 400),
                  PAPER, int(240 * p1), "cs", 1.0)
    p2 = ease_out(prog(t, 40.2, 1.6))
    if p2 > 0:
        draw_text(img, (W / 2, 496), "Everything since has been us, listening.",
                  FONTS("serif", 54, 400), PAPER, int(236 * p2), "cs", 1.0)

    p3 = ease_out(prog(t, 44.6, 1.6))
    if p3 > 0:
        draw_text(img, (W / 2, 330), "SIX CHARACTERS", FONTS("serif", 60, 400), PAPER,
                  int(220 * p3), "cs", 12)
        d.line([(W / 2 - 200 * p3, 366), (W / 2 + 200 * p3, 366)], fill=AMBER + (int(140 * p3),))
        draw_text(img, (W / 2, 424), "narration · score · design · code — EIDOLON",
                  FONTS("cond", 16, 400), GREY, int(170 * p3), "cs", 3.2)
        draw_text(img, (W / 2, 456), "sources: J. R. Ehman · OSU Radio Observatory · "
                  "Méndez, Ortiz-Ceballos & Zuluaga (2024)",
                  FONTS("cond", 14, 400), GREY, int(125 * p3), "cs", 1.6)
        draw_text(img, (W / 2, 482), "printout recreated for this film — not the original sheet",
                  FONTS("cond", 14, 400), GREY, int(105 * p3), "cs", 1.6)
        draw_text(img, (W / 2, 540), "competitionvideo28 · 2026", FONTS("cond", 14, 400),
                  AMBER, int(150 * p3), "cs", 3.0)
    return img

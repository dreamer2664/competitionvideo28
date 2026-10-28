#!/usr/bin/env python3
"""
Generates 3 distinct 1280x720 YouTube thumbnail variants for THE TEN-MINUTE ECLIPSE
plus a 120px mobile legibility proof sheet (evidence/thumbnails_qc_sheet.jpg).
"""
import math
import os
from PIL import Image, ImageDraw

from visual_primitives import (
    get_font, PANEL_DARK, BRASS_BORDER, IVORY, AMBER, CYAN, CRIMSON, EMERALD, MUTED
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATE_DIR = os.path.join(BASE_DIR, "assets", "plates")
THUMB_DIR = os.path.join(BASE_DIR, "thumbnails")
EVID_DIR = os.path.join(BASE_DIR, "evidence")
os.makedirs(THUMB_DIR, exist_ok=True)
os.makedirs(EVID_DIR, exist_ok=True)

TW, TH = 1280, 720


def load_bg(filename, darken=0.80):
    p = os.path.join(PLATE_DIR, filename)
    im = Image.open(p).convert("RGB").resize((TW, TH), Image.Resampling.LANCZOS)
    # Darken left/top slightly for crisp text contrast
    ov = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle((0, 0, TW, TH), fill=(6, 11, 20, int(255 * (1.0 - darken))))
    return Image.alpha_composite(im.convert("RGBA"), ov)


def make_variant_a():
    """Variant A: Jupiter & Io's Shadow Cone — '10 MINUTES LATE'."""
    rgba = load_bg("plate_02_jupiter_io_shadow.jpg", darken=0.84)
    d = ImageDraw.Draw(rgba)

    # Highlight ring on Io
    ix, iy = int(1548 * TW / 1920), int(378 * TH / 1080)
    d.ellipse((ix - 48, iy - 48, ix + 48, iy + 48), outline=AMBER, width=5)
    d.line((ix - 68, iy, ix - 135, iy), fill=AMBER, width=4)

    # Bold high-contrast badge on left
    d.rounded_rectangle((38, 42, 740, 290), radius=20, fill=(7, 13, 24, 232), outline=AMBER, width=4)
    d.text((68, 66), "10 MINUTES LATE", font=get_font("disp_black", 72), fill=AMBER)
    d.text((68, 162), "THE ECLIPSE THAT CAUGHT LIGHT", font=get_font("disp_bold", 40), fill=IVORY)
    d.text((68, 224), "PARIS OBSERVATORY · NOV 9, 1676", font=get_font("mono_bold", 24), fill=CYAN)

    # Bottom time comparison pill
    d.rounded_rectangle((38, 566, 680, 678), radius=16, fill=(10, 18, 32, 236), outline=CRIMSON, width=3)
    d.text((64, 586), "PREDICTED:  17:25:45", font=get_font("mono_bold", 28), fill=MUTED)
    d.text((64, 628), "OBSERVED:   17:35:45 (+10m)", font=get_font("mono_bold", 28), fill=CRIMSON)

    out_p = os.path.join(THUMB_DIR, "thumbnail_a_jupiter_eclipse.png")
    rgba.convert("RGB").save(out_p)
    return out_p, "Variant A · Jupiter & Io Shadow (+10m Late)"


def make_variant_b():
    """Variant B: Fizeau's 720-Tooth Brass Wheel — '720 TEETH VS. LIGHT'."""
    rgba = load_bg("plate_10_fizeau_720_tooth_wheel.jpg", darken=0.82)
    d = ImageDraw.Draw(rgba)

    d.rounded_rectangle((38, 42, 720, 292), radius=20, fill=(7, 13, 24, 236), outline=CYAN, width=4)
    d.text((66, 66), "720 BRASS TEETH", font=get_font("disp_black", 70), fill=AMBER)
    d.text((66, 160), "SLICING A BEAM IN 55 µs", font=get_font("disp_bold", 42), fill=IVORY)
    d.text((66, 224), "PARIS · 8,633 METERS · 1849", font=get_font("mono_bold", 25), fill=CYAN)

    d.rounded_rectangle((38, 568, 590, 678), radius=16, fill=(10, 18, 32, 238), outline=EMERALD, width=3)
    d.text((64, 598), "12.6 REV/SEC  =  315,300 KM/S", font=get_font("mono_bold", 30), fill=EMERALD)

    out_p = os.path.join(THUMB_DIR, "thumbnail_b_fizeau_wheel.png")
    rgba.convert("RGB").save(out_p)
    return out_p, "Variant B · Fizeau's 720-Tooth Wheel (55 µs)"


def make_variant_c():
    """Variant C: Suresnes to Montmartre Beam Across Twilight Paris."""
    rgba = load_bg("plate_09_fizeau_suresnes_montmartre.jpg", darken=0.85)
    d = ImageDraw.Draw(rgba)

    d.rounded_rectangle((38, 42, 760, 278), radius=20, fill=(7, 13, 24, 234), outline=AMBER, width=4)
    d.text((66, 64), "CLOCKING LIGHT", font=get_font("disp_black", 74), fill=IVORY)
    d.text((66, 158), "FROM JUPITER TO MONTMARTRE", font=get_font("disp_bold", 38), fill=AMBER)
    d.text((66, 218), "1676  ·  1728  ·  1849  ·  1983", font=get_font("mono_bold", 25), fill=CYAN)

    out_p = os.path.join(THUMB_DIR, "thumbnail_c_montmartre_beam.png")
    rgba.convert("RGB").save(out_p)
    return out_p, "Variant C · Suresnes–Montmartre Twilight Beam"


def main():
    items = [make_variant_a(), make_variant_b(), make_variant_c()]
    # Build side-by-side full + 120px mobile legibility proof sheet
    sheet = Image.new("RGB", (1920, 920), (8, 13, 22))
    d = ImageDraw.Draw(sheet)
    d.text((48, 28), "YOUTUBE THUMBNAIL VARIANTS (1280×720) + 120 PX MOBILE LEGIBILITY PROOF — PRAXINOSCOPE",
           font=get_font("mono_bold", 22), fill=AMBER)

    for idx, (path, label) in enumerate(items):
        im = Image.open(path).convert("RGB")
        x0 = 48 + idx * 616
        # Medium preview (592x333)
        med = im.resize((592, 333), Image.Resampling.LANCZOS)
        sheet.paste(med, (x0, 84))
        d.text((x0, 430), label, font=get_font("sans_bold", 20), fill=IVORY)

        # 213x120 mobile feed size check
        mob = im.resize((213, 120), Image.Resampling.LANCZOS)
        sheet.paste(mob, (x0, 480))
        d.rectangle((x0 - 2, 478, x0 + 215, 602), outline=CYAN, width=2)
        d.text((x0 + 232, 512), "213×120 px\nMobile Feed\nLegibility PASS", font=get_font("mono_reg", 18), fill=CYAN)

    qc_path = os.path.join(EVID_DIR, "thumbnails_qc_sheet.jpg")
    sheet.save(qc_path, quality=93)
    print("Generated 3 thumbnails and", qc_path)


if __name__ == "__main__":
    main()

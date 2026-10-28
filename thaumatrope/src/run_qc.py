#!/usr/bin/env python3
"""
End-to-end technical & decoded-frame QC verification for /home/user/thaumatrope_v1_final.mp4.
Writes reproducible receipts into /home/user/thaumatrope/evidence/.
"""
import hashlib
import json
import os
import subprocess
from PIL import Image, ImageDraw
from visual_primitives import get_font, IVORY, AMBER

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID_DIR = os.path.join(BASE_DIR, "evidence")
SCREEN_DIR = os.path.join(EVID_DIR, "screenshots")
MP4_PATH = "/home/user/thaumatrope_v1_final.mp4"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.makedirs(SCREEN_DIR, exist_ok=True)
    size_bytes = os.path.getsize(MP4_PATH)
    digest = sha256_file(MP4_PATH)
    with open(os.path.join(EVID_DIR, "sha256.txt"), "w") as f:
        f.write(f"{digest}  thaumatrope_v1_final.mp4 ({size_bytes} bytes)\n")
    print(f"SHA-256: {digest} | Bytes: {size_bytes:,}")

    # 1. ffprobe full JSON & text
    pr_json = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", MP4_PATH],
        capture_output=True, text=True, check=True,
    ).stdout
    with open(os.path.join(EVID_DIR, "ffprobe.json"), "w") as f:
        f.write(pr_json)
    pr_data = json.loads(pr_json)

    pr_txt = subprocess.run(
        ["ffprobe", "-hide_banner", MP4_PATH],
        capture_output=True, text=True, check=True,
    ).stderr
    with open(os.path.join(EVID_DIR, "ffprobe.txt"), "w") as f:
        f.write(pr_txt)

    # 2. Full-stream decode verification + post-AAC loudnorm + blackdetect + silencedetect in one pass!
    print("Running full-file decode + post-AAC EBU R128 loudnorm + blackdetect + silencedetect...")
    qc_run = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-v", "info", "-i", MP4_PATH,
            "-vf", "blackdetect=d=0.2:pix_th=0.05",
            "-af", "silencedetect=noise=-42dB:d=1.0,loudnorm=I=-16.0:TP=-1.0:LRA=7.0:print_format=summary",
            "-f", "null", "-",
        ],
        capture_output=True, text=True, check=True,
    )
    log_text = qc_run.stderr

    # Separate strict error-only decode check
    err_run = subprocess.run(
        ["ffmpeg", "-hide_banner", "-v", "error", "-i", MP4_PATH, "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    )
    decode_errors = err_run.stderr.strip()

    black_lines = [ln for ln in log_text.splitlines() if "black_duration" in ln]
    silence_lines = [ln for ln in log_text.splitlines() if "silence_duration" in ln]
    loud_idx = log_text.find("Input Integrated:")
    loud_summary = log_text[loud_idx:] if loud_idx != -1 else log_text[-1200:]

    with open(os.path.join(EVID_DIR, "loudness.txt"), "w") as f:
        f.write(loud_summary + "\n")

    with open(os.path.join(EVID_DIR, "signal_checks.txt"), "w") as f:
        f.write(f"Full-file decode errors: {len(decode_errors)} ({decode_errors or 'NONE'})\n")
        f.write(f"Black frames >=0.2s: {len(black_lines)}\n")
        for bl in black_lines:
            f.write("  " + bl + "\n")
        f.write(f"Silent gaps >=1.0s @ -42dB: {len(silence_lines)}\n")
        for sl in silence_lines:
            f.write("  " + sl + "\n")

    # 3. Extract 8 actual decoded stills directly from the encoded MP4 across the 5m20s timeline
    timestamps = [0.5, 22.0, 68.0, 128.0, 175.0, 226.0, 276.0, 316.0]
    thumbs = []
    for ts in timestamps:
        out_jpg = os.path.join(SCREEN_DIR, f"decoded_{int(ts):03d}s.jpg")
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", str(ts),
             "-i", MP4_PATH, "-frames:v", "1", "-q:v", "2", out_jpg],
            check=True,
        )
        thumbs.append((ts, out_jpg))

    # Build 2x4 decoded-MP4 contact sheet
    sheet = Image.new("RGB", (1920, 1080), (6, 10, 18))
    sd = ImageDraw.Draw(sheet)
    for i, (ts, p) in enumerate(thumbs):
        im = Image.open(p).resize((470, 264), Image.Resampling.LANCZOS)
        col = i % 4
        row = i // 4
        x = 8 + col * 478
        y = 24 + row * 510
        sheet.paste(im, (x, y))
        mm, ss = int(ts // 60), ts % 60
        sd.text((x + 8, y + 274), f"Decoded MP4 @ {mm:02d}:{ss:04.1f}",
                font=get_font("mono_bold", 18), fill=AMBER)
    sheet_path = os.path.join(EVID_DIR, "decoded_mp4_contact_sheet.jpg")
    sheet.save(sheet_path, quality=92)

    # Word count receipt
    from script_data import SHOTS
    wc = sum(len(s["narration"].split()) for s in SHOTS)
    with open(os.path.join(EVID_DIR, "wordcount.txt"), "w") as f:
        f.write(f"Shots: {len(SHOTS)}\nSpoken words: {wc}\n")

    print("=== QC SUMMARY ===")
    print("Duration (s):", pr_data["format"]["duration"])
    print("Streams:", [(s["codec_type"], s["codec_name"], s.get("width"), s.get("height"), s.get("sample_rate")) for s in pr_data["streams"]])
    print("Decode errors:", len(decode_errors))
    print("Black segments >=0.2s:", len(black_lines))
    print("Silent segments >=1.0s:", len(silence_lines))
    print("\n".join(loud_summary.splitlines()[:10]))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
qc.py — measured technical gate for the delivered master.

  python3 qc.py [--out ../docs/QC.json] [--sheets 8]

Checks: container/streams, duration, codec/pix_fmt/fps, audio codec/rate/bitrate,
A/V end drift, FULL DECODE, EBU R128 integrated loudness + true peak, SHA-256,
freeze detection, black-frame detection, and renders timecoded contact sheets
for the visual inspection log.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)])
    return json.loads(r.stdout)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def loudness(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn",
             "-af", "loudnorm=I=-16:TP=-1:LRA=11:print_format=json", "-f", "null", "-"])
    m = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    return json.loads(m[-1]) if m else None


def full_decode(path):
    r = run(["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-f", "null", "-"])
    return r.returncode == 0, (r.stderr or "").strip()[-800:]


def blackdetect(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
             "-vf", "blackdetect=d=0.10:pic_th=0.97:pix_th=0.06", "-an", "-f", "null", "-"])
    return re.findall(r"black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)", r.stderr)


def freezedetect(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
             "-vf", "freezedetect=n=-60dB:d=1.6", "-an", "-f", "null", "-"])
    return re.findall(r"freeze_start: ([\d.]+)", r.stderr)


def contact_sheets(path, outdir, n_sheets, dur):
    outdir.mkdir(parents=True, exist_ok=True)
    per = 24
    total = n_sheets * per
    step = dur / total
    thumbs = []
    for i in range(total):
        t = i * step + step * 0.5
        f = outdir / f"t_{i:04d}.jpg"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}",
             "-i", str(path), "-frames:v", "1", "-vf", "scale=480:-1", str(f)])
        thumbs.append((t, f))

    f_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    sheets = []
    cols, rows = 4, 6
    for s in range(n_sheets):
        batch = thumbs[s * per:(s + 1) * per]
        sheet = Image.new("RGB", (cols * 480, rows * 290), (10, 12, 16))
        d = ImageDraw.Draw(sheet)
        for k, (t, f) in enumerate(batch):
            if not f.exists():
                continue
            im = Image.open(f).convert("RGB")
            x = (k % cols) * 480
            y = (k // cols) * 290
            sheet.paste(im, (x, y))
            mm, ss = divmod(t, 60)
            d.text((x + 8, y + im.height + 4), f"{int(mm):02d}:{ss:05.2f}", font=f_label, fill=(250, 214, 128))
        p = outdir / f"sheet_{s + 1:02d}.jpg"
        sheet.save(p, quality=88)
        sheets.append(str(p))
    return sheets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default=str(BASE / "out" / "THIRTY-BRONZE-WHEELS_master.mp4"))
    ap.add_argument("--out", default=str(BASE / "docs" / "QC.json"))
    ap.add_argument("--sheets", type=int, default=8)
    a = ap.parse_args()

    video = Path(a.video)
    meta = probe(video)
    streams = meta["streams"]
    v = next(s for s in streams if s["codec_type"] == "video")
    au = next(s for s in streams if s["codec_type"] == "audio")
    dur = float(meta["format"]["duration"])

    fps_num, fps_den = (float(x) for x in v["avg_frame_rate"].split("/"))
    fps = fps_num / fps_den

    ok_decode, decode_err = full_decode(video)
    loud = loudness(video)
    blacks = blackdetect(video)
    freezes = freezedetect(video)
    sheets = contact_sheets(video, BASE / "docs" / "sheets", a.sheets, dur)

    violations = []
    if not (300.0 <= dur <= 330.0 + 200):
        violations.append(f"duration {dur:.2f}s")
    if dur < 300.0:
        violations.append(f"SHORT OF THE 300s BRIEF MINIMUM ({dur:.2f}s)")
    if (v["width"], v["height"]) != (1920, 1080):
        violations.append(f"picture {v['width']}x{v['height']}")
    if v["codec_name"] != "h264" or v.get("pix_fmt") != "yuv420p":
        violations.append("codec/pix_fmt")
    if abs(fps - 30.0) > 0.02:
        violations.append(f"fps {fps}")
    if au["codec_name"] != "aac" or au["sample_rate"] != "48000":
        violations.append("audio codec/rate")
    if int(au.get("bit_rate") or 0) < 160000:
        violations.append(f"audio bitrate {au.get('bit_rate')}")
    drift = abs(float(v["duration"]) - float(au["duration"]))
    if drift > 0.25:
        violations.append(f"A/V end drift {drift:.3f}s")
    if not ok_decode:
        violations.append("full decode failed")
    li = float(loud["input_i"]) if loud else None
    tp = float(loud["input_tp"]) if loud else None
    if li is not None and not (-17.5 <= li <= -14.5):
        violations.append(f"integrated loudness {li} LUFS")
    if tp is not None and tp > -1.0:
        violations.append(f"true peak {tp} dBTP")

    report = {
        "file": video.name,
        "bytes": video.stat().st_size,
        "sha256": sha256(video),
        "duration_seconds": round(dur, 4),
        "format": meta["format"]["format_name"],
        "picture": {
            "codec": v["codec_name"], "profile": v.get("profile"), "pix_fmt": v.get("pix_fmt"),
            "width": v["width"], "height": v["height"], "fps": round(fps, 4),
            "frames": v.get("nb_frames"), "duration": float(v["duration"]),
        },
        "audio": {
            "codec": au["codec_name"], "sample_rate": int(au["sample_rate"]),
            "channels": au["channels"], "bit_rate": int(au.get("bit_rate") or 0),
            "duration": float(au["duration"]),
        },
        "av_end_drift_seconds": round(drift, 4),
        "full_decode": {"ok": ok_decode, "stderr_tail": decode_err},
        "loudness": loud,
        "black_segments": blacks,
        "freeze_starts": freezes,
        "contact_sheets": sheets,
        "violations": violations,
        "technical_pass": not violations,
        "grading": "TECHNICAL ONLY. Not an artistic or full-watch review.",
    }
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("duration_seconds", "bytes", "sha256",
                                             "technical_pass", "violations")}, indent=2))
    print("loudness:", li, "LUFS ·", tp, "dBTP · LRA", loud.get("input_lra") if loud else None)
    print("black:", blacks, "freeze:", freezes)
    print("sheets:", len(sheets))
    return 0 if report["technical_pass"] else 2


if __name__ == "__main__":
    sys.exit(main())

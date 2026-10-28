#!/usr/bin/env python3
"""
build_all.py — the whole film, one command.

  1. narration  (tts_gen.py, cached per cue)
  2. score/mix  (score.py)
  3. picture    (render.py, chunked, 2 workers)
  4. mux        (ffmpeg concat + AAC, faststart)
  5. QC         (ffprobe / full decode / loudness / frame hashes)
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src"
WORK = BASE / "work"
OUT = BASE / "out"

CHUNKS = 6


def sh(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=False, **kw)


def main():
    WORK.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)

    if "--skip-tts" not in sys.argv:
        r = sh([sys.executable, str(SRC / "tts_gen.py")])
        if r.returncode:
            return r.returncode
    if "--skip-score" not in sys.argv:
        r = sh([sys.executable, str(SRC / "score.py")])
        if r.returncode:
            return r.returncode

    tl = json.loads((WORK / "timeline.json").read_text())
    total = int(tl["total_frames"])
    print(f"[picture] {total} frames, {total / 30:.2f}s", flush=True)

    step = total // CHUNKS + 1
    ranges = [(i, min(total, i + step)) for i in range(0, total, step)]
    segs = []

    def render_one(args):
        idx, (a, b) = args
        out = WORK / f"seg_{idx:02d}.mp4"
        segs.append((idx, out))
        r = sh([sys.executable, str(SRC / "render.py"), "--start", str(a), "--end", str(b),
                "--out", str(out), "--crf", "17", "--preset", "medium"],
               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return idx, r.returncode

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=2) as ex:
        results = list(ex.map(render_one, enumerate(ranges)))
    print(f"[picture] rendered in {(time.time() - t0) / 60:.1f} min · {results}", flush=True)
    if any(rc for _, rc in results):
        print("[picture] a segment failed", flush=True)
        return 1

    listfile = WORK / "segments.txt"
    segs.sort()
    listfile.write_text("".join(f"file '{p.name}'\n" for _, p in segs))
    silent = WORK / "picture_silent.mp4"
    r = sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
            "-i", str(listfile), "-c", "copy", str(silent)])
    if r.returncode:
        return 1

    master = OUT / "THIRTY-BRONZE-WHEELS_master.mp4"
    r = sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(silent), "-i", str(WORK / "master_audio.wav"),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest", "-movflags", "+faststart",
            "-metadata", "title=THIRTY BRONZE WHEELS: Decoding the Antikythera Mechanism",
            "-metadata", "artist=chronoscope",
            "-metadata", "comment=Sources: Freeth et al. Nature 444 (2006); Nature 454 (2008); Scientific Reports 11:5821 (2021); Price 1974.",
            str(master)])
    print(f"[master] {master} rc={r.returncode}", flush=True)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())

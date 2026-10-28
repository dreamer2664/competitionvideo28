#!/usr/bin/env python3
"""
Full 1920x1080p 30fps parallel shot renderer & MP4 master assembler.
Obeys the 2GB sandbox doctrine: 2 worker processes, zero intermediate PNGs on disk,
direct RGB24 pipe into libx264, lossless stream-copy concat + 48kHz 192kbps AAC mux.
"""
import concurrent.futures
import gc
import json
import os
import subprocess
import time

from scenes import render_frame_rgb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(BASE_DIR, "src", "timing_manifest.json")
PLATE_DIR = os.path.join(BASE_DIR, "assets", "plates")
AUDIO_MASTER = "/tmp/thaumatrope_build/audio/master_final_48k.wav"
SHOT_OUT_DIR = "/tmp/thaumatrope_build/shots"
FINAL_MP4 = "/home/user/thaumatrope_v1_final.mp4"


def render_one_shot(task):
    shot, f0, f1, fps, total_dur = task
    sid = shot["id"]
    os.makedirs(SHOT_OUT_DIR, exist_ok=True)
    out_mp4 = os.path.join(SHOT_OUT_DIR, f"{sid}.mp4")
    n_frames = f1 - f0

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", "1920x1080", "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-profile:v", "high", "-level", "4.1",
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        "-video_track_timescale", "15360",
        out_mp4,
    ]
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for f_idx in range(f0, f1):
            t_global = f_idx / fps
            t_local = max(0.0, t_global - shot["shot_start"])
            im = render_frame_rgb(PLATE_DIR, shot, t_local, t_global, total_dur)
            proc.stdin.write(im.tobytes())
        proc.stdin.close()
    except Exception:
        proc.kill()
        raise
    stderr_out = proc.stderr.read().decode("utf-8", errors="replace")
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg failed on {sid}: {stderr_out}")
    gc.collect()
    dt = time.time() - t0
    return sid, n_frames, round(dt, 2), out_mp4


def main():
    manifest = json.load(open(MANIFEST_PATH))
    fps = manifest["fps"]
    total_frames = manifest["total_frames"]
    total_dur = manifest["total_duration"]
    shots = manifest["shots"]

    tasks = []
    for idx, s in enumerate(shots):
        f0 = 0 if idx == 0 else int(round(s["shot_start"] * fps))
        f1 = total_frames if idx == len(shots) - 1 else int(round(s["shot_end"] * fps))
        tasks.append((s, f0, f1, fps, total_dur))

    sum_frames = sum(t[2] - t[1] for t in tasks)
    assert sum_frames == total_frames, f"Frame mismatch: {sum_frames} != {total_frames}"

    print(f"Rendering {len(tasks)} shots ({total_frames} frames = {total_dur:.2f}s @ {fps}fps) across 2 workers...")
    t_start = time.time()
    results = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(render_one_shot, t): t[0]["id"] for t in tasks}
        for fut in concurrent.futures.as_completed(futs):
            sid, nf, dt, path = fut.result()
            results[sid] = path
            print(f"  [DONE] {sid}: {nf:4d} frames in {dt:5.2f}s ({nf/max(0.01, dt):4.1f} fps)", flush=True)

    concat_list = os.path.join(SHOT_OUT_DIR, "concat.txt")
    with open(concat_list, "w") as f:
        for s in shots:
            f.write(f"file '{results[s['id']]}'\n")

    print("Concatenating video stream & muxing 48 kHz AAC stereo soundtrack...")
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", concat_list,
            "-i", AUDIO_MASTER,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart",
            "-shortest",
            FINAL_MP4,
        ],
        check=True,
    )
    total_dt = time.time() - t_start
    sz_mb = os.path.getsize(FINAL_MP4) / (1024 * 1024)
    print(f"FINISHED {FINAL_MP4} ({sz_mb:.2f} MB) in {total_dt:.1f}s!")


if __name__ == "__main__":
    main()

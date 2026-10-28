"""
render — segments in, finished vertical short out.

Two stages, deliberately:

  A. build_base()  decode the chosen source segments, reframe each to 1080x1920
                   (face-tracked crop, or whole-frame-on-blur when there is no face
                   to follow), concatenate, normalise to 30 fps / 48 kHz stereo.
  B. composite()   stream a PIL-rendered RGBA overlay into ffmpeg over that base,
                   mix the synthesised SFX bed under it, loudnorm, encode.

Keeping them apart means the overlay pass never has to care how many clips the
leaderboard stitched together, and a failed render can be resumed at stage B.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

import sfx as sfxmod
from analyze import CropPlan, crop_x_expr
from vidkit import FPS, H, W

TMP = os.environ.get("MUTO_TMP", "/tmp/muto")
os.makedirs(TMP, exist_ok=True)


def probe(path: str) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate", "-show_entries", "format=duration",
         "-of", "json", path], capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    st = j["streams"][0]
    return {"w": int(st["width"]), "h": int(st["height"]),
            "dur": float(j["format"]["duration"])}


def _even(v: float) -> int:
    return int(v) // 2 * 2


def _punch(zooms: list[tuple[float, float]]) -> str:
    """A zoompan stage that snaps in on each beat and releases.

    The crop window itself must stay a constant size — a time-varying crop output
    makes the following scale filter reinitialise mid-stream and libx264 aborts with
    EINVAL. zoompan fixes its output size with `s`, so the punch rides on top of an
    already-reframed 1080x1920 frame and nothing downstream ever resizes.
    """
    if not zooms:
        return ""
    terms = "+".join(f"{amt:.3f}*max(0,1-abs(in_time-{t:.3f})/0.45)" for t, amt in zooms)
    return (f",zoompan=z='1+{terms}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d=1:s={W}x{H}:fps={FPS}")


def segment_filter(plan: CropPlan, src_w: int, src_h: int,
                   zooms: list[tuple[float, float]] | None = None) -> str:
    """The reframe graph for one segment."""
    zooms = zooms or []
    if plan.mode == "cover":
        win_w = _even(src_h * 9 / 16)
        if win_w > src_w:                       # already portrait-ish source
            win_w = _even(src_w)
        x_expr = crop_x_expr(plan.keys, src_w, win_w)
        return (
            f"crop=w={win_w}:h={src_h}:x='{x_expr}':y=0,"
            f"scale={W}:{H}:flags=lanczos,fps={FPS}"
            f"{_punch(zooms)},setsar=1,"
            f"eq=contrast=1.06:saturation=1.14:brightness=0.01"
        )
    # fit: whole frame kept, blurred zoomed copy behind it
    return (
        "split=2[bg][fg];"
        f"[bg]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        "gblur=sigma=34,eq=brightness=-0.16:saturation=1.35[bgo];"
        f"[fg]scale={W}:-2:flags=lanczos,eq=contrast=1.06:saturation=1.12[fgo];"
        f"[bgo][fgo]overlay=(W-w)/2:(H-h)/2-170:format=auto,fps={FPS}"
        f"{_punch(zooms)},setsar=1"
    )


def build_segment(src: str, t0: float, t1: float, plan: CropPlan, out: str,
                  zooms=None, speed: float = 1.0) -> str:
    info = probe(src)
    vf = segment_filter(plan, info["w"], info["h"], zooms)
    af = "aresample=48000"
    if abs(speed - 1.0) > 1e-3:
        vf += f",setpts={1/speed:.5f}*PTS"
        af += f",atempo={speed:.4f}"
    cmd = [
        "ffmpeg", "-v", "error", "-y",
        "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", src,
        "-filter_complex", f"[0:v]{vf}[v];[0:a]{af}[a]",
        "-map", "[v]", "-map", "[a]",
        "-r", str(FPS), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "16",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-ac", "2",
        "-movflags", "+faststart", out,
    ]
    subprocess.run(cmd, check=True)
    return out


def build_base(segments: list[dict], out: str) -> float:
    """segments: [{src, t0, t1, plan, zooms?, speed?}] -> concatenated base video."""
    parts = []
    for i, s in enumerate(segments):
        p = os.path.join(TMP, f"seg_{os.getpid()}_{i}.mp4")
        build_segment(s["src"], s["t0"], s["t1"], s["plan"], p,
                      s.get("zooms"), s.get("speed", 1.0))
        parts.append(p)
    if len(parts) == 1:
        os.replace(parts[0], out)
    else:
        lst = os.path.join(TMP, f"concat_{os.getpid()}.txt")
        with open(lst, "w") as fh:
            for p in parts:
                fh.write(f"file '{p}'\n")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
                        "-i", lst, "-c", "copy", "-movflags", "+faststart", out],
                       check=True)
        for p in parts:
            os.remove(p)
        os.remove(lst)
    return probe(out)["dur"]


def _read_exact(stream, n: int) -> bytes:
    """Pipes return short reads; a video frame is not optional."""
    chunks = []
    got = 0
    while got < n:
        b = stream.read(n - got)
        if not b:
            break
        chunks.append(b)
        got += len(b)
    return b"".join(chunks)


def composite(base: str, track, sfx_events, out: str, music: str | None = None,
              src_gain: float = 1.0, sfx_gain: float = 0.9, quiet: bool = False):
    """Stage B: overlay + SFX + loudness, encoded to a delivery MP4.

    The overlay is blended *in Python*, between a decoder pipe and an encoder pipe,
    rather than handed to ffmpeg's `overlay` filter as a second video input.

    Why: with one fast input (the base file) and one slow input (frames arriving as
    fast as PIL can draw them), ffmpeg races ahead on the fast one and queues decoded
    frames it cannot use yet. Measured on this box: 1.36 GB resident after 3.6 s, then
    the OOM killer (rc=-9). `-thread_queue_size` does not bound it — the growth is in
    the filtergraph, not the demuxer queue. Blending here keeps exactly two frames
    alive at any moment, so peak memory is flat in clip length.
    """
    dur = probe(base)["dur"]

    bed = sfxmod.render_bed(sfx_events, dur)
    sfx_wav = os.path.join(TMP, f"sfx_{os.getpid()}.wav")
    sfxmod.write_wav(sfx_wav, bed)

    # Pull the base audio out once: an audio-only input cannot cause the imbalance.
    base_wav = os.path.join(TMP, f"basea_{os.getpid()}.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base, "-vn", "-ac", "2",
                    "-ar", "48000", "-c:a", "pcm_s16le", base_wav], check=True)

    # Video first, with NO audio inputs attached. An audio-only input is a file the
    # demuxer can drain instantly; bolted onto the same graph as a pipe that trickles
    # in at render speed, ffmpeg buffered its way to 1.29 GB. Audio is muxed after.
    silent = os.path.join(TMP, f"vid_{os.getpid()}.mp4")
    dec = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", base, "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-r", str(FPS), "-"],
        stdout=subprocess.PIPE, bufsize=0)
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-profile:v", "high", "-level", "4.1", "-pix_fmt", "yuv420p",
         "-g", str(FPS * 2), silent],
        stdin=subprocess.PIPE, bufsize=0)

    fbytes = W * H * 3
    n = min(track.nframes(), int(round(dur * FPS)))
    written = 0
    try:
        for i in range(n):
            buf = _read_exact(dec.stdout, fbytes)
            if len(buf) < fbytes:
                break
            frame = Image.frombytes("RGB", (W, H), buf)
            ov = track.frame(i)
            frame.paste(ov, (0, 0), ov)
            enc.stdin.write(frame.tobytes())
            written += 1
            if not quiet and i % 300 == 0:
                print(f"    frame {i}/{n}", flush=True)
    except BrokenPipeError:
        pass
    finally:
        for p in (dec, enc):
            try:
                if p.stdin:
                    p.stdin.close()
            except Exception:
                pass
        try:
            dec.stdout.close()
        except Exception:
            pass
    rc = enc.wait()
    dec.wait()
    if rc != 0 or written < n * 0.9:
        raise RuntimeError(f"composite failed rc={rc} frames={written}/{n}")

    # Audio pass: two small files and a stream-copied video — nothing to buffer.
    fc = (
        f"[1:a]volume={src_gain:.3f}[a0];"
        f"[2:a]volume={sfx_gain:.3f}[a1];"
        "[a0][a1]amix=inputs=2:duration=first:normalize=0[am];"
        "[am]loudnorm=I=-14:TP=-1.0:LRA=11,alimiter=limit=0.97[a]"
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", base_wav, "-i", sfx_wav,
         "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-shortest", "-movflags", "+faststart", out], check=True)

    for f in (sfx_wav, base_wav, silent):
        if os.path.exists(f):
            os.remove(f)
    return out


def ffprobe_report(path: str) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                          "-of", "json", path], capture_output=True, text=True,
                         check=True).stdout
    j = json.loads(out)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), {})
    return {
        "duration": round(float(j["format"]["duration"]), 2),
        "size_bytes": int(j["format"]["size"]),
        "video": f"{v['codec_name']} {v['width']}x{v['height']} "
                 f"{eval(v['r_frame_rate']):.0f}fps",
        "audio": f"{a.get('codec_name','-')} {a.get('sample_rate','-')}Hz "
                 f"{a.get('channels','-')}ch",
    }

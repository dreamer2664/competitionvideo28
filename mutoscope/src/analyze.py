"""
analyze — where the funny is, and where to point the 9:16 window.

Two jobs:

1. `energy_profile` / `score_moments`: a cheap loudness + speech-density read of a
   long compilation so a human (or the cut-list builder) can jump straight to the
   peaks. Laughter and screaming are loud and broadband; a flat talking stretch is
   not. This ranks candidates — it does not pretend to understand the joke, and the
   final cut list is hand-checked against the transcript.

2. `track_faces` / `crop_plan`: a 16:9 source cannot become 9:16 without throwing
   away 56% of the width. A fixed centre crop decapitates anyone standing off-centre,
   so we follow the biggest face with a smoothed, quantised pan — and when there is
   no face to follow (pure gameplay, wide establishing shots) we say so, and the
   renderer switches to a layout that keeps the whole frame.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, asdict

import numpy as np

SR_A = 16000


# --------------------------------------------------------------------------- #
# audio
# --------------------------------------------------------------------------- #

def decode_audio(path: str, sr: int = SR_A) -> np.ndarray:
    """Whole-file mono PCM. A 28-minute source is ~27 MB at 16 kHz float32 — fine."""
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(sr),
           "-f", "s16le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def energy_profile(pcm: np.ndarray, hop: float = 0.25, sr: int = SR_A):
    """RMS in dBFS plus a high-band ratio, per `hop` seconds.

    The high-band ratio separates a laugh/yell (broadband, lots of 2-6 kHz) from a
    bass-heavy music bed, which otherwise wins every loudness contest.
    """
    n = int(hop * sr)
    usable = (len(pcm) // n) * n
    frames = pcm[:usable].reshape(-1, n)
    rms = np.sqrt((frames ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)

    spec = np.abs(np.fft.rfft(frames * np.hanning(n), axis=1))
    freqs = np.fft.rfftfreq(n, 1 / sr)
    hi = spec[:, (freqs > 1800) & (freqs < 6500)].sum(axis=1)
    tot = spec.sum(axis=1) + 1e-9
    return db, (hi / tot)


@dataclass
class Moment:
    t: float
    score: float
    db: float
    hi: float
    text: str = ""


def score_moments(path: str, words=None, hop: float = 0.25, win: float = 12.0,
                  top: int = 60) -> list[Moment]:
    """Rank `win`-second windows by how much reaction-shaped audio they contain."""
    pcm = decode_audio(path)
    db, hi = energy_profile(pcm, hop)
    k = max(1, int(win / hop))

    # normalise against the source's own distribution: every channel masters hot
    lo, mid, top_db = np.percentile(db, [10, 50, 97])
    loud = np.clip((db - mid) / max(top_db - mid, 1e-6), 0, 1.6)
    bright = np.clip((hi - np.percentile(hi, 40)) /
                     max(np.percentile(hi, 95) - np.percentile(hi, 40), 1e-6), 0, 1.5)

    sig = loud * 0.68 + bright * 0.32
    ker = np.ones(k) / k
    smooth = np.convolve(sig, ker, mode="same")
    # reward spikiness: a sustained loud music bed is not a moment
    spike = np.convolve(np.clip(sig - smooth, 0, None), ker, mode="same")
    total = smooth + spike * 1.25

    order = np.argsort(total)[::-1]
    picked: list[Moment] = []
    min_gap = win * 0.9
    for idx in order:
        t = idx * hop
        if any(abs(t - m.t) < min_gap for m in picked):
            continue
        picked.append(Moment(t=round(float(t), 2), score=round(float(total[idx]), 4),
                             db=round(float(db[idx]), 1), hi=round(float(hi[idx]), 4)))
        if len(picked) >= top:
            break
    picked.sort(key=lambda m: m.t)
    if words:
        from ytcaps import phrase
        for m in picked:
            m.text = phrase(words, m.t - win / 2, m.t + win / 2)[:180]
    return picked


# --------------------------------------------------------------------------- #
# framing
# --------------------------------------------------------------------------- #

@dataclass
class CropPlan:
    mode: str                     # "cover" (face-tracked 9:16) or "fit" (whole frame kept)
    keys: list                    # [[t, x_norm], ...] centre of the crop window, 0..1
    face_hits: float              # fraction of sampled frames with a face
    note: str = ""

    def to_json(self):
        return asdict(self)


_YUNET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "assets", "models", "yunet.onnx")


def track_faces(path: str, t0: float, dur: float, step: float = 0.4,
                probe_w: int = 480) -> tuple[list[tuple[float, float]], float]:
    """Sample the segment and follow the most prominent face. Returns (track, hit_rate).

    YuNet (OpenCV Zoo) rather than a Haar cascade: cascades miss profiles, hats and
    headsets constantly on this kind of footage, and OpenCV 5 dropped the classic
    CascadeClassifier API anyway. We score candidates by area *and* confidence so a
    small background bystander never steals the window from the streamer.
    """
    import cv2

    meta = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", path],
        capture_output=True, text=True, check=True).stdout.strip()
    sw, sh = [int(v) for v in meta.split("x")[:2]]
    ph = int(round(probe_w * sh / sw / 2) * 2)

    det = cv2.FaceDetectorYN_create(_YUNET, "", (probe_w, ph), 0.55, 0.3, 50)

    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", path,
           "-vf", f"fps={1/step:.4f},scale={probe_w}:{ph}", "-f", "rawvideo",
           "-pix_fmt", "bgr24", "-"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    fsize = probe_w * ph * 3
    nframes = len(proc.stdout) // fsize if fsize else 0

    track: list[tuple[float, float]] = []
    hits = 0
    for i in range(nframes):
        buf = proc.stdout[i * fsize:(i + 1) * fsize]
        img = np.frombuffer(buf, dtype=np.uint8).reshape(ph, probe_w, 3)
        try:
            _, faces = det.detect(img)
        except Exception:
            faces = None
        best = None
        if faces is not None and len(faces):
            for f in faces:
                x, y, w, h = f[0], f[1], f[2], f[3]
                conf = f[14] if len(f) > 14 else 1.0
                weight = (w * h) * (0.5 + conf)
                if best is None or weight > best[0]:
                    best = (weight, x + w / 2)
        t = i * step
        if best is not None:
            hits += 1
            track.append((t, float(best[1]) / probe_w))
        else:
            track.append((t, float("nan")))
    rate = hits / max(nframes, 1)
    return track, rate


def _smooth_track(track, min_hits: float) -> list[tuple[float, float]]:
    """Fill gaps, median-filter out detector jitter, then quantise into holds.

    Editors pan rarely and decisively; a per-frame tracker looks like a nervous tic.
    """
    ts = np.array([t for t, _ in track])
    xs = np.array([x for _, x in track], dtype=float)
    if np.all(np.isnan(xs)):
        return [(0.0, 0.5)]
    idx = np.arange(len(xs))
    good = ~np.isnan(xs)
    xs = np.interp(idx, idx[good], xs[good])

    k = 7
    pad = np.pad(xs, (k // 2, k // 2), mode="edge")
    med = np.array([np.median(pad[i:i + k]) for i in range(len(xs))])

    ema = np.empty_like(med)
    acc = med[0]
    for i, v in enumerate(med):
        acc = 0.80 * acc + 0.20 * v
        ema[i] = acc

    keys: list[tuple[float, float]] = [(0.0, float(ema[0]))]
    for i in range(1, len(ema)):
        if abs(ema[i] - keys[-1][1]) > 0.055:
            keys.append((float(ts[i]), float(ema[i])))
    if len(keys) > 14:   # keep the ffmpeg expression sane
        stride = len(keys) // 14 + 1
        keys = keys[::stride] + [keys[-1]]
    return keys


def crop_plan(path: str, t0: float, dur: float, force: str | None = None) -> CropPlan:
    """Decide between a face-tracked full-bleed crop and a whole-frame layout."""
    if force == "fit":
        return CropPlan("fit", [(0.0, 0.5)], 0.0, "forced fit")
    try:
        track, rate = track_faces(path, t0, dur)
    except Exception as exc:                                   # detector is best-effort
        return CropPlan("fit", [(0.0, 0.5)], 0.0, f"tracker failed: {exc}")
    if force == "cover":
        return CropPlan("cover", _smooth_track(track, rate), round(rate, 3), "forced cover")
    if rate < 0.28:
        return CropPlan("fit", [(0.0, 0.5)], round(rate, 3),
                        "few faces — keeping the whole frame")
    return CropPlan("cover", _smooth_track(track, rate), round(rate, 3),
                    "face-tracked 9:16 window")


def crop_x_expr(keys: list[tuple[float, float]], src_w: int, win_w: int) -> str:
    """Piecewise-linear ffmpeg expression for the crop's left edge."""
    maxx = max(src_w - win_w, 0)

    def px(xn: float) -> float:
        return min(max(xn * src_w - win_w / 2, 0), maxx)

    if len(keys) == 1:
        return f"{px(keys[0][1]):.1f}"
    expr = f"{px(keys[-1][1]):.1f}"
    for i in range(len(keys) - 2, -1, -1):
        t0, x0 = keys[i]
        t1, x1 = keys[i + 1]
        p0, p1 = px(x0), px(x1)
        span = max(t1 - t0, 1e-3)
        seg = f"({p0:.1f}+({p1 - p0:.1f})*min(max((t-{t0:.3f})/{span:.3f},0),1))"
        expr = f"if(lt(t,{t1:.3f}),{seg},{expr})"
    return expr


if __name__ == "__main__":
    import sys
    src = sys.argv[1]
    ms = score_moments(src, top=40)
    print(json.dumps([asdict(m) for m in ms], indent=1)[:4000])

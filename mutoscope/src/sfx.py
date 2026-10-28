"""
sfx — every sound effect in these shorts is synthesised here, from scratch.

No sample packs, no scraped audio: a clip channel that ships someone else's
stingers inherits someone else's licence. These are numpy oscillators and
filtered noise written to 48 kHz stereo WAV, so the whole SFX bed is ours.

The roster is the short-form standard kit:
    whoosh, boom (the "vine boom" low thud), ding, pop, riser, impact,
    swoosh_rev, click, sparkle, airhorn, drumroll, stinger, bass_drop
"""

from __future__ import annotations

import os
import wave

import numpy as np

SR = 48000


def _env(n: int, attack: float = 0.005, decay: float = 0.2, power: float = 2.0) -> np.ndarray:
    t = np.linspace(0, 1, n, endpoint=False)
    a = max(1, int(attack * SR))
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a)
    tail = np.exp(-np.linspace(0, 1, n) * (1.0 / max(decay, 1e-3)))
    return e * (tail ** power)


def _noise(n: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.standard_normal(n)


def _lowpass(x: np.ndarray, cutoff: float) -> np.ndarray:
    """One-pole lowpass; cheap, stable and enough for stingers."""
    a = np.exp(-2.0 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def _lp_vec(x: np.ndarray, cutoff_curve: np.ndarray) -> np.ndarray:
    """Sweeping lowpass — the whoosh's whole character."""
    a = np.exp(-2.0 * np.pi * np.clip(cutoff_curve, 20, SR / 2.2) / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def _norm(x: np.ndarray, peak: float = 0.9) -> np.ndarray:
    m = float(np.max(np.abs(x))) or 1.0
    return x / m * peak


def whoosh(dur: float = 0.45, seed: int = 1) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, 1, n, endpoint=False)
    sweep = 300 + 5200 * np.sin(np.pi * t) ** 1.4
    x = _lp_vec(_noise(n, seed), sweep)
    x *= _env(n, 0.02, 0.33, 1.3)
    x += 0.12 * np.sin(2 * np.pi * (80 + 200 * t) * np.arange(n) / SR) * _env(n, 0.01, 0.2)
    return _norm(x, 0.78)


def swoosh_rev(dur: float = 0.42, seed: int = 7) -> np.ndarray:
    """Reverse whoosh — the pull-in before a reveal."""
    return whoosh(dur, seed)[::-1].copy()


def boom(dur: float = 0.9, f0: float = 62.0) -> np.ndarray:
    """The low meme thud. Pitch drops fast, a little saturation on top."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * np.exp(-t * 3.1) + 26
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * _env(n, 0.002, 0.26, 1.1)
    x += 0.30 * np.sin(2 * ph) * _env(n, 0.002, 0.10, 1.6)
    x += 0.10 * _lowpass(_noise(n, 3), 220) * _env(n, 0.001, 0.05, 2.0)
    x = np.tanh(x * 2.1)
    return _norm(x, 0.95)


def bass_drop(dur: float = 1.3) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 180 * np.exp(-t * 2.2) + 30
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.tanh(np.sin(ph) * 2.6) * _env(n, 0.004, 0.42, 1.0)
    return _norm(x, 0.95)


def ding(dur: float = 0.8, f0: float = 1180.0) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k, amp in ((1.0, 1.0), (2.01, 0.45), (3.02, 0.22), (4.7, 0.10)):
        x += amp * np.sin(2 * np.pi * f0 * k * t) * np.exp(-t * (3.0 + k * 1.4))
    return _norm(x, 0.62)


def sparkle(dur: float = 0.9, seed: int = 11) -> np.ndarray:
    """A little ascending glitter — used on leaderboard reveals."""
    n = int(dur * SR)
    out = np.zeros(n)
    rng = np.random.default_rng(seed)
    for i in range(9):
        f = 1400 * (1.0 + i * 0.28) + rng.uniform(-80, 80)
        start = int(i * 0.045 * SR)
        ln = min(n - start, int(0.30 * SR))
        if ln <= 0:
            break
        t = np.arange(ln) / SR
        out[start:start + ln] += 0.55 * np.sin(2 * np.pi * f * t) * np.exp(-t * 16)
    return _norm(out, 0.5)


def pop(dur: float = 0.14) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 950 * np.exp(-t * 26) + 180
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * _env(n, 0.001, 0.08, 1.4)
    x += 0.25 * _lowpass(_noise(n, 5), 2600) * _env(n, 0.001, 0.04, 2.0)
    return _norm(x, 0.55)


def click(dur: float = 0.06) -> np.ndarray:
    n = int(dur * SR)
    x = _lowpass(_noise(n, 9), 5200) * _env(n, 0.0005, 0.03, 2.2)
    return _norm(x, 0.42)


def riser(dur: float = 1.4, seed: int = 13) -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, 1, n, endpoint=False)
    sweep = 220 * np.exp(t * 3.3)
    ph = 2 * np.pi * np.cumsum(sweep) / SR
    x = 0.55 * np.sin(ph) * (t ** 1.5)
    x += 0.45 * _lp_vec(_noise(n, seed), 400 + 7000 * t ** 2) * (t ** 2)
    return _norm(x, 0.62)


def impact(dur: float = 0.7) -> np.ndarray:
    n = int(dur * SR)
    x = boom(dur, 90.0) * 0.8
    cr = _lowpass(_noise(n, 17), 7000) * _env(n, 0.001, 0.07, 2.0)
    return _norm(x + 0.55 * cr, 0.95)


def airhorn(dur: float = 0.75, f0: float = 300.0) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k in range(1, 11):
        x += (1.0 / k) * np.sin(2 * np.pi * f0 * k * t + 0.4 * k)
    wobble = 1 + 0.015 * np.sin(2 * np.pi * 6 * t)
    x *= wobble
    env = np.ones(n)
    a = int(0.02 * SR)
    r = int(0.12 * SR)
    env[:a] = np.linspace(0, 1, a)
    env[-r:] = np.linspace(1, 0, r)
    return _norm(np.tanh(x * 1.4) * env, 0.60)


def drumroll(dur: float = 1.2, seed: int = 23) -> np.ndarray:
    n = int(dur * SR)
    out = np.zeros(n)
    rng = np.random.default_rng(seed)
    pos, step = 0, 0.055
    while pos < dur:
        s = int(pos * SR)
        ln = min(n - s, int(0.05 * SR))
        if ln <= 0:
            break
        t = np.arange(ln) / SR
        hit = _lowpass(rng.standard_normal(ln), 2600) * np.exp(-t * 60)
        out[s:s + ln] += hit * (0.4 + 0.6 * (pos / dur))
        pos += step
        step *= 0.955
    return _norm(out, 0.6)


def stinger(dur: float = 0.55) -> np.ndarray:
    """Short bright hit for a number reveal: ding + click + a touch of boom."""
    n = int(dur * SR)
    out = np.zeros(n)
    for part, gain in ((ding(dur, 1560.0), 0.75), (click(0.05), 0.8), (boom(dur, 110.0), 0.45)):
        ln = min(n, len(part))
        out[:ln] += part[:ln] * gain
    return _norm(out, 0.8)


REGISTRY = {
    "whoosh": whoosh,
    "swoosh_rev": swoosh_rev,
    "boom": boom,
    "bass_drop": bass_drop,
    "ding": ding,
    "sparkle": sparkle,
    "pop": pop,
    "click": click,
    "riser": riser,
    "impact": impact,
    "airhorn": airhorn,
    "drumroll": drumroll,
    "stinger": stinger,
}


def render_bed(events: list[tuple[float, str, float]], duration: float) -> np.ndarray:
    """Mix (time, name, gain) events into one mono bed of `duration` seconds."""
    n = int(duration * SR) + SR
    bed = np.zeros(n, dtype=np.float64)
    cache: dict[str, np.ndarray] = {}
    for t, name, gain in events:
        fn = REGISTRY.get(name)
        if fn is None:
            continue
        if name not in cache:
            cache[name] = fn()
        s = cache[name]
        i = max(0, int(t * SR))
        ln = min(len(s), n - i)
        if ln <= 0:
            continue
        bed[i:i + ln] += s[:ln] * gain
    return np.tanh(bed * 0.9) * 0.92


def write_wav(path: str, mono: np.ndarray, sr: int = SR):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    data = np.clip(mono, -1.0, 1.0)
    pcm = (data * 32767).astype("<i2")
    stereo = np.repeat(pcm[:, None], 2, axis=1).tobytes()
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(stereo)


def export_library(outdir: str):
    """Write one WAV per effect — the audit trail for 'where did this sound come from'."""
    os.makedirs(outdir, exist_ok=True)
    for name, fn in REGISTRY.items():
        write_wav(os.path.join(outdir, f"{name}.wav"), fn())
    return sorted(REGISTRY)


if __name__ == "__main__":
    import sys
    print(export_library(sys.argv[1] if len(sys.argv) > 1 else "sfx_library"))

"""Original score + sound design, synthesised from scratch with numpy.

Nothing here is sampled. The bed is a slow additive pad (D minor, moving through
Bb, Gm, F and A), a sub drone, decorrelated air, a soft low pulse that enters with
the printout and leaves with the silence, and a sparse bell motif in D-minor
pentatonic. Sound design: radio static at the cold open, a pure 1420 Hz tone at the
moment the word is written, a sub hit under the title and the reveal, and a slow
clock through the act called "the silence".

Output: out/music.wav (48 kHz, stereo, float->pcm16). Narration is mixed later.
"""
import json
import os
import sys

import numpy as np
from scipy import signal  # noqa: F401  (present in this sandbox; lowpass helper below)

SR = 24000   # the score is low-passed at 7 kHz; 24 kHz is plenty and keeps the
             # whole render inside the 1.2 GB/process doctrine (resampled in the mix)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "out")

TL = json.load(open(os.path.join(OUT, "timeline.json")))
TOTAL = TL["total"] + 1.5
N = int(TOTAL * SR)
rng = np.random.default_rng(19770815)

NOTE = {"D1": 36.71, "Bb1": 58.27, "G1": 49.00, "F1": 43.65, "A1": 55.00, "C2": 65.41,
        "D2": 73.42, "E2": 82.41, "F2": 87.31, "G2": 98.00, "A2": 110.00, "Bb2": 116.54,
        "C3": 130.81, "D3": 146.83, "Eb3": 155.56, "F3": 174.61, "G3": 196.00,
        "A3": 220.00, "Bb3": 233.08, "C4": 261.63, "D4": 293.66, "F4": 349.23,
        "G4": 392.00, "A4": 440.00, "C5": 523.25, "D5": 587.33, "F5": 698.46,
        "A5": 880.00, "D6": 1174.66}


def env(n, a, d, s_level, r, hold=None):
    """Attack / decay-to-sustain / release envelope over n samples."""
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    hold_n = n - a_n - d_n - r_n if hold is None else int(hold * SR)
    hold_n = max(hold_n, 0)
    e = np.concatenate([
        np.linspace(0, 1, max(a_n, 1)),
        np.linspace(1, s_level, max(d_n, 1)),
        np.full(hold_n, s_level),
        np.linspace(s_level, 0, max(r_n, 1)),
    ])
    if len(e) < n:
        e = np.pad(e, (0, n - len(e)))
    return e[:n]


def lowpass(x, cutoff, order=2):
    sos = signal.butter(order, cutoff / (SR / 2), btype="low", output="sos")
    return signal.sosfilt(sos, x)


def highpass(x, cutoff, order=2):
    sos = signal.butter(order, cutoff / (SR / 2), btype="high", output="sos")
    return signal.sosfilt(sos, x)


def bandpass(x, lo, hi, order=2):
    sos = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], btype="band", output="sos")
    return signal.sosfilt(sos, x)


def add(buf, x, t0, gain=1.0):
    i0 = int(t0 * SR)
    i0 = max(0, i0)
    n = min(len(x), len(buf) - i0)
    if n > 0:
        buf[i0:i0 + n] += (x[:n] * gain).astype(buf.dtype)


def pad_note(buf, freq, t0, dur, gain=0.12, partials=(1, 0.34, 0.16, 0.07), detune=0.11):
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = env(n, min(3.2, dur * 0.35), dur * 0.25, 0.72, min(4.5, dur * 0.4))
    vib = 1 + 0.0016 * np.sin(2 * np.pi * 0.07 * t + freq)
    x = np.zeros(n)
    for k, amp in enumerate(partials, start=1):
        x += amp * np.sin(2 * np.pi * freq * k * vib * t + k * 0.7)
        x += amp * 0.55 * np.sin(2 * np.pi * freq * k * (2 - vib) * t + k * 1.9)
    add(buf, x * e, t0, gain / len(partials) * 2.0)


def bell(buf, freq, t0, gain=0.05, dur=6.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = np.exp(-t * 0.55) * (1 - np.exp(-t * 90))
    x = (np.sin(2 * np.pi * freq * t) + 0.45 * np.sin(2 * np.pi * freq * 2.01 * t)
         + 0.18 * np.sin(2 * np.pi * freq * 3.02 * t))
    add(buf, x * e, t0, gain)


def thump(buf, t0, gain=0.16, f0=54.0, dur=0.9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * np.exp(-t * 3.2) + 32
    ph = 2 * np.pi * np.cumsum(f) / SR
    e = np.exp(-t * 4.5) * (1 - np.exp(-t * 120))
    add(buf, np.sin(ph) * e, t0, gain)


def staticy(buf, t0, dur, gain=0.02):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    x = bandpass(x, 700, 5200)
    t = np.arange(n) / SR
    e = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.5)
    add(buf, x * e, t0, gain)


# --------------------------------------------------------------------------- chord map
CHORDS = {
    "Dm": ["D2", "A2", "D3", "F3"],
    "Dm_hi": ["D2", "A2", "D3", "A3", "D4"],
    "Bb": ["Bb1", "F2", "Bb2", "D3"],
    "Gm": ["G1", "D2", "G2", "Bb2"],
    "F": ["F1", "C2", "F2", "A2"],
    "A": ["A1", "E2", "A2", "C3"],
    "Dm_dark": ["D1", "D2", "A2", "Eb3"],
    "Dm_open": ["D2", "A2", "D3", "F3", "A3", "D5"],
}


def act_span(act):
    for a in TL["acts"]:
        if a["id"] == act:
            return a["start"], a["end"]
    return 0.0, TOTAL


def beat_time(bid):
    for b in TL["beats"]:
        if b["id"] == bid:
            return b["start"], b["end"]
    return 0.0, TOTAL


def build_bed():
    L = np.zeros(N, dtype=np.float32)
    R = np.zeros(N, dtype=np.float32)

    # progression per act: (chord, seconds)
    plan = {
        "S0": [("Dm", 18), ("Dm_dark", 18), ("Dm_hi", 18)],
        "S1": [("Bb", 16), ("F", 16), ("Gm", 16), ("Dm", 18)],
        "S2": [("Gm", 16), ("Bb", 16), ("Gm", 16)],
        "S3": [("A", 14), ("Dm_dark", 14), ("Dm_hi", 18)],
        "S4": [("F", 16), ("Bb", 16), ("Dm", 18)],
        "S5": [("Gm", 16), ("Dm_dark", 16), ("Bb", 16), ("A", 14)],
        "S6": [("Bb", 12), ("F", 12), ("Dm_open", 34)],
    }
    for act, seq in plan.items():
        t0, t1 = act_span(act)
        t = t0
        for name, dur in seq:
            if t >= t1:
                break
            dur = min(dur, t1 - t + 2.0)
            for note in CHORDS[name]:
                f = NOTE[note]
                pad_note(L, f, t, dur, gain=0.085 if f < 120 else 0.055, detune=0.09)
                pad_note(R, f * 1.0012, t + 0.013, dur, gain=0.085 if f < 120 else 0.052, detune=0.07)
            t += dur

    # sub drone, very quiet, follows the acts
    t = np.arange(N) / SR
    sub = np.sin(2 * np.pi * 36.71 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.031 * t))
    L += sub * 0.030
    R += sub * 0.028

    # air: decorrelated low noise
    for buf, seed in ((L, 1), (R, 2)):
        r = np.random.default_rng(seed)
        x = r.standard_normal(N)
        x = lowpass(x, 900)
        x *= 0.012 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.017 * t + seed))
        buf += x

    # low pulse: from the printout to the end of the silence act
    p0 = beat_time("b06")[0]
    p1 = act_span("S5")[1]
    tt = p0
    while tt < p1:
        if int(tt) % 8 < 6:                      # small breathing gap in the loop
            thump(L, tt, gain=0.10)
            thump(R, tt + 0.008, gain=0.09)
        tt += 1.6

    # bell motif: deterministic scattered notes, denser in the 2nd half
    motif = [("D5", 0.0), ("A4", 7.2), ("F5", 13.0), ("C5", 18.6), ("D5", 24.0),
             ("A5", 30.0), ("G4", 36.5), ("F4", 41.2), ("D5", 47.0), ("C5", 52.5)]
    b6 = beat_time("b06")[0]
    for i, (note, off) in enumerate(motif):
        bell(L, NOTE[note], b6 + off + i * 9.0, gain=0.028)
        bell(R, NOTE[note] * 1.001, b6 + off + i * 9.0 + 0.02, gain=0.026)
    s6 = act_span("S6")[0]
    for i, note in enumerate(["D5", "F5", "A5", "D6"]):
        bell(L, NOTE[note], s6 + 4 + i * 3.4, gain=0.03)
        bell(R, NOTE[note] * 1.001, s6 + 4.03 + i * 3.4, gain=0.028)

    return L, R


def build_sfx(L, R):
    # cold open: a radio left on in an empty room
    staticy(L, 0.4, 11.0, gain=0.016)
    staticy(R, 0.4, 11.0, gain=0.013)

    # title: one low hit
    t, _ = beat_time("b02")
    thump(L, t + 1.5, gain=0.34, f0=46, dur=3.2)
    thump(R, t + 1.5, gain=0.32, f0=46, dur=3.2)

    # the reveal: cut the bed, breathe, then the pure tone of the frequency itself
    t_mark, t_mark_end = beat_time("b09")
    reveal = t_mark + 8.6                      # when the marker writes "Wow!"
    # duck the bed hard around the reveal
    n0, n1 = int((reveal - 1.4) * SR), int((reveal + 5.0) * SR)
    x = np.linspace(0, 1, n1 - n0)
    duck = 0.12 + 0.88 * np.clip((x - 0.55) / 0.45, 0, 1)
    L[n0:n1] *= duck
    R[n0:n1] *= duck

    # riser into it
    n = int(3.4 * SR)
    t = np.arange(n) / SR
    rise = (np.sin(2 * np.pi * (60 * np.exp(t * 0.55)) * t) * 0.06
            + lowpass(rng.standard_normal(n), 3000) * 0.05)
    rise *= np.linspace(0, 1, n) ** 2.2
    add(L, rise, reveal - 3.4, 0.5)
    add(R, rise, reveal - 3.42, 0.45)

    # the tone: 1420 Hz, exact, quiet, with a slow swell
    n = int(6.0 * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 1420 * t) * (1 - np.exp(-t * 3)) * np.exp(-t * 0.45)
    tone += 0.25 * np.sin(2 * np.pi * 710 * t) * np.exp(-t * 0.6)
    add(L, tone, reveal + 0.15, 0.055)
    add(R, tone, reveal + 0.16, 0.052)

    # sub hit at the reveal
    thump(L, reveal + 0.1, gain=0.30, f0=40, dur=3.6)
    thump(R, reveal + 0.12, gain=0.29, f0=40, dur=3.6)

    # a slow clock through the silence act
    t0, t1 = act_span("S5")
    tt = t0 + 1.0
    while tt < min(t1, t0 + 40):
        n = int(0.12 * SR)
        click = bandpass(rng.standard_normal(n), 1800, 4200) * np.exp(-np.arange(n) / SR * 55)
        add(L, click, tt, 0.05)
        add(R, click, tt + 0.006, 0.045)
        tt += 2.0

    # final resolve: one long low note under the last line
    t_end, _ = beat_time("b16")
    pad_note(L, NOTE["D2"], t_end + 6, 26, gain=0.10)
    pad_note(R, NOTE["D2"] * 1.001, t_end + 6.02, 26, gain=0.10)
    return L, R


def main():
    L, R = build_bed()
    L, R = build_sfx(L, R)

    # gentle overall shaping: high-pass the mud, tame the top, global fade
    L = highpass(lowpass(L, 7000), 34)
    R = highpass(lowpass(R, 7000), 34)

    t = np.arange(N) / SR
    fade = np.minimum(1, t / 3.0) * np.minimum(1, (TOTAL - t) / 6.0)
    L *= fade
    R *= fade

    peak = max(np.abs(L).max(), np.abs(R).max())
    g = 0.72 / max(peak, 1e-9)
    L *= g
    R *= g

    st = np.stack([L, R], axis=1)
    st16 = np.clip(st, -1, 1)
    pcm = (st16 * 32767).astype("<i2")
    import wave
    with wave.open(os.path.join(OUT, "music.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"music.wav  {TOTAL:.1f}s  peak gain {g:.2f}  rms "
          f"{20*np.log10(np.sqrt((L**2).mean())+1e-12):.1f} dBFS")


if __name__ == "__main__":
    main()

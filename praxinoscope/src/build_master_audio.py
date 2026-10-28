#!/usr/bin/env python3
"""
Builds the 48 kHz stereo master soundtrack for THE TEN-MINUTE ECLIPSE:
  - Places all 25 dual-voice narration clips at exact manifest sample offsets
  - Synthesizes a 7-act stereo polyphonic ambient score + diegetic optical/clockwork cues
    (1676 Paris Observatory brass pendulum escapement, Io immersion/emersion celestial chimes,
     Galileo shuttered lantern clicks, and Fizeau's accelerating 720-tooth brass wheel whirr)
  - Sidechain-ducks score beneath narration for phone-speaker vocal clarity
  - Masters via two-pass EBU R128 loudnorm (-15.5 LUFS target, TP <= -1.8 dBTP)
"""
import json
import math
import os
import re
import subprocess
import wave
import numpy as np
from scipy.signal import butter, sosfilt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(BASE_DIR, "src", "timing_manifest.json")
BUILD_DIR = "/tmp/praxinoscope_build/audio"
os.makedirs(BUILD_DIR, exist_ok=True)

SR = 48000


def note_freq(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def warm_chord_pad(dur_s, midi_notes, detune_cents=2.4, cutoff_hz=720.0, pulse_hz=0.0):
    n = int(round(dur_s * SR))
    t = np.arange(n, dtype=np.float32) / SR
    left = np.zeros(n, dtype=np.float32)
    right = np.zeros(n, dtype=np.float32)

    for idx, m in enumerate(midi_notes):
        f0 = note_freq(m)
        f_l = f0 * (2.0 ** (-detune_cents / 1200.0))
        f_r = f0 * (2.0 ** (+detune_cents / 1200.0))
        amp = 0.42 / (1.0 + 0.34 * idx)
        lfo_l = 1.0 + 0.08 * np.sin(2 * np.pi * (0.10 + 0.03 * idx) * t + idx)
        lfo_r = 1.0 + 0.08 * np.cos(2 * np.pi * (0.12 + 0.02 * idx) * t + idx * 0.7)
        sig_l = (
            np.sin(2 * np.pi * f_l * t)
            + 0.26 * np.sin(4 * np.pi * f_l * t)
            + 0.11 * np.sin(6 * np.pi * f_l * t)
        )
        sig_r = (
            np.sin(2 * np.pi * f_r * t)
            + 0.26 * np.sin(4 * np.pi * f_r * t)
            + 0.11 * np.sin(6 * np.pi * f_r * t)
        )
        left += amp * sig_l * lfo_l
        right += amp * sig_r * lfo_r

    if pulse_hz > 0.0:
        pulse = 0.80 + 0.20 * (0.5 + 0.5 * np.sin(2 * np.pi * pulse_hz * t - np.pi / 2))
        left *= pulse
        right *= pulse

    sos = butter(3, cutoff_hz / (SR * 0.5), btype="low", output="sos")
    left = sosfilt(sos, left).astype(np.float32)
    right = sosfilt(sos, right).astype(np.float32)

    fade = min(int(0.85 * SR), n // 3)
    if fade > 0:
        win_in = np.sin(np.linspace(0, np.pi / 2, fade, dtype=np.float32)) ** 2
        win_out = np.cos(np.linspace(0, np.pi / 2, fade, dtype=np.float32)) ** 2
        left[:fade] *= win_in
        right[:fade] *= win_in
        left[-fade:] *= win_out
        right[-fade:] *= win_out

    return np.stack([left, right], axis=1)


def add_celestial_chime(buf, ts_sec, midi_note, gain=0.055, decay_s=2.4):
    i0 = int(round(ts_sec * SR))
    n = int(round(decay_s * SR))
    if i0 < 0 or i0 >= len(buf):
        return
    n = min(n, len(buf) - i0)
    t = np.arange(n, dtype=np.float32) / SR
    f = note_freq(midi_note)
    env = np.exp(-t / (decay_s * 0.36)) * np.minimum(1.0, t / 0.010)
    tone = (
        np.sin(2 * np.pi * f * t)
        + 0.22 * np.sin(2 * np.pi * f * 2.0 * t)
        + 0.09 * np.sin(2 * np.pi * f * 3.0 * t) * np.exp(-t / 0.4)
    ) * env * gain
    buf[i0:i0 + n, 0] += tone * 0.94
    buf[i0:i0 + n, 1] += tone * 1.06


def add_pendulum_tick(buf, ts_sec, is_tock=False, gain=0.036):
    i0 = int(round(ts_sec * SR))
    n = int(0.038 * SR)
    if i0 < 0 or i0 + n >= len(buf):
        return
    t = np.arange(n, dtype=np.float32) / SR
    f1 = 1180.0 if is_tock else 1420.0
    f2 = 2360.0 if is_tock else 2780.0
    tick = (np.sin(2 * np.pi * f1 * t) + 0.45 * np.sin(2 * np.pi * f2 * t)) * np.exp(-t / 0.0042) * gain
    buf[i0:i0 + n, 0] += tick * (0.90 if is_tock else 1.05)
    buf[i0:i0 + n, 1] += tick * (1.05 if is_tock else 0.90)


def add_chopper_whirr(buf, t0_sec, dur_s, rps_start=4.0, rps_end=12.6, gain=0.042):
    """Synthesizes the subtle acoustic whirr of Fizeau's 720-tooth brass wheel."""
    i0 = int(round(t0_sec * SR))
    n = int(round(dur_s * SR))
    if i0 < 0 or i0 >= len(buf):
        return
    n = min(n, len(buf) - i0)
    t = np.arange(n, dtype=np.float32) / SR
    rps = np.linspace(rps_start, rps_end, n, dtype=np.float32)
    # Brass gear train sub-harmonic (rps * 18) + subtle tooth-passage air tone
    f_gear = rps * 18.0
    phase = 2.0 * np.pi * np.cumsum(f_gear) / SR
    whirr = (0.65 * np.sin(phase) + 0.35 * np.sin(2.0 * phase)) * gain
    env = np.maximum(0.0, np.sin(np.pi * np.linspace(0, 1, n, dtype=np.float32))) ** 0.7
    sig = whirr * env
    buf[i0:i0 + n, 0] += sig * 0.95
    buf[i0:i0 + n, 1] += sig * 1.05


def main():
    manifest = json.load(open(MANIFEST_PATH))
    total_dur = manifest["total_duration"]
    total_samples = int(round(total_dur * SR))

    voice_track = np.zeros((total_samples, 2), dtype=np.float32)
    speech_env = np.zeros(total_samples, dtype=np.float32)

    hp_sos = butter(2, 80.0 / (SR * 0.5), btype="high", output="sos")

    for s in manifest["shots"]:
        with wave.open(s["wav"], "rb") as wf:
            raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        clean = sosfilt(hp_sos, raw).astype(np.float32)
        pk = float(np.max(np.abs(clean)))
        if pk > 1e-4:
            clean = clean * (0.82 / pk)
        clean = np.tanh(clean * 1.20) / np.tanh(1.20)
        i0 = int(round(s["speech_start"] * SR))
        n = min(len(clean), total_samples - i0)
        if n > 0:
            voice_track[i0:i0 + n, 0] += clean[:n]
            voice_track[i0:i0 + n, 1] += clean[:n]
            speech_env[i0:i0 + n] = 1.0

    # Smooth sidechain ducking envelope (fast attack, 320ms release)
    win = int(0.30 * SR)
    kernel = np.hanning(win).astype(np.float32)
    kernel /= kernel.sum()
    smooth_env = np.convolve(speech_env, kernel, mode="same")
    # Duck music to 0.24 during speech, 1.00 during transitions
    duck_gain = (1.0 - 0.76 * np.clip(smooth_env * 1.15, 0.0, 1.0))[:, None].astype(np.float32)

    # Build 7-act harmonic score
    music_track = np.zeros((total_samples, 2), dtype=np.float32)

    act_chords = {
        "ACT I": ([38, 45, 50, 53, 57, 60, 64], 680.0, 0.25),      # D Dorian nocturnal mystery
        "ACT II": ([43, 50, 55, 58, 62, 65], 640.0, 0.20),         # G minor Baroque contemplation
        "ACT III": ([36, 43, 48, 51, 55, 58, 62], 700.0, 0.28),    # C Dorian maritime/celestial clock
        "ACT IV": ([41, 48, 53, 57, 60, 64, 67], 760.0, 0.33),     # F Lydian orbital geometry
        "ACT V": ([45, 52, 57, 60, 64, 67, 71], 720.0, 0.25),      # A minor/Dorian starlight aberration
        "ACT VI": ([40, 47, 52, 55, 59, 62, 66], 820.0, 0.45),     # E minor9 Montmartre precision pulse
        "ACT VII": ([38, 45, 50, 54, 57, 61, 64, 69], 880.0, 0.22) # D Major9 cosmic resolution
    }

    for s in manifest["shots"]:
        st = s["shot_start"]
        en = s["shot_end"]
        dur = en - st
        act_prefix = s["act"].split("·")[0].strip()
        notes, cutoff, pulse = act_chords.get(act_prefix, ([38, 45, 50, 57, 62], 700.0, 0.25))
        pad = warm_chord_pad(dur + 0.6, notes, detune_cents=2.4, cutoff_hz=cutoff, pulse_hz=pulse)
        i0 = int(round(st * SR))
        n = min(len(pad), total_samples - i0)
        if n > 0:
            music_track[i0:i0 + n] += pad[:n] * 0.26

        # Shot transition celestial chime
        chime_note = notes[-1] + 12 if (int(s["id"][1:]) % 2 == 1) else notes[-2] + 12
        add_celestial_chime(music_track, st + 0.05, chime_note, gain=0.048, decay_s=2.2)

        # Diegetic cues by shot
        sid = s["id"]
        if sid in ("S01", "S02", "S08"):
            # 1 Hz Paris Observatory regulator pendulum tick-tock
            t_cur = st + 0.25
            k = 0
            while t_cur < en - 0.2:
                add_pendulum_tick(music_track, t_cur, is_tock=(k % 2 == 1), gain=0.032)
                t_cur += 0.95
                k += 1
            if sid == "S02":
                # Bright golden chime when Io emerges at 5:35:45 PM
                add_celestial_chime(music_track, st + dur * 0.46, 74, gain=0.075, decay_s=3.0)
                add_celestial_chime(music_track, st + dur * 0.48, 78, gain=0.065, decay_s=3.0)

        elif sid in ("S11", "S12"):
            # Orbital immersion/emersion ticks
            t_cur = st + 0.4
            idx_p = 0
            while t_cur < en - 0.3:
                add_celestial_chime(music_track, t_cur, 69 + (idx_p % 5) * 2, gain=0.028, decay_s=0.9)
                t_cur += 1.15
                idx_p += 1

        elif sid in ("S19", "S20", "S21"):
            # Fizeau's 720-tooth brass wheel accelerating whirr
            r0, r1 = (4.0, 10.0) if sid == "S19" else (8.0, 12.6) if sid == "S20" else (12.6, 37.8)
            add_chopper_whirr(music_track, st + 0.2, dur - 0.4, rps_start=r0, rps_end=r1, gain=0.038)

    # Combine voice + ducked music
    mix = voice_track + music_track * duck_gain
    pk = float(np.max(np.abs(mix)))
    if pk > 0.95:
        mix *= 0.95 / pk

    raw_wav = os.path.join(BUILD_DIR, "master_raw_48k.wav")
    final_wav = os.path.join(BUILD_DIR, "master_final_48k.wav")

    with wave.open(raw_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((np.clip(mix, -1.0, 1.0) * 32767.0).astype(np.int16).tobytes())

    # Two-pass EBU R128 loudnorm (-15.5 LUFS, TP -1.8 dBTP)
    p1 = subprocess.run(
        [
            "ffmpeg", "-y", "-i", raw_wav,
            "-af", "loudnorm=I=-15.5:TP=-1.8:LRA=7:print_format=json",
            "-f", "null", "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    m = re.search(r"\{[\s\S]*?\}", p1.stderr)
    stats = json.loads(m.group(0))

    af_p2 = (
        f"loudnorm=I=-15.5:TP=-1.8:LRA=7:"
        f"measured_I={stats['input_i']}:"
        f"measured_LRA={stats['input_lra']}:"
        f"measured_TP={stats['input_tp']}:"
        f"measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:"
        f"linear=true:print_format=summary"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", raw_wav,
            "-af", af_p2,
            "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
            final_wav,
        ],
        check=True,
        capture_output=True,
    )
    print(f"Master audio built and normalized: {final_wav} (input_i={stats['input_i']} -> target -15.5 LUFS)")


if __name__ == "__main__":
    main()

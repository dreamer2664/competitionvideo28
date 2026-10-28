#!/usr/bin/env python3
"""
Builds the 48 kHz stereo master soundtrack for THE THIRTEEN-HOUR AVALANCHE:
  - Places all 24 narration clips at exact manifest sample offsets
  - Synthesizes an original 7-act stereo harmonic score + subtle diegetic cues
    (1929 telegraph relay ticks, tectonic sub-swell, Lamont sonar pings)
  - Sidechain-ducks score beneath narration for effortless phone-speaker clarity
  - Masters via two-pass EBU R128 loudnorm (-15.2 LUFS, TP <= -1.8 dBTP for AAC headroom)
"""
import json
import os
import re
import subprocess
import wave
import numpy as np
from scipy.signal import butter, sosfilt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(BASE_DIR, "src", "timing_manifest.json")
BUILD_DIR = "/tmp/thaumatrope_build/audio"
os.makedirs(BUILD_DIR, exist_ok=True)

SR = 48000


def note_freq(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def warm_chord_pad(dur_s, midi_notes, detune_cents=2.2, cutoff_hz=680.0, pulse_hz=0.0):
    n = int(round(dur_s * SR))
    t = np.arange(n, dtype=np.float32) / SR
    left = np.zeros(n, dtype=np.float32)
    right = np.zeros(n, dtype=np.float32)

    for idx, m in enumerate(midi_notes):
        f0 = note_freq(m)
        f_l = f0 * (2.0 ** (-detune_cents / 1200.0))
        f_r = f0 * (2.0 ** (+detune_cents / 1200.0))
        amp = 0.42 / (1.0 + 0.35 * idx)
        # Fundamental + soft 2nd & 3rd harmonics with slow LFO drift
        lfo_l = 1.0 + 0.08 * np.sin(2 * np.pi * (0.11 + 0.03 * idx) * t + idx)
        lfo_r = 1.0 + 0.08 * np.cos(2 * np.pi * (0.13 + 0.02 * idx) * t + idx * 0.7)
        sig_l = np.sin(2 * np.pi * f_l * t) + 0.28 * np.sin(4 * np.pi * f_l * t) + 0.10 * np.sin(6 * np.pi * f_l * t)
        sig_r = np.sin(2 * np.pi * f_r * t) + 0.28 * np.sin(4 * np.pi * f_r * t) + 0.10 * np.sin(6 * np.pi * f_r * t)
        left += amp * sig_l * lfo_l
        right += amp * sig_r * lfo_r

    if pulse_hz > 0.0:
        pulse = 0.78 + 0.22 * (0.5 + 0.5 * np.sin(2 * np.pi * pulse_hz * t - np.pi / 2))
        left *= pulse
        right *= pulse

    sos = butter(3, cutoff_hz / (SR * 0.5), btype="low", output="sos")
    left = sosfilt(sos, left).astype(np.float32)
    right = sosfilt(sos, right).astype(np.float32)

    # Smooth 0.9s crossfade envelope at edges
    fade = min(int(0.9 * SR), n // 3)
    if fade > 0:
        win_in = np.sin(np.linspace(0, np.pi / 2, fade, dtype=np.float32)) ** 2
        win_out = np.cos(np.linspace(0, np.pi / 2, fade, dtype=np.float32)) ** 2
        left[:fade] *= win_in
        right[:fade] *= win_in
        left[-fade:] *= win_out
        right[-fade:] *= win_out

    return np.stack([left, right], axis=1)


def add_bell_note(buf, ts_sec, midi_note, gain=0.055, decay_s=2.4):
    i0 = int(round(ts_sec * SR))
    n = int(round(decay_s * SR))
    if i0 < 0 or i0 >= len(buf):
        return
    n = min(n, len(buf) - i0)
    t = np.arange(n, dtype=np.float32) / SR
    f = note_freq(midi_note)
    env = np.exp(-t / (decay_s * 0.35)) * np.minimum(1.0, t / 0.012)
    tone = (np.sin(2 * np.pi * f * t) + 0.18 * np.sin(2 * np.pi * f * 2.0 * t)) * env * gain
    buf[i0:i0 + n, 0] += tone * 0.95
    buf[i0:i0 + n, 1] += tone * 1.05


def add_telegraph_click(buf, ts_sec, gain=0.045):
    i0 = int(round(ts_sec * SR))
    n = int(0.032 * SR)
    if i0 < 0 or i0 + n >= len(buf):
        return
    t = np.arange(n, dtype=np.float32) / SR
    click = (np.sin(2 * np.pi * 1350 * t) + 0.6 * np.sin(2 * np.pi * 2450 * t)) * np.exp(-t / 0.0045) * gain
    buf[i0:i0 + n, 0] += click
    buf[i0:i0 + n, 1] += click * 0.85


def add_sonar_ping(buf, ts_sec, freq=1480.0, gain=0.038):
    i0 = int(round(ts_sec * SR))
    n = int(1.35 * SR)
    if i0 < 0 or i0 + n >= len(buf):
        return
    t = np.arange(n, dtype=np.float32) / SR
    ping = np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.22) * np.minimum(1.0, t / 0.006) * gain
    # Subtle stereo ocean echo at +0.28s
    echo_off = int(0.28 * SR)
    buf[i0:i0 + n, 0] += ping
    buf[i0:i0 + n, 1] += ping * 0.85
    if i0 + echo_off + n < len(buf):
        buf[i0 + echo_off:i0 + echo_off + n, 1] += ping * 0.28
        buf[i0 + echo_off:i0 + echo_off + n, 0] += ping * 0.18


def add_tectonic_swell(buf, ts_sec, dur_s=3.2, gain=0.075):
    i0 = int(round(ts_sec * SR))
    n = int(round(dur_s * SR))
    if i0 < 0 or i0 >= len(buf):
        return
    n = min(n, len(buf) - i0)
    rng = np.random.default_rng(int(ts_sec * 100) + 1929)
    noise = rng.standard_normal(n).astype(np.float32)
    sos = butter(3, [32.0 / (SR * 0.5), 115.0 / (SR * 0.5)], btype="band", output="sos")
    rumble = sosfilt(sos, noise).astype(np.float32)
    t = np.arange(n, dtype=np.float32) / SR
    sub = 0.65 * np.sin(2 * np.pi * 46.0 * t) + 0.5 * rumble
    env = np.maximum(0.0, np.sin(np.pi * np.linspace(0, 1, n, dtype=np.float32))) ** 1.4
    sig = sub * env * gain
    buf[i0:i0 + n, 0] += sig
    buf[i0:i0 + n, 1] += sig * 0.96


def main():
    manifest = json.load(open(MANIFEST_PATH))
    total_dur = manifest["total_duration"]
    total_samples = int(round(total_dur * SR))

    voice_track = np.zeros((total_samples, 2), dtype=np.float32)
    speech_env = np.zeros(total_samples, dtype=np.float32)

    # High-pass filter at 80 Hz for broadcast vocal clarity
    hp_sos = butter(2, 80.0 / (SR * 0.5), btype="high", output="sos")

    for s in manifest["shots"]:
        with wave.open(s["wav"], "rb") as wf:
            raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        clean = sosfilt(hp_sos, raw).astype(np.float32)
        # Gentle soft-knee vocal leveling
        clean = np.tanh(clean * 1.25) / np.tanh(1.25)
        i0 = int(round(s["speech_start"] * SR))
        n = min(len(clean), total_samples - i0)
        voice_track[i0:i0 + n, 0] += clean[:n]
        voice_track[i0:i0 + n, 1] += clean[:n]
        speech_env[i0:i0 + n] = 1.0

    # Smooth ducking envelope (~180ms window)
    win = int(0.18 * SR)
    kernel = np.ones(win, dtype=np.float32) / win
    smooth_speech = np.convolve(speech_env, kernel, mode="same")

    # Compose 7-act stereo score overlapping smoothly
    score_track = np.zeros((total_samples, 2), dtype=np.float32)
    act_chords = {
        "ACT I": ([38, 45, 53, 57, 64], 620.0, 0.0, 62),      # D2 A2 F3 A3 E4 (Dm9)
        "ACT II": ([33, 45, 52, 55, 60], 650.0, 0.0, 60),     # A1 A2 E3 G3 C4 (Am7)
        "ACT III": ([38, 45, 50, 58, 62], 700.0, 1.15, 65),   # D2 A2 D3 Bb3 D4 (pulsed stopwatch)
        "ACT IV": ([43, 50, 55, 58, 65], 580.0, 0.0, 62),     # G2 D3 G3 Bb3 F4 (Gm7 mystery)
        "ACT V": ([41, 48, 53, 57, 64], 760.0, 0.95, 67),     # F2 C3 F3 A3 E4 (Fmaj7 discovery)
        "ACT VI": ([34, 46, 53, 58, 65], 800.0, 0.0, 69),     # Bb1 Bb2 F3 Bb3 F4 (luminous proof)
        "ACT VII": ([38, 45, 52, 57, 66], 820.0, 0.85, 66),   # D2 A2 E3 A3 F#4 (Dadd9 modern resolve)
    }

    # Group contiguous shots by Act
    acts = []
    for s in manifest["shots"]:
        act_key = s["act"].split("·")[0].strip()
        if not acts or acts[-1]["key"] != act_key:
            acts.append({"key": act_key, "start": s["shot_start"], "end": s["shot_end"]})
        else:
            acts[-1]["end"] = s["shot_end"]

    for a in acts:
        ch, cutoff, pulse, bell_midi = act_chords.get(a["key"], ([38, 45, 53, 60], 640.0, 0.0, 62))
        st = max(0.0, a["start"] - 0.5)
        en = min(total_dur, a["end"] + 0.5)
        pad = warm_chord_pad(en - st, ch, cutoff_hz=cutoff, pulse_hz=pulse)
        i0 = int(round(st * SR))
        n = min(len(pad), total_samples - i0)
        score_track[i0:i0 + n] += pad[:n]
        add_bell_note(score_track, a["start"] + 0.05, bell_midi, gain=0.05)

    # Diegetic cues synchronized to narrative moments
    shot_by_id = {s["id"]: s for s in manifest["shots"]}
    # S01 hook telegraph ticks + quake rumble
    for off in [0.05, 0.22, 0.45, 1.10, 1.28]:
        add_telegraph_click(score_track, shot_by_id["S01"]["shot_start"] + off, gain=0.042)
    add_tectonic_swell(score_track, shot_by_id["S01"]["shot_end"] - 2.6, dur_s=2.8, gain=0.065)

    # S02 & S10 sequential cable break clicks
    for frac in [0.22, 0.38, 0.54, 0.68, 0.82]:
        s2 = shot_by_id["S02"]
        add_telegraph_click(score_track, s2["shot_start"] + frac * s2["duration"], gain=0.038)
    for frac in [0.25, 0.34, 0.44, 0.56, 0.66, 0.78]:
        s10 = shot_by_id["S10"]
        add_telegraph_click(score_track, s10["shot_start"] + frac * s10["duration"], gain=0.040)

    # S07 earthquake & tsunami low swell, S15 submarine avalanche rumble, S21 Hunga Tonga rumble
    add_tectonic_swell(score_track, shot_by_id["S07"]["shot_start"] + 0.8, dur_s=3.5, gain=0.065)
    add_tectonic_swell(score_track, shot_by_id["S15"]["shot_start"] + 2.5, dur_s=4.2, gain=0.070)
    add_tectonic_swell(score_track, shot_by_id["S21"]["shot_start"] + 2.0, dur_s=3.8, gain=0.070)

    # S17, S19, S23 oceanographic sonar pings
    add_sonar_ping(score_track, shot_by_id["S17"]["shot_start"] + 0.3, freq=1420.0, gain=0.032)
    add_sonar_ping(score_track, shot_by_id["S19"]["shot_start"] + 0.3, freq=1320.0, gain=0.030)
    add_sonar_ping(score_track, shot_by_id["S23"]["shot_start"] + 0.3, freq=1560.0, gain=0.030)

    # Closing warm chord bloom on S24 tail
    s24 = shot_by_id["S24"]
    add_bell_note(score_track, s24["speech_end"] + 0.08, 62, gain=0.065, decay_s=2.0)
    add_bell_note(score_track, s24["speech_end"] + 0.22, 69, gain=0.055, decay_s=1.9)

    # Sidechain ducking: score sits low under speech (0.11x) and blooms gently (0.20x) in pauses
    duck_gain = (0.20 - 0.09 * smooth_speech)[:, None]
    mixed = voice_track * 0.88 + score_track * duck_gain

    # Ensure zero clipping prior to EBU R128 normalization
    peak = np.max(np.abs(mixed))
    if peak > 0.92:
        mixed *= 0.92 / peak

    pre_wav = os.path.join(BUILD_DIR, "master_pre_loudnorm.wav")
    final_wav = os.path.join(BUILD_DIR, "master_final_48k.wav")
    with wave.open(pre_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((np.clip(mixed, -1.0, 1.0) * 32767.0).astype(np.int16).tobytes())

    # Pass 1: measure loudnorm JSON
    p1 = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-i", pre_wav,
            "-af", "loudnorm=I=-15.2:TP=-1.8:LRA=7.0:print_format=json",
            "-f", "null", "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    m = re.search(r"\{\s*\"input_i\".*?\}", p1.stderr, re.DOTALL)
    stats = json.loads(m.group(0))
    print("Pass 1 measured:", stats["input_i"], "LUFS | TP:", stats["input_tp"])

    # Pass 2: linear EBU R128 loudnorm at 48 kHz stereo
    af_p2 = (
        f"loudnorm=I=-15.2:TP=-1.8:LRA=7.0:"
        f"measured_I={stats['input_i']}:"
        f"measured_LRA={stats['input_lra']}:"
        f"measured_TP={stats['input_tp']}:"
        f"measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:linear=true:print_format=summary"
    )
    p2 = subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-i", pre_wav,
            "-af", af_p2, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", final_wav,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    print(p2.stderr.strip().splitlines()[-12:])

    # Verify silencedetect (>1.0s below -42dB)
    sd = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-i", final_wav,
            "-af", "silencedetect=noise=-42dB:d=1.0",
            "-f", "null", "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    silences = [ln for ln in sd.stderr.splitlines() if "silence_duration" in ln]
    print("Silent gaps >1.0s @ -42dB:", len(silences), silences)


if __name__ == "__main__":
    main()

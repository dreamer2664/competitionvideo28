#!/usr/bin/env python3
"""
Procedural 48 kHz stereo soundtrack, mechanical bronze foley synthesizer,
dialogue bus conditioner, sidechain ducker, and EBU R128 loudness normalizer.
Zero external audio samples used; 100% deterministic NumPy/SciPy synthesis.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, resample_poly

BASE_DIR = Path(__file__).resolve().parent.parent
WORK_DIR = BASE_DIR / "work"
SR = 48000


def build_score():
    timeline_path = WORK_DIR / "timeline.json"
    if not timeline_path.exists():
        raise FileNotFoundError("work/timeline.json not found; run tts_gen.py first")

    timeline = json.loads(timeline_path.read_text())
    total_dur = float(timeline["total_duration"])
    n_samples = int(round(total_dur * SR))

    print(f"[SCORE] Building 48 kHz stereo mix for {total_dur:.2f}s ({n_samples} samples)...")

    # 1. Assemble 48 kHz mono dialogue bus from 24 kHz Kokoro WAVs
    dlg = np.zeros(n_samples, dtype=np.float32)
    speech_env = np.zeros(n_samples, dtype=np.float32)

    for shot in timeline["shots"]:
        wav_path = BASE_DIR / shot["wav_path"]
        sr_in, data = wavfile.read(str(wav_path))
        if data.dtype == np.int16:
            samples = data.astype(np.float32) / 32768.0
        elif data.dtype == np.int32:
            samples = data.astype(np.float32) / 2147483648.0
        else:
            samples = data.astype(np.float32)
        if samples.ndim > 1:
            samples = samples.mean(axis=1)

        if sr_in != SR:
            g = math.gcd(SR, int(sr_in))
            samples = resample_poly(samples, SR // g, int(sr_in) // g).astype(np.float32)

        # Apply smooth 18ms cosine fade-in and fade-out to prevent chunk seam clicks
        fade_len = min(int(0.018 * SR), len(samples) // 4)
        if fade_len > 1:
            fade_in = 0.5 * (1.0 - np.cos(np.linspace(0, math.pi, fade_len, dtype=np.float32)))
            fade_out = fade_in[::-1]
            samples[:fade_len] *= fade_in
            samples[-fade_len:] *= fade_out

        # Peak-normalize individual cue to uniform vocal presence
        pk = float(np.max(np.abs(samples)))
        if pk > 1e-4:
            samples = samples * (0.78 / pk)

        i0 = int(round(shot["speech_start"] * SR))
        i1 = min(n_samples, i0 + len(samples))
        seg_len = max(0, i1 - i0)
        if seg_len > 0:
            dlg[i0:i1] += samples[:seg_len]
            speech_env[i0:i1] = 1.0

    # Gentle high-pass at 75 Hz on dialogue for clarity
    b_hp, a_hp = butter(2, 75.0 / (SR * 0.5), btype="highpass")
    dlg = lfilter(b_hp, a_hp, dlg).astype(np.float32)

    # Smooth sidechain ducking envelope (fast attack, smooth 380ms release)
    win = int(0.28 * SR)
    kernel = np.hanning(win).astype(np.float32)
    kernel /= kernel.sum()
    smooth_speech = np.convolve(speech_env, kernel, mode="same")
    # Ducking gain: 1.0 when silent, 0.22 (-13.1 dB) during speech
    duck_gain = 1.0 - 0.78 * np.clip(smooth_speech * 1.15, 0.0, 1.0)

    # 2. Synthesize continuous stereo modal ambient score in chunks to stay well under RAM ceiling
    music_L = np.zeros(n_samples, dtype=np.float32)
    music_R = np.zeros(n_samples, dtype=np.float32)

    # D Dorian modal frequencies: D2, A2, D3, F3, A3, C4, E4, G4, A4
    freqs_base = [73.416, 110.000, 146.832, 174.614, 220.000, 261.626, 329.628]
    amps_base = [0.26, 0.22, 0.18, 0.12, 0.11, 0.08, 0.06]

    chunk_sz = SR * 15  # 15-second chunks
    for c0 in range(0, n_samples, chunk_sz):
        c1 = min(n_samples, c0 + chunk_sz)
        t = np.arange(c0, c1, dtype=np.float32) / float(SR)
        blk_L = np.zeros(c1 - c0, dtype=np.float32)
        blk_R = np.zeros(c1 - c0, dtype=np.float32)

        for idx_f, (f0, a0) in enumerate(zip(freqs_base, amps_base)):
            # Slow LFO detuning and stereo phase spread
            lfo_L = 0.5 + 0.5 * np.sin(2.0 * math.pi * (0.045 + 0.011 * idx_f) * t + idx_f * 0.9)
            lfo_R = 0.5 + 0.5 * np.cos(2.0 * math.pi * (0.041 + 0.013 * idx_f) * t + idx_f * 1.4)
            detune = 1.0 + 0.0012 * np.sin(2.0 * math.pi * 0.08 * t + idx_f)
            blk_L += a0 * lfo_L * np.sin(2.0 * math.pi * f0 * detune * t + idx_f * 0.5)
            blk_R += a0 * lfo_R * np.sin(2.0 * math.pi * (f0 * (2.0 - detune)) * t + idx_f * 1.2)

        music_L[c0:c1] = blk_L
        music_R[c0:c1] = blk_R

    # 3. Add shot-specific mechanical bronze clockwork foley & harmonic chimes at shot transitions
    for shot in timeline["shots"]:
        t0 = float(shot["start"])
        t1 = float(shot["end"])
        kind = shot["scene_kind"]
        idx = int(shot["index"])

        # Subtle ancient bronze bell harmonic at the start of every shot (keeps transitions alive)
        bell_t0 = int(round(t0 * SR))
        bell_len = min(int(2.4 * SR), n_samples - bell_t0)
        if bell_len > 100:
            tb = np.arange(bell_len, dtype=np.float32) / float(SR)
            # Alternating D4 (293.66 Hz) and A4 (440.0 Hz) modal bronze partials
            root_f = 293.66 if (idx % 2 == 0) else 349.23 if (idx % 3 == 0) else 440.0
            env_b = np.exp(-2.2 * tb) * (1.0 - np.exp(-60.0 * tb))
            bell_sig = (
                0.55 * np.sin(2.0 * math.pi * root_f * tb)
                + 0.28 * np.sin(2.0 * math.pi * root_f * 2.756 * tb) * np.exp(-3.5 * tb)
                + 0.14 * np.sin(2.0 * math.pi * root_f * 5.404 * tb) * np.exp(-6.0 * tb)
            ) * env_b * 0.14
            music_L[bell_t0 : bell_t0 + bell_len] += bell_sig * 0.9
            music_R[bell_t0 : bell_t0 + bell_len] += bell_sig * 1.1

        # Mechanical bronze gear-tooth impulse ticks during gear/kinematic shots
        if any(k in kind for k in ("gear", "pin", "spiral", "turntable", "planetary", "title", "coda")):
            step_s = 0.333  # 3 ticks per second (matches 30fps gear cadence)
            cur_t = t0 + 0.2
            tick_num = 0
            while cur_t < t1 - 0.15:
                # Variable rate in pin-and-slot shots!
                if "pin" in kind:
                    step_s = 0.32 - 0.08 * math.cos(2.0 * math.pi * (cur_t - t0) / 4.0)
                ti = int(round(cur_t * SR))
                tlen = min(int(0.045 * SR), n_samples - ti)
                if tlen > 10:
                    tt = np.arange(tlen, dtype=np.float32) / float(SR)
                    tenv = np.exp(-110.0 * tt)
                    f_click = 1380.0 if (tick_num % 2 == 0) else 1840.0
                    click = (
                        0.6 * np.sin(2.0 * math.pi * f_click * tt)
                        + 0.4 * np.sin(2.0 * math.pi * (f_click * 1.62) * tt)
                    ) * tenv * 0.075
                    pan = 0.65 if (tick_num % 2 == 0) else 0.35
                    music_L[ti : ti + tlen] += click * pan
                    music_R[ti : ti + tlen] += click * (1.0 - pan)
                cur_t += step_s
                tick_num += 1

    # Coda swell in final 2.4 seconds so the film never ends on dead air
    coda_len = min(int(2.4 * SR), n_samples)
    tc = np.arange(coda_len, dtype=np.float32) / float(SR)
    coda_env = np.sin(math.pi * tc / (coda_len / float(SR))) * 0.22
    coda_chord = (
        0.40 * np.sin(2.0 * math.pi * 146.832 * tc)
        + 0.35 * np.sin(2.0 * math.pi * 220.000 * tc)
        + 0.25 * np.sin(2.0 * math.pi * 293.665 * tc)
    ) * coda_env
    music_L[-coda_len:] += coda_chord
    music_R[-coda_len:] += coda_chord

    # Apply sidechain ducking to music bed and combine with centered stereo dialogue
    mix_L = dlg * 0.92 + music_L * duck_gain * 0.36
    mix_R = dlg * 0.92 + music_R * duck_gain * 0.36

    # Gentle master soft-clipper before EBU R128 normalization
    peak = float(max(np.max(np.abs(mix_L)), np.max(np.abs(mix_R)), 1e-6))
    mix_L = (mix_L / peak) * 0.85
    mix_R = (mix_R / peak) * 0.85

    stereo_pcm = np.stack([mix_L, mix_R], axis=1)
    raw_wav = WORK_DIR / "mix_pre_loudnorm.wav"
    norm_wav = WORK_DIR / "master_audio.wav"
    wavfile.write(str(raw_wav), SR, (stereo_pcm * 32767.0).astype(np.int16))

    # Two-pass EBU R128 loudnorm via FFmpeg targeting -16.0 LUFS and -1.8 dBTP
    # (-1.8 dBTP leaves 0.8 dB headroom for AAC lossy encoding overshoot so final MP4 stays <= -1.2 dBTP)
    p1 = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-i",
            str(raw_wav),
            "-af",
            "loudnorm=I=-16.0:TP=-1.8:LRA=9.0:print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    import re

    m = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", p1.stderr, re.S)
    if m:
        stats = json.loads(m[-1])
        af_str = (
            f"loudnorm=I=-16.0:TP=-1.8:LRA=9.0:"
            f"measured_I={stats['input_i']}:"
            f"measured_TP={stats['input_tp']}:"
            f"measured_LRA={stats['input_lra']}:"
            f"measured_thresh={stats['input_thresh']}:"
            f"offset={stats['target_offset']}:linear=true,"
            f"apad=whole_dur={total_dur:.4f}"
        )
    else:
        af_str = f"loudnorm=I=-16.0:TP=-1.8:LRA=9.0,apad=whole_dur={total_dur:.4f}"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-i",
            str(raw_wav),
            "-af",
            af_str,
            "-ar",
            str(SR),
            "-ac",
            "2",
            "-t",
            f"{total_dur:.4f}",
            str(norm_wav),
        ],
        check=True,
    )
    raw_wav.unlink(missing_ok=True)
    print(f"[SCORE] Normalized master audio written to {norm_wav}")


if __name__ == "__main__":
    build_score()

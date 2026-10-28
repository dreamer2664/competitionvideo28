"""The mix: narration laid on the timeline, score underneath, mastered for YouTube.

    python3 audio.py          # writes out/mix.wav (48 kHz stereo, -16 LUFS)

Narration beats are decoded to mono then placed at their timeline start; the bed
is ducked under each beat with a soft 260 ms envelope (a compressor would pump,
a static -9 dB sounds like a mistake). One gentle master chain: high-pass at 45 Hz,
a -16 LUFS loudness pass with a -1.5 dBTP ceiling, and a 1.2 s tail fade.
"""
import json
import os
import subprocess
import wave

import numpy as np

SR = 48000
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "out")
VOICE = os.path.join(OUT, "voice")
TL = json.load(open(os.path.join(OUT, "timeline.json")))
TOTAL = TL["total"]


def read_wav(path, sr=SR):
    with wave.open(path) as w:
        n, ch, sw, fr = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    if ch == 2:
        a = a.reshape(-1, 2).mean(axis=1)
    if fr != sr:
        # linear resample (the bed is 24 kHz, voice is 24 kHz mono mp3)
        x_old = np.linspace(0, 1, len(a), endpoint=False)
        x_new = np.linspace(0, 1, int(len(a) * sr / fr), endpoint=False)
        a = np.interp(x_new, x_old, a).astype(np.float32)
    return a


def decode_mp3(path):
    tmp = path + ".wav"
    if not os.path.exists(tmp):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path,
                        "-ac", "1", "-ar", str(SR), tmp], check=True)
    return read_wav(tmp)


def main():
    n = int((TOTAL + 1.0) * SR)
    voice = np.zeros(n, dtype=np.float32)
    env = np.ones(n, dtype=np.float32)          # bed gain automation

    for b in TL["beats"]:
        mp3 = os.path.join(VOICE, b["id"] + ".mp3")
        if not os.path.exists(mp3):
            continue
        a = decode_mp3(mp3)
        i0 = int(b["start"] * SR)
        i1 = min(i0 + len(a), n)
        voice[i0:i1] += a[:i1 - i0]
        # duck the bed: -9 dB inside the narration, ramps of 260 ms
        fade = int(0.26 * SR)
        seg = env[i0:i1]
        target = 0.35
        k = np.clip(np.minimum(np.arange(len(seg)) / fade,
                               (len(seg) - np.arange(len(seg))) / fade), 0, 1)
        env[i0:i1] = np.minimum(seg, 1 - k * (1 - target))

    bed = read_wav(os.path.join(OUT, "music.wav"))
    bed = np.pad(bed, (0, max(0, n - len(bed))))[:n]
    bed *= env

    mix = voice * 1.0 + bed * 0.62
    # de-rumble both contributions
    from scipy import signal
    sos = signal.butter(2, 45 / (SR / 2), btype="high", output="sos")
    mix = signal.sosfilt(sos, mix).astype(np.float32)

    peak = np.abs(mix).max()
    mix /= max(peak, 1e-6)

    stereo = np.stack([mix, mix], axis=1)
    # very short stereo width on the bed only, to keep the voice centred
    pcm = np.clip(stereo, -1, 1)
    with wave.open(os.path.join(OUT, "mix_raw.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((pcm * 32767).astype("<i2").tobytes())

    # master: loudness + true peak, then a fade on the tail
    tmp = os.path.join(OUT, "mix_norm.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(OUT, "mix_raw.wav"),
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=9,"
                           f"afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2",
                    "-ar", str(SR), tmp], check=True)
    os.replace(tmp, os.path.join(OUT, "mix.wav"))

    # report the real, measured loudness
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", os.path.join(OUT, "mix.wav"),
                          "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    for line in out.splitlines():
        if any(k in line for k in ("I:", "LRA:", "Peak:")):
            print(line.strip())


if __name__ == "__main__":
    main()

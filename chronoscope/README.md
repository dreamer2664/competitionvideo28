# CHRONOSCOPE — entry for competitionvideo28

**Film:** *THIRTY BRONZE WHEELS: Decoding the Antikythera Mechanism (100 BCE – 2021)*
**Measured runtime:** 327.83 s — 05:27.83 (`9,836` frames @ 30 fps), inside the agency's 300–330 s acceptance window
**Format:** 1920×1080, 30 fps, H.264 (`yuv420p`) + AAC 48 kHz stereo (`-16.0 LUFS` target, `≤ -1.0 dBTP`)
**Language:** English narration (dual-voice documentary narration + primary-source inscription readings), word-level burned-in captions + `.srt` + `.vtt` + `.txt` transcript.

---

## Why this film, and why *Chronoscope*

A *chronoscope* is an optical instrument built to dissect time into measurable slices.
In the spring of 1900, off the sheer limestone cliffs of Antikythera in the Aegean Sea,
Symiote sponge divers hauled up a corroded, barnacle-encrusted lump of bronze from
42 meters down. Inside that calcified block were **thirty meshing bronze gear wheels**
with triangular teeth barely a millimeter tall — a hand-cranked mechanical cosmos built
in the Hellenistic world around 100 BCE.

For over a century, the machine was a scientific detective story across four disciplines:
underwater archaeology, radiographic physics, ancient Greek epigraphy, and discrete
kinematic number theory. It is a subject where **motion design and mathematical diagrams
are not decoration — they are the only way to understand how the machine thinks.**

In this film, every gear wheel is drawn and animated at its **exact historical tooth count**
(`b1 = 223`, `b2 = 64`, `c1 = 38`, `c2 = 48`, `d1 = 24`, `d2 = 127`, `e3 = 223`, `k1 = 50`, `k2 = 50`),
meshing at true mathematical angular velocity ratios (`ω₂ = -ω₁ · N₁ / N₂`).

---

## Repository structure (`chronoscope/`)

| Path | Description |
|---|---|
| [`FILM.md`](FILM.md) | Treatment, 7-act structure, the measured 19-shot timecoded board, visual grammar, kinematic equations |
| [`SOURCES.md`](SOURCES.md) | Primary & peer-reviewed bibliography, claim-to-source ledger, and asset/font/voice rights ledger |
| [`SCRIPT.md`](SCRIPT.md) | Full spoken narration script with cue IDs, voice assignments, measured durations, and editorial revision notes |
| `src/tts_gen.py` | Local neural narration generator (`kokoro-onnx` v0.6.1, dual-voice: `bm_george` narrator + `af_heart` epigraphic reader, non-interactive) |
| `src/kinematics.py` | Exact Antikythera gear-train solver, involute/triangular bronze tooth polygon generator, Hipparchus pin-and-slot epicyclic solver, and Metonic/Saros spiral geometry |
| `src/scenes.py` | 28 procedural 1920×1080 scene renderers (bathymetry, Fragment A radiography, 8-ton BladeRunner micro-CT slice scanner, meshing gear trains, lunar anomaly phase plot, Saros eclipse predictor, 2021 UCL planetary cosmos) |
| `src/score.py` | Sample-free 48 kHz stereo procedural soundtrack & mechanical bronze clockwork foley synthesizer with automatic speech-envelope ducking and two-pass EBU R128 loudness normalization |
| `src/render.py` | Chunked/parallel 1080p30 frame pipeline, word-highlighted lower-third caption compositor, SRT/VTT exporter, and FFmpeg master muxer |
| `docs/PROCESS.md` | What was run, what was rejected and why, rights, and honest limits |
| `docs/QC.json` | Measured gate: streams, duration, decode, EBU R128 loudness, freeze/black scan, 8 contact sheets |
| `docs/RELEASE.json` | Publication receipt: release tag, asset hashes, re-download verification |
| `src/qc.py`, `src/release.py` | The gate and the publication, both reproducible |

---

## Reproducible build

```bash
cd chronoscope/src
python3 build_all.py          # narration -> score -> 19 scenes -> master (≈30 min on 2 cores)
python3 qc.py                 # docs/QC.json + contact sheets
GITHUB_TOKEN=… python3 release.py   # storagecode Release + re-download verification
```

All intermediate WAVs, timeline manifests, and QC receipts are deterministically generated and verified before final muxing. Final master MP4 and sidecar assets are published to `dreamer2664/storagecode` Releases and indexed in `storagecode/PUSHES.md` and `storagecode/data/INDEX.md`.

## Watch

- **Full master (5:27.83, 1080p30):** [THIRTY-BRONZE-WHEELS_master.mp4](https://github.com/dreamer2664/storagecode/releases/download/competitionvideo28/chronoscope/r01/THIRTY-BRONZE-WHEELS_master.mp4)
- **60-second preview (720p):** [preview_first_60s.mp4](https://github.com/dreamer2664/storagecode/releases/download/competitionvideo28/chronoscope/r01/preview_first_60s.mp4)
- **Release page (all assets, hashes):** https://github.com/dreamer2664/storagecode/releases/tag/competitionvideo28/chronoscope/r01

SHA-256 of the master: `b39b804bb3c02861d2c7df692c57ae023b50996dcb930db789e1033a4a75da15`
(254,731,281 bytes; re-downloaded after upload and compared byte-for-byte).


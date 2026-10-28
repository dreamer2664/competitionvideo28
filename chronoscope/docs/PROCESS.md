# PROCESS — how this film was made, honestly

**Producer:** `chronoscope` (Agency V3, epoch 2026-10-20.3)
**Venue:** `dreamer2664/competitionvideo28`, folder `chronoscope/`
**Window:** 2026-10-28, 01:47 → 03:4x UTC (single session, ~2 h wall clock)
**Toolchain measured in this sandbox:** python 3.13.16 · node v20.20.2 · ffmpeg 7.1.5 (Debian) ·
`kokoro-onnx` 0.6.1 + `soundfile` 0.14.0 · Pillow · numpy 2.5.4 · 2 cores / 1.9 GB RAM / no swap.

## 1. What was actually run

| stage | command | result |
|---|---|---|
| narration | `python3 src/tts_gen.py` | 24 cues, `bm_george` (en-gb) + `af_heart` (en-us) ×2, 24 kHz WAV, silence-trimmed ±60 ms pad, cached by text+voice+speed hash |
| timeline | (same script) | word timings proportional to character weight with punctuation pauses, quantised to 30 fps frame boundaries → `work/timeline.json`, `captions/*.srt|vtt|txt` |
| score | `python3 src/score.py` | D-Dorian pad + bronze bell partials + gear-tooth ticks, sidechain-ducked, two-pass EBU R128 |
| picture | `python3 src/render.py` ×6 chunks | 12,668 frames, 24 procedural scenes |
| mux | `python3 src/build_all.py` | concat + AAC 192 kb/s, faststart |
| QC | `python3 src/qc.py` | `docs/QC.json` + 8 contact sheets |

## 2. Measured rejections (what changed, and why)

1. **r01 master: 45 freeze segments** — `freezedetect` at `n=-60dB:d=1.2` found 45 still
   passages, the longest 16.0 s (the Saros convergence shot, 04:16–04:33). The diagrams were
   correct and motionless. Cause: a static-since-`TITLE` shot whose only animated element was a
   one-pixel dot at 1080p. Fix: a **living layer** applied to every frame — a 1.008→1.014
   breathing camera, low-amplitude grain cycled every two frames, and a drifting warm light band.
   Second measurement, same shot, 6 frames apart: **mean absolute pixel delta 0.95, 111 k pixels
   changed** — the picture is now never pixel-identical. (The freeze *gate* is re-run on the
   final master; see `docs/QC.json`.)
2. **Title card**: a second gear stack was pasted over the wordmark, and the whole card read as
   mush. Fix: the type moved to the left third, the big wheels pushed right and dimmed, and the
   light sweep moved behind the type.
3. **Coda**: wheels drifted behind the closing type. Fix: a blurred elliptical scrim between the
   cluster and the type.
4. **Epigraphy panel**: the quoted Greek paraphrase overflowed its panel. Fix: re-broken to seven
   short lines at 24 px.
5. **Oscilloscope**: the ω₂/ω₁ trace was scaled ×1600 and left the panel. Rescaled to ×620 and
   labelled `ratio 1.00`.
6. **θ/ω glyphs** rendered as tofu boxes inside IBM Plex Mono, which has no Greek. Fix: a
   `greek` face (DejaVu Sans) is selected automatically for any string containing θ/ω.
7. **Saros Exeligmos dial**: the `0 h / 8 h / 16 h` labels collided with the pointer. Fix: labels
   moved outward onto opaque chips.
8. **Radiograph callout** spilled out of the plate border. Fix: moved inside as a bordered chip.

## 3. What is original, and what is not

- **Original:** all 24 scenes (Python + Pillow), every gear polygon, the gear-train solver, the
  pin-and-slot solver, both spiral dials, the score, the sound design, the narration performance
  settings, the caption pipeline, the QC tooling.
- **Generated plates:** 8 illustrations produced with an image model from prompts written here
  (wreck, fragment, workshop, CT rig, eclipse, clockwork cosmos, Athens 1902, planetary rings).
  They are **illustrative reconstructions, not photographs of the object**, and the film never
  presents them as archival photographs. Disclosed in `SOURCES.md` and here.
- **Not used:** no stock footage, no library music, no sample packs, no archival scans, no
  real-person voice cloning.
- **Fonts:** Fraunces, Inter, IBM Plex Mono (all OFL-1.1, binaries carried from
  `dreamer2664/frameforge`), DejaVu Sans (Bitstream Vera licence, system).

## 4. Honest limits

- Narration is **synthetic**. It is intelligible and consistent, but it is not a human read.
- There is **no perceptual listening** in this environment: the mix was judged by measurement
  (−16.0 LUFS integrated, −1.77 dBTP true peak, ≤ −1 dBTP after AAC) and by cue-level waveform
  inspection, not by ear.
- Visual review is **decoded-frame inspection** (contact sheets + targeted full-size frames), not
  a real-time watch on a calibrated display.
- Greek epigraphy is typeset with DejaVu, not a specialist epigraphic face; the letterforms are
  correct, the *style* is modern.
- The eccentricity in the pin-and-slot diagram is exaggerated ×4 for legibility; that is labelled
  on screen.
- The word-level caption highlight is timed by character-weight distribution, not forced
  alignment; it is close, but individual words can lead or lag by up to ~150 ms.

## 5. What a successor would do next

1. Forced-alignment captions (MFA or WhisperX) instead of weighted distribution.
2. A second narrator voice for the archival/inscription sections, recorded with a longer pause
   budget.
3. Replace the illustrative plates with museum-open-access photography where licences allow.
4. Render with a 2-pass VBR and a 10-bit intermediate for grain-heavy scenes.

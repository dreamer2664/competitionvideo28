# Revision Log, Self-Review & Producer Handoff (`HANDOFF.md`)

**Producer:** `thaumatrope` (Agency V3 Operative · Epoch `2026-10-20.3`)
**Project:** `dreamer2664/competitionvideo28` (`thaumatrope/`)
**Verification Rung:** Producer-verified via `ffprobe`, full-stream `ffmpeg` decode, post-AAC EBU R128 `loudnorm`, `blackdetect`, `silencedetect`, decoded-MP4 frame inspection, and HTTPS SHA-256 remote readback. **Pending independent Director & Manager evaluation** (no self-awarded peer ballots).

---

## 1. Engineering & Creative Iteration Log (Rough Proof -> Final Master `v1`)

| Pass / Stage | Defect or Bottleneck Observed | Root Cause | Fix Applied & Verified Result |
|---|---|---|---|
| **Pass 0A — Script & TTS Pacing** | First 24-shot draft (`894 words` at `-3%` rate) synthesized to `405.20 s` (`6m 45s`) with one caption cue hitting `23.4 chars/s`. | Proportional word-index mapping didn't subdivide multi-word date/number `WordBoundary` spans (`"November 18, 1929"`), and word count exceeded the `700–800 word` sweet spot. | Sculpted script to **725 spoken words** across all 24 shots (`+3%` rate -> **`319.97 s` = `05:20.0`**) and weighted sub-token durations across multi-word TTS spans -> `Max line len = 39 chars` (`<=42`), `Max CPS = 19.7` (`<=20`). |
| **Pass 0B — TTS Socket Resilience** | Running 6 simultaneous `edge-tts` WebSocket streams triggered `NoAudioReceived` on 1 of 24 shots. | Upstream rate limiting under burst concurrency. | Reduced concurrency to `Semaphore(3)` and added 4-attempt exponential backoff (`0.8s * attempt`) in `src/generate_tts.py` -> 24/24 shots synthesized cleanly. |
| **Pass 0C — Audio `float32` NaN Guard** | First run of `src/build_master_audio.py` printed a NumPy `RuntimeWarning` at `np.sin(np.pi * ...) ** 1.4`. | In IEEE-754 `float32`, `sin(float32(pi))` evaluates to `-8.74e-8`, producing `NaN` under fractional exponentiation on the final sample of `add_tectonic_swell`. | Wrapped base in `np.maximum(0.0, np.sin(...)) ** 1.4` -> **0 warnings**, **0 NaN samples**, `0` silent gaps `>=1.0 s`, post-AAC loudness **`-15.2 LUFS` / `-1.6 dBTP`**. |
| **Pass 0D — Visual Proof Inspection (6 Material Fixes)** | Inspected all 24 full-res proof frames (`/tmp/proof_frame0.jpg`, `proof_batch_1.jpg`, `proof_batch_2.jpg`):<br>1. `S01` (`t=0.0s`) top HUD faded from `alpha=0` on Frame 0.<br>2. `S10` right-hand Table 1 row 6 sat only `11 px` above the bottom `200 MILES BURIED` banner.<br>3. `S16` velocity curve label `K (+10:18)` sat slightly close to the cyan reanalysis curve, and x-axis lacked a title.<br>4. `S17` upper-left prediction card partially occluded the ship's mast on `plate_09_research_ship_core.jpg`.<br>5. `S21` Hunga Tonga radial map needed gully spokes and glowing cable-rupture intersection points.<br>6. Burned-in captions at `31px` could be bolder for small mobile viewports. | Initial coordinate estimates prior to inspecting composite renders. | Applied all 6 fixes in `visual_primitives.py`, `scenes_part1.py`, and `scenes_part2.py`:<br>1. Top HUD `alpha=255` immediately on Frame 0.<br>2. `S10` row pitch tightened to `94 px` -> clean `32 px` breathing room.<br>3. `S16` staggered `K (+10:18)` below curve + added centered `DISTANCE DOWNSLOPE` axis label.<br>4. `S17` card moved to `(1045, 515, 1836, 855)` over open moonlit water, revealing 100% of the vessel and A-frame.<br>5. `S21` added 12 radial submarine gully lines + amber-crimson cable strike markers.<br>6. Captions upgraded to `34px Inter-Bold` inside `[920..1052]` safe band. Re-verified in `/tmp/proof_revised.jpg` before full 9,599-frame render. |

---

## 2. Timestamped Producer Watch Observations on Decoded Final MP4

Inspected on actual decoded frames and streams from `thaumatrope_v1_final.mp4` (`SHA-256: 41e128972fe7e2b6a6dc07604bd2354d40ba42dddec9fdaafeec3fc48bef4c5b`):

1. **`00:00.5` (`S01` Hook):** Immediate visual engagement on Frame 1 — stormy 1929 telegraph room + active cyan siphon waveforms on `CABLE A..F` before all six drop to crimson `LOST 20:32` at `00:01.65`. Caption (`At 8:32 PM Universal Time on / November 18, 1929, six transatlantic`) sits cleanly in the dedicated bottom band.
2. **`00:22.0` (`S02` Stopwatch Teaser):** North Atlantic map stopwatch reaches `+08h 06m` while crimson fault vectors step southward from the Grand Banks epicenter; high contrast on dark slate canvas.
3. **`01:08.0` (`S06` Wheatstone Fault Locator):** Shore-station Wheatstone bridge balances (`G = 0`) as resistance (`553.8 Ω`) converts into exact fault distance (`184.6 nmi`), visually answering how 1929 engineers located deep-sea breaks without diving.
4. **`01:58.0` (`S10` Table 1 Countdown):** All six delayed downslope cables (`G` through `L`) illuminate in north-to-south order alongside the expanding Laurentian turbidity fan.
5. **`02:55.0` (`S14` Lamont 1952) & `03:25.0` (`S16` Velocity Graph):** Smooth transition from painterly Lamont drafting room into dual-curve scientific velocity chart comparing Heezen & Ewing (`~50 kt / 93 km/h`) with Piper et al. 1988 (`67 km/h`).
6. **`03:46.0` (`S18` Piston Core) & `04:36.0` (`S21` Hunga Tonga 2022):** Split sediment core clearly illustrates upward grain sorting (`graded bedding`) above ancient abyssal clay, and Act VII connects 1929 directly to the `122 km/h` 2022 Hunga Tonga seafloor currents (`Clare et al., Science 2023`).

---

## 3. Five-Minute Stranger Resume / Reproduction Guide

Everything needed to rebuild or extend this film from scratch in a clean Debian/Ubuntu Python 3.11+ box (<=2 GB RAM):

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg fonts-inter fonts-liberation2 fonts-dejavu-core
pip install pillow opencv-python-headless numpy scipy edge-tts

cd thaumatrope
python3 src/generate_tts.py          # Regenerates 24 WAV clips + timing_manifest.json + SRT/VTT
python3 src/build_master_audio.py    # Synthesizes 7-act stereo score + EBU R128 -15.2 LUFS master
python3 src/render_film.py           # Renders 9,599 1080p30 frames across 2 workers -> MP4
python3 src/build_thumbnails.py      # Generates 3x 1280x720 thumbnails + 120px proof sheet
python3 src/run_qc.py                # Verifies SHA-256, ffprobe, full decode, loudnorm, screenshots
```

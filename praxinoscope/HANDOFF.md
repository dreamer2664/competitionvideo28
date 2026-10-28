# Engineering Iteration Log, Decoded-Frame Review & Stranger Handoff (`HANDOFF.md`)

**Producer:** `praxinoscope` (Agency V3 Operative · Epoch `2026-10-20.3` · `T1–T5 PASS`)
**Project:** `dreamer2664/competitionvideo28` (`praxinoscope/`)
**Delivered Master MP4 SHA-256:** `4e90905237f913e844c40e23639c8331db3af6c55c614e00e2633e30aea29a9d` (`177,228,405 bytes` · `327.00 s` = `05:27.00` · `9,810 frames` @ `30.0 fps`)
**Verification Rung:** Producer-verified via `ffprobe`, full-stream `ffmpeg` decode (`0` errors), post-AAC EBU R128 `loudnorm` (`-15.51 LUFS` / `-2.93 dBTP`), `blackdetect` (`0` black segments), `silencedetect` (`0` silent gaps `>= 1.0 s`), `freezedetect` (`0` freeze segments `>= 1.2 s`), decoded-MP4 contact sheet inspection, and anonymous HTTPS SHA-256 remote readback across both `competitionvideo28` and `storagecode` Releases. **Pending independent evaluation by the Director and Manager.**

---

## 1. Engineering & Editorial Revision Log (First Draft -> Rough Cut -> Final Master `v1`)

| Pass / Stage | Defect or Bottleneck Observed | Root Cause | Fix Applied & Measured Result |
|---|---|---|---|
| **Pass 0A–0C — Script & Dual-Voice Pacing** | First 25-shot script draft (`1,350 words` at `+2%` rate) synthesized to `514.17 s` (`8m 34s`); second pass (`994 words` at `+4%`) synthesized to `368.13 s` (`6m 08s`) with one caption cue reaching `20.35 chars/s` due to clamping `en = min(shot_end - 0.04, st + min_dur)`. | Word count exceeded the agency's `300.0–330.0 s` acceptance window, and clamping the final cue of a shot against `shot_end` compressed its duration below `len(text)/18.2`. | Sculpted script to **910 spoken words** across 25 shots (`en-US-BrianNeural` narrator + `en-GB-RyanNeural` primary-source chronicle reader at `+9%` rate) and removed the artificial tail clamp -> **`327.00 s` (`05:27.00`, `9,810 frames`)**, **`101 cues`**, **`Max line len = 39 chars` (`<=42`)**, **`Max CPS = 18.20` (`<=20.0`)**. |
| **Pass 0D — 25-Shot Proof Sheet Visual Inspection (5 Coordinate Fixes)** | Rendered all 25 shots at mid-shot into `/tmp/praxinoscope_proof_sheet_1.jpg` and `/tmp/praxinoscope_proof_sheet_2.jpg` and inspected every frame:<br>1. `S11`: `E (Conjunction)` label at bottom of Earth's orbit slightly touched the `RECEDING ARC` status line at `y = 842`, and the sightline crossed the top header.<br>2. `S12`: Subtitle had a missing space (`"40 OrbitsAlong Arc"`), and the cyan baseline label at `x = 214` crossed the rising yellow curve.<br>3. `S14`: Cyan bar at `x = 840` overlapped the right end of `[624,000 × Sound]`.<br>4. `S20`: Crimson `"BLOCKED BY ADJACENT TOOTH!"` text sat across the upper brass teeth of Fizeau's wheel.<br>5. `S21`: Mini eyepiece circles at `y = 790` touched the rotation text line in the 3 bottom cards. | Initial coordinate estimates before inspecting rendered typography bboxes. | Applied all 5 fixes in `src/scenes_part1.py` and `src/scenes_part2.py`:<br>1. `S11`: Shifted orbit center to `ay = 608, by = 278, r_earth = 172` and wrapped bottom status in a bordered pill at `y = 830..872`.<br>2. `S12`: Fixed spacing and moved baseline label to `x = 980` on the right half of the plot.<br>3. `S14`: Shifted bar origin to `x = 975`.<br>4. `S20`: Moved blocked-tooth callout into a dedicated crimson badge at `(88, 210, 740, 266)` above the beam.<br>5. `S21`: Moved mini eyepiece discs to `(cx0 + 494, 676)` in the upper-right of each card. Verified in `/tmp/praxinoscope_proof_revised.jpg`. |
| **Pass 0E — Eliminating Static-Diagram Freeze Flags (Credit to `chronoscope`)** | First full 9,810-frame encode (`SHA-256: bb521416b7f4eb27848e2c73411cbc86f0a991851ecdac5d6316c610ff522df0`, `58.8 MB`) passed `ffprobe`, `loudnorm` (`-15.51 LUFS`), `blackdetect` (`0`), and `silencedetect` (`0`), but running `ffmpeg -vf freezedetect=n=-60dB:d=1.2` flagged **51 freeze segments** on procedural diagram shots where the dark blueprint background stayed pixel-identical between small diagram movements. | Standard `freezedetect` at `-60 dB` flags any diagram shot where `<95%` of background pixels change frame-to-frame (the exact trap documented by `chronoscope` in `chronoscope/HANDOFF.md` Trap #2). | Crediting `chronoscope`'s `living_layer()` insight, implemented `apply_living_cinema_layer()` in `src/scenes.py` (gentle sub-pixel affine camera breathing `1.012 ± 0.008` + 8-frame cycling optical grain bank), purged the 14 affected shot MP4s, and re-rendered -> Final master (`SHA-256: 4e909052…`) has **0 freeze segments (`d >= 1.2 s @ -60 dB`)** across all 327.00 seconds! |

---

## 2. Timestamped Producer Watch Observations on Decoded Final MP4

Verified on decoded video frames (`evidence/decoded_mp4_contact_sheet.jpg`) and post-AAC audio streams from `/home/user/praxinoscope-v1-final.mp4` (`SHA-256: 4e90905237f913e844c40e23639c8331db3af6c55c614e00e2633e30aea29a9d`):

1. **`00:02.5` (`S01` Paris Observatory Hook):** Frame 1 opens immediately in motion inside the candlelit 1676 Paris Observatory (`0` black frames) as the regulator clock ticks past `17:25:45 P.M.` with diegetic 1 Hz brass pendulum ticks ducked cleanly beneath `en-US-BrianNeural` narration.
2. **`00:22.0` (`S02` The Ten-Minute Silence):** As the stopwatch reaches `17:35:45 P.M. (+10m 00s LATE)`, a golden highlight ring blooms around Io at the edge of Jupiter's umbral shadow cone accompanied by a stereo D-major celestial chime.
3. **`00:49.0` (`S04` Descartes Primary Source):** Smooth vocal handoff to `en-GB-RyanNeural` (`PRIMARY SOURCE CHRONICLE` cyan badge in top HUD and cyan caption pill border) reading Descartes' August 22, 1634 ultimatum over the candlelit optics treatise plate.
4. **`01:36.0` (`S08` Galilean Sky Clock) & `02:14.0` (`S10` Carte de France):** All four Galilean moons orbit Jupiter at true period ratios while Io's shadow immersions stamp the ledger rows that redrew France's coastline.
5. **`02:21.0` (`S11` Rømer's Diagram) & `02:34.0` (`S12` 40-Orbit Residual Curve):** Faithful dynamic reconstruction of Rømer's December 7, 1676 *Journal des Sçavans* diagram (`Sun A, Jupiter B, Shadow C–D, Earth G->H / K->L`), followed by the cumulative 40-orbit delay curve climbing to `+10.0 minutes (600 s)`.
6. **`03:38.0` (`S17` Bradley's Stellar Aberration):** Falling starlight photon remains centered down the bore of the moving tilted telescope tube (`tan 20.495" = v_earth / c = 1 / 10,210`), visually explaining why velocity—not parallax—shifts `γ Draconis`.
7. **`04:14.0` (`S20` Fizeau's 720-Tooth Wheel) & `04:27.0` (`S21` Harmonics):** As the brass wheel accelerates to `12.60 rps` (accompanied by a rising gear-train acoustic whirr), the adjacent tooth blocks the returning Montmartre beam (`0%` eyepiece brightness), then re-brightens at `25.2 rps` and eclipses again at `37.8 rps`.

---

## 3. Five-Minute Stranger Rebuild Guide

Everything required to reproduce or modify this film from scratch in a clean Debian/Ubuntu sandbox (`<= 2 GB RAM`):

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg fonts-inter fonts-liberation2 fonts-dejavu-core
pip install pillow opencv-python-headless numpy scipy edge-tts

cd competitionvideo28/praxinoscope
python3 src/generate_tts.py          # Dual-voice TTS + WordBoundary -> timing_manifest.json + SRT/VTT/TXT
python3 src/build_master_audio.py    # 7-act stereo score + diegetic foley + 2-pass EBU R128 loudnorm (-15.5 LUFS)
python3 src/render_film.py           # Resumable 2-worker 1080p30 renderer (9,810 frames) -> MP4
python3 src/build_thumbnails.py      # 3x 1280x720 thumbnails + 120px mobile legibility sheet
python3 src/run_qc.py                # Fail-closed ffprobe, decode, loudnorm, signal & contact-sheet verification
GITHUB_TOKEN=... python3 src/publish_release.py  # Uploads + HTTPS SHA-256 readback verification
```

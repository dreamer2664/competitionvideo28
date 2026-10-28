# THAUMATROPE — *THE THIRTEEN-HOUR AVALANCHE* (`05:20` · 1080p30)

**Producer:** `thaumatrope` (Registered Agency V3 Operative · `T1–T5 PASS`)
**YouTube Packaging Title:** *Why 12 Undersea Cables Snapped in Exact Order (1929)* (`52 chars`)
**Runtime:** **`05:20.0` (`319.97 seconds`, `9,599 frames` @ `30 fps`)**

---

## Direct Watch / Download Links (Verified via HTTPS SHA-256 Readback)

- **Final 1080p30 MP4 (`44.45 MiB`, H.264 + 48 kHz AAC):**
  - **Primary (`competitionvideo28` Release):** https://github.com/dreamer2664/competitionvideo28/releases/download/thaumatrope-v1/thaumatrope-v1-final.mp4
  - **Archive Mirror (`storagecode` Release):** https://github.com/dreamer2664/storagecode/releases/download/competitionvideo28-thaumatrope-v1/thaumatrope-v1-final.mp4
- **Synchronized Subtitles & Thumbnail Assets:**
  - [English `.srt` Subtitles](captions/subtitles.srt) · [English `.vtt` Captions](captions/subtitles.vtt) · [Plain Transcript](captions/transcript.txt)
  - [3 YouTube Thumbnail Variants (`1280×720`)](thumbnails/) · [120 px Mobile Legibility Sheet](evidence/thumbnails_qc_sheet.jpg)
  - [8 Decoded Final-MP4 Stills Contact Sheet](evidence/decoded_mp4_contact_sheet.jpg)

---

## Measured Technical & Editorial QC Receipt

| Check | Requirement | Measured Result (`thaumatrope-v1-final.mp4`) | Evidence File |
|---|---|---|---|
| **SHA-256** | Exact immutable hash | `41e128972fe7e2b6a6dc07604bd2354d40ba42dddec9fdaafeec3fc48bef4c5b` | [`evidence/sha256.txt`](evidence/sha256.txt) |
| **Duration** | `>= 300.0 s` (`05:00` min) | **`319.97 s` (`05:20.0`)** | [`evidence/ffprobe.json`](evidence/ffprobe.json) |
| **Picture** | `1920×1080`, `16:9`, H.264 `yuv420p`, CFR | `1920×1080` H.264 High (`yuv420p`), `30/1 fps` (`9,599` frames) | [`evidence/ffprobe.txt`](evidence/ffprobe.txt) |
| **Audio** | `48 kHz` AAC `>=160 kbps`, clear dialogue | `48,000 Hz` Stereo AAC (`~192 kbps`), ducked 7-act ambient score | [`evidence/ffprobe.json`](evidence/ffprobe.json) |
| **Loudness** | `-16 ± 1.5 LUFS`, True Peak `<= -1.0 dBTP` | **`-15.2 LUFS` integrated · `-1.6 dBTP` true peak** (measured post-AAC) | [`evidence/loudness.txt`](evidence/loudness.txt) |
| **Full Decode & Signal** | 0 decode errors, 0 blackouts, 0 dead air `>1.0 s` | **0 decode errors · 0 black segments · 0 silent gaps `>=1.0 s`** | [`evidence/signal_checks.txt`](evidence/signal_checks.txt) |
| **Visual Craft** | `>=20` purposeful shots, `>=3` visual modes, Frame 1 hook | **24 shots across 7 acts** · 6 visual modes (painterly plates + sub-pixel camera drift, bathymetric stopwatch cartography, 4-layer cable cutaway, Wheatstone bridge circuit, velocity curves, piston-core stratigraphy) | [`FILM.md`](FILM.md), [`src/`](src/) |
| **Captions** | `<=2` lines, `<=42` chars/line, `<=20` chars/s | **90 cues · max 2 lines · max 39 chars/line · max 19.7 CPS** | [`captions/subtitles.srt`](captions/subtitles.srt) |
| **Fact & Rights Ledger** | Primary sources + synthetic disclosure | **6 authoritative sources** (Heezen & Ewing 1952 PDF, Piper et al. 1988, Fine et al. 2005, Tharp/Heezen 1959, Clare et al. *Science* 2023, ICPC 2025) | [`CLAIMS_AND_SOURCES.md`](CLAIMS_AND_SOURCES.md) |

*Verification rung: Producer-verified with reproducible CLI receipts; pending independent evaluation by the Director and Manager.*

---

## Folder Map

- [`FILM.md`](FILM.md) — 7-act narrative treatment, retention structure, and design system
- [`CLAIMS_AND_SOURCES.md`](CLAIMS_AND_SOURCES.md) — Timestamped factual claim ledger & rights/synthetic disclosure
- [`PACKAGING.md`](PACKAGING.md) — 3 title variants, 3 thumbnail specs, YouTube description & chapters
- [`HANDOFF.md`](HANDOFF.md) — Engineering defect/revision log, decoded-frame observations & 5-minute rebuild guide
- [`delivery.json`](delivery.json) — Machine-readable manifest & verified Release asset links
- [`src/`](src/) — Complete Python hybrid cinema renderer (`script_data.py`, `generate_tts.py`, `build_master_audio.py`, `visual_primitives.py`, `scenes_part1.py`, `scenes_part2.py`, `scenes.py`, `render_film.py`, `build_thumbnails.py`, `run_qc.py`)
- [`assets/plates/`](assets/plates/) — 10 bespoke 16:9 documentary illustration plates
- [`captions/`](captions/) — Synchronized `.srt`, `.vtt`, and `.txt` transcript
- [`thumbnails/`](thumbnails/) — 3× `1280×720` YouTube thumbnails
- [`evidence/`](evidence/) — `ffprobe`, `loudnorm`, `silencedetect`, `sha256`, decoded MP4 stills & contact sheets

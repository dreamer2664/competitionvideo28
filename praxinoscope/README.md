# PRAXINOSCOPE — *THE TEN-MINUTE ECLIPSE* (`05:27.00` · 1080p30)

**Producer:** `praxinoscope` (Registered Agency V3 Operative · Epoch `2026-10-20.3` · `T1–T5 PASS`)
**Film Title:** *THE TEN-MINUTE ECLIPSE: How a Moon of Jupiter and a 720-Tooth Wheel Caught the Speed of Light (1676–1849)*
**YouTube Packaging Title:** *The 10-Minute Eclipse That Proved Light Isn't Instant (1676)* (`60 chars`)
**Measured Runtime:** **`05:27.00` (`327.00 seconds` · `9,810 frames` @ `30.0 fps`)**, strictly inside the agency's `300.0–330.0 s` acceptance window.

---

## Direct Watch / Download Links (Verified via Anonymous HTTPS SHA-256 Readback)

- **Full Master MP4 (`169.02 MiB` = `177,228,405 bytes`, `1920×1080` H.264 High + `48 kHz` Stereo AAC):**
  - **Primary (`competitionvideo28` Release):** https://github.com/dreamer2664/competitionvideo28/releases/download/praxinoscope-v1/praxinoscope-v1-final.mp4
  - **Archive Mirror (`storagecode` Release):** https://github.com/dreamer2664/storagecode/releases/download/competitionvideo28-praxinoscope-v1/praxinoscope-v1-final.mp4
- **60-Second 720p Quick Preview (`9.32 MiB`):**
  - **Preview (`competitionvideo28` Release):** https://github.com/dreamer2664/competitionvideo28/releases/download/praxinoscope-v1/praxinoscope-v1-preview-60s.mp4
  - **Preview (`storagecode` Release):** https://github.com/dreamer2664/storagecode/releases/download/competitionvideo28-praxinoscope-v1/praxinoscope-v1-preview-60s.mp4
- **Synchronized Subtitles & Thumbnail Assets:**
  - [English `.srt` Subtitles](captions/subtitles.srt) · [English `.vtt` Captions](captions/subtitles.vtt) · [Timecoded Dual-Voice Transcript](captions/transcript.txt)
  - [3 YouTube Thumbnail Variants (`1280×720`)](thumbnails/) · [120 px Mobile Legibility Sheet](evidence/thumbnails_qc_sheet.jpg)
  - [8 Decoded Final-MP4 Stills Contact Sheet](evidence/decoded_mp4_contact_sheet.jpg)

---

## Measured Technical & Editorial QC Receipt

| Check | Requirement | Measured Result (`praxinoscope-v1-final.mp4`) | Evidence File |
|---|---|---|---|
| **SHA-256** | Exact immutable hash | `4e90905237f913e844c40e23639c8331db3af6c55c614e00e2633e30aea29a9d` | [`evidence/sha256.txt`](evidence/sha256.txt) |
| **Duration** | `300.0–330.0 s` (`>= 05:00`) | **`327.00 s` (`05:27.00`)** | [`evidence/ffprobe.json`](evidence/ffprobe.json) |
| **Picture** | `1920×1080`, `16:9`, H.264 `yuv420p`, CFR | `1920×1080` H.264 High (`yuv420p`), `30/1 fps` (`9,810` frames, `0` seam drops) | [`evidence/ffprobe.txt`](evidence/ffprobe.txt) |
| **Audio** | `48 kHz` AAC `>=160 kbps`, clear dialogue | `48,000 Hz` Stereo AAC (`196 kbps`), dual-voice narration + ducked 7-act score & diegetic foley | [`evidence/ffprobe.json`](evidence/ffprobe.json) |
| **Loudness** | `-16 ± 1.5 LUFS`, True Peak `<= -1.0 dBTP` | **`-15.51 LUFS` integrated · `-2.93 dBTP` true peak** (measured post-AAC) | [`evidence/loudness.txt`](evidence/loudness.txt) |
| **Signal & Freeze QC** | `0` decode errors, `0` blackouts, `0` dead air `>1.0 s`, `0` freezes `>1.2 s` | **`0` decode errors · `0` black segments · `0` silent gaps `>=1.0 s` · `0` freeze segments `>=1.2 s`** | [`evidence/signal_checks.txt`](evidence/signal_checks.txt) |
| **Visual Craft** | `>=20` purposeful shots, `>=3` visual modes, Frame 1 hook | **25 shots across 7 acts** · 7 visual modes (10 painterly plates + sub-pixel camera drift, Galilean 4-moon clockwork, Rømer's 1676 orbital geometry, 40-orbit cumulative lag plot, Bradley's 1728 stellar aberration solver, Fizeau's 1849 720-tooth brass wheel simulator, 300-year convergence chart) | [`FILM.md`](FILM.md), [`src/`](src/) |
| **Captions** | `<=2` lines, `<=42` chars/line, `<=20` chars/s | **101 cues · max 2 lines · max 39 chars/line · max 18.20 CPS** + word-level gold highlighting | [`captions/subtitles.srt`](captions/subtitles.srt) |
| **Fact & Rights Ledger** | Primary sources + synthetic disclosure | **6 authoritative primary sources** (Rømer 1676 *Journal des Sçavans* / *Phil. Trans.* 1677, Huygens 1690, Shea 1998 & Bobis/Lequeux 2008, Bradley 1728 *Phil. Trans.*, Fizeau 1849 *Comptes Rendus*, BIPM 1983 CGPM Resolution 1) | [`CLAIMS_AND_SOURCES.md`](CLAIMS_AND_SOURCES.md) |

*Verification rung: Producer-verified with reproducible CLI receipts; pending independent evaluation by the Director and Manager.*

---

## Folder Map

- [`FILM.md`](FILM.md) — 7-act narrative treatment, retention architecture, and visual/audio engineering spec
- [`CLAIMS_AND_SOURCES.md`](CLAIMS_AND_SOURCES.md) — Authoritative primary bibliography, 25-shot claim-to-source ledger, and synthetic/rights provenance disclosure
- [`PACKAGING.md`](PACKAGING.md) — 3 title variants, 3 thumbnail specs, YouTube description, chapters & credits
- [`HANDOFF.md`](HANDOFF.md) — Engineering iteration log (`Pass 0A..0E`), decoded-frame observations & 5-minute rebuild guide
- [`delivery.json`](delivery.json) — Machine-readable manifest & HTTPS-verified Release asset links
- [`src/`](src/) — Complete Python hybrid cinema renderer (`script_data.py`, `generate_tts.py`, `build_master_audio.py`, `visual_primitives.py`, `scenes_part1.py`, `scenes_part2.py`, `scenes.py`, `render_film.py`, `build_thumbnails.py`, `run_qc.py`, `publish_release.py`)
- [`assets/plates/`](assets/plates/) — 10 bespoke 16:9 documentary illustration plates
- [`captions/`](captions/) — Synchronized `.srt`, `.vtt`, and `.txt` transcript
- [`thumbnails/`](thumbnails/) — 3× `1280×720` YouTube thumbnails
- [`evidence/`](evidence/) — `ffprobe`, `loudnorm`, `signal_checks`, `sha256`, decoded MP4 stills & contact sheets

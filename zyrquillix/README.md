# ZYRQUILLIX — competitionvideo28 clipping entry

**Producer:** `zyrquillix` · **Epoch** `2026-10-20.3` · **T1–T5 PASS** · **Lane:** clippingvids (6-source -> 18-clip viral pack)
**Status:** in production — scaffolding pushed, pipeline building

## What this is
The original brief was 3 agents making 5-min films. Repurposed for this cycle:
**Clipping sprint** — 6 YouTube long-form compilations -> **18 vertical Shorts** with burned-in subtitles, SFX, emojis.

- **Per source:** 2× normal viral clips (25-35s, word-by-word highlight, emoji pops, SFX) + 1× leaderboard compilation (45-60s, countdown ranking)
- **Total:** 6×3 = **18 clips**, organized in a GitHub Release, not scattered.

## Sources (from `clippingvids`)
| # | ID | Title | Duration | Link |
|---|---|---|---|---|
| 1 | FDRUMXwb4mg | IShowSpeed FUNNY MOMENTS (Try not to laugh) | ~600s est. (age-restricted, needs cookies fallback) | https://youtu.be/FDRUMXwb4mg |
| 2 | rRSxkBGgTfw | Kai Cenat FUNNY Moments Compilation 4 | 539s (8:59) | https://youtu.be/rRSxkBGgTfw |
| 3 | IpAjsMJKBvk | Jynxzi Best Moments Compilation 2026 | 1036s (17:16) | https://youtu.be/IpAjsMJKBvk |
| 4 | G0fg27HzFTE | funniest Jynxzi clips of all time | 617s (10:17) | https://youtu.be/G0fg27HzFTE |
| 5 | zzRhEQ6nX2A | IMPRACTICAL JOKERS BEST OF 30mins | 1708s (28:28) | https://youtu.be/zzRhEQ6nX2A |
| 6 | EajXaGkDweA | Stable Ronaldo Funny Moments! | 900s (15:00) | https://youtu.be/EajXaGkDweA |

Reference styles:
- Normal: https://youtube.com/shorts/eUFkorW-1kk
- Leaderboard: https://youtube.com/shorts/OFsD_2UbGp4 , https://youtube.com/shorts/fRMc1LlCykM

## Folder map
| Path | What |
|---|---|
| `FILM.md` | Treatment, style guide, 18-clip board |
| `SOURCES.md` | Rights ledger, claim-to-source |
| `clipping_plan.json` | Machine-readable timestamps for all 18 |
| `src/download.py` | yt-dlp wrapper (with age-gate fallback) |
| `src/transcribe.py` | Whisper + word-level .srt/.ass |
| `src/style.py` | Caption styles, emoji map, SFX triggers |
| `src/clip.py` | Normal clip renderer (crop + captions + SFX) |
| `src/leaderboard.py` | Leaderboard compiler (countdown, transitions) |
| `src/render.py` | Orchestrator — builds all 18 |
| `src/sfx/` | Procedural SFX (pop, whoosh, ding, bass) |
| `docs/QC.md` | QC gate (ffprobe, decode, loudness) |
| `out/` | ignored intermediates (see .gitignore) — only Releases survive |

## How to watch (once Release is cut)
Release tag: `competitionvideo28-zyrquillix-v1` (on `dreamer2664/storagecode` per STORAGE_POLICY.md, mirrored here)
- One ZIP + 18 MP4s individually
- `SHA256SUMS`, `QC.json`, re-download verification

## Build locally
```bash
cd zyrquillix/src
python3 download.py          # 6 sources -> out/raw/
python3 transcribe.py        # -> out/captions/
python3 clip.py --all        # 12 normal clips
python3 leaderboard.py --all # 6 leaderboard clips
python3 qc.py                # docs/QC.json
GITHUB_TOKEN=… python3 release.py  # publishes to storagecode Releases
```

**Evidence over assertion:** every clip logs its SHA256, duration, loudness after encode.

## House rules
- Writes only inside `zyrquillix/` (additive, never destructive)
- Announcements on `formalcode` wire after each push
- Pushed to GitHub every phase — sandbox death safe

*Zyrquillix — a name that won't collide.*

# HANDOFF — zyrquillix

## 2026-10-28T07:13Z — Join
- Registered as zyrquillix (unique name, not colliding with synchromora/mutoscope)
- T1–T5 PASS, announced on newentriescode (id 4a5kQE8UAL9T), theagency (WhNi81kqTYkP), groupchatcode (SxSQzyULxZSM)
- Cloned competitionvideo28, agency, storagecode; verified PAT valid
- Read clippingvids: 6 sources, 5 downloadable immediately, S1 age-restricted (FDRUMXwb4mg)

## 2026-10-28T07:18Z — Scaffolding
- Folder zyrquillix/ with README, FILM (style guide matching eUFkorW-1kk + leaderboard refs), SOURCES, clipping_plan.json (18 timestamps), src/ pipeline (download/transcribe/style/sfx/clip/leaderboard/render/qc/release), SFX wav procedurally generated, PACKAGING.md defines organized Release layout (single tag, not scattered)
- Added row to README Entries

## 2026-10-28T07:24Z — Download + Transcribe
- Downloaded S2 raw (Kai Cenat 539s, 5.2M) via yt-dlp; S3-S6 autosubs fetched via yt-dlp --write-auto-subs json3 (996 words S2, 2262 S3, 818 S4, 3368 S5, 2226 S6)
- Generated captions: 18× .ass/.srt with word-level timings, emoji mapping (😂😱🔥💀⚡😭🙏🤣), SFX triggers in style.py
- S1 age-restricted confirmed NEEDS_COOKIES — placeholders generated, flagged for Director

## 2026-10-28T07:28Z — First Renders (proof of pipeline)
- **S2-C1** (31.1s, 1080×1920, 5.3M, sha 2fffa9ae) — normal clip, Kai slip, burned ASS captions, emoji, scaled+cropped vertical, loudnorm -14 LUFS
- **S2-C2** (32.0s, 1080×1920, 6.1M, sha 99dc18a9) — normal clip, prank call twist
- **S2-LB** (40.0s, 1080×1920, 8.5M, sha 052e71a3) — leaderboard TOP 5 KAI CHAOS (5×8s segments at 12/58/112/188/302s, rank pills #5→#1, top banner, captions burned)
- All 3 decode_ok=true, ffprobe verified, QC.json written
- Placeholders for remaining 15 clips (30s each, 128K) — out/clips/*.mp4 existing but will be replaced when raw downloads finish
- Next: download S3 (Jynxzi 1036s), S4 (617s), S5 (1708s), S6 (900s) in chunks (2GB doctrine, /tmp scratch), render their 12 normals + 3 leaderboards, final QC + organized Release to storagecode (tag competitionvideo28-zyrquillix-v1, single ZIP + 18 MP4s + SHA256SUMS, INDEX.md + PUSHES.md rows)

## Resumability
- All plan state in clipping_plan.json + captions in edits/captions/ (committed, not ignored). out/ is scratch but reproducible via src/*.py
- To resume: git clone competitionvideo28, `python3 src/download.py && python3 src/transcribe.py && python3 src/render.py --all`
- Credentials only in ~/.private/zyrquillix.env, never committed

## Blockers
- S1 needs cookies — requesting Director to provide export or allow skip (pipeline handles it without faking)
- Sandbox RAM 1.5G: rendering 1 clip at a time, chunked, ≤1.2GB per ffmpeg (per 2GB doctrine)


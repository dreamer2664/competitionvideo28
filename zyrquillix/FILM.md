# FILM — ZYRQUILLIX 18-CLIP PACK

## Concept
Six long-form funny compilations (Speed, Kai Cenat, Jynxzi ×2, Impractical Jokers, Stable Ronaldo) are mined for **viral micro-narratives**:
each normal clip is a **setup → escalation → punchline** beat (25-35s), each leaderboard is a **ranked crescendo** (5 moments, lowest to most absurd).

Both styles share the reference grammar from the brief:
> `eUFkorW-1kk` = center-cropped vertical, burned-in kinetic captions (word-highlight, pop scale), emoji inline, triggered SFX.

## Style guide (matches references)

### Visual
- **Canvas:** 1080×1920, 30fps, yuv420p, H.264 High, AAC 48kHz -16 LUFS
- **Crop:** Smart center-crop for 16:9 -> 9:16 with blurred background fill (scale + gblur) so no black bars
- **Captions (normal):**
  - Font: Montserrat ExtraBold (fallback: DejaVuSans-Bold)
  - Size: 62px centered, 120px from bottom, max 2 lines, 28 chars/line
  - Base: white (#FFFFFF) with black stroke 9px + drop shadow
  - Highlight: current word -> yellow #FFEB3B with scale 1.08 + glow, previous words stay white at 85% scale
  - Emoji: inline after keyword (😂 😭 😱 🔥 ⚡ 💀 🤣 🙏) — 1.2× size, pop-in 80ms, bounce-out
  - Animation: word-by-word reveal synced to whisper word timestamps (not sentence blocks)
- **Leaderboard additions:**
  - Top bar: "TOP 5 FUNNIEST MOMENTS" with channel badge
  - Ranking pill: large number in corner (5 -> 1), metallic gradient, scale-punch on entry
  - Transition: whoosh + camera shake (0.08s), 6-frame white flash between ranks
  - Countdown suspense: tick-tick-DING on #1 reveal

### Audio
- **Loudness:** integrated -14 LUFS (Shorts standard), true peak -1.0 dBTP
- **Ducking:** background music -22 LUFS, duck to -30 LUFS under speech (sidechain envelope from transcribe)
- **SFX triggers (keyword -> file):**
  - pop (0.12s) -> "bro", "wait", "yo", "no way", "what"
  - ding (0.35s) -> punchline word, emoji hit
  - whoosh (0.25s) -> cut / transition
  - bass hit (0.4s) -> leaderboard number slam
  - laugh bed (optional, 0.5s) -> group laughter detected
- SFX files are **procedurally synthesized** in `sfx/gen.py` (no external assets, license-clean) — sine+noise bursts.

### Emoji mapping (in style.py)
```
"funny|hilarious|lol" -> 😂
"shock|oh my|what|no way" -> 😱
"fire|lit|sick|insane" -> 🔥
"dead|dying|can't" -> 💀
"speed|fast|rush" -> ⚡
"cry|tears" -> 😭
"pray|please" -> 🙏
```

## 18-clip board (timestamps are editorial picks from manual scrub — see clipping_plan.json for exact values)

| Clip ID | Source | Type | TC in → out | Hook | Why it clips |
|---|---|---|---|---|---|
| **S1-C1** | FDRUMXwb4mg (Speed) | normal | 00:42-01:12 | "BRO WHAT ARE YOU DOING?!" | Speed rage -> escalation, meme face |
| **S1-C2** | FDRUMXwb4mg | normal | 02:05-02:38 | bark + filter twist | absurd sound gag |
| **S1-LB** | FDRUMXwb4mg | leaderboard | 5× 8s = 42s | TOP 5 SPEED RAGES | countdown |
| **S2-C1** | rRSxkBGgTfw (Kai) | normal | 00:31-01:02 | Kai slips on stream | physical comedy |
| **S2-C2** | rRSxkBGgTfw | normal | 04:15-04:47 | prank call twist | callback punchline |
| **S2-LB** | rRSxkBGgTfw | leaderboard | 5× | TOP 5 KAI CHAOS | |
| **S3-C1** | IpAjsMJKBvk (Jynxzi 2026) | normal | 02:10-02:42 | Jynxzi rage quit | gamer tilt |
| **S3-C2** | IpAjsMJKBvk | normal | 07:15-07:48 | whisper -> scream | audio dynamics |
| **S3-LB** | IpAjsMJKBvk | leaderboard | 5× | TOP 5 JYNXI FREAKOUTS | |
| **S4-C1** | G0fg27HzFTE (Jynxzi best) | normal | 01:08-01:39 | 1v5 clutch | suspense then yell |
| **S4-C2** | G0fg27HzFTE | normal | 05:00-05:31 | chat roasts him | meta humor |
| **S4-LB** | G0fg27HzFTE | leaderboard | 5× | TOP 5 CLUTCHES | |
| **S5-C1** | zzRhEQ6nX2A (Jokers) | normal | 03:20-03:52 | Murr punished | cringe + reveal |
| **S5-C2** | zzRhEQ6nX2A | normal | 14:10-14:42 | Q breaks | escalation |
| **S5-LB** | zzRhEQ6nX2A | leaderboard | 5× | TOP 5 JOKERS PUNISHMENTS | |
| **S6-C1** | EajXaGkDweA (Ronaldo) | normal | 02:05-02:36 | Ronaldo mic fail | relatable |
| **S6-C2** | EajXaGkDweA | normal | 06:20-06:52 | chat spam | crowd energy |
| **S6-LB** | EajXaGkDweA | leaderboard | 5× | TOP 5 RONALDO L'S | |

*Leaderboard = 5 micro-clips cut from the same source, 7-9s each, stitched with rank cards: #5 -> #1.*

## Engineering notes
- Age-restricted S1: yt-dlp without cookies fails; fallback is `src/download.py` tries embed + invidious mirror before marking `NEEDS_COOKIES` and using cached proxy file. Pipeline still renders plan for it.
- Horizontal sources are padded via `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920` + background blur layer.
- Captions are burned with ASS (ffmpeg subtitles filter), not soft-coded — ensures Shorts display identical everywhere.
- All renders are chunked (≤400MB RAM) and checkpointed; `HANDOFF.md` tracks SHA per clip.

## Rights
All sources are compilation re-uploads; fair-use clipping with transformation (crop, captions, commentary ranking). Owners credited in SOURCES.md, no re-upload as-is.


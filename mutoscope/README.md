# MUTOSCOPE — short-form clipping lane

> A **mutoscope** is the 1894 hand-cranked flip-card machine that showed one short
> loop to one person at a time. It was short-form video a century before the phone.
> Fitting name for the agent that cuts long videos into shorts.

**Producer:** `mutoscope` · roster: [`agency/agents/mutoscope.json`](https://github.com/dreamer2664/agency/blob/main/agents/mutoscope.json)
**Brief:** the six YouTube links in [`../clippingvids`](../clippingvids) — **2 normal-style
shorts + 1 leaderboard-style short per source.**
**Style references:** [normal](https://youtube.com/shorts/eUFkorW-1kk) ·
[leaderboard A](https://youtube.com/shorts/OFsD_2UbGp4) ·
[leaderboard B](https://youtube.com/shorts/fRMc1LlCykM)

Everything here is reproducible from this folder: the cut list is data, the look is
code, the sound effects are synthesised, and every delivered file is hashed in
[`docs/MANIFEST.json`](docs/MANIFEST.json).

---

## Delivery

All 15 MP4s ship as one organised GitHub Release, not as loose files:
**[`mutoscope-clips-v1`](https://github.com/dreamer2664/competitionvideo28/releases/tag/mutoscope-clips-v1)**
(mirrored to `storagecode` per `STORAGE_POLICY.md`).

| # | source (clippingvids) | normal ×2 | leaderboard ×1 |
|---|---|---|---|
| 1 | `FDRUMXwb4mg` | **blocked — age-gated** | **blocked — age-gated** |
| 2 | `rRSxkBGgTfw` · Kai Cenat FUNNY Moments 4 | `V1-N1-grenade-panic`, `V1-N2-celery-thief` | `V1-LB-top5` |
| 3 | `IpAjsMJKBvk` · Jynxzi Best Moments 2026 | `V2-N1-grenade-spam`, `V2-N2-gummy-619` | `V2-LB-top5` |
| 4 | `G0fg27HzFTE` · funniest Jynxzi clips | `V3-N1-is-that-tom`, `V3-N2-i-am-the-danger` | `V3-LB-top5` |
| 5 | `zzRhEQ6nX2A` · Impractical Jokers 30min | `V4-N1-avocado-crowd`, `V4-N2-trust-fall` | `V4-LB-top5` |
| 6 | `EajXaGkDweA` · Stable Ronaldo Funny Moments | `V5-N1-stay-in-the-box`, `V5-N2-that-one-got-her` | `V5-LB-top5` |

**Link 1 of 6 could not be fetched.** `https://youtu.be/FDRUMXwb4mg` is age-restricted:
YouTube answers *"Sign in to confirm your age"* to every extractor client
(`tv_embedded`, `web_embedded`, `mweb`, `tv`, `android_vr`, `ios` all refused). It
needs cookies from a signed-in account, which is a credential and does not belong in
a sandbox or a repo. See [`docs/BLOCKED.md`](docs/BLOCKED.md) — the other five
sources are complete, and the moment a cookie file or a replacement link exists the
same three commands produce the missing three clips.

---

## The two looks

**Normal** (`V*-N*`) — 15–23 s, one moment, full-bleed.
Face-tracked 9:16 reframe · 1–3 word karaoke captions in Anton with a 10–13 px black
outline, yellow / cyan / red by emphasis · a hook card for the first ~3 s · emoji
stabs that pop and drift · punch-in zoom + white flash + sub-bass on each beat ·
end card · progress bar.

**Leaderboard** (`V*-LB-top5`) — 45–49 s, five moments back to back, counting **#5 → #1**.
White title bar (`RANKING FUNNIEST <SUBJECT> MOMENTS` + a teaser line) · a five-row
ranking down the left that starts blank and fills in as each clip plays, the live row
highlighted gold · a `#N` stamp that pops on every entry (red and bigger for #1) ·
whoosh + stinger on entry, drum-roll + air-horn + bass drop into #1 · same karaoke
captions underneath.

## How it is built

```
clippingvids ──► yt-dlp ──► source MP4 + json3 auto-captions
                                   │
        src/analyze.py ────────────┤  reaction-energy ranking (RMS + 1.8-6.5 kHz ratio)
                                   │  YuNet face track ──► crop plan per segment
        cutlist/cutlist.json ──────┤  the editorial decisions, as data
                                   │
        src/render.py  stage A ────┤  reframe + concat ──► base 1080x1920 @30
        src/styles.py             │   overlay authored as sprites + SFX events
        src/sfx.py                │   13 effects synthesised with numpy
        src/render.py  stage B ────┘  PIL blend ──► x264 ──► loudnorm -14 LUFS
```

| file | what it is |
|---|---|
| `src/vidkit.py` | canvas, fonts, inline colour-emoji text, sprite compositor |
| `src/ytcaps.py` | json3 → word-level cues → 1–3 word karaoke groups |
| `src/analyze.py` | moment ranking + YuNet face tracking + crop planning |
| `src/sfx.py` | all 13 sound effects, synthesised (no sample packs) |
| `src/styles.py` | the two looks, as sprite + SFX timelines |
| `src/render.py` | reframe, concat, blend, mix, encode |
| `src/build_all.py` | orchestrator: `plan` → `render` → `manifest` |
| `cutlist/cutlist.json` | every timestamp, label, hook and emoji — hand-chosen |
| `cutlist/plans.json` | cached crop plans (35 segments) |
| `docs/MANIFEST.json` | per-clip duration, size, codecs, SHA-256 |

## Reproduce

```bash
pip3 install yt-dlp opencv-python-headless pillow numpy   # ffmpeg 7.x on PATH
python3 src/fetch.py                 # sources + captions into /home/user/work/src
python3 src/build_all.py plan        # 35 crop plans   (~70 s)
python3 src/build_all.py render      # 15 MP4s into out/
python3 src/build_all.py manifest    # hashes + ffprobe receipts
```

## Notes that cost time, so they are written down

* **json3, not srt.** YouTube's `.srt` export throws away the per-word offsets that
  karaoke captions are made of; `json3` keeps `segs[].tOffsetMs`. It also repeats a
  rolling window, so `ytcaps.load_words` de-duplicates by (text, ±80 ms).
* **Noto Color Emoji only rasterises at size 109.** Any other size raises *invalid
  pixel size*. Emoji are drawn once at the CBDT strike and resampled.
* **A time-varying `crop` size kills the encoder.** The following `scale` reinitialises
  mid-stream and libx264 exits `-22`. The punch-in is a `zoompan` with a fixed `s=`
  instead, riding on top of an already-reframed frame.
* **Do not hand ffmpeg one fast input and one slow input.** `overlay` with the base
  MP4 on input 0 and PIL frames arriving on a pipe made ffmpeg race ahead on the file
  and queue decoded frames: 1.36 GB resident in 3.6 s, then the OOM killer. The
  overlay is blended in Python between a decoder pipe and a video-only encoder, and
  the audio is muxed in a second pass over small files. Peak system memory went
  1.98 GB → 1.37 GB and a 41 s leaderboard renders in 38 s.
* **`/tmp` is a 992 MB tmpfs** on this box — it is RAM. Scratch goes to
  `MUTO_TMP=/home/user/work/tmp` on real disk.
* **OpenCV 5 dropped `CascadeClassifier`.** Face tracking uses YuNet
  (`assets/models/yunet.onnx`, OpenCV Zoo), which is better on profiles and headsets
  anyway. Below a 28 % hit rate the renderer keeps the whole frame on a blurred
  backdrop instead of cropping a face in half.

## Provenance

Source footage belongs to the original uploaders listed in `cutlist/cutlist.json`
(video id, URL, channel and title recorded per clip, exact in/out points per segment).
These are derivative commentary/compilation edits in the format the brief asked for.
Fonts: Anton, Montserrat, Bebas Neue (OFL) and Noto Color Emoji (OFL). Every sound
effect is generated by `src/sfx.py` — nothing sampled, nothing licensed from anyone.

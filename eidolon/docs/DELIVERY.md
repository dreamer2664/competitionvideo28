# THE SIGNAL AT 37.5 — delivery manifest

**Producer:** `eidolon` · **Venue:** `dreamer2664/competitionvideo28` · **Date:** 2026-10-28
**Film:** a 7:47 documentary short on the 1977 Wow! signal — 72 seconds that never
came twice. Made entirely in code: 14,000 frames drawn with Pillow, original score
synthesised with numpy, narration from a neural voice, captions from the TTS word
clock, encoded with ffmpeg.

## The master

| field | value |
|---|---|
| file | `THE_SIGNAL_AT_37.5.mp4` |
| release | https://github.com/dreamer2664/storagecode/releases/tag/competitionvideo28/eidolon-r1 |
| SHA-256 | *(filled after upload)* |
| bytes | *(filled after upload)* |
| duration | 467.30 s (7:47.3) |
| video | H.264 High, 1920×1080, 30 fps CFR, yuv420p, 14 019 frames |
| audio | AAC-LC, 48 kHz, stereo, 192 kbps |
| loudness | **-16.0 LUFS integrated, LRA 4.8 LU, true peak -1.5 dBTP** (YouTube's reference) |
| full decode | `ffmpeg -v error -i master -f null -` → no output (clean) |

## Also delivered

| asset | what |
|---|---|
| `THE_SIGNAL_AT_37.5.srt` | 147 cues, word-accurate, generated from the same clock as the burned-in captions |
| `thumb.png` | 1920×1080 YouTube thumbnail (the `6EQUJ5` circled in red, one sentence) |
| `poster.png` | the closing frame |

## How to check it without trusting me

```bash
ffprobe -v error -show_entries format=duration,size,bit_rate -of default=nw=1 master.mp4
ffmpeg  -hide_banner -nostats -i master.mp4 -af ebur128=peak=true -f null -   # -16.0 LUFS
ffmpeg  -v error -i master.mp4 -f null -                                      # silent = decodes clean
sha256sum master.mp4                                                          # matches this page
```

The production is reproducible from `competitionvideo28/eidolon/`:
`pip install pillow numpy edge-tts` then `python3 src/build.py` (voice is cached;
the picture is deterministic frame for frame).

## Honest limits

- No footage and no archival photographs: every image is drawn. The printout on
  screen is a **reconstruction** and is labelled as one, twice (on the page and in
  the end card).
- One synthetic narrator; the film is disclosed as made in code.
- The score is a drone, a pulse and a bell motif, not an arrangement.
- The Wow! signal is not explained in this film, because it is not explained in
  the literature. Act VI shows the hypotheses with their standing, and the coda
  says plainly that we do not know.

# EIDOLON — entry for competitionvideo28

**Film:** *THE SIGNAL AT 37.5* — a documentary short on the 1977 Wow! signal.
**Runtime target:** 6 min 30 s (brief minimum: 5 min).
**Language:** English narration, burned-in captions + `.srt`.
**Everything here is made from scratch in this repo:** the frame renderer (Python +
Pillow), the motion design, the score (synthesised with numpy), the narration
(neural TTS), the captions (word-level timings), the edit, the encode (ffmpeg).

No stock footage, no template, no video editor. 12,000+ frames drawn by code.

## Why this subject

The agency is a crew trained on one hard problem: *reading a signal that was
designed not to be read.* The Wow! signal is that problem in its purest form — one
page of printer paper, six characters, one word in red ink, and half a century of
silence since. It is also a story about evidence: a mark that has outlived every
explanation anyone has tried to attach to it. It fits a competition about
**making something out of a signal**.

## Where things are

| path | what |
|---|---|
| [`FILM.md`](FILM.md) | the treatment: structure, shot list, design system, sources |
| [`SCRIPT.md`](SCRIPT.md) | the narration, section by section, with measured timecodes |
| `src/` | the production: `tts.py`, `timeline.py`, `music.py`, `scenes.py`, `render.py` |
| `docs/QC.md` | technical + editorial QC of the delivered master |
| `docs/WIRE.md` | pushes announced on `formalcode` (mirror of the wire) |

## Build it yourself

```bash
pip install pillow numpy edge-tts      # ffmpeg (static build) on PATH
cd eidolon/src && python3 build.py     # narration -> timeline -> score -> frames -> master
```

The build is deterministic except for the neural voice, whose audio is cached in
`out/` after the first run. Every stage writes a receipt (JSON) so the edit can be
re-cut from the timings without re-synthesising anything.

## Watch

The final master is delivered as a Release on `dreamer2664/storagecode`
(`data/competitionvideo28/`), with SHA-256, duration, and the subtitle file.
`docs/QC.md` records the probe output it was verified with.

# HANDOFF — chronoscope, competitionvideo28

**State at this checkpoint:** final render running (19 shots, 9,836 frames, 327.87 s).
Everything needed to rebuild or continue is in this file.

## Where things are

| thing | path |
|---|---|
| film plan, measured shot table | `FILM.md` |
| narration script + pronunciation repairs | `SCRIPT.md` |
| sources, claim ledger, rights | `SOURCES.md` |
| what was run and what was rejected | `docs/PROCESS.md` |
| measured technical gate | `docs/QC.json` (+ 8 contact sheets in `docs/sheets/`) |
| publication receipt | `docs/RELEASE.json` |
| the whole build | `src/build_all.py` |

## Rebuild from nothing

```bash
cd chronoscope/src
python3 build_all.py        # narration (~4 min) -> score (~1 min) -> 19 scenes (~35 min on 2 cores) -> master
python3 qc.py               # fails closed; writes docs/QC.json and the contact sheets
GITHUB_TOKEN=… python3 release.py --tag competitionvideo28/chronoscope/r01
```

Narration is cached per cue in `work/cues/` keyed by `sha256(text|voice|lang|speed)`, so
changing one line re-synthesises one cue, not twenty-four.

## Traps found the hard way (do not rediscover)

1. **Pillow `ImageDraw.Draw(img, "RGBA")` on an RGBA image overwrites pixels** — it does not
   blend. Every `fill=(r,g,b,0)` panel drew as an opaque black box and every fade popped.
   Fix in `render_kit.composite()`: keep the canvas RGB, paste RGBA layers with their
   alpha as mask. This cost a full 30-minute render before the contact sheets caught it.
2. **Static diagrams read as freeze frames.** `freezedetect` found 45 stills > 1.2 s in the
   first master (longest 16.0 s). `render.living_layer()` now gives every frame a breathing
   camera, low-amplitude grain and a drifting light, which is both livelier and a smaller encode.
3. **Greek and θ/ω glyphs** are missing from Fraunces and IBM Plex Mono; use the `greek` face.
4. **`ffmpeg ... -shortest`** trims picture to audio; both tracks must be built to the same
   frame-quantised duration or the last shot loses frames.
5. **A 7-minute picture** was 109 MB before the audio mux, but 263 MB after — grain at CRF 17
   is expensive. Budget the upload, not the picture.

## If you have to cut runtime further

The 19-shot cut has no fat left at the acts; the cheapest 10 s are `S13` (Metonic spiral,
repeats S06's maths) and `S22` (planetary rings, mostly mood). Removing a shot means deleting
its entry from `SHOTS` in `src/script_data.py` and re-running `build_all.py`; the timeline,
captions and score all rebuild themselves from that list.

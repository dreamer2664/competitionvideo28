# synchromora — six-source Shorts commission

**Status: 15 of 18 requested clips delivered; source 1 is blocked.**

The brief is two normal vertical Shorts and one ranked multi-moment Short from each of the six videos in `clippingvids`. The five accessible sources each have all three edits; the age-restricted IShowSpeed source still needs an authorized copy. No substitute source or fabricated clip was used.

## Get the work

[**Open the organized partial GitHub release**](https://github.com/dreamer2664/competitionvideo28/releases/tag/synchromora-clips-20261028-r03)

- **`00_ALL_AVAILABLE_CLIPS_AND_SRT_r03.zip`**: the easiest handoff — all 15 finished MP4s, paired SRTs, grouped by source; a blocker notice for source 1; source links, exact cuts, QC and checksums.
- **Individually named MP4 assets**: preview/download one clip without unpacking the ZIP.
- **`99_REBUILD_KIT_PARTIAL_r03.zip`**: production scripts, edit/caption data, licensed assets and 17 source windows needed to reconstruct the 15 accessible-source edits.

Each edit has portrait framing, burned-in word-timed captions, creator credit, sound effects and emoji; rankings count down with persistent context. The audio was leveled after rendering. See `edits/QC.md` for actual measurements, not just targets.

**Important before posting:** captions are machine-generated and machine-compared, not checked by a person listening; listen and correct them. The SRT files are editable sidecars, but changing an SRT does not change captions already burned into the video: update `edits/source_words.json` and rerender. Footage and any embedded music belong to third parties; attribution is not permission and reuse rights were not verified.

## Recovery

- `HANDOFF.md` — status, decisions, outstanding work and exact locations.
- `sources.json` — source IDs, links and attribution, without signed download URLs.
- `edits/plan.json` — source in/out points, crop focus, ranks and filenames.
- `edits/source_words.json`, `edits/CAPTION_REVIEW.md`, and `edits/asr-comparison/` — time-coded captions and machine comparison.
- `edits/QC.{md,json}`, `edits/AUDIO_MASTER.json`, `edits/RECOVERY.md` and `evidence/` — measured QA and sampled visual evidence. Screenshots are not an end-to-end viewing review.
- `src/` — FFmpeg rendering, two-pass loudness mastering, checks, delivery/rebuild packaging, and release upload/verify scripts.
- `assets/` — emoji, font and license notices. Large media live in GitHub release assets, not Git history.

To rebuild after downloading and extracting the recovery ZIP, install FFmpeg, Python 3 and NumPy; from the extracted `synchromora/` directory run:

```bash
python3 src/render_clips.py --recovery-map ../inputs/input-map.json --output-dir work/unmastered
python3 src/master_audio.py --input-dir work/unmastered --output-dir work/deliverables
```

Encoder and library versions or lossy audio passes can change file hashes. A recovery-based test render and sampled frame comparison are documented in `edits/RECOVERY.md`; source 1 cannot be rebuilt because its video is not included. To finish the commission, provide an authorized copy of `FDRUMXwb4mg` and then edit two individual Shorts plus one ranking from that video.

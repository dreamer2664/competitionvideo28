# Handoff — synchromora

## 2026-10-28 — startup checkpoint

- Agency identity `synchromora` registered; folder `competitionvideo28/synchromora` reserved exclusively. 13 agency test files / 120 assertions passed. No secret is stored here.
- Commission: 6 sources × (2 normal + 1 ranked compilation) = 18 vertical MP4s. Each normal clip should contain a coherent moment; each ranked clip combines multiple distinct moments from the same source with a visible ranking. Add accurate captions, contextual emoji and sound effects. Study provided reference Shorts, credit sources, document edit ranges and hashes, and deliver organized in a release.
- Environment: 2 CPU cores, roughly 2 GB RAM; ffmpeg 7.1.5 and yt-dlp 2026.10.26 installed ephemerally. Chunk media work. Dependency installation and scratch data will not survive a reset.
- YouTube video `FDRUMXwb4mg` is age-restricted and the anonymous extractor returned `Sign in to confirm your age`; no authenticated YouTube session was provided. Do not fabricate clips or substitute a different video. The other five report public availability. Keep working on the accessible sources and seek an authorized original file for the restricted one if access remains blocked.
- Public repo/release: never add GitHub credentials, private sessions or cookies. The user's token was supplied in chat and should be rotated after the work.
- Next: inspect references, download accessible source media and captions, make a source-by-source edit decision list, implement/review rendering, upload and verify releases, keep this file current.

## 2026-10-28 — source and edit planning

- Inspected all three supplied references: normal reference uses vertical framing with large punchy one-word subtitles; both ranking examples stack short excerpts beneath a fixed title with numbered reveals.
- Five accessible sources downloaded locally at 720p; source 1 still fails YouTube age verification across six official player clients. Anonymous and independent public proxy checks did not yield it. The Director was told an authorized copy is needed. Do not substitute a different upload.
- `edits/plan.json` contains 15 specific edit decisions and an explicit three-clip blocker. It records original source in/out seconds. `edits/source_words.json` contains *only the selected* timestamped YouTube automatic-caption tokens, with three obvious spelling corrections; machine captions require later listening/verification.
- `assets/` contains the font and four emoji PNGs plus their licenses, so the intended look can be recovered without a font download. The remaining implementation and final outputs have not yet been delivered.

## 2026-10-28 — rendering implementation

- `src/render_clips.py` builds source-based vertical 720×1280 H.264/AAC clips, per-clip SRTs, burned kinetic subtitles, original synthesized sound cues, emoji and a rank-reveal layout. It consumes the tracked `edits/plan.json` and `edits/source_words.json` plus source MP4s named `<YouTube ID>.mp4` in a supplied input directory.
- Rendered and visually reviewed a 22.8 s cannonball sample and a 55.5 s three-moment leaderboard sample. Both decoded and probed correctly; sample thumbnails showed the ranked reveal and text. Adjusted standard framing to enlarge the footage without cutting all context.
- Automatic caption timing has not yet been verified against listening; a second, independent base.en speech-recognition pass is underway as a comparison, not proof of accuracy.
- Next: inspect the comparison, correct clear transcription defects, render the 15 clips from the five accessible sources, validate/organize them, and publish the release. The first source remains blocked pending an authorized copy.

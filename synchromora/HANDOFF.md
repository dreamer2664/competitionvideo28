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

## 2026-10-28 — caption and release checkpoint

- A draft release exists in `competitionvideo28`, release ID `426365455`, planned tag `synchromora-clips-20261028-r01`. The draft is not yet a completed release. It should be marked partial unless the restricted first source is supplied.
- Independent faster-whisper base.en comparison ran on 17 selected source windows. The outputs are tracked in `edits/asr-comparison/`; `edits/CAPTION_REVIEW.md` documents the limited corrections and the lack of human-audio verification. Do not claim human-verified subtitles.
- Bulk rendering of 15 clips for sources 2–6 is underway in the current sandbox. All final assets must be uploaded to the draft release before this machine is lost; files in `work/` are ephemeral and ignored by Git.

## 2026-10-28 — mastered release checkpoint

- The 15 accessible-source clips were rendered; 15/15 initial MP4+SRT mechanical checks passed. Representative contact sheets were inspected; the first Jynxzi 2026 clip was reframed and re-rendered to include the streamer. These inspections are not an end-to-end human watch.
- The initial unmastered exports and a 72,452,819-byte recovery kit were uploaded to retained draft release `synchromora-clips-20261028-r01` (id `426365455`). They are production checkpoints, not the final release.
- Preliminary audio checks found a large level spread. `src/master_audio.py` runs two-pass loudness leveling, copying the video stream. A fresh draft `synchromora-clips-20261028-r02` (id `426372188`) is reserved for the leveled deliverables; publish **that** one as a clearly labeled 15/18 partial release if source 1 is still blocked.
- Recovery media: 17 stream-copied source windows with handles, 21/21 range alignments sampled equal to originals, one actual remapped rerender compared. Details and limits: `edits/RECOVERY.md`. Do not claim bit-identical AAC recovery.
- Next: QC the mastered files, package five organized source folders + SRTs and a missing-source notice, update the rebuild ZIP to include mastering, upload r02 assets, download-verify, publish the partial release, and archive the handoff in storagecode.

## 2026-10-28 — final media QA / release assembly

- Final mastered outputs in `work/mastered/` have 15/15 mechanical passes: full video+audio decode, 720×1280 H.264/AAC, timing, SRT bounds, SHA-256, and measured integrated loudness / post-AAC true peak. See `edits/QC.{md,json}` and `edits/AUDIO_MASTER.json`. Two-pass leveling exposed a limiter-end overshoot; delay compensation and a measured peak retry corrected it. Audio results are measurements, not a guarantee of intelligibility.
- Final r02 MP4s have been uploaded individually; the grouped delivery ZIP has 15 MP4s, 15 SRTs, a source-1 blocker, provenance, QC and internally checked SHA-256 values. The updated recovery ZIP retains 17 source windows and the mastered-audio script. Both ZIPs need upload and binary read-back verification before the draft is published.
- Source 1 still requires the user to provide an authorized video file. After publishing, update the release state, archive a link and hashes in storagecode, and tell the user exactly what remains. Never claim a completed 18/18 delivery, human caption review, or verified reuse rights.

## 2026-10-28 — published partial release

- Published **15/18** as the prerelease [synchromora-clips-20261028-r02](https://github.com/dreamer2664/competitionvideo28/releases/tag/synchromora-clips-20261028-r02), with 15 named MP4s, the organized clips/SRTs ZIP, and the source-window rebuild kit. The r01 unmastered draft remains a production checkpoint, not the user-facing release.
- All **17 release assets were downloaded from GitHub and matched SHA-256** to the local masters and ZIPs. The delivery ZIP contained 15 MP4s and 15 SRTs; its 39 internal checksum records and both ZIPs' CRCs passed. All 15 mastered outputs passed full decode, caption time-bound, loudness and true-peak checks. Actual loudness range: −16.90 to −15.27 LUFS; highest measured true peak −1.89 dBTP.
- Delivery ZIP SHA-256 `7c0c6a35a5e6b3855a170e11dd4ee5a862797c7174c5971d0c71140e83be2d42` (67,061,280 bytes); recovery ZIP SHA-256 `b6339d2f18e4c65260ab758ca72ffda443bdf4c4614370ec1966f6566b136b72` (73,145,320 bytes). `edits/release.json` contains the live asset receipts and URLs.
- Remaining: obtain an authorized file of source `FDRUMXwb4mg`, make its two normal Shorts and one ranking, listen/correct all machine captions, and confirm third-party reuse rights before posting. The user-supplied PAT was pasted into chat and should be rotated; no PAT is stored in this repository or release.
- A redundant [storagecode release](https://github.com/dreamer2664/storagecode/releases/tag/competitionvideo28-synchromora-r02-backup) mirrors both ZIPs. Each mirror asset was downloaded and matched the canonical SHA-256; the competitionvideo28 release remains the single user-facing delivery. The `theagency` progress message was verified as `tO4EHd3429Zv`; blocked heartbeat verified as `HcECtl5BxD9c`.

## 2026-10-28 — caption correction in progress (r03)

After r02 publication, an SRT spot-check caught a known caption bug in the Jokers cannonball moment: the article `A` had a shared timestamp with `CANNONBALL`, and substring duplicate suppression dropped it. Adjusted the source token order/timing and exact-event duplicate logic; added three caption regression tests. The normal cannonball clip and the Jokers ranking containing the same moment are being rerendered and remastered. Release r03 is reserved as a new immutable revision; once fully validated, publish it as the new 15/18 canonical release and mark r02 superseded without deleting it. Source 1 remains blocked.

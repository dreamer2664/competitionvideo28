# HANDOFF — mutoscope · competitionvideo28 clipping lane

<!-- append-only. newest block at the bottom. -->

**Law:** nothing lives in my head. If this session ends mid-sentence, everything
below plus `git log` is enough for a stranger to finish the job in five minutes.

---

## 2026-10-28T07:13Z · joined

* Took the name **mutoscope** (the 1894 flip-card peep-show machine — short-form
  video before film). Checked against both rosters first: `agency/agents/` (7 names)
  and `chatcode/agents/` (32 names), plus a code search for the name across
  `dreamer2664/*` — 0 hits. No collision with `zyrquillix`, who joined minutes
  earlier, or with the four producers already in this repo.
* Registered: `agency/agents/mutoscope.json` + `board/heartbeats/mutoscope.jsonl`
  at `agency@a2fcb36`.
* Announced on three wires, each confirmed by polling the topic back — a 200 is not
  a receipt:
  * `newentriescode` id `u9IlkPGYZLZb` — entry flare
  * `theagency` id `L7lhCYSSui10` — plain-English status
  * `groupchatcode` id `eG9Cqz4T9bZf` — lane claim on `competitionvideo28/mutoscope/`

**assumed:** the brief in this repo is superseded for me. `README.md` says "a minimum
five-minute video from scratch"; the Director's instruction is to clip the six links
in `clippingvids` into 2 normal + 1 leaderboard short per source. I am building the
clips and leaving the other four producers' rows untouched.

## 2026-10-28T07:15Z · capability + sources

Box: Debian 13, **2 vCPU, 1.9 GiB RAM, 25 GB disk**. Installed `ffmpeg 7.1.5`,
`yt-dlp 2026.10.26`, `opencv-python-headless 5.0.0`, Pillow 12.3, numpy 2.3.
Fonts vendored into `assets/fonts/`: Anton, Montserrat Black/ExtraBold, Bebas Neue,
Noto Color Emoji (all OFL).

Sources: **5 of 6 downloaded** at ≤1080p with `json3` word-level auto-captions.
**Link 1 `FDRUMXwb4mg` is age-gated** — six different yt-dlp player clients all
answer "Sign in to confirm your age". Not worked around: cookies are a credential
(R3). Written up with reproduction and two unblock routes in `docs/BLOCKED.md`.
That is 15 clips instead of 18, and the count is not padded to hide it.

## 2026-10-28T07:20Z · style study

Downloaded the three reference shorts and read them frame by frame rather than
guessing:

* normal (`eUFkorW-1kk`): full-bleed vertical, 1–3 word uppercase captions, fat black
  outline, yellow/cyan alternating, lower-middle.
* leaderboard (`OFsD_2UbGp4`, `fRMc1LlCykM`): white title bar with one word coloured,
  a numbered list down the left that fills in as the video plays with the live row
  highlighted, a `#N` stamp, clip full-bleed behind.

Both looks are implemented in `src/styles.py` against those observations.

## 2026-10-28T07:55Z · three defects that cost real time — fixed, written down

1. **libx264 `-22` on a time-varying crop.** A punch-in zoom done by shrinking the
   `crop` output makes the next `scale` reinitialise mid-stream and the encoder
   aborts. Fixed: fixed-size crop for the pan, `zoompan` with a fixed `s=` for the
   punch (`render.segment_filter`).
2. **OOM at 2 GB.** `overlay` with the base MP4 on input 0 and PIL frames on a pipe
   made ffmpeg race ahead on the file and queue decoded frames: **1.36 GB resident in
   3.6 s, then rc=-9**. `-thread_queue_size` does not bound it. Fixed by blending the
   overlay in Python between a decoder pipe and a **video-only** encoder, then muxing
   audio in a second pass over small files. Peak system memory 1.98 → 1.37 GB; a 41 s
   leaderboard went from killed to 38 s.
3. **`/tmp` is a 992 MB tmpfs** — i.e. RAM. All scratch moved to
   `MUTO_TMP=/home/user/work/tmp`.

Also: OpenCV 5 removed `CascadeClassifier`, so face tracking uses **YuNet**
(`assets/models/yunet.onnx`). Better on profiles/headsets than Haar was anyway.

## 2026-10-28T08:00Z · cut list locked

`cutlist/cutlist.json` — 35 segments, hand-picked by reading each full transcript
against the reaction-energy ranking in `src/analyze.py`, then looking at a frame from
every single segment. Four were replaced after that visual pass (recorded in
`_revisions` in the file): one sat across an SMPTE colour-bar transition card, one on
a half-black multicam layout, one on a blank wall, one on ten seconds of a DAW window.

`cutlist/plans.json` — cached crop plans for all 35 segments. All resolved to
face-tracked `cover`; hit rates 0.43–1.00.

---

## Where it stands / what is next

* [x] roster + wires + lane claim
* [x] sources + captions (5/6; 6th blocked, documented)
* [x] render engine, both styles, SFX synthesised
* [x] cut list + crop plans
* [ ] render 15 clips → `out/` (`build_all.py render`, resumable, skips finished)
* [ ] `build_all.py manifest` → `docs/MANIFEST.json` (hashes)
* [ ] `src/release.py` → one organised Release, every asset verified by read-back
* [ ] mirror receipts to `storagecode` (`data/competitionvideo28/…`) + `PUSHES.md` row
* [ ] row in this repo's root `README.md` table

**To resume after a sandbox reset:**

```bash
git clone https://github.com/dreamer2664/competitionvideo28 && cd competitionvideo28/mutoscope
pip3 install yt-dlp opencv-python-headless pillow numpy   # + ffmpeg 7.x
python3 src/fetch.py                       # re-pull sources (cutlist has the ids)
export MUTO_TMP=/home/user/work/tmp        # never /tmp — it is a tmpfs
python3 src/build_all.py render            # skips anything already in out/
python3 src/build_all.py manifest
GITHUB_TOKEN=… python3 src/release.py
```

Nothing in `out/` is needed to resume — it is all rebuildable from `cutlist/` and the
source ids. `out/` is gitignored on purpose: large media goes to Releases, never into
ordinary git (`STORAGE_POLICY.md`).

---

## 2026-10-28 ~08:15 UTC — DELIVERED (15/18)

Everything below is done and verified, not planned.

**Release:** https://github.com/dreamer2664/competitionvideo28/releases/tag/mutoscope-clips-v1
15 assets · 250,620,207 bytes · 439.65 s · public, not a draft, not a prerelease.
Confirmed readable **anonymously** (no token): asset re-downloaded, `ffprobe` decodes
`h264 1080x1920 30fps + aac`, SHA-256 matches `docs/RELEASE_RECEIPT.json`.

**Late fixes after the first QC pass:**
1. `V4-N2-trust-fall` was +0.1 dBTP. Re-limited audio only (`-c:v copy`,
   `alimiter=limit=0.85`) → −15.7 LUFS / −1.0 dBTP.
2. Source **V2 (`IpAjsMJKBvk`) carries its own burned-in word-by-word captions**
   at roughly y≈0.75 of frame. Ours were landing directly on top of them, which
   read as a stutter. Added a per-source `caption_dy` in `cutlist.json`
   (V2 = −380) threaded through `build_all.py` → `styles.py`, and re-rendered
   all three V2 clips. Verified on frames in `/home/user/work/qc/v2fix.jpg`.
   **If you add more sources, check for burned-in captions before rendering.**
3. `docs/MANIFEST.json` regenerated after both fixes — hashes are current.

**Final loudness, all 15:** −11.6 to −15.7 LUFS, every true peak ≤ −0.3 dBTP.

**Archived to storagecode @ `f47dbe9`:** `data/competitionvideo28/2026-10-28-mutoscope/`
(cut list, crop plans, manifest, release receipt, `ASSETS.md` per-asset bindings,
BLOCKED, PRODUCER_README, HANDOFF) + rows in `data/INDEX.md` and `PUSHES.md`
+ `shifts/2026-10-28-mutoscope.md`. `yt-training-s1` slots deliberately untouched —
different campaign.

**Still open — the only open thing:** source 1 `FDRUMXwb4mg` is age-restricted, so
3 of the briefed 18 clips do not exist. Nothing was faked to fill the gap. To finish:

```
python3 src/fetch.py FDRUMXwb4mg          # needs cookies, or swap the link
# add the V0 block to cutlist/cutlist.json (copy a V1 block, retime)
python3 src/build_all.py plan V0 && python3 src/build_all.py render V0
GITHUB_TOKEN=... python3 src/release.py   # patches the existing release in place
```

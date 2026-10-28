# PACKAGING — how the 18 clips are organized in a Release

**Tag:** `competitionvideo28-zyrquillix-v1` on `dreamer2664/storagecode` (primary per STORAGE_POLICY.md) + mirror on `competitionvideo28`

## Layout (not scattered)
```
Release assets:
├── zyrquillix-18clip-pack.zip          # all 18 mp4s + QC + SOURCES
├── S2-C1_Kai-slip.mp4                  # example: 31s, 1080x1920
├── S2-C2_Kai-prank.mp4
├── S2-LB_Kai-Top5.mp4
├── ... (18 total, naming: <clipID>_<hook>.mp4)
├── QC.json                             # durations, hashes, decode
├── QC.md
├── SHA256SUMS
└── clipping_plan.json
```

## Why not scattered?
- One GitHub Release URL = single source of truth
- Each file hashed + re-download verified via `release.py`
- `data/INDEX.md` row + `PUSHES.md` ledger entry in storagecode point to exact tag + SHA

## Verification
```bash
gh release download competitionvideo28-zyrquillix-v1 -R dreamer2664/storagecode
sha256sum -c SHA256SUMS
ffprobe -show_entries format=duration -of csv -p 0 S2-C1*.mp4
```

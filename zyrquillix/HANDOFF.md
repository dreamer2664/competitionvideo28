# HANDOFF — zyrquillix

## 2026-10-28T07:13Z — Join
- Registered as zyrquillix (unique name, not colliding with synchromora/mutoscope)
- T1-T5 PASS, announced on newentriescode (id 4a5kQE8UAL9T), theagency (WhNi81kqTYkP), groupchatcode (SxSQzyULxZSM)
- Cloned competitionvideo28, agency, storagecode; verified PAT still valid
- Read clippingvids: 6 sources, confirmed 5 downloadable, 1 age-restricted (FDRUMXwb4mg)
- Pushing scaffolding now: README, FILM, SOURCES, clipping_plan.json

## 2026-10-28T07:18Z — Scaffolding pushed
- Folder zyrquillix/ created with full treatment + plan for 18 clips
- Next: generate src/ pipeline (download, transcribe, style, clip, leaderboard)
- Then: push pipeline + generate SFX + demo render 1 normal + 1 leaderboard from S2 (Kai Cenat accessible)
- Then: full 18 renders chunked, QC, release to storagecode

## Resumability
- All state in clipping_plan.json and git; no local-only intermediates needed to restart
- If sandbox dies: git clone competitionvideo28, continue from last pushed HANDOFF line
- Credentials: ~/.private/zyrquillix.env (GITHUB_TOKEN) — never committed

## Blockers
- S1 age-restricted: yt-dlp needs cookies; fallback is to mark NEEDS_COOKIES and still publish plan + placeholder, request Director to supply cookies or allow skip
- Torch/whisper heavy model download can OOM on 1.5GB RAM; using whisper.cpp tiny or YouTube auto-captions fallback


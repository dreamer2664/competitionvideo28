# BLOCKED — link 1 of 6 is age-gated

**Status: 5 of 6 sources delivered (15 of 18 clips). One source cannot be fetched
from this sandbox. Not worked around, not faked, not quietly dropped.**

## The fact

```
$ yt-dlp --skip-download https://youtu.be/FDRUMXwb4mg
ERROR: [youtube] FDRUMXwb4mg: Sign in to confirm your age. This video may be
inappropriate for some users. Use --cookies-from-browser or --cookies for the
authentication.
```

`https://youtu.be/FDRUMXwb4mg?is=j9DGpwDcEz1bdhKG` — line 1 of
[`../../clippingvids`](../../clippingvids) — is **age-restricted**. YouTube will not
serve its manifest to an anonymous client.

## What was tried

Every extractor client yt-dlp 2026.10.26 offers, each a separate request path that
has historically bypassed different gates:

| player client | result |
|---|---|
| `tv_embedded` | `Sign in to confirm your age` |
| `web_embedded` | `Sign in to confirm your age` |
| `mweb` | `Sign in to confirm your age` |
| `tv` | `Sign in to confirm your age` |
| `android_vr` | `Sign in to confirm your age` |
| `ios` | `Sign in to confirm your age` |
| default (`web_safari` + `tv`) | `Sign in to confirm your age` |

Six for six. The embed-bypass routes that used to work on age-gated videos are
closed; this is an account check, not a region or rate-limit problem.

## What was deliberately *not* done

* **No cookie scraping, no account.** A YouTube session cookie is a live credential.
  `ORDERS.md` R3 and `START_HERE.md` §6 are explicit: tokens and credentials never
  land in a sandbox, a repo, a commit or a wire. A clip is not worth a red line.
* **No third-party proxy/mirror front-ends.** They would mean shipping footage from
  an unverifiable source and calling it the Director's link.
* **No substitution in silence.** Swapping in a different video and reporting "6 of 6"
  would be the exact "evidence over assertion" failure the house rules name.
* **No padding the count.** The other five sources could easily have produced 18 clips.
  They produced 15, because the brief says *three per link* and link 1 has no footage.

## How to unblock it — two ways, both cheap

**A. A cookie file (fastest).** Export `youtube.com` cookies from a signed-in browser
to `cookies.txt`, keep it outside the repo, then:

```bash
yt-dlp --cookies /path/to/cookies.txt \
  -f "bv*[height<=1080]+ba/b[height<=1080]" --merge-output-format mp4 \
  --write-auto-subs --sub-langs en-orig,en --sub-format json3 \
  -o '/home/user/work/src/FDRUMXwb4mg.%(ext)s' https://youtu.be/FDRUMXwb4mg
```

**B. A replacement link.** Drop any reachable URL into `clippingvids` in place of
line 1.

Either way the remaining three clips are three commands:

```bash
python3 src/build_all.py plan                 # adds V0's segments to plans.json
python3 src/build_all.py render V0            # 2 normal + 1 leaderboard
python3 src/build_all.py manifest             # re-hash, re-receipt
```

The cut list entry for it is pre-stubbed as source `V0` in
`cutlist/cutlist.json` once the transcript is readable — the picker
(`src/analyze.py score_moments`) ranks candidate moments automatically, so choosing
the five leaderboard beats and two normal moments is minutes of review, not a rebuild.

---

*Recorded by `mutoscope`, 2026-10-28. Rung: **verified** — the error above is
reproducible on this box with the command shown.*

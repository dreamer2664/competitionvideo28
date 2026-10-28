# QC — THE SIGNAL AT 37.5

Filled from the actual master, not from intent. Every number below is the output of
the command printed beside it.

## Technical

| check | command | result |
|---|---|---|
| container plays, duration | `ffprobe -v error -show_entries format=duration -of csv=p=0` | **467.30 s (7:47.3)** — 2:47 over the brief's 5:00 floor |
| resolution / fps / codec | `ffprobe -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name,pix_fmt` | **1920×1080, 30/1 CFR, h264 High, yuv420p, 14 019 frames** |
| audio | `ffprobe -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels` | **aac, 48 000 Hz, 2 ch, 191.6 kbps** |
| loudness | `ffmpeg -i master -af ebur128=peak=true -f null -` | **-16.0 LUFS integrated · LRA 4.8 LU · true peak -1.4 dBFS** (YouTube reference is -14; -16 is the documentary sweet spot) |
| full decode (no errors) | `ffmpeg -v error -i master -f null -` | **no output, exit 0** (whole 7:47 decoded, 80 s of wall time) |
| hash | `sha256sum THE_SIGNAL_AT_37.5.mp4` | **61e54c74a901ddfaa5d7cc249b03f107d10125e7455c48573bf1440ca0973e63** · 670 154 285 bytes |
| captions | `THE_SIGNAL_AT_37.5.srt` | **147 cues · mean 2.96 s · longest 5.08 s** (no cue exceeds 6.5 s) |
| silence / black | `silencedetect n=-45dB d=1.2`, `blackdetect d=0.2` | **0 silent gaps > 1.2 s**; 5 black segments, all deliberate act cards or hard cuts, none longer than the card |
| brightness (phone test) | mean luma of 12 sampled frames | **17–21 / 255** on the dark plates, 97 on the paper act — lifted from 4 before the grade pass so it reads on a phone at half brightness |

## Editorial

| question | verdict |
|---|---|
| Is every factual claim sourced? | Yes — frequency 1420.4556 MHz, 72 s / six 12-second samples, 30σ, the two horns, the instrument geometry, the 1998 demolition, the 2016 and 2024 hypotheses: see `FILM.md` §7. |
| Is the "reconstruction" labelled? | Yes — the printout is on screen with a persistent label that it is a reconstruction, and again in the end card. |
| Does it say what is unknown? | Yes — act V ends on "Plausible. Not confirmed", and the coda refuses to conclude. |
| Runtime over the 5-minute brief? | Yes — see Technical. |
| Any filler? | No static credit roll; the credits sit over the closing frame with the score resolving. |

## Self-critique (what a hostile reviewer would say)

- **Type-heavy.** Five of the seventeen shots are almost entirely typographic. That is
  the design language, but a viewer who wants footage will feel it around 2:00 and 4:30.
  Mitigation: those shots carry the most information, and the film earns them with the
  drawn shots between them.
- **One synthetic voice.** It is a good voice and the film is disclosed as made in code,
  but it is not a human narrator.
- **The score is simple.** A drone, a pulse and a bell motif, not an orchestra.
- **Nothing is filmed.** No archival photographs are used (rights, and the taste of a
  single visual language), so the evidence is re-drawn rather than shown.
- **The paper act is a light flash.** Two shots (the printout, the reader) sit at a
  mean luma around 100–150 between plates at 20. It is deliberate — the film's one
  bright room — but a reviewer should know it is the only place that happens.
- **Deliberate durations, not accidents:** the longest single shot is 43 s (the
  hypotheses shot in act VI), driven by the narration; everything else is 11–38 s.

# QC — THE SIGNAL AT 37.5

Filled from the actual master, not from intent. Every number below is the output of
the command printed beside it.

## Technical

| check | command | result |
|---|---|---|
| container plays, duration | `ffprobe -v error -show_entries format=duration -of csv=p=0` | *pending* |
| resolution / fps / codec | `ffprobe -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name,pix_fmt` | *pending* |
| audio | `ffprobe -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels` | *pending* |
| loudness | `ffmpeg -i master -af ebur128=peak=true -f null -` | *pending* |
| full decode (no errors) | `ffmpeg -v error -i master -f null -` | *pending* |
| hash | `sha256sum` | *pending* |
| captions | `.srt` present, 147 cues, no cue longer than 6.5 s | *pending* |

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

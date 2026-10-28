# THE SIGNAL AT 37.5 — treatment

> A documentary short about the Wow! signal: one page of printer paper, six
> characters, seventy-two seconds, and fifty years of silence.

**Runtime:** ~6:30 · **Format:** 1920×1080, 30 fps, H.264 + AAC · **Narration:** English
**Voice:** neutral documentary, low and unhurried · **Score:** original, synthesised

---

## 1. The promise to the viewer

Not "aliens". The film is about the *shape* of a piece of evidence:

- what a radio telescope actually does when it listens,
- how a signal gets written onto paper as six characters,
- why those six characters deserved the word **Wow!**,
- why nobody has been able to make them happen again — and what that silence is
  worth.

Tone: quiet, precise, a little haunted. No jump cuts, no stock alien imagery, no
claims the record doesn't support. Every number in the narration is sourced
(`FILM.md` §7).

## 2. Structure

| # | act | time | what happens |
|---|---|---|---|
| 0 | **Cold open** | 0:00–0:48 | Black. Date, place, time. The Big Ear silhouette against a turning star field. The promise: *seventy-two seconds, and then never again.* Title. |
| 1 | **The machine** | 0:48–2:00 | How Big Ear works: a tiltable flat reflector, a fixed paraboloid, two horns, wire mesh, the Earth as the motor. 72 seconds is not a coincidence — it is the beam width divided by the sky's rotation. |
| 2 | **The print** | 2:00–3:05 | Nightly output as characters: 0–9, then A–Z for anything louder. Fan-fold paper. A volunteer reads it by eye. |
| 3 | **The word** | 3:05–4:05 | 19 August 1977. Channel 2. `6 E Q U J 5`. The rise and fall. Thirty sigma. Red pen. One word. |
| 4 | **Why it mattered** | 4:05–5:10 | The three properties that made astronomers take it seriously: frequency (the hydrogen line), width (<10 kHz in one channel of fifty), shape (symmetric drift curve). Plus the anomaly: only one of two horns heard it. |
| 5 | **The silence** | 5:10–6:05 | Re-observations, other telescopes, the demolition of Big Ear in 1998, the modern arrays, and the hypotheses — comets, reflections, scintillation, magnetised hydrogen. Still unconfirmed. |
| 6 | **Coda** | 6:05–6:30 | The coordinates. The honest verdict. "For seventy-two seconds, the sky was loud." |

## 3. Visual system

A single design language across all seven acts, so the film reads as one object:

- **Palette** — ink `#07080B`, paper `#EFE9DC`, amber `#E3A24B`, signal cyan
  `#8FD6DF`, marker red `#C0392B`.
- **Type** — *Cormorant Garamond* (titles, numerals with old-style elegance),
  *Inter* (captions, body), *Oswald* (labels, coordinates, small caps).
- **Texture** — a fine 1-px grid, slow drifting star fields, film grain, vignette,
  a single soft lens bloom. Nothing glossy, nothing neon.
- **Motion grammar** — one idea per shot, always *drawn* rather than cut: lines
  stroke on, characters resolve out of noise, numbers count, ink spreads. Easings
  are slow (cubic in/out), durations 0.6–1.6 s. Cuts only at act boundaries.
- **Sound** — a D-minor drone that gains a pulse at the print, a pure 1420 Hz tone
  at the reveal (the frequency under discussion, played at a quiet level), and a
  resolving chord at the coda. Sound design is synthesised, not sampled.

## 4. Shot list (as built)

```
S0  A  Fade up on: 15 AUGUST 1977 / DELAWARE, OHIO / 10:16 PM          (type, 9 s)
S0  B  Star field, horizon, Big Ear drawn in one continuous line       (line, 20 s)
S0  C  Title: THE SIGNAL AT 37.5 + promise line                         (type, 14 s)
S1  A  Schematic: flat reflector → paraboloid → horns, rays bending     (diagram, 26 s)
S1  B  Dimension labels tick on; a moon disc for scale                  (diagram, 16 s)
S1  C  The beam: a strip of sky sliding across in 72 s, six samples     (animation, 24 s)
S2  A  The printout: 50 channels of characters typed out live           (data, 26 s)
S2  B  Zoom to the alphanumeric scale: 0–9, A–Z                         (type, 16 s)
S2  C  A hand-held sheet, a lamp, somebody reading                      (paper, 20 s)
S3  A  Channel 2 resolves: 6 E Q U J 5, one character at a time         (data, 22 s)
S3  B  The drift curve drawn above it: rise, peak, fall                 (graph, 20 s)
S3  C  Red circle strokes on; "Wow!" written in marker                  (ink, 18 s)
S4  A  The hydrogen line: atom, 1420.4058 MHz, the water hole           (diagram, 26 s)
S5  A  Timeline 1977→2026: searches, instruments, the silence           (timeline, 30 s)
S5  B  Hypotheses appear and are crossed out                            (type, 25 s)
S6  A  Coordinates, the beam, the closing line, credits                 (type, 25 s)
```

Every shot is a pure function of time (`scenes.py`), so any of them can be
re-rendered alone while keeping the edit identical.

## 5. Captions

Burned in as lower-third captions, two lines maximum, word-level timing taken from
the TTS word-boundary stream — the active word lifts in brightness. A matching
`.srt` is delivered with the master (YouTube-style, sentence-cased, no mid-word
breaks).

## 6. What was deliberately NOT done

- No claim that the signal was alien; no re-enactment of a "message".
- No stock footage or library music (licensing + the competition wanted authorship).
- No filler: no long credits roll, no looping background to reach the runtime.
  If a section doesn't carry information or feeling, it was cut.

## 7. Sources (for the narration)

- J. R. Ehman, "The Big Ear Wow! Signal — What We Know and Don't Know About It
  After 30 Years" (bigear.org, 2007/2010) — frequency 1420.4556 MHz, 72 s, six
  12-second samples, 30σ, negative horn.
- J. D. Kraus / OSU Radio Observatory (bigear.org): instrument geometry —
  flat reflector 104 m × 30 m, paraboloid 110 m × 21 m, 2,200 m², 53 m equivalent,
  8′ × 40′ beam, meridian transit, 50 channels × 10 kHz.
- Wikipedia, "Wow! signal" and "Ohio State University Radio Observatory" (cross-check
  only; primary figures above).
- A. Méndez, K. Ortiz-Ceballos, J. I. Zuluaga, "Arecibo Wow! I: An Astrophysical
  Explanation for the Wow! Signal", arXiv:2408.08513 (2024) — hydrogen-cloud /
  magnetar hypothesis, and the 22:16 EST timestamp.
- A. Paris (2016), comet hypothesis, and its published rebuttals.

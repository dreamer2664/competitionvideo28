# THIRTY BRONZE WHEELS — Film Treatment & Storyboard

> **Subtitle:** *Decoding the 2,000-Year-Old Computer From the Bottom of the Aegean Sea*
> **Producer:** `chronoscope` · **Runtime (measured):** 327.87 s (5:27.87) · **Resolution:** 1920×1080 @ 30 fps

---

## 1. Audience Promise & Editorial Thesis

**Viewer promise (delivered in the first 15 seconds):**
How did a shoebox-sized block of corroded bronze pulled from a Roman shipwreck in 1900
compute the 19-year Metonic calendar, the elliptical velocity changes of the Moon, and
the exact month and hour of solar and lunar eclipses — using prime-number gear trains
and a pin-and-slot differential 1,700 years before Isaac Newton?

Rather than treating the Antikythera Mechanism as a vague "ancient mystery", this film
treats it as **engineering**: we open the bronze case, trace the prime factorizations on
each axle, watch the 2005 450-kilovolt X-ray CT scanner slice through 82 calcified
fragments, and see how each gear ratio solves a specific astronomical mismatch between
the Sun, the Moon, and the stars.

---

## 2. Seven-Act Narrative Architecture

| Act | Title | Window | Core Visual & Scientific Mechanism |
|---|---|---|---|
| **I** | **42 Meters Down** | `0:00 – 0:48` | Cold open in the Aegean Sea (spring 1900). Captain Dimitrios Kontos and sponge diver Elias Stadiatis descend 42m off Cape Glyfadia, Antikythera. May 17, 1902: archaeologist Valerios Stais spots a calcified bronze wheel with 60-degree triangular teeth (`Fragment A`). |
| **II** | **The Calendar Problem** | `0:48 – 1:40` | Why ancient calendars drift: one tropical year (`365.2422` days) does not divide evenly by one synodic lunar month (`29.53059` days). The Babylonian/Greek Metonic discovery: **19 solar years = 235 lunar months** (`6,939.6` days). |
| **III** | **The Prime-Number Gear Train** | `1:40 – 2:38` | Entering the front drive wheel `b1` (223/224 teeth) and `b2` (64 teeth). Tracing the exact Metonic & sidereal train discovered by Price (1974) and corrected by Freeth et al. (2006): `64/38 × 48/24 × 127/32 = 254/19` — turning 19 solar rotations into 254 sidereal revolutions of the Moon. |
| **IV** | **Eight Tons of X-Rays** | `2:38 – 3:32` | Why surface inspection failed for 103 years. In 2005, the Antikythera Mechanism Research Project brings an 8-ton, 450 kV micro-focus X-ray CT scanner (*BladeRunner*) and Polynomial Texture Mapping dome to Athens. Virtual 50-micron slices reveal 30 bronze gears and 3,000+ characters of Corinthian Greek user-manual text. |
| **V** | **The Saros Eclipse Spiral** | `3:32 – 4:24` | The lower back dial: a 4-turn Archimedean spiral divided into **223 synodic months** (the Saros cycle = 18 years, 11 days, 8 hours). How the three lunar periods (Synodic, Draconic node crossing, Anomalistic distance) align every 223 months, and why the 8-hour fraction requires the tiny **Exeligmos** triple-wheel (`54 years`) dial. |
| **VI** | **The Pin, the Slot, and Kepler's Moon** | `4:24 – 5:12` | The crown jewel on the rear axle: gears `k1` and `k2` (50 teeth each) mounted on axes offset by `1.1 mm`, linked by a pin sliding in a radial slot. As `k1` rotates at constant speed, `k2` speeds up at perigee and slows down at apogee — mechanically computing Hipparchus's epicyclic lunar anomaly across the entire gear train. |
| **VII** | **The Lost Cosmos & Coda** | `5:12 – 5:50` | The 2021 UCL breakthrough (Freeth et al., *Scientific Reports*): decoding the missing front planetary section using inscribed numbers `462` (Venus) and `442` (Saturn). Why this technology vanished into Byzantine/Islamic geared astrolabes before re-emerging in 14th-century European cathedral clocks. Closing reflection. |

---

## 3. The 19-shot cut, as built (measured)

Runtime **327.83 s** on the delivered master (`9,833` frames @ 30 fps as probed; the timeline builds 9,836 — concat seams eat 3) — inside the agency's
300–330 s acceptance window *and* above the competition minimum of five minutes.
Five shots from the original 24-shot board were cut for runtime discipline after the first
assembly measured 7:02: the Babylon/Meton grid, Price's 1974 radiograph, the eclipse-glyph
detail, the oscilloscope, and the "what remained open" coda beat. Their arguments were folded
into the neighbouring narration rather than dropped. (See `docs/PROCESS.md` §2.)

| shot | time | title | scene |
|---|---|---|---|
| `S01` | 00:00.00–00:15.23 | The Shelf Off Cape Glyfadia, Spring 1900 | `bathymetry_dive` |
| `S02` | 00:15.23–00:32.47 | Athens, May 17, 1902: The Calcified Lump | `museum_discovery` |
| `S03` | 00:32.47–00:48.47 | Title Lockup: Thirty Bronze Wheels | `title_lockup` |
| `S04` | 00:48.47–01:07.50 | The Incommensurable Sky: 365.2422 vs 29.5306 | `calendar_drift` |
| `S06` | 01:07.50–01:27.73 | Nineteen Years, 235 Months, 254 Orbits | `sidereal_vector` |
| `S07` | 01:27.73–01:47.97 | Factoring 254 / 19 Into Buildable Teeth | `prime_factorization` |
| `S08` | 01:47.97–02:07.10 | Live Kinematic Train: 64/38 x 48/24 x 127/32 | `live_gear_train` |
| `S10` | 02:07.10–02:25.07 | The 2005 BladeRunner 450 kV Micro-CT Rig | `bladerunner_rig` |
| `S11` | 02:25.07–02:40.00 | Virtual 50-Micron Tomography Scrub | `ct_slice_scanner` |
| `S12` | 02:40.00–02:54.17 | Reading the Parapegma Inscriptions | `ptm_epigraphy` |
| `S13` | 02:54.17–03:11.30 | Upper Back Dial: Corinthian Calendar & Olympiad | `metonic_spiral_dial` |
| `S14` | 03:11.30–03:28.73 | Three Lunar Cycles Converge: 223 Months | `saros_convergence` |
| `S15` | 03:28.73–03:46.37 | The 223-Tooth Gear e3 & The Exeligmos Dial | `saros_spiral_dial` |
| `S17` | 03:46.37–04:02.00 | The Anomaly of the Moon's Elliptical Speed | `lunar_ellipse_anomaly` |
| `S18` | 04:02.00–04:19.00 | Hipparchus in Bronze: Gears k1 and k2 | `pin_and_slot_sim` |
| `S20` | 04:19.00–04:38.13 | The Epicyclic Turntable on e3 (8.85-Year Precession) | `epicyclic_turntable` |
| `S21` | 04:38.13–04:53.60 | The 2021 UCL Planetary Breakthrough (462 & 442) | `ucl_venus_saturn` |
| `S22` | 04:53.60–05:11.43 | Fragment D's 63-Tooth Wheel & Concentric Rings | `planetary_ring_cosmos` |
| `S24` | 05:11.43–05:27.87 | Coda: The Cosmos in the Palm of a Hand | `coda_blueprint` |

## 4. Visual & Audio Design System

### Color Palette (Museum Dark + Radiographic Bronze)
- **Abyssal Slate (Canvas BG):** `#080B10` to `#0E1621` radial vignette
- **Aegean Deep Water:** `#102A3A` / `#1D4E68`
- **Corinthian Bronze (Primary Gears):** `#C88A3E` (base), `#F2C47E` (specular tooth highlight), `#6E4618` (bevel shadow)
- **Archaeological Patina (Verdigris):** `#2B8A78` (oxidized copper), `#5CE0C6` (active highlight)
- **Micro-CT X-Ray Cyan:** `#6CE5FF` (high-density attenuation), `#16384C` (voxel grid)
- **Eclipse Crimson / Alert:** `#E25549`
- **Epigraphic Parchment (Typography):** `#F3EFE6` (primary), `#9FB0C2` (secondary labels)

### Typography (All OFL / Open-Licensed & Glyph-Verified)
- **Display / Act Titles:** *Fraunces* (`Fraunces.ttf`, OFL) — high-contrast old-style serif evoking museum monographs.
- **UI / Explanatory Diagrams / Captions:** *Inter* (`Inter-SemiBold.ttf`, `Inter-Medium.ttf`, `Inter-Regular.ttf`, OFL) — maximum legibility at 1080p and mobile viewports.
- **Kinematic Ratios / Telemetry / Timecodes:** *IBM Plex Mono* (`IBMPlexMono-Medium.ttf`, `IBMPlexMono-Regular.ttf`, OFL) — tabular numerals for live gear counters and CT slice coordinates.
- **Ancient Greek Epigraphy & Math Symbols:** *DejaVu Sans* (`/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`) — verified complete coverage for Greek capitals (`Π Α Ρ Α Π Η Γ Μ Α`, `Σ`, `Η`) and mathematical operators (`×`, `÷`, `≈`, `ω`, `Δ`).

### Sound & Loudness Architecture
- **Narration:** `kokoro-onnx` v0.6.1 at 24 kHz → resampled to 48 kHz stereo.
  - Primary Narrator: `bm_george` (measured ~145 WPM, warm British documentary baritone).
  - Epigraphic / Primary-Source Voice: `af_heart` (clear contrast when reading translated Greek inscriptions from the bronze plates).
- **Original Procedural Score (`score.py`):**
  - Synthesized in 48 kHz floating-point NumPy: D-Dorian modal pad with slow filter evolution, subtle metallic bronze harmonic overtones (`1:2.76:5.40` bell partials), and rhythmic escapement/gear-tooth ticks synced to the mechanical scenes.
  - Sidechain ducking: music bed sits `-18 dB` below speech during active narration and swells gently (`+5 dB`) during inter-act transitions.
  - Final master normalized via two-pass EBU R128 `loudnorm` + true-peak brickwall ceiling to hit **`-16.0 LUFS` (±0.5)** and **`≤ -1.2 dBTP`**.

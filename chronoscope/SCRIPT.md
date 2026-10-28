# SCRIPT.md — Measured Timecoded Narration & Pronunciation Ledger

**Film:** *THIRTY BRONZE WHEELS: Decoding the Antikythera Mechanism*
**Measured Runtime:** `422.27 s` (`12668` frames @ `30.0 fps`, `07:02.27`)
**Voices:**
- `bm_george` (`kokoro-onnx` `0.6.1`, `en-gb`, speed `0.94–0.96`): Primary documentary narrator
- `af_heart` (`kokoro-onnx` `0.6.1`, `en-us`, speed `0.95`): Primary-source ancient Greek inscription reader (`S12`, `S16`)

## 1. Editorial & Pronunciation Repairs Recorded Before Synthesis

| Term in Display / Captions | Phonemic Defect in Raw TTS | Repaired Synthesis Spelling | Verified IPA Output |
|---|---|---|---|
| `Hipparchus` | Soft `ch` `/hˈɪpɑːtʃəs/` | `Hipparkus` | `/hˈɪpɑːkəs/` |
| `Exeligmos` | Slurred stress `/ɛɡzɪlˈɪɡməʊz/` | `Ex-el-ig-moss` | `/ˈɛksˌɛlˈɪɡmˈɒs/` |
| `100 BCE` | Read as unit word | `one hundred B C E` | Distinct initials |
| `450-kilovolt CT` | Clipped acronym | `four hundred and fifty kilovolt C T` | Clear letter articulation |
| `b2, c1, c2, d1, d2, e2, e3, k1, k2` | Lowercase letter-number run-on | `B two, C one, C two, D one, D two, E two, E three, K one, K two` | Distinct gear callsigns |

---

## 2. Measured 24-Shot Narration Script

### ACT I · 42 METERS DOWN

- **`S01` (`00:00.00 – 00:16.57` · `16.57s` total / `14.77s` speech · voice `bm_george` · scene `bathymetry_dive`)**
  > In the spring of 1900, blown off course where the Aegean meets the Cretan Sea, sponge diver Elias Stadiatis dropped forty-two meters down a submerged cliff off Antikythera and found a Roman shipwreck.

- **`S02` (`00:16.57 – 00:34.30` · `17.73s` total / `16.73s` speech · voice `bm_george` · scene `museum_discovery`)**
  > Among marble statues and amphorae hauled to Athens sat a corroded lump of bronze. On May 17, 1902, archaeologist Valerios Stais noticed the drying case had cracked open, exposing miniature sixty-degree gear teeth.

- **`S03` (`00:34.30 – 00:51.10` · `16.80s` total / `15.51s` speech · voice `bm_george` · scene `title_lockup`)**
  > No machine like it was supposed to exist for another fourteen centuries. Inside eighty-two calcified fragments were thirty bronze wheels that computed the calendar, predicted eclipses, and modeled the variable speed of the Moon.

### ACT II · THE CALENDAR PROBLEM

- **`S04` (`00:51.10 – 01:10.67` · `19.57s` total / `18.56s` speech · voice `bm_george` · scene `calendar_drift`)**
  > To understand why someone cut those teeth around 100 BCE, start with the headache of every ancient astronomer: one solar year of 365.24 days does not divide evenly by a lunar month of 29.53 days.

- **`S05` (`01:10.67 – 01:28.80` · `18.13s` total / `17.23s` speech · voice `bm_george` · scene `metonic_grid`)**
  > Twelve lunar months fall short of a solar year by nearly eleven days. Babylonian and Greek astronomers found an almost miraculous integer resonance: nineteen solar years equal almost exactly 235 lunar months, within two hours.

- **`S06` (`01:28.80 – 01:49.43` · `20.63s` total / `19.53s` speech · voice `bm_george` · scene `sidereal_vector`)**
  > Here is the mechanical catch. In nineteen years, the Moon completes 235 phase cycles relative to the Sun. Because Earth itself circles the Sun nineteen times, the Moon completes 235 plus 19—or 254—orbits against the stars.

### ACT III · THE PRIME-NUMBER GEAR TRAIN

- **`S07` (`01:49.43 – 02:10.17` · `20.73s` total / `19.73s` speech · voice `bm_george` · scene `prime_factorization`)**
  > How do you turn the fraction 254 over 19 into bronze? You cannot easily cut a single 254-tooth wheel. Instead, the designer factored 254 into 2 times the prime number 127, and chained six gears across three axles.

- **`S08` (`02:10.17 – 02:29.83` · `19.67s` total / `18.66s` speech · voice `bm_george` · scene `live_gear_train`)**
  > Watch the exact train inside Fragment A: the 64-tooth drive wheel b2 turns a 38-tooth gear c1; c2 with 48 teeth drives d1 with 24; and d2 with 127 teeth drives the 32-tooth lunar spindle e2.

- **`S09` (`02:29.83 – 02:52.30` · `22.47s` total / `21.37s` speech · voice `bm_george` · scene `price_radiograph`)**
  > Multiply 64 over 38, times 48 over 24, times 127 over 32: the factors cancel to 254 over 19. Historian Derek de Solla Price glimpsed this in 1974 using flat X-rays, but overlapping shadows hid the deeper gears.

### ACT IV · EIGHT TONS OF X-RAYS

- **`S10` (`02:52.30 – 03:10.80` · `18.50s` total / `17.50s` speech · voice `bm_george` · scene `bladerunner_rig`)**
  > Because the fragments were far too fragile to travel, in 2005 an international team led by Tony Freeth shipped an eight-ton, 450-kilovolt micro-focus CT scanner—nicknamed BladeRunner—straight to the museum in Athens.

- **`S11` (`03:10.80 – 03:26.17` · `15.37s` total / `14.45s` speech · voice `bm_george` · scene `ct_slice_scanner`)**
  > Slicing through the bronze in fifty-micron layers, three-dimensional tomography separated gears packed closer than a millimeter apart—and revealed over three thousand hidden Greek characters etched into the casing.

- **`S12` (`03:26.17 – 03:40.93` · `14.77s` total / `13.68s` speech · voice `af_heart` · scene `ptm_epigraphy`)**
  > The inscriptions read like an astronomical manual: "The spiral is divided into 235 sections... The golden little sphere shows the Sun; in the evening the Pleiades rise, and the Hyades set."

### ACT V · THE SAROS ECLIPSE SPIRAL

- **`S13` (`03:40.93 – 03:58.57` · `17.63s` total / `16.64s` speech · voice `bm_george` · scene `metonic_spiral_dial`)**
  > On the upper back plate, a five-turn spiral tracks all 235 months of the Metonic cycle, inscribed with twelve Corinthian month names—suggesting a heritage tied to Corinth or Syracuse—plus a dial for the Olympic Games.

- **`S14` (`03:58.57 – 04:16.40` · `17.83s` total / `16.94s` speech · voice `bm_george` · scene `saros_convergence`)**
  > Below it sits the Saros eclipse predictor. An eclipse only happens when a New or Full Moon aligns with the tilted node of the Moon's orbit. Every 223 lunar months—eighteen years, eleven days, and eight hours—all three cycles lock.

- **`S15` (`04:16.40 – 04:34.53` · `18.13s` total / `17.15s` speech · voice `bm_george` · scene `saros_spiral_dial`)**
  > Driven by a massive 223-tooth gear e3, the pointer sweeps a four-turn spiral marked with Sigma for lunar and Eta for solar eclipses—while the tiny Exeligmos dial adds zero, eight, or sixteen hours to the predicted time.

- **`S16` (`04:34.53 – 04:46.27` · `11.73s` total / `10.62s` speech · voice `af_heart` · scene `eclipse_glyph_detail`)**
  > Even the color and direction of the obscured sky were cataloged on the back cover: "Lunar eclipse at the ninth hour; solar eclipse... winds from the east, and dark crimson light."

### ACT VI · THE PIN, THE SLOT & KEPLER'S MOON

- **`S17` (`04:46.27 – 05:02.43` · `16.17s` total / `15.16s` speech · voice `bm_george` · scene `lunar_ellipse_anomaly`)**
  > Yet the mechanism's deepest triumph lies tucked at the back of Fragment A. Because the Moon's orbit is elliptical, it speeds up near perigee and slows down near apogee—varying from fourteen degrees a day to under twelve.

- **`S18` (`05:02.43 – 05:19.87` · `17.43s` total / `16.52s` speech · voice `bm_george` · scene `pin_and_slot_sim`)**
  > To reproduce the lunar theory of Hipparchus, the maker stacked two fifty-tooth gears, k1 and k2, with their axles offset by just 1.1 millimeters. A pin on k1 slides inside a radial slot cut into k2.

- **`S19` (`05:19.87 – 05:33.87` · `14.00s` total / `13.12s` speech · voice `bm_george` · scene `pin_slot_oscilloscope`)**
  > As the lower gear turns at a constant rate, the effective radius of the driving pin changes continuously—forcing the upper gear to accelerate and decelerate in a smooth harmonic wave.

- **`S20` (`05:33.87 – 05:53.63` · `19.77s` total / `18.65s` speech · voice `bm_george` · scene `epicyclic_turntable`)**
  > Better still, that entire pin-and-slot pair rides piggyback on the rotating 223-tooth Saros gear e3—so the orientation of the Moon's apogee slowly precesses around the sky every 8.85 years, just as it does in nature.

### ACT VII · THE LOST COSMOS & CODA

- **`S21` (`05:53.63 – 06:09.60` · `15.97s` total / `14.97s` speech · voice `bm_george` · scene `ucl_venus_saturn`)**
  > What about the missing front section? In 2021, researchers at University College London decoded two numbers on the front plate: 462 years for Venus, and 442 years for Saturn.

- **`S22` (`06:09.60 – 06:27.87` · `18.27s` total / `17.36s` speech · voice `bm_george` · scene `planetary_ring_cosmos`)**
  > Using an orphaned 63-tooth gear from Fragment D—since 462 factors into 6 times 7 times 11—they showed how concentric bronze rings displayed Mercury, Venus, Mars, Jupiter, and Saturn around the Zodiac.

- **`S23` (`06:27.87 – 06:44.97` · `17.10s` total / `16.21s` speech · voice `bm_george` · scene `historical_lineage`)**
  > Historians still debate whether the workshop stood on Rhodes in the era of Hipparchus or in the tradition of Archimedes. Its echoes survived in Byzantine and Islamic geared astrolabes before reawakening in European clockwork.

- **`S24` (`06:44.97 – 07:02.27` · `17.30s` total / `14.58s` speech · voice `bm_george` · scene `coda_blueprint`)**
  > Two thousand years on the seafloor dissolved its wooden frame and froze its axles in stone. Yet the prime numbers held—thirty bronze wheels proving that the sky itself obeys a law you can hold in your hands.

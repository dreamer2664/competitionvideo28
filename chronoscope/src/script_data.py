#!/usr/bin/env python3
"""
Complete 24-shot script, narration cues, pronunciation repairs, and visual parameters
for THIRTY BRONZE WHEELS: Decoding the Antikythera Mechanism (100 BCE - 2021).
Producer: chronoscope
"""

FILM_META = {
    "title": "THIRTY BRONZE WHEELS: Decoding the Antikythera Mechanism",
    "subtitle": "How a 2,000-Year-Old Bronze Computer Predicted Eclipses and Planetary Motion",
    "producer": "chronoscope",
    "fps": 30,
    "width": 1920,
    "height": 1080,
}

# 24 purposeful shots across 7 acts.
# Each entry provides:
# - id: Shot ID (S01..S24)
# - act: Act number and title
# - title: Short shot title
# - voice: 'bm_george' (primary documentary narrator, en-gb) or 'af_heart' (epigraphic inscription voice, en-us)
# - speed: TTS speed multiplier
# - lead_in: Pre-speech visual breathing room (seconds)
# - tail_out: Post-speech visual breathing room (seconds)
# - display_text: Clean text for burned-in captions, SRT, VTT, and transcript
# - tts_text: Pronunciation-repaired text for Kokoro-82M ONNX synthesis
# - scene_kind: Identifier for the procedural 30fps renderer in scenes.py

SHOTS = [
    # ACT I: 42 METERS DOWN
    {
        "id": "S01",
        "act": "ACT I · 42 METERS DOWN",
        "title": "The Shelf Off Cape Glyfadia, Spring 1900",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_01_shipwreck.jpg",
        "scene_kind": "bathymetry_dive",
        "display_text": (
            "In the spring of 1900, blown off course where the Aegean meets the Cretan Sea, "
            "sponge diver Elias Stadiatis dropped forty-two meters down a submerged cliff off Antikythera "
            "and found a Roman shipwreck."
        ),
        "tts_text": (
            "In the spring of nineteen hundred, blown off course where the Aegean meets the Cretan Sea, "
            "sponge diver Elias Stadiatis dropped forty-two meters down a submerged cliff off Antikythera "
            "and found a Roman shipwreck."
        ),
    },
    {
        "id": "S02",
        "act": "ACT I · 42 METERS DOWN",
        "title": "Athens, May 17, 1902: The Calcified Lump",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_07_athens_museum_1902.jpg",
        "scene_kind": "museum_discovery",
        "display_text": (
            "Among marble statues and amphorae hauled to Athens sat a corroded lump of bronze. "
            "On May 17, 1902, archaeologist Valerios Stais noticed the drying case had cracked open, "
            "exposing miniature sixty-degree gear teeth."
        ),
        "tts_text": (
            "Among marble statues and amphorae hauled to Athens sat a corroded lump of bronze. "
            "On May seventeenth, nineteen oh two, archaeologist Valerios Stais noticed the drying case had cracked open, "
            "exposing miniature sixty-degree gear teeth."
        ),
    },
    {
        "id": "S03",
        "act": "ACT I · 42 METERS DOWN",
        "title": "Title Lockup: Thirty Bronze Wheels",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.95,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_02_fragment_a.jpg",
        "scene_kind": "title_lockup",
        "display_text": (
            "No machine like it was supposed to exist for another fourteen centuries. "
            "Inside eighty-two calcified fragments were thirty bronze wheels that computed the calendar, "
            "predicted eclipses, and modeled the variable speed of the Moon."
        ),
        "tts_text": (
            "No machine like it was supposed to exist for another fourteen centuries. "
            "Inside eighty-two calcified fragments were thirty bronze wheels that computed the calendar, "
            "predicted eclipses, and modeled the variable speed of the Moon."
        ),
    },

    # ACT II: THE CALENDAR PROBLEM
    {
        "id": "S04",
        "act": "ACT II · THE CALENDAR PROBLEM",
        "title": "The Incommensurable Sky: 365.2422 vs 29.5306",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_03_hellenistic_workshop.jpg",
        "scene_kind": "calendar_drift",
        "display_text": (
            "To understand why someone cut those teeth around 100 BCE, start with the headache of every ancient astronomer: "
            "one solar year of 365.24 days does not divide evenly by a lunar month of 29.53 days."
        ),
        "tts_text": (
            "To understand why someone cut those teeth around one hundred B C E, start with the headache of every ancient astronomer: "
            "one solar year of three hundred and sixty-five point two four days does not divide evenly by a lunar month of twenty-nine point five three days."
        ),
    },
    {
        "id": "S06",
        "act": "ACT II · THE CALENDAR PROBLEM",
        "title": "Nineteen Years, 235 Months, 254 Orbits",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_03_hellenistic_workshop.jpg",
        "scene_kind": "sidereal_vector",
        "display_text": (
            "Babylonian and Greek astronomers had already found the trick: 19 solar years equal almost exactly 235 lunar months. "
            "The Moon needs 235 phase cycles against the Sun, plus Earth's own 19 orbits, to return to the same place against the stars."
        ),
        "tts_text": (
            "Babylonian and Greek astronomers had already found the trick: nineteen solar years equal almost exactly two hundred and thirty-five lunar months. "
            "The Moon needs two hundred and thirty-five phase cycles against the Sun, plus Earth's own nineteen orbits, to return to the same place against the stars."
        ),
    },

    # ACT III: THE PRIME-NUMBER GEAR TRAIN
    {
        "id": "S07",
        "act": "ACT III · THE PRIME-NUMBER GEAR TRAIN",
        "title": "Factoring 254 / 19 Into Buildable Teeth",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_02_fragment_a.jpg",
        "scene_kind": "prime_factorization",
        "display_text": (
            "How do you turn the fraction 254 over 19 into bronze? "
            "You cannot easily cut a single 254-tooth wheel. "
            "Instead, the designer factored 254 into 2 times the prime number 127, and chained six gears across three axles."
        ),
        "tts_text": (
            "How do you turn the fraction two hundred and fifty-four over nineteen into bronze? "
            "You cannot easily cut a single two hundred and fifty-four tooth wheel. "
            "Instead, the designer factored two hundred and fifty-four into two times the prime number one hundred and twenty-seven, and chained six gears across three axles."
        ),
    },
    {
        "id": "S08",
        "act": "ACT III · THE PRIME-NUMBER GEAR TRAIN",
        "title": "Live Kinematic Train: 64/38 x 48/24 x 127/32",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_02_fragment_a.jpg",
        "scene_kind": "live_gear_train",
        "display_text": (
            "Watch the exact train inside Fragment A: the 64-tooth drive wheel b2 turns a 38-tooth gear c1; "
            "c2 with 48 teeth drives d1 with 24; and d2 with 127 teeth drives the 32-tooth lunar spindle e2."
        ),
        "tts_text": (
            "Watch the exact train inside Fragment A: the sixty-four tooth drive wheel B two turns a thirty-eight tooth gear C one; "
            "C two with forty-eight teeth drives D one with twenty-four; and D two with one hundred and twenty-seven teeth drives the thirty-two tooth lunar spindle E two."
        ),
    },

    # ACT IV: EIGHT TONS OF X-RAYS
    {
        "id": "S10",
        "act": "ACT IV · EIGHT TONS OF X-RAYS",
        "title": "The 2005 BladeRunner 450 kV Micro-CT Rig",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_04_xray_tomography.jpg",
        "scene_kind": "bladerunner_rig",
        "display_text": (
            "Because the fragments were far too fragile to travel, in 2005 an international team led by Tony Freeth "
            "shipped an eight-ton, 450-kilovolt micro-focus CT scanner—nicknamed BladeRunner—straight to the museum in Athens."
        ),
        "tts_text": (
            "Because the fragments were far too fragile to travel, in two thousand and five an international team led by Tony Freeth "
            "shipped an eight-ton, four hundred and fifty kilovolt micro-focus C T scanner, nicknamed Blade Runner, straight to the museum in Athens."
        ),
    },
    {
        "id": "S11",
        "act": "ACT IV · EIGHT TONS OF X-RAYS",
        "title": "Virtual 50-Micron Tomography Scrub",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_04_xray_tomography.jpg",
        "scene_kind": "ct_slice_scanner",
        "display_text": (
            "Slicing through the bronze in fifty-micron layers, three-dimensional tomography separated gears "
            "packed closer than a millimeter apart—and revealed over three thousand hidden Greek characters "
            "etched into the casing."
        ),
        "tts_text": (
            "Slicing through the bronze in fifty-micron layers, three-dimensional tomography separated gears "
            "packed closer than a millimeter apart, and revealed over three thousand hidden Greek characters "
            "etched into the casing."
        ),
    },
    {
        "id": "S12",
        "act": "ACT IV · EIGHT TONS OF X-RAYS",
        "title": "Reading the Parapegma Inscriptions",
        "voice": "af_heart",
        "lang": "en-us",
        "speed": 0.95,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_04_xray_tomography.jpg",
        "scene_kind": "ptm_epigraphy",
        "display_text": (
            "The inscriptions read like an astronomical manual: "
            "\"The spiral is divided into 235 sections... The golden little sphere shows the Sun; "
            "in the evening the Pleiades rise, and the Hyades set.\""
        ),
        "tts_text": (
            "The inscriptions read like an astronomical manual: "
            "The spiral is divided into two hundred and thirty-five sections. The golden little sphere shows the Sun; "
            "in the evening the Pleiades rise, and the Hyades set."
        ),
    },

    # ACT V: THE SAROS ECLIPSE SPIRAL
    {
        "id": "S13",
        "act": "ACT V · THE SAROS ECLIPSE SPIRAL",
        "title": "Upper Back Dial: Corinthian Calendar & Olympiad",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_05_saros_eclipse.jpg",
        "scene_kind": "metonic_spiral_dial",
        "display_text": (
            "On the upper back plate, a five-turn spiral tracks all 235 months of the Metonic cycle, "
            "inscribed with twelve Corinthian month names—suggesting a heritage tied to Corinth or Syracuse—plus a dial for the Olympic Games."
        ),
        "tts_text": (
            "On the upper back plate, a five-turn spiral tracks all two hundred and thirty-five months of the Metonic cycle, "
            "inscribed with twelve Corinthian month names, suggesting a heritage tied to Corinth or Syracuse, plus a dial for the Olympic Games."
        ),
    },
    {
        "id": "S14",
        "act": "ACT V · THE SAROS ECLIPSE SPIRAL",
        "title": "Three Lunar Cycles Converge: 223 Months",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_05_saros_eclipse.jpg",
        "scene_kind": "saros_convergence",
        "display_text": (
            "Below it sits the Saros eclipse predictor. An eclipse only happens when a New or Full Moon aligns "
            "with the tilted node of the Moon's orbit. Every 223 lunar months—eighteen years, eleven days, and eight hours—all three cycles lock."
        ),
        "tts_text": (
            "Below it sits the Saros eclipse predictor. An eclipse only happens when a New or Full Moon aligns "
            "with the tilted node of the Moon's orbit. Every two hundred and twenty-three lunar months, eighteen years, eleven days, and eight hours, all three cycles lock."
        ),
    },
    {
        "id": "S15",
        "act": "ACT V · THE SAROS ECLIPSE SPIRAL",
        "title": "The 223-Tooth Gear e3 & The Exeligmos Dial",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_05_saros_eclipse.jpg",
        "scene_kind": "saros_spiral_dial",
        "display_text": (
            "Driven by a massive 223-tooth gear e3, the pointer sweeps a four-turn spiral marked with Sigma for lunar "
            "and Eta for solar eclipses—while the tiny Exeligmos dial adds zero, eight, or sixteen hours to the predicted time."
        ),
        "tts_text": (
            "Driven by a massive two hundred and twenty-three tooth gear E three, the pointer sweeps a four-turn spiral marked with Sigma for lunar "
            "and Eta for solar eclipses, while the tiny Ex-el-ig-moss dial adds zero, eight, or sixteen hours to the predicted time."
        ),
    },

    # ACT VI: THE PIN, THE SLOT, AND KEPLER'S MOON
    {
        "id": "S17",
        "act": "ACT VI · THE PIN, THE SLOT & KEPLER'S MOON",
        "title": "The Anomaly of the Moon's Elliptical Speed",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_06_clockwork_cosmos.jpg",
        "scene_kind": "lunar_ellipse_anomaly",
        "display_text": (
            "Yet the mechanism's deepest triumph lies tucked at the back of Fragment A. "
            "Because the Moon's orbit is elliptical, it speeds up near perigee and slows down near apogee—"
            "varying from fourteen degrees a day to under twelve."
        ),
        "tts_text": (
            "Yet the mechanism's deepest triumph lies tucked at the back of Fragment A. "
            "Because the Moon's orbit is elliptical, it speeds up near perigee and slows down near apogee, "
            "varying from fourteen degrees a day to under twelve."
        ),
    },
    {
        "id": "S18",
        "act": "ACT VI · THE PIN, THE SLOT & KEPLER'S MOON",
        "title": "Hipparchus in Bronze: Gears k1 and k2",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_06_clockwork_cosmos.jpg",
        "scene_kind": "pin_and_slot_sim",
        "display_text": (
            "To reproduce the lunar theory of Hipparchus, the maker stacked two fifty-tooth gears, k1 and k2, "
            "with their axles offset by just 1.1 millimeters. A pin on k1 slides inside a radial slot cut into k2."
        ),
        "tts_text": (
            "To reproduce the lunar theory of Hipparkus, the maker stacked two fifty-tooth gears, K one and K two, "
            "with their axles offset by just one point one millimeters. A pin on K one slides inside a radial slot cut into K two."
        ),
    },
    {
        "id": "S20",
        "act": "ACT VI · THE PIN, THE SLOT & KEPLER'S MOON",
        "title": "The Epicyclic Turntable on e3 (8.85-Year Precession)",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_06_clockwork_cosmos.jpg",
        "scene_kind": "epicyclic_turntable",
        "display_text": (
            "Better still, that entire pin-and-slot pair rides piggyback on the rotating 223-tooth Saros gear e3—"
            "so the orientation of the Moon's apogee slowly precesses around the sky every 8.85 years, just as it does in nature."
        ),
        "tts_text": (
            "Better still, that entire pin-and-slot pair rides piggyback on the rotating two hundred and twenty-three tooth Saros gear E three, "
            "so the orientation of the Moon's apogee slowly precesses around the sky every eight point eight five years, just as it does in nature."
        ),
    },

    # ACT VII: THE LOST COSMOS & CODA
    {
        "id": "S21",
        "act": "ACT VII · THE LOST COSMOS & CODA",
        "title": "The 2021 UCL Planetary Breakthrough (462 & 442)",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_08_planetary_rings.jpg",
        "scene_kind": "ucl_venus_saturn",
        "display_text": (
            "What about the missing front section? In 2021, researchers at University College London decoded two numbers "
            "on the front plate: 462 years for Venus, and 442 years for Saturn."
        ),
        "tts_text": (
            "What about the missing front section? In twenty twenty-one, researchers at University College London decoded two numbers "
            "on the front plate: four hundred and sixty-two years for Venus, and four hundred and forty-two years for Saturn."
        ),
    },
    {
        "id": "S22",
        "act": "ACT VII · THE LOST COSMOS & CODA",
        "title": "Fragment D's 63-Tooth Wheel & Concentric Rings",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.96,
        "lead_in": 0.16,
        "tail_out": 0.24,
        "plate": "plate_08_planetary_rings.jpg",
        "scene_kind": "planetary_ring_cosmos",
        "display_text": (
            "Using an orphaned 63-tooth gear from Fragment D—since 462 factors into 6 times 7 times 11—they showed how "
            "concentric bronze rings displayed Mercury, Venus, Mars, Jupiter, and Saturn around the Zodiac."
        ),
        "tts_text": (
            "Using an orphaned sixty-three tooth gear from Fragment D, since four hundred and sixty-two factors into six times seven times eleven, they showed how "
            "concentric bronze rings displayed Mercury, Venus, Mars, Jupiter, and Saturn around the Zodiac."
        ),
    },
    {
        "id": "S24",
        "act": "ACT VII · THE LOST COSMOS & CODA",
        "title": "Coda: The Cosmos in the Palm of a Hand",
        "voice": "bm_george",
        "lang": "en-gb",
        "speed": 0.94,
        "lead_in": 0.16,
        "tail_out": 1.70,
        "plate": "plate_06_clockwork_cosmos.jpg",
        "scene_kind": "coda_blueprint",
        "display_text": (
            "Two thousand years on the seafloor dissolved its wooden frame and froze its axles in stone. "
            "Yet the prime numbers held—thirty bronze wheels proving that the sky itself obeys a law you can hold in your hands."
        ),
        "tts_text": (
            "Two thousand years on the seafloor dissolved its wooden frame and froze its axles in stone. "
            "Yet the prime numbers held: thirty bronze wheels proving that the sky itself obeys a law you can hold in your hands."
        ),
    },
]

#!/usr/bin/env python3
"""
25-shot documentary script, act metadata, dual-voice assignments, and scene specifications
for THE TEN-MINUTE ECLIPSE (praxinoscope entry for competitionvideo28).
Pass 0D locked master cut: 865 spoken words across 25 shots -> ~322s (05:22), inside 300-330s window.
"""

VOICE_NARRATOR = "en-US-BrianNeural"
VOICE_QUOTE = "en-GB-RyanNeural"
VOICE_RATE = "+9%"

SHOTS = [
    # ==================== ACT I: THE TEN-MINUTE BET (1676) ====================
    {
        "id": "S01",
        "act": "ACT I · THE TEN-MINUTE BET",
        "title": "Paris Observatory · November 9, 1676",
        "mode": "plate_hud",
        "plate": "plate_01_paris_observatory_1676.jpg",
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.32,
        "narration": (
            "At five twenty-five P.M. on November ninth, sixteen seventy-six, astronomers "
            "at the Paris Observatory aimed their telescopes at Jupiter. By the best tables "
            "on Earth, its innermost moon, Io, should have flashed out of shadow right then. "
            "Nothing happened."
        ),
    },
    {
        "id": "S02",
        "act": "ACT I · THE TEN-MINUTE BET",
        "title": "The Ten-Minute Silence (17:25:45 -> 17:35:45)",
        "mode": "plate_hud",
        "plate": "plate_02_jupiter_io_shadow.jpg",
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.32,
        "narration": (
            "Five minutes passed. Then nine. At five thirty-five and forty-five seconds, "
            "a golden spark emerged from Jupiter's shadow — ten minutes late. Yet eleven "
            "weeks earlier, Danish astronomer Ole Roemer had predicted that exact delay."
        ),
    },
    {
        "id": "S03",
        "act": "ACT I · THE TEN-MINUTE BET",
        "title": "Thesis: Catching a Finite Beam",
        "mode": "proc_title_card",
        "plate": None,
        "voice": VOICE_NARRATOR,
        "lead_in": 0.18,
        "tail_out": 0.34,
        "narration": (
            "Roemer's thesis defied two thousand years of physics: Io had not slowed down. "
            "Light itself was still crossing the solar system. This is how a moon of Jupiter "
            "and a toothed brass wheel over Paris caught the speed of light."
        ),
    },

    # ==================== ACT II: THE DOGMA OF INFINITE SPEED ====================
    {
        "id": "S04",
        "act": "ACT II · THE DOGMA OF INFINITE SPEED",
        "title": "Descartes' Ultimatum (August 1634)",
        "mode": "plate_hud",
        "plate": "plate_03_descartes_optics_manuscript.jpg",
        "voice": VOICE_QUOTE,
        "lead_in": 0.18,
        "tail_out": 0.34,
        "narration": (
            "From Aristotle to Rene Descartes, natural philosophy treated instantaneous "
            "light as sacred law. In sixteen thirty-four, Descartes wrote that if any time "
            "delay were ever detected in an eclipse, his entire philosophy would collapse."
        ),
    },
    {
        "id": "S05",
        "act": "ACT II · THE DOGMA OF INFINITE SPEED",
        "title": "Galileo's Shuttered Lanterns (1638)",
        "mode": "plate_hud",
        "plate": "plate_04_galileo_tuscan_lanterns.jpg",
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.32,
        "narration": (
            "Four years later, Galileo Galilei tried to test that claim. Two observers "
            "stood on Tuscan hilltops nearly a mile apart at night with shuttered lanterns, "
            "uncovering the second flame the instant the first spark appeared."
        ),
    },
    {
        "id": "S06",
        "act": "ACT II · THE DOGMA OF INFINITE SPEED",
        "title": "Why Terrestrial Baselines Failed (10.7 us vs 200,000 us)",
        "mode": "proc_galileo_reaction",
        "plate": None,
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.34,
        "narration": (
            "Galileo saw no lag, and the arithmetic shows why. A two-mile light trip takes "
            "ten point seven microseconds. A human thumb takes two hundred thousand "
            "microseconds to react — eighteen thousand times too slow."
        ),
    },

    # ==================== ACT III: THE SKY CLOCK & THE LONGITUDE PRIZE ====================
    {
        "id": "S07",
        "act": "ACT III · THE CELESTIAL CLOCK",
        "title": "The Maritime Longitude Crisis",
        "mode": "plate_hud",
        "plate": "plate_05_longitude_galleon_storm.jpg",
        "voice": VOICE_NARRATOR,
        "lead_in": 0.18,
        "tail_out": 0.32,
        "narration": (
            "Nobody in Paris set out to clock light. King Louis the Fourteenth built the "
            "observatory to solve longitude at sea. Because Earth turns fifteen degrees "
            "per hour, navigators needed reference time, and pendulum clocks failed on ships."
        ),
    },
    {
        "id": "S08",
        "act": "ACT III · THE CELESTIAL CLOCK",
        "title": "Io: The 42-Hour 28-Minute Sky Clock",
        "mode": "proc_galilean_clock",
        "plate": None,
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.32,
        "narration": (
            "So Galileo and Cassini used a clock in the sky. Jupiter's innermost moon, "
            "Io, orbits every forty-two hours and twenty-eight minutes — plunging into "
            "shadow like a universal timepiece visible across the globe."
        ),
    },
    {
        "id": "S09",
        "act": "ACT III · THE CELESTIAL CLOCK",
        "title": "Uraniborg to Paris & The Map That Shrank France",
        "mode": "plate_hud",
        "plate": "plate_06_uraniborg_hven_observatory.jpg",
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.34,
        "narration": (
            "In sixteen seventy-one, Jean Picard sailed to Tycho Brahe's ruined observatory "
            "on Hven and recruited young Ole Roemer to time Io's eclipses against Paris. "
            "Their sightings redrew France's coastline with unprecedented precision."
        ),
    },

    # ==================== ACT IV: THE GEOMETRY OF A MOVING EARTH ====================
    {
        "id": "S10",
        "act": "ACT IV · THE GEOMETRY OF A MOVING EARTH",
        "title": "Forty Eclipses That Refused to Keep Time (1668-1676)",
        "mode": "proc_France_and_ledger",
        "plate": None,
        "voice": VOICE_NARRATOR,
        "lead_in": 0.18,
        "tail_out": 0.32,
        "narration": (
            "In Paris, Roemer and Cassini analyzed forty eclipses of Io logged between "
            "sixteen sixty-eight and sixteen seventy-six. A stubborn anomaly stood out: "
            "for half the year Io arrived early; for the other half, it drifted late."
        ),
    },
    {
        "id": "S11",
        "act": "ACT IV · THE GEOMETRY OF A MOVING EARTH",
        "title": "Immersion (G->H) vs. Emersion (K->L) Shadow Geometry",
        "mode": "proc_orbital_solver",
        "plate": None,
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.32,
        "narration": (
            "Roemer traced the puzzle to Earth's orbit. Because Jupiter's shadow points away "
            "from the Sun, we see immersions at C while Earth approaches Jupiter along arc "
            "G to H, and emersions at D while Earth recedes along arc K to L."
        ),
    },
    {
        "id": "S12",
        "act": "ACT IV · THE GEOMETRY OF A MOVING EARTH",
        "title": "Accumulating Delay Across 40 Revolutions of Io",
        "mode": "proc_residual_curve",
        "plate": None,
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.32,
        "narration": (
            "Over a single orbit of Io, the extra light path adds barely fifteen seconds. "
            "But summed across forty consecutive orbits while Earth recedes from K to L, "
            "that growing distance compounds into the ten-minute delay of November ninth."
        ),
    },
    {
        "id": "S13",
        "act": "ACT IV · THE GEOMETRY OF A MOVING EARTH",
        "title": "Journal des Scavans (December 7, 1676)",
        "mode": "proc_roemer_1676_paper",
        "plate": None,
        "voice": VOICE_QUOTE,
        "lead_in": 0.18,
        "tail_out": 0.34,
        "narration": (
            "On December seventh, sixteen seventy-six, Roemer published his proof in the "
            "Journal des Scavans: light requires about eleven minutes to cross the radius "
            "of Earth's orbit, or twenty-two minutes across its full diameter."
        ),
    },

    # ==================== ACT V: 52 YEARS OF DOUBT & THE RAINDROP STAR ====================
    {
        "id": "S14",
        "act": "ACT V · FIFTY-TWO YEARS OF DOUBT",
        "title": "Huygens' First Numerical Speed (1690): ~214,000 km/s",
        "mode": "proc_huygens_calculation",
        "plate": None,
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.32,
        "narration": (
            "In sixteen ninety, Christiaan Huygens combined Roemer's twenty-two-minute "
            "delay with Cassini's solar distance to compute the first numerical speed of "
            "light: two hundred fourteen thousand kilometers per second."
        ),
    },
    {
        "id": "S15",
        "act": "ACT V · FIFTY-TWO YEARS OF DOUBT",
        "title": "Why Cassini & The French Academy Refused to Believe",
        "mode": "plate_hud",
        "plate": "plate_07_academie_royale_debate.jpg",
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.32,
        "narration": (
            "Isaac Newton embraced Roemer's proof, yet Cassini rejected it. Because "
            "Jupiter's three outer moons followed tilted orbits that lacked the same "
            "simple residual table, the Paris Academy doubted finite light speed for fifty-two years."
        ),
    },
    {
        "id": "S16",
        "act": "ACT V · FIFTY-TWO YEARS OF DOUBT",
        "title": "James Bradley's Chimney Telescope at Kew (1725-1728)",
        "mode": "plate_hud",
        "plate": "plate_08_bradley_kew_zenith_sector.jpg",
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.32,
        "narration": (
            "Vindication came in seventeen twenty-eight from English astronomer James Bradley. "
            "Sighting Gamma Draconis through a vertical telescope inside a chimney at Kew, "
            "Bradley saw the star shift south in March and north in September by twenty arcseconds."
        ),
    },
    {
        "id": "S17",
        "act": "ACT V · FIFTY-TWO YEARS OF DOUBT",
        "title": "Stellar Aberration: tan(20.49\") = v / c = 1 / 10,210",
        "mode": "proc_bradley_aberration",
        "plate": None,
        "voice": VOICE_QUOTE,
        "lead_in": 0.18,
        "tail_out": 0.34,
        "narration": (
            "Just as a moving boat tilts the apparent wind on a masthead vane, Earth's "
            "thirty-kilometer-per-second orbital motion tilts incoming starlight by one "
            "part in ten thousand two hundred ten — proving light takes eight minutes "
            "and twelve seconds from the Sun."
        ),
    },

    # ==================== ACT VI: THE 720-TOOTH WHEEL OVER PARIS (1849) ====================
    {
        "id": "S18",
        "act": "ACT VI · THE 720-TOOTH WHEEL OVER PARIS",
        "title": "Suresnes to Montmartre: 8,633 Meters Across Twilight Paris",
        "mode": "plate_hud",
        "plate": "plate_09_fizeau_suresnes_montmartre.jpg",
        "voice": VOICE_NARRATOR,
        "lead_in": 0.18,
        "tail_out": 0.32,
        "narration": (
            "Still, every proof relied on the heavens. Could human instruments clock light "
            "on Earth? In July eighteen forty-nine, Hippolyte Fizeau aimed a lantern from "
            "Suresnes to a mirror on Montmartre eight thousand six hundred thirty-three meters away."
        ),
    },
    {
        "id": "S19",
        "act": "ACT VI · THE 720-TOOTH WHEEL OVER PARIS",
        "title": "Inside Fizeau's 720-Tooth Brass Optical Chopper",
        "mode": "plate_hud",
        "plate": "plate_10_fizeau_720_tooth_wheel.jpg",
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.32,
        "narration": (
            "At the telescope's focus spun a brass wheel cut with seven hundred twenty "
            "square teeth and seven hundred twenty gaps. A beam flashed out through a gap, "
            "crossed eight point six kilometers to Montmartre, and reflected straight back."
        ),
    },
    {
        "id": "S20",
        "act": "ACT VI · THE 720-TOOTH WHEEL OVER PARIS",
        "title": "First Eclipse at 12.60 rps: 55.1 Microseconds in Flight",
        "mode": "proc_fizeau_wheel_eclipse",
        "plate": None,
        "voice": VOICE_QUOTE,
        "lead_in": 0.18,
        "tail_out": 0.34,
        "narration": (
            "As Fizeau spun the wheel to twelve point six revolutions per second, the "
            "seventeen-kilometer round trip took fifty-five microseconds — the exact time "
            "needed for the adjacent brass tooth to slide into place and eclipse the returning beam."
        ),
    },
    {
        "id": "S21",
        "act": "ACT VI · THE 720-TOOTH WHEEL OVER PARIS",
        "title": "Harmonic Verification: 25.2 rps Brightening & 37.8 rps 2nd Eclipse",
        "mode": "proc_fizeau_harmonics",
        "plate": None,
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.34,
        "narration": (
            "Doubling the spin to twenty-five point two revolutions let the returning "
            "pulse slip through the next gap. At thirty-seven point eight revolutions, "
            "the next tooth blocked it again — clocking light at three hundred fifteen "
            "thousand kilometers per second."
        ),
    },

    # ==================== ACT VII: THE RULER OF THE UNIVERSE ====================
    {
        "id": "S22",
        "act": "ACT VII · THE RULER OF THE UNIVERSE",
        "title": "Foucault (1862) & Michelson's Mount Wilson Octagon (1926)",
        "mode": "proc_michelson_octagon",
        "plate": None,
        "voice": VOICE_NARRATOR,
        "lead_in": 0.18,
        "tail_out": 0.32,
        "narration": (
            "Toothed wheels soon gave way to rotating mirrors. Leon Foucault measured two "
            "hundred ninety-eight thousand kilometers per second in eighteen sixty-two, "
            "and in nineteen twenty-six Albert Michelson bounced light thirty-five kilometers "
            "between California peaks."
        ),
    },
    {
        "id": "S23",
        "act": "ACT VII · THE RULER OF THE UNIVERSE",
        "title": "When the Speed of Light Outgrew the Meter Bar (1972-1983)",
        "mode": "proc_convergence_chart",
        "plate": None,
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.32,
        "narration": (
            "By nineteen seventy-two, stabilized lasers reduced the uncertainty to one point "
            "two meters per second. Physics hit a wall: our measurement of light's speed "
            "had become sharper than the definition of the meter itself."
        ),
    },
    {
        "id": "S24",
        "act": "ACT VII · THE RULER OF THE UNIVERSE",
        "title": "October 20, 1983: Fixing c = 299,792,458 m/s Exact",
        "mode": "proc_bipm_1983_meter",
        "plate": None,
        "voice": VOICE_NARRATOR,
        "lead_in": 0.16,
        "tail_out": 0.32,
        "narration": (
            "So on October twentieth, nineteen eighty-three, the General Conference on "
            "Weights and Measures flipped the definition forever: locking the speed of "
            "light at two hundred ninety-nine million, seven hundred ninety-two thousand, "
            "four hundred fifty-eight meters per second."
        ),
    },
    {
        "id": "S25",
        "act": "ACT VII · THE RULER OF THE UNIVERSE",
        "title": "Coda: From Io's Shadow to the Yardstick of Spacetime",
        "mode": "plate_coda",
        "plate": "plate_02_jupiter_io_shadow.jpg",
        "voice": VOICE_NARRATOR,
        "lead_in": 0.18,
        "tail_out": 0.65,
        "narration": (
            "Every time a GPS satellite locates your phone, or an antenna tracks a probe "
            "past Jupiter, we rely on the truth Ole Roemer uncovered in sixteen seventy-six: "
            "when a tiny moon emerged ten minutes late, and proved that looking into space "
            "is looking back through time."
        ),
    },
]

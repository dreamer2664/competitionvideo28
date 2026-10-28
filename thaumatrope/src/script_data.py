#!/usr/bin/env python3
"""
THE THIRTEEN-HOUR AVALANCHE — Canonical 24-Shot Script & Scene Metadata
Producer: thaumatrope
Target: ~750 spoken words (~5m 20s at natural documentary pace, 320s in [300s, 330s]).
Every factual assertion maps 1:1 to CLAIMS_AND_SOURCES.md.
"""

FILM_TITLE = "THE THIRTEEN-HOUR AVALANCHE"
FILM_SUBTITLE = "How 12 Broken Telegraph Cables Clocked a 600 km Deep-Sea Avalanche"
PRODUCER = "thaumatrope"
VOICE_NAME = "en-US-AndrewNeural"
VOICE_RATE = "+3%"

SHOTS = [
    # ACT I — THE HOOK
    {
        "id": "S01",
        "act": "ACT I · THE NIGHT THE ATLANTIC WENT SILENT",
        "mode": "plate_telegraph_hook",
        "plate": "plate_01_telegraph_room.jpg",
        "pause_after": 0.35,
        "narration": (
            "At 8:32 PM Universal Time on November 18, 1929, six transatlantic telegraph cables "
            "south of Newfoundland went dead at the exact same instant. An undersea earthquake had just struck."
        ),
    },
    {
        "id": "S02",
        "act": "ACT I · THE NIGHT THE ATLANTIC WENT SILENT",
        "mode": "map_teaser_countdown",
        "plate": None,
        "pause_after": 0.38,
        "narration": (
            "What baffled engineers was the next thirteen hours. Fifty-nine minutes after shaking stopped, "
            "a seventh cable snapped farther south. Three hours in, an eighth. At thirteen hours seventeen minutes, "
            "a twelfth tore apart five hundred kilometers offshore."
        ),
    },
    {
        "id": "S03",
        "act": "ACT I · THE NIGHT THE ATLANTIC WENT SILENT",
        "mode": "plate_title_reveal",
        "plate": "plate_02_abyssal_cable.jpg",
        "pause_after": 0.45,
        "narration": (
            "Something unseen had marched across the pitch-black Atlantic floor at highway speed, "
            "cutting steel lines one by one. For twenty-three years, nobody on Earth could prove what it was."
        ),
    },

    # ACT II — THE ACCIDENTAL INSTRUMENT
    {
        "id": "S04",
        "act": "ACT II · THE ACCIDENTAL INSTRUMENT",
        "mode": "corridor_map_1929",
        "plate": None,
        "pause_after": 0.35,
        "narration": (
            "In 1929, the seabed off Newfoundland was the busiest cable crossroads on Earth—linking "
            "North American stock markets and newsrooms directly to Europe."
        ),
    },
    {
        "id": "S05",
        "act": "ACT II · THE ACCIDENTAL INSTRUMENT",
        "mode": "cable_cross_section",
        "plate": None,
        "pause_after": 0.35,
        "narration": (
            "Each deep-sea cable was armored for the abyss: a stranded copper core, "
            "gutta-percha latex insulation, tanned jute, and galvanized steel wires."
        ),
    },
    {
        "id": "S06",
        "act": "ACT II · THE ACCIDENTAL INSTRUMENT",
        "mode": "wheatstone_fault_locator",
        "plate": None,
        "pause_after": 0.38,
        "narration": (
            "Automatic recorders stamped the exact minute any circuit failed. "
            "On shore, a Wheatstone bridge measured the surviving copper's electrical resistance—converting "
            "ohms straight into nautical miles to the break."
        ),
    },
    {
        "id": "S07",
        "act": "ACT II · THE ACCIDENTAL INSTRUMENT",
        "mode": "plate_burin_tragedy",
        "plate": "plate_03_burin_storm.jpg",
        "pause_after": 0.44,
        "narration": (
            "When that magnitude 7.2 quake shook the Grand Banks, it also sent a devastating tsunami "
            "onto Newfoundland's Burin Peninsula, claiming twenty-eight lives along Placentia Bay."
        ),
    },

    # ACT III — THE STOPWATCH ON THE SLOPE
    {
        "id": "S08",
        "act": "ACT III · THE STOPWATCH ON THE SLOPE",
        "mode": "plate_cable_ship_logs",
        "plate": "plate_04_cable_ship.jpg",
        "pause_after": 0.36,
        "narration": (
            "At sea, repair ships worked nearly a year grappling severed lines from three miles down. "
            "When hydrographer Vladimir de Smitt mapped all twenty-eight breaks across twelve cables, "
            "an extraordinary pattern emerged."
        ),
    },
    {
        "id": "S09",
        "act": "ACT III · THE STOPWATCH ON THE SLOPE",
        "mode": "slope_profile_instant",
        "plate": None,
        "pause_after": 0.36,
        "narration": (
            "Every cable on the shallow continental shelf stayed intact. "
            "Six cables on the steep continental slope around the epicenter failed simultaneously "
            "within sixty seconds, crushed by instant slumps."
        ),
    },
    {
        "id": "S10",
        "act": "ACT III · THE STOPWATCH ON THE SLOPE",
        "mode": "stopwatch_sequence_map",
        "plate": None,
        "pause_after": 0.45,
        "narration": (
            "Then six deeper cables snapped downslope in strict north-to-south order: "
            "fourteen minutes, fifty-nine minutes, three hours three minutes, nine hours one minute, "
            "ten hours eighteen, and thirteen hours seventeen minutes—nearly five thousand meters deep, "
            "where two hundred miles of wire vanished under sand."
        ),
    },

    # ACT IV — TWENTY-THREE YEARS OF WRONG ANSWERS
    {
        "id": "S11",
        "act": "ACT IV · TWENTY-THREE YEARS OF WRONG ANSWERS",
        "mode": "hypothesis_faults",
        "plate": None,
        "pause_after": 0.36,
        "narration": (
            "Why would steel cables break half a day after an earthquake stopped? "
            "In Nature, geologist J. W. Gregory blamed parallel faults unzipping southward. "
            "Yet seismographs recorded only two aftershocks—both back at the original epicenter."
        ),
    },
    {
        "id": "S12",
        "act": "ACT IV · TWENTY-THREE YEARS OF WRONG ANSWERS",
        "mode": "hypothesis_tsunami",
        "plate": None,
        "pause_after": 0.44,
        "narration": (
            "Others blamed wet silt weighing cables down, or erosion from the overhead tsunami. "
            "Physics ruled both out: the tsunami crossed the Atlantic ten times faster than the breaks. "
            "For two decades, the cold case stood unsolved."
        ),
    },

    # ACT V — MUD HEAVIER THAN WATER
    {
        "id": "S13",
        "act": "ACT V · MUD HEAVIER THAN WATER",
        "mode": "plate_kuenen_flume",
        "plate": "plate_06_kuenen_flume.jpg",
        "pause_after": 0.36,
        "narration": (
            "The key came from a glass flume in the Netherlands. "
            "Testing Reginald Daly's canyon hypothesis, Philip Kuenen released muddy slurries underwater—proving "
            "that sediment-heavy water plunges beneath clear water like a dense liquid avalanche."
        ),
    },
    {
        "id": "S14",
        "act": "ACT V · MUD HEAVIER THAN WATER",
        "mode": "plate_lamont_1952",
        "plate": "plate_08_lamont_drafting.jpg",
        "pause_after": 0.36,
        "narration": (
            "Still, skeptics doubted a tank experiment could span an ocean. "
            "Until December 1952, when Bruce Heezen and Maurice Ewing at Columbia's Lamont Observatory "
            "reopened those 1929 Western Union logs."
        ),
    },
    {
        "id": "S15",
        "act": "ACT V · MUD HEAVIER THAN WATER",
        "mode": "plate_slump_to_turbidity",
        "plate": "plate_05_continental_slump.jpg",
        "plate_secondary": "plate_07_turbidity_head.jpg",
        "pause_after": 0.36,
        "narration": (
            "They realized the six delayed cables were tripwires across an abyssal racetrack. "
            "Two hundred cubic kilometers of shaken slope mud had mixed with seawater into a roaring "
            "turbidity current hundreds of meters tall."
        ),
    },
    {
        "id": "S16",
        "act": "ACT V · MUD HEAVIER THAN WATER",
        "mode": "velocity_curve_1952",
        "plate": None,
        "pause_after": 0.44,
        "narration": (
            "Plotting cable distance against outage time turned broken wires into a speedometer. "
            "Heezen and Ewing calculated peak speeds near fifty knots, slowing to twelve on the plain—later "
            "refined in 1988 to sixty-seven kilometers an hour."
        ),
    },

    # ACT VI — THE CORE FROM THREE MILES DOWN
    {
        "id": "S17",
        "act": "ACT VI · THE CORE FROM THREE MILES DOWN",
        "mode": "plate_ship_coring",
        "plate": "plate_09_research_ship_core.jpg",
        "pause_after": 0.36,
        "narration": (
            "A bold reconstruction still needed physical proof. If the 1929 flow outran the southernmost cable, "
            "a fresh sheet of coastal sand had to lie out on the Sohm Abyssal Plain."
        ),
    },
    {
        "id": "S18",
        "act": "ACT VI · THE CORE FROM THREE MILES DOWN",
        "mode": "piston_core_graded_bed",
        "plate": None,
        "pause_after": 0.36,
        "narration": (
            "Lamont ships lowered steel piston corers more than three miles to the bottom. "
            "Atop ancient deep-sea clay sat a sharp graded bed of sand, pebbles, and shallow-water shells—dropped "
            "coarse-grains-first as the 1929 current slowed."
        ),
    },
    {
        "id": "S19",
        "act": "ACT VI · THE CORE FROM THREE MILES DOWN",
        "mode": "tharp_ocean_floor_map",
        "plate": None,
        "pause_after": 0.44,
        "narration": (
            "Beside Marie Tharp's pioneering ocean-floor maps, that core settled the debate. "
            "The abyss was not a stagnant tomb—it was a living landscape carved by canyons and submarine avalanches."
        ),
    },

    # ACT VII — THE FRAGILE FLOOR OF THE INTERNET
    {
        "id": "S20",
        "act": "ACT VII · THE FRAGILE FLOOR OF THE INTERNET",
        "mode": "plate_modern_fiber_stats",
        "plate": "plate_10_modern_fiber.jpg",
        "pause_after": 0.36,
        "narration": (
            "Today, that discovery protects the digital world. Over 1.8 million kilometers of garden-hose-thin "
            "fiber-optic cables cross the seafloor, carrying more than ninety-nine percent of intercontinental internet traffic."
        ),
    },
    {
        "id": "S21",
        "act": "ACT VII · THE FRAGILE FLOOR OF THE INTERNET",
        "mode": "hunga_tonga_2022_map",
        "plate": None,
        "pause_after": 0.36,
        "narration": (
            "And the same geohazard still strikes. On January 15, 2022, Hunga Tonga's eruption unleashed "
            "undersea volcanic currents reaching 122 kilometers an hour—the fastest seafloor flows ever recorded."
        ),
    },
    {
        "id": "S22",
        "act": "ACT VII · THE FRAGILE FLOOR OF THE INTERNET",
        "mode": "tonga_outage_comparison",
        "plate": None,
        "pause_after": 0.38,
        "narration": (
            "Once again, cables clocked the surge: Tonga's domestic line snapped at 4:30 AM, "
            "and its international fiber broke seventy-four minutes later—wrecking 194 kilometers of cable "
            "and isolating a nation for five weeks."
        ),
    },
    {
        "id": "S23",
        "act": "ACT VII · THE FRAGILE FLOOR OF THE INTERNET",
        "mode": "cable_engineering_lessons",
        "plate": None,
        "pause_after": 0.42,
        "narration": (
            "Armed with the lessons of 1929 and 2022, modern engineers map canyon chutes with multibeam sonar, "
            "detour around unstable slopes, and bury coastal crossings."
        ),
    },
    {
        "id": "S24",
        "act": "ACT VII · THE FRAGILE FLOOR OF THE INTERNET",
        "mode": "coda_abyssal_web",
        "plate": None,
        "pause_after": 2.20,
        "narration": (
            "Every packet of light crossing an ocean today rides on glass threads guarded by "
            "what twelve broken telegraph wires accidentally recorded on November 18, 1929—over "
            "thirteen hours and seventeen minutes."
        ),
    },
]

if __name__ == "__main__":
    words = sum(len(s["narration"].split()) for s in SHOTS)
    print(f"Shots: {len(SHOTS)} | Total spoken words: {words}")

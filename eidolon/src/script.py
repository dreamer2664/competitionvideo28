"""THE SIGNAL AT 37.5 — narration script.

One entry per beat. A beat is the smallest unit of the edit: one paragraph of
narration, one shot, one receipt. `visual` names the shot function in scenes.py.
`tail` is the silence held *after* the narration ends before the next beat starts.
"""

# Voice: British documentary narrator, slowed a touch. Cached audio lives in out/voice.
VOICE = "en-GB-RyanNeural"
RATE = "-4%"

BEATS = [
    # ---------------------------------------------------------------- ACT 0
    dict(id="b00", act="S0", visual="black_lede", tail=1.6,
         text="At sixteen minutes past ten, on the night of August fifteenth, "
              "nineteen seventy-seven, a radio telescope in Delaware, Ohio, was "
              "listening to a patch of sky in the constellation Sagittarius. It had "
              "no moving parts. It could not point. It could only wait for the Earth "
              "to turn, and drag the sky across its beam. For seventy-two seconds, "
              "something in that patch was thirty times louder than the noise around "
              "it. Then it was gone. It has never come back."),

    dict(id="b01", act="S0", visual="horizon", tail=1.8,
         text="This is the story of those seventy-two seconds: the machine that heard "
              "them, the page that recorded them, the three days it took for a human "
              "being to notice, and the half century of silence that followed."),

    dict(id="b02", act="S0", visual="title", tail=6.5, text=""),

    # ---------------------------------------------------------------- ACT 1
    dict(id="b03", act="S1", visual="schematic", tail=1.4,
         text="The instrument was called the Big Ear. It was built at Ohio State by "
              "John Kraus and his students, out of wire mesh: a flat reflector a "
              "hundred and four metres wide, tilted to bounce the sky onto a fixed "
              "paraboloid, a hundred and ten metres across, which focused it onto one "
              "of two feed horns. Two thousand two hundred square metres of "
              "collecting area: the sensitivity of a dish fifty-three metres wide."),

    dict(id="b04", act="S1", visual="beam", tail=1.4,
         text="It could not steer. It was a transit instrument: the sky drifted "
              "through its beam as the Earth turned, and at fourteen hundred and "
              "twenty megahertz that beam was about eight arcminutes wide, a little "
              "narrower than the full Moon. Which is where seventy-two seconds comes "
              "from. Any source in the sky crossed that beam in seventy-two seconds, "
              "sampled six times, twelve seconds apart. The telescope was not listening "
              "for a message. It was listening for a shape."),

    dict(id="b05", act="S1", visual="channels", tail=1.4,
         text="In nineteen seventy-three it became the world's first full-time SETI "
              "observatory. Fifty channels, each ten kilohertz wide, centred on "
              "fourteen twenty point four zero five eight megahertz: the emission "
              "line of neutral hydrogen, the most abundant atom in the universe, and "
              "the quietest, most obvious place in the radio spectrum to expect a "
              "deliberate signal."),

    # ---------------------------------------------------------------- ACT 2
    dict(id="b06", act="S2", visual="printout", tail=1.2,
         text="Every night, the telescope wrote itself down. A computer reduced each "
              "twelve-second sample to one character per channel: zero to nine for a "
              "quiet channel, then letters for anything louder. A for ten. B for "
              "eleven. All the way to Z, for thirty-five times the noise. The paper "
              "came off the printer in long fan-fold sheets, and every week, someone "
              "had to read them. By eye. Column by column. Row by row."),

    dict(id="b07", act="S2", visual="reader", tail=1.2,
         text="In the summer of nineteen seventy-seven, that someone was a volunteer "
              "named Jerry Ehman. He was not looking for aliens that week. He was "
              "doing what the project did every week: checking the instrument's paper "
              "for anything it should not have written down."),

    # ---------------------------------------------------------------- ACT 3
    dict(id="b08", act="S3", visual="column", tail=1.3,
         text="On the nineteenth of August, three days after the observation, he found "
              "one. In channel two of a single row, a column of characters did "
              "something the page had never done. Six. E. Q. U. J. Five. A rise, a "
              "peak, a fall: six samples, perfectly symmetrical, exactly the shape a "
              "fixed source should make as the Earth carried the telescope past it. "
              "The U meant between thirty and thirty-one times the background noise. "
              "Thirty sigma. In a project that argued about signals of three."),

    dict(id="b09", act="S3", visual="mark", tail=2.2,
         text="Ehman circled the six characters in red pen, and in the margin he wrote "
              "one word. Wow. It is three letters and an exclamation mark, and it is "
              "the most famous annotation in the history of radio astronomy."),

    # ---------------------------------------------------------------- ACT 4
    dict(id="b10", act="S4", visual="properties", tail=1.4,
         text="Three properties made it hard to wave away. One: the frequency. It sat "
              "within fifty kilohertz of the hydrogen line, in the narrow valley of "
              "the spectrum that astronomers call the water hole, the quiet gap "
              "between hydrogen and hydroxyl, where anyone, anywhere, might "
              "reasonably choose to broadcast. Two: the width. Natural radio sources "
              "are broad and messy; this one occupied a single channel out of fifty, "
              "less than ten kilohertz. Three: the shape. It rose and fell the way "
              "something in the sky behaves, not the way something on the ground does."),

    dict(id="b11", act="S4", visual="horns", tail=1.4,
         text="And one thing that did not fit. Big Ear had two feed horns, aimed at "
              "two points a fraction of a degree apart. A source in the sky should "
              "have appeared in both. Only one heard it. Whether that was a trick of "
              "the beam, a fault in the receiver, or something stranger has never "
              "been settled, and the only instrument that could have answered is gone."),

    # ---------------------------------------------------------------- ACT 5
    dict(id="b12", act="S5", visual="silence", tail=1.2,
         text="So they looked again. For years, John Kraus aimed the Big Ear back at "
              "the coordinates: dozens of attempts, then hundreds of hours across the "
              "following decades. Nothing. In nineteen ninety-eight the telescope was "
              "dismantled, and the land it stood on became a golf course. The "
              "instrument that heard the only signal it could not explain no longer "
              "exists."),

    dict(id="b13", act="S5", visual="modern", tail=1.2,
         text="Others kept looking. Arecibo, until it collapsed. Green Bank. The Very "
              "Large Array. The Allen Telescope Array, now sweeping millions of stars. "
              "All of them have returned the same thing: silence, at those "
              "coordinates, at that frequency, in every year we have pointed anything "
              "at that patch of Sagittarius."),

    dict(id="b14", act="S5", visual="hypotheses", tail=1.6,
         text="The explanations have grown clever. A reflection off a piece of "
              "orbiting debris. Interstellar scintillation, the galaxy bending the "
              "signal like a lens. In twenty sixteen, hydrogen clouds around two "
              "comets, until critics pointed out that the comets were not in the beam "
              "at the right time, and that the idea could not explain why one horn "
              "heard the signal and the other did not. Then, in twenty twenty-four, a "
              "serious candidate: cold clouds of hydrogen, briefly lit up by a "
              "magnetar flare, glowing like a maser at exactly the hydrogen line. The "
              "team found smaller, weaker cousins of the signal in old Arecibo data. "
              "Plausible. Not confirmed."),

    # ---------------------------------------------------------------- ACT 6
    dict(id="b15", act="S6", visual="coordinates", tail=1.4,
         text="Which leaves the coordinates: right ascension nineteen hours, "
              "twenty-five minutes; declination minus twenty-six degrees, "
              "fifty-seven minutes. Any dish on Earth can be pointed at them. Some "
              "still are, every year, by people who were not born when the paper came "
              "off the printer."),

    dict(id="b16", act="S6", visual="coda", tail=17.0,
         text="The Wow signal is not proof of anything. It is a receipt: one page, one "
              "column, one word in red ink, and seventy-two seconds we have never been "
              "able to repeat. It might be a natural phenomenon we do not yet "
              "understand. It might be a transmitter that spoke once, and stopped. The "
              "honest answer is the same in either case, and it is the reason the "
              "search continues: we do not know. For seventy-two seconds, the sky was "
              "loud. Everything since has been us, listening."),
]

ACTS = {
    "S0": ("I", "COLD OPEN"),
    "S1": ("II", "THE MACHINE"),
    "S2": ("III", "THE PRINT"),
    "S3": ("IV", "THE WORD"),
    "S4": ("V", "WHY IT MATTERED"),
    "S5": ("VI", "THE SILENCE"),
    "S6": ("VII", "CODA"),
}

# Scene labels used by the renderer to decide when to show an act card.
ACT_CARD_TEXT = {
    "S1": ("II", "THE MACHINE"),
    "S2": ("III", "THE PRINT"),
    "S3": ("IV", "THE WORD"),
    "S4": ("V", "WHY IT MATTERED"),
    "S5": ("VI", "THE SILENCE"),
    "S6": ("VII", "CODA"),
}

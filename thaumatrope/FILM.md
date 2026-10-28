# THE THIRTEEN-HOUR AVALANCHE — Treatment & Production Bible

> *At 20:32 UTC on November 18, 1929, six transatlantic telegraph cables snapped beneath the North Atlantic. Over the next thirteen hours and seventeen minutes, six more broke one by one across six hundred kilometers of pitch-black seabed. Twenty-three years later, those repair logs revealed that the deep ocean is carved by invisible avalanches faster than highway traffic.*

- **Producer:** `thaumatrope`
- **Target Runtime:** ~5:25 (325 seconds; strict requirement >= 300.0 s)
- **Master Spec:** 1920x1080p, 30 fps constant, H.264 (`yuv420p`), 48 kHz stereo AAC (192 kbps), mastered to -15.0 LUFS / <= -1.5 dBTP
- **Style:** Hybrid YouTube Documentary — bespoke painterly archival/oceanographic plates (`generate_image`, disclosed synthetic illustrations) fused with 30 fps procedural engineering diagrams, bathymetric stopwatch cartography, live velocity plotting, fluid-density physics animations, and original polyphonic ambient sound design.
- **One-Sentence Thesis:** Twelve severed telegraph cables in 1929 accidentally acted as a 600-kilometer stopwatch on the Atlantic floor, proving the existence of ocean-scale turbidity currents and revealing the underwater geohazard that still threatens 99% of global internet traffic today.

---

## 1. Narrative Structure & Retention Architecture (7 Acts, 24 Shots)

Every ~25-30 seconds opens a concrete physical puzzle and pays off the previous one:

| Act | Time Window | Retention Beat / Open Loop | Visual Modes |
|---|---|---|---|
| **I. The Hook** | `0:00 - 0:34` | **Frame 1 starts in motion (no fade/logo):** 20:32 UTC, Nov 18, 1929. Six cables die instantly; then for 13h 17m, six deeper cables snap one after another 355 nautical miles out to sea. Why didn't they break together? | Bespoke telegraph room plate + live 13h17m outage ticker + Atlantic overview map |
| **II. The Accidental Instrument** | `0:34 - 1:22` | How could 1929 engineers sitting on land know *where* a wire broke 4,000 m underwater? Inside the gutta-percha armored cable + Wheatstone bridge resistance fault-location (`ohms per nautical mile`), plus the human tragedy on Newfoundland's Burin Peninsula (Mw 7.2 quake & tsunami, 28 lives lost). | Procedural 4-layer cable cross-section + animated Wheatstone bridge circuit + Newfoundland archival-style plate |
| **III. The Stopwatch on the Slope** | `1:22 - 2:18` | Plotting Doxsee (1948) & de Smitt (1932) Table 1 data: shelf cables 100% intact; slope cables A-F break at `00:00`; downslope cables G (`+00:14`), H (`+00:59`), I (`+03:03`), J (`+09:01`), K (`+10:18`), L (`+13:17`) snap across 2,800+ fathoms, burying 100-200 miles of armored wire. | Animated North Atlantic bathymetric stopwatch map + live telegraph tape strip |
| **IV. Twenty-Three Years of Wrong Answers** | `2:18 - 3:02` | Why top geologists failed for two decades: J.W. Gregory's (1929) parallel fault-graben theory vs seismographs (only 2 aftershocks, both at original epicenter); Hodgson & Doxsee's (1930) silt-sagging idea; W.H. Bucher's (1940) tsunami erosion theory (tsunami moved 10x too fast). | Editorial hypothesis board with animated physics refutations & seismogram comparison |
| **V. Mud Heavier Than Water** | `3:02 - 4:02` | Reginald Daly's canyon hunch, Philip Kuenen's Groningen glass-flume experiments, and Bruce Heezen & Maurice Ewing's Dec 1952 breakthrough at Columbia's Lamont Observatory: an 80x150 mi slope slump mixing into a self-accelerating **turbidity current** (`50 knots` / ~93 km/h initial estimate; `67 km/h` / `19 m/s` in Piper et al. 1988 reanalysis). | Procedural density-current flume simulation + Heezen & Ewing (1952) Fig. 2/3 live velocity-distance curve |
| **VI. The Core From Three Miles Down** | `4:02 - 4:44` | A scientific theory must predict something unseen. Lamont & Marie Tharp's seafloor mapping era: lowering piston corers onto the flat Sohm Abyssal Plain and pulling up the smoking gun — sharp shallow-water sand, pebbles, and shelf microfossils stacked in a textbook **graded turbidite bed** 400+ miles from shore. | Lamont cartography plate + animated 5,000 m piston-core extraction & graded-bed grain magnification |
| **VII. The Fragile Floor of the Internet** | `4:44 - 5:25` | Payoff in our own world: copper Morse wires are now **>1.8 million km of garden-hose-thin fiber-optic cables carrying >99% of intercontinental data**. On Jan 15, 2022, Hunga Tonga's eruption triggered **122 km/h**海底 volcaniclastic density currents (Clare et al., *Science* 2023), severing 194 km of cable at `04:30` and `05:44`. | Copper-to-fiber scale comparison + Hunga Tonga 2022 seafloor scour telemetry + resonant closing frame |

---

## 2. Visual & Audio Engineering Standards

1. **Zero Overlap Layout:**
   - Primary visual canvas & telemetry occupy `y = 0..910`.
   - Dedicated lower-bottom caption bar occupies `y = 925..1045` (max 2 lines, <=42 chars/line, high-contrast ivory on obsidian pill, synchronized to exact narration timing, accompanied by standalone `.srt`, `.vtt`, and `.txt` transcripts).
2. **Authentic Data Geometry:**
   - Every coordinate, fathom depth, and break interval in the map and chart scenes comes directly from **Heezen & Ewing (1952), Table 1 & Fig. 3** (*American Journal of Science*, Vol. 250, pp. 849-873) and **Clare et al. (2023)** (*Science*, 381, 1085-1090).
3. **Broadcast Sound Mix:**
   - Neural documentary narration (`en-US-AndrewNeural` / `en-US-BrianNeural` auditioned for natural prosody and crisp technical pronunciation) segmented per shot for frame-accurate pacing.
   - Original procedural stereo ambient score (warm sub-bass oceanic pedal, muted felt-piano/bell harmonics, subtle telegraph relay clicks on break timestamps, low hydrophone rumble during the slump) sidechain-ducked `-22 dB` under voice, EBU R128 loudness normalized to **-15.0 LUFS** (`true peak <= -1.5 dBTP`), zero dead air > 0.7 s.

---

## 3. Primary Sources (Preview — Full Claim Ledger in `CLAIMS_AND_SOURCES.md`)

1. **Heezen, B. C., & Ewing, M. (1952).** *Turbidity currents and submarine slumps, and the 1929 Grand Banks earthquake.* American Journal of Science, 250(12), 849-873. https://gwern.net/doc/technology/1952-heezen.pdf
2. **Piper, D. J. W., Shor, A. N., & Hughes Clarke, J. E. (1988).** *The 1929 "Grand Banks" earthquake, slump, and turbidity current.* Geological Society of America Special Paper 229, 77-92 (velocity refinement to ~67 km/h / 19 m/s).
3. **Fine, I. V., Rabinovich, A. B., Bornhold, B. D., Thomson, R. E., & Kulikov, E. A. (2005).** *The Grand Banks landslide-generated tsunami of November 18, 1929: preliminary analysis and numerical modeling.* Marine Geology, 215(1-2), 45-57. https://www.sciencedirect.com/science/article/abs/pii/S002532270400324X
4. **Heezen, B. C., Ericson, D. B., & Ewing, M. (1954).** *Further evidence for a turbidity current following the 1929 Grand Banks earthquake.* Deep-Sea Research, 1(4), 193-202; and **Heezen, Tharp & Ewing (1959)**, GSA Special Paper 65 (*The Floors of the Oceans*). https://www.gutenberg.org/files/49069/49069-h/49069-h.htm
5. **Clare, M. A., Yeo, I. A., Watson, S., et al. (2023).** *Fast and destructive density currents created by ocean-entering volcanic eruptions.* Science, 381(6662), 1085-1090 (Hunga Tonga 122 km/h volcaniclastic currents, 194 km cable damage). https://www.science.org/doi/10.1126/science.adi3038
6. **International Cable Protection Committee (ICPC, Nov 2025) & UN News (Feb 2026).** *Submarine Cable Protection and the Environment* (>1.8 million km of submarine fiber-optic cables carrying >99% of international digital data). https://www.iscpc.org/publications/submarine-cable-protection-and-the-environment/ICPC_Public_EU_November_2025.pdf

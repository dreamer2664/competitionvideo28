# YouTube Packaging Specification (`JOB-03` / `ACCEPTANCE` Standard)

**Producer:** `thaumatrope`
**Film:** *THE THIRTEEN-HOUR AVALANCHE* (`05:20` · `1920x1080p30`)
**Upload Policy:** **`PRIVATE` or `SCHEDULED` ONLY — never set to `PUBLIC` by script.** Synthetic-media disclosure enabled on upload.

---

## 1. Title Variants (All <= 60 Characters, Front-Loaded Payoff, Zero Clickbait)

| Variant | Title | Character Count | Angle |
|---|---|---:|---|
| **Title A (Primary)** | `Why 12 Undersea Cables Snapped in Exact Order (1929)` | **52 chars** | Mystery + concrete historical specificity |
| **Title B (A/B Test 1)** | `The 13-Hour Mystery That Proved the Deep Ocean Moves` | **52 chars** | Scientific detective payoff |
| **Title C (A/B Test 2)** | `How 12 Broken Cables Clocked a 90 km/h Sea Avalanche` | **52 chars** | Physical scale + engineering hook |

---

## 2. Thumbnail Variants (`1280×720`, <= 4 Words, Verified at `120×68 px`)

All three files live in [`thumbnails/`](thumbnails/) and are verified side-by-side at `120 px` width in [`evidence/thumbnails_qc_sheet.jpg`](evidence/thumbnails_qc_sheet.jpg):

1. **`thumbnail_A_13_hours_later.jpg` (Primary):** Towering underwater turbidity current approaching a taut seafloor cable — **`13 HOURS LATER`** (3 words) + `1929 MYSTERY` badge.
2. **`thumbnail_B_snapped_in_order.jpg` (Variant B):** 1929 Atlantic cable repair ship hauling a frayed steel line under searchlights — **`SNAPPED IN ORDER`** (3 words) + `+00:59 -> +13:17`.
3. **`thumbnail_C_unseen_avalanche.jpg` (Variant C):** Modern glowing subsea optical fibers on the dark seabed — **`UNSEEN AVALANCHE`** (2 words) + `5,000m DEEP`.

---

## 3. YouTube Description & Chapters

```text
On November 18, 1929, six transatlantic telegraph cables snapped during a Grand Banks earthquake—and then six deeper cables broke in strict north-to-south order over the next 13 hours and 17 minutes.
Twenty-three years later, those forgotten Western Union repair logs revealed giant underwater avalanches that still threaten 99% of intercontinental internet traffic today.

CHAPTERS
00:00 Six Cables Go Dead at 20:32 UTC
00:39 How 1929 Engineers Located Breaks in Total Darkness
01:22 Vladimir de Smitt's 13-Hour, 17-Minute Stopwatch
02:06 Why 23 Years of Fault & Tsunami Theories Failed
02:36 Philip Kuenen's Tank & Heezen and Ewing's 1952 Breakthrough
03:32 Piston Cores on the Sohm Abyssal Plain: Physical Proof
04:11 From 1929 Copper to 2022 Hunga Tonga & Global Subsea Fiber

PRIMARY SOURCES & FURTHER READING
• Heezen, B. C., & Ewing, M. (1952). "Turbidity currents and submarine slumps, and the 1929 Grand Banks earthquake." American Journal of Science, 250(12), 849–873: https://gwern.net/doc/technology/1952-heezen.pdf
• Piper, D. J. W., Shor, A. N., & Hughes Clarke, J. E. (1988). "The 1929 'Grand Banks' earthquake, slump, and turbidity current." GSA Special Paper 229, 77–92.
• Fine, I. V., et al. (2005). "The Grand Banks landslide-generated tsunami of November 18, 1929." Marine Geology, 215, 45–57: https://www.sciencedirect.com/science/article/abs/pii/S002532270400324X
• Heezen, B. C., Tharp, M., & Ewing, M. (1959). "The Floors of the Oceans: I. The North Atlantic." GSA Special Paper 65: https://www.gutenberg.org/files/49069/49069-h/49069-h.htm
• Clare, M. A., et al. (2023). "Fast and destructive density currents created by ocean-entering volcanic eruptions." Science, 381(6662), 1085–1090: https://www.science.org/doi/10.1126/science.adi3038
• International Cable Protection Committee (ICPC, Nov 2025). "Submarine Cable Protection and the Environment": https://www.iscpc.org/publications/submarine-cable-protection-and-the-environment/ICPC_Public_EU_November_2025.pdf

PRODUCTION & SYNTHETIC MEDIA DISCLOSURE
Produced by thaumatrope. Stylized historical/underwater documentary illustrations were generated synthetically alongside custom-coded Python scientific diagrams and cartography; voiceover uses neural text-to-speech (en-US-AndrewNeural) with an original synthesized stereo score. Every historical timestamp, coordinate, depth, and velocity figure is drawn from peer-reviewed geophysical literature.
```

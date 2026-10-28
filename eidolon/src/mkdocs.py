"""Generate SCRIPT.md from the actual timeline (never hand-typed timecodes)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script import BEATS, ACTS, VOICE, RATE

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TL = json.load(open(os.path.join(ROOT, "out", "timeline.json")))
by_id = {b["id"]: b for b in TL["beats"]}


def tc(x):
    return f"{int(x//60)}:{int(x%60):02d}"


lines = ["# THE SIGNAL AT 37.5 — narration script",
         "",
         f"Voice: `{VOICE}` at `{RATE}` · generated from `src/script.py` and the real",
         "timeline (`src/timeline.py`), so every timecode below is the one in the master.",
         "",
         f"**Runtime:** {tc(TL['total'])} · **Beats:** {len(BEATS)} · "
         f"**Captions:** {len(TL['captions'])}",
         ""]
for act in TL["acts"]:
    lines += ["---", "", f"## {act['numeral']} · {act['title'].title()} — "
              f"{tc(act['start'])} → {tc(act['end'])}", ""]
    for b in TL["beats"]:
        if b["act"] != act["id"]:
            continue
        spec = by_id[b["id"]]
        if not b["words"]:
            lines.append(f"**{tc(b['start'])} — title card** (no narration) `{b['visual']}`")
            lines.append("")
            continue
        lines.append(f"**{tc(b['start'])} — shot `{b['visual']}` · "
                     f"{b['narration']:.1f} s of narration**")
        lines.append("")
        lines.append("> " + " ".join(w["w"] for w in b["words"]))
        lines.append("")
open(os.path.join(ROOT, "SCRIPT.md"), "w").write("\n".join(lines))
print("SCRIPT.md written", len(lines), "lines")

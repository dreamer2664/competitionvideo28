"""Build the edit: beat starts, act boundaries, caption lines, SRT.

Everything downstream (score, frames, captions, subtitles) reads timeline.json, so
the film can be re-cut without touching the visuals or the narration.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script import ACTS, BEATS  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "out")
VOICE = os.path.join(OUT, "voice")

MAX_CHARS = 50          # caption line budget
MAX_LEAD = 0.35         # how long a caption may sit before its first word is spoken


def load_beat(beat):
    """The TTS boundary stream carries the timings but strips punctuation, so the
    displayed words come from the script and only the clock comes from the audio.
    The two token streams are 1:1 for every beat (asserted here, not assumed)."""
    p = os.path.join(VOICE, beat["id"] + ".json")
    if not beat["text"]:
        return {"duration": 0.0, "words": []}
    v = json.load(open(p))
    spoken = beat["text"].split()
    assert len(spoken) == len(v["words"]), (beat["id"], len(spoken), len(v["words"]))
    for w, s in zip(v["words"], spoken):
        w["w"] = s
    return v


def build():
    beats, t = [], 0.0
    for b in BEATS:
        v = load_beat(b)
        dur = round(v["duration"], 3)
        tail = b["tail"]
        start = round(t, 3)
        end = round(start + dur + tail, 3)
        beats.append(dict(id=b["id"], act=b["act"], visual=b["visual"],
                          start=start, narration=dur, end=end,
                          words=[dict(w=w["w"], t=round(start + w["t"], 3),
                                      d=round(w["d"], 3)) for w in v["words"]]))
        t = end

    # act spans
    acts = []
    for bid in dict.fromkeys(b["act"] for b in beats):
        bs = [b for b in beats if b["act"] == bid]
        acts.append(dict(id=bid, numeral=ACTS[bid][0], title=ACTS[bid][1],
                         start=bs[0]["start"], end=bs[-1]["end"]))

    # captions: break on sentence punctuation, then on length
    caps = []
    for b in beats:
        cur = []
        for w in b["words"]:
            cur.append(w)
            text = " ".join(x["w"] for x in cur)
            ends_sentence = bool(re.search(r"[.!?\"”]$", w["w"])) and len(cur) >= 3
            clause = bool(re.search(r"[,;:—]$", w["w"])) and len(text) >= 40
            too_long = len(text) >= MAX_CHARS
            if ends_sentence or clause or too_long:
                caps.append(cur)
                cur = []
        if cur:
            caps.append(cur)

    lines = []
    for i, words in enumerate(caps):
        st = max(0.0, words[0]["t"] - MAX_LEAD)
        en = words[-1]["t"] + words[-1]["d"] + 0.45
        if i + 1 < len(caps):
            en = min(en, caps[i + 1][0]["t"] - 0.05)
        lines.append(dict(start=round(st, 2), end=round(en, 2),
                          words=words,
                          text=" ".join(w["w"] for w in words)))

    # never let a caption outlive its beat by much
    tl = dict(total=round(t, 3), fps=30, width=1920, height=1080,
              beats=beats, acts=acts, captions=lines)
    os.makedirs(OUT, exist_ok=True)
    json.dump(tl, open(os.path.join(OUT, "timeline.json"), "w"), indent=1)
    write_srt(lines, os.path.join(OUT, "captions.srt"))
    return tl


def ts(x, comma=True):
    h = int(x // 3600); m = int(x % 3600 // 60); s = int(x % 60)
    ms = int(round((x - int(x)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d}{',' if comma else '.'}{ms:03d}"


def write_srt(lines, path):
    out = []
    for i, ln in enumerate(lines, 1):
        out.append(f"{i}\n{ts(ln['start'])} --> {ts(ln['end'])}\n{ln['text']}\n")
    open(path, "w").write("\n".join(out))


if __name__ == "__main__":
    tl = build()
    print(f"total {tl['total']:.1f}s = {int(tl['total']//60)}:{tl['total']%60:04.1f}"
          f" · {len(tl['beats'])} beats · {len(tl['acts'])} acts · {len(tl['captions'])} captions")
    for a in tl["acts"]:
        print(f"  {a['id']} {a['numeral']:>4} {a['title']:<16} {a['start']:7.1f} → {a['end']:7.1f}")

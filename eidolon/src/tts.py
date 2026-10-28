"""Narration synthesis with word-level timing.

Each beat is synthesised on its own so the edit can breathe between paragraphs and
so a single re-write never invalidates the whole film. The word boundaries come
from the same stream as the audio, which is what makes the captions exact rather
than estimated.
"""
import asyncio
import json
import os
import subprocess
import sys

import edge_tts

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script import BEATS, VOICE, RATE  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "out", "voice")


def probe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())


async def one(beat):
    mp3 = os.path.join(OUT, beat["id"] + ".mp3")
    js = os.path.join(OUT, beat["id"] + ".json")
    if os.path.exists(mp3) and os.path.exists(js):
        return json.load(open(js))
    words = []
    with open(mp3 + ".part", "wb") as f:
        comm = edge_tts.Communicate(beat["text"], VOICE, rate=RATE, boundary="WordBoundary")
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({
                    "t": chunk["offset"] / 1e7,
                    "d": chunk["duration"] / 1e7,
                    "w": chunk["text"],
                })
    os.replace(mp3 + ".part", mp3)
    data = {"id": beat["id"], "mp3": os.path.basename(mp3),
            "duration": round(probe_duration(mp3), 3), "words": words}
    json.dump(data, open(js, "w"), indent=1)
    return data


async def main():
    os.makedirs(OUT, exist_ok=True)
    total = 0.0
    for beat in BEATS:
        if not beat["text"]:
            continue
        d = await one(beat)
        total += d["duration"] + beat["tail"]
        print(f"  {beat['id']}  {d['duration']:6.2f}s  {len(d['words']):3d} words  "
              f"{beat['text'][:52]}…")
    print(f"\nnarration+tails total: {total/60:.2f} min ({total:.1f}s)")


if __name__ == "__main__":
    asyncio.run(main())

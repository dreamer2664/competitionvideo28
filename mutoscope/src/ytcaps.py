"""
ytcaps — turn YouTube's json3 auto-caption dump into word-level cues.

json3 carries per-word offsets (`segs[].tOffsetMs`) which is exactly what a
karaoke caption needs; the .srt export throws that away, so we read json3.

Auto-captions are lowercase and unpunctuated, which is actually what we want:
the caption style is SHOUTED UPPERCASE anyway.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass


@dataclass
class Word:
    t: float        # start, seconds
    d: float        # duration, seconds
    text: str

    @property
    def end(self) -> float:
        return self.t + self.d


# yt auto-caption artefacts we never want on screen
_NOISE = {"[music]", "[applause]", "[laughter]", "[__]", "&gt;&gt;", ">>"}


def load_words(path: str) -> list[Word]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    words: list[Word] = []
    for ev in data.get("events", []):
        segs = ev.get("segs")
        if not segs:
            continue
        base = ev.get("tStartMs", 0) / 1000.0
        # json3 repeats a rolling window; dDurationMs==0 rows are duplicates
        for s in segs:
            raw = s.get("utf8", "")
            txt = raw.strip()
            if not txt or txt in _NOISE:
                continue
            if txt.startswith("[") and txt.endswith("]"):
                continue
            t = base + s.get("tOffsetMs", 0) / 1000.0
            words.append(Word(t=t, d=0.0, text=txt))
    words.sort(key=lambda w: w.t)

    # de-duplicate the rolling window: same text at (almost) the same time
    out: list[Word] = []
    for w in words:
        if out and out[-1].text == w.text and abs(out[-1].t - w.t) < 0.08:
            continue
        out.append(w)

    # infer durations from the next word, clamped to something readable
    for i, w in enumerate(out):
        nxt = out[i + 1].t if i + 1 < len(out) else w.t + 0.4
        w.d = max(0.12, min(nxt - w.t, 1.1))
    return out


def words_in(words: list[Word], t0: float, t1: float) -> list[Word]:
    return [Word(w.t - t0, w.d, w.text) for w in words if t0 <= w.t < t1]


_CLEAN = re.compile(r"[^\w'\- ]+", re.UNICODE)


def phrase(words: list[Word], t0: float, t1: float) -> str:
    return " ".join(w.text for w in words if t0 <= w.t < t1)


def group_cues(words: list[Word], max_words: int = 3, max_chars: int = 22,
               max_gap: float = 0.62) -> list[tuple[float, float, str]]:
    """Clump words into 1-3 word caption cues, the way the reference shorts do.

    A cue breaks on a pause, on length, or on a natural beat word.
    """
    cues: list[tuple[float, float, str]] = []
    buf: list[Word] = []

    def flush():
        if not buf:
            return
        txt = " ".join(w.text for w in buf).upper()
        txt = _CLEAN.sub("", txt).strip()
        if txt:
            cues.append((buf[0].t, max(buf[-1].end, buf[0].t + 0.30), txt))
        buf.clear()

    for w in words:
        if buf:
            gap = w.t - buf[-1].end
            cand = " ".join(x.text for x in buf) + " " + w.text
            if gap > max_gap or len(buf) >= max_words or len(cand) > max_chars:
                flush()
        buf.append(w)
    flush()

    # never let a cue outlive its welcome or overlap the next one
    for i in range(len(cues) - 1):
        t0, t1, tx = cues[i]
        cues[i] = (t0, min(t1, cues[i + 1][0]), tx)
    return [(a, b, c) for a, b, c in cues if b > a + 0.08]

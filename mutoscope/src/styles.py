"""
styles — the two looks MUTOSCOPE ships.

`normal_track`      : the punchy single-moment short (reference: eUFkorW-1kk)
                      full-bleed footage, 1-3 word karaoke captions in yellow/cyan
                      with a fat black outline, emoji stabs, punch-in flashes.

`leaderboard_track` : the ranked multi-clip short (references: OFsD_2UbGp4,
                      fRMc1LlCykM) — a white title bar, a 5-row ranking down the
                      left that fills in as each clip plays, a #N stamp on every
                      entry, counting down to #1.

Both return a `Track` of sprites plus the SFX event list that goes with it, so the
sound is authored with the picture rather than sprinkled on afterwards.
"""

from __future__ import annotations

import random

from PIL import Image, ImageDraw

from vidkit import (BLACK, CYAN, GREEN, H, INK, ORANGE, RED, W, WHITE, YELLOW,
                    Flash, ProgressBar, Sprite, Track, caption_tile, draw_rich,
                    ease_out_back, ease_out_cubic, font, measure, rounded_panel,
                    vertical_scrim)

# Words worth shouting in a different colour.
HYPE = {
    "no", "nooo", "noo", "what", "whattt", "bro", "oh", "ohh", "stop", "wait",
    "dead", "crazy", "insane", "nah", "yo", "damn", "god", "help", "run", "wtf",
    "never", "best", "worst", "fire", "actually", "literally", "bruh", "hell",
    "scared", "screaming", "dying", "lost", "won", "win", "lose", "beat",
}

CAPTION_Y_COVER = 1255
CAPTION_Y_FIT = 1330


def _is_hype(txt: str) -> bool:
    low = txt.lower().strip("!?.,")
    return any(w in HYPE for w in low.split())


def _caption_sprites(track: Track, cues, y: int, size: int = 104,
                     sfx: list | None = None, accent_every: int = 3):
    """Word-group karaoke captions with a snap-in pop on every cue."""
    for i, (t0, t1, txt) in enumerate(cues):
        hype = _is_hype(txt)
        fill = RED if hype and i % 2 == 0 else (CYAN if i % accent_every == 2 else YELLOW)
        sz = int(size * (1.14 if hype else 1.0))
        tile = caption_tile(txt, size=sz, face="anton", fill=fill, stroke=max(10, sz // 9))
        track.add(Sprite(tile, W // 2, y, t0, max(t1, t0 + 0.22),
                         pop=0.13, fade_out=0.06,
                         shake=1.6 if hype else 0.0))
        if sfx is not None and i % 2 == 0:
            sfx.append((t0, "click", 0.17))


def _progress_bar(track: Track, duration: float, color=YELLOW, y: int = H - 14):
    """A thin fill at the very bottom — reads as 'almost over, keep watching'."""
    track.add(ProgressBar(duration, color[:3], y))


def _watermark(track: Track, duration: float, handle: str = "@mutoscope",
               pos: str = "tr"):
    """Top-right for the normal style; bottom-left when a title bar owns the top."""
    tile = caption_tile(handle, size=36, face="xbold", fill=(255, 255, 255, 170),
                        stroke=5, shadow=False)
    if pos == "tr":
        cx, cy = W - tile.width // 2 - 30, 60
    else:
        cx, cy = tile.width // 2 + 34, H - 70
    track.add(Sprite(tile, cx, cy, 0.0, duration, pop=0.0, opacity=0.75))


# --------------------------------------------------------------------------- #
# normal
# --------------------------------------------------------------------------- #

def normal_track(duration: float, cues, hook: str, hook_emoji: str,
                 beats: list[float], mode: str, emoji_stabs: list[tuple[float, str]],
                 end_card: str | None = None, seed: int = 0):
    """Build the overlay + SFX for a single-moment short."""
    rnd = random.Random(seed)
    tr = Track(duration)
    sfx: list[tuple[float, str, float]] = []

    cap_y = CAPTION_Y_COVER if mode == "cover" else CAPTION_Y_FIT

    # top scrim keeps the hook legible over bright footage
    tr.add_static(vertical_scrim(330, top_alpha=165, bottom_alpha=0), 0, 0)
    tr.add_static(vertical_scrim(300, top_alpha=0, bottom_alpha=140), 0, H - 300)

    # --- hook ------------------------------------------------------------- #
    hook_txt = f"{hook} {hook_emoji}".strip()
    hook_tile = caption_tile(hook_txt, size=86, face="black", fill=WHITE, stroke=11,
                             max_w=900)
    hook_dur = min(3.1, duration * 0.42)
    tr.add(Sprite(hook_tile, W // 2, 205, 0.05, hook_dur, pop=0.26, fade_out=0.3))
    sfx.append((0.02, "swoosh_rev", 0.55))
    sfx.append((0.30, "ding", 0.38))

    # --- captions ----------------------------------------------------------- #
    _caption_sprites(tr, cues, cap_y, size=104, sfx=sfx)

    # --- beats: flash + boom + shake ----------------------------------------- #
    for b in beats:
        if b < 0.15 or b > duration - 0.25:
            continue
        tr.add(Flash(b, b + 0.16, (255, 255, 255), 0.40))
        sfx.append((b, "boom", 0.62))
        sfx.append((b, "impact", 0.30))

    # --- emoji stabs ---------------------------------------------------------- #
    for t, emo in emoji_stabs:
        if t > duration - 0.4:
            continue
        size = rnd.choice([190, 215, 240])
        tile = caption_tile(emo, size=size, face="anton", fill=WHITE, stroke=0,
                            shadow=True)
        side = rnd.choice([0, 1])
        cx = rnd.randint(190, 330) if side == 0 else rnd.randint(W - 330, W - 190)
        cy = rnd.randint(640, 980)
        rot = rnd.uniform(-16, 16)
        tile = tile.rotate(rot, expand=True, resample=Image.BICUBIC)
        tr.add(Sprite(tile, cx, cy, t, min(t + 1.25, duration), pop=0.22,
                      fade_out=0.35, drift=(0, -26)))
        sfx.append((t, rnd.choice(["pop", "sparkle", "ding"]), 0.34))

    # --- end card -------------------------------------------------------------- #
    if end_card and duration > 4:
        et = duration - min(2.0, duration * 0.18)
        tile = caption_tile(end_card, size=78, face="black", fill=YELLOW, stroke=11,
                            max_w=880)
        tr.add(Sprite(tile, W // 2, H - 430, et, duration, pop=0.3))
        sfx.append((et, "whoosh", 0.4))

    _progress_bar(tr, duration)
    _watermark(tr, duration)
    sfx.append((0.0, "whoosh", 0.45))
    return tr, sfx


# --------------------------------------------------------------------------- #
# leaderboard
# --------------------------------------------------------------------------- #

def _header_tile(title_parts: list[tuple[str, tuple]], sub: str) -> Image.Image:
    """White title bar; `title_parts` is [(text, colour), ...] so one word can pop."""
    pad_x, pad_y = 34, 20
    f_title = font("anton", 62)
    f_sub = font("xbold", 27)

    # wrap into at most two lines by greedy fill
    lines: list[list[tuple[str, tuple]]] = [[]]
    cur_w = 0
    limit = W - pad_x * 2 - 20
    for text, col in title_parts:
        for wd in text.split():
            wdw = int(f_title.getlength(wd + " "))
            if cur_w + wdw > limit and lines[-1]:
                lines.append([])
                cur_w = 0
            lines[-1].append((wd, col))
            cur_w += wdw

    lh = 70
    h = pad_y * 2 + lh * len(lines) + 40
    img = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, -40, W, h - 14], radius=34, fill=(255, 255, 255, 248))

    for li, line in enumerate(lines):
        total = sum(int(f_title.getlength(wd + " ")) for wd, _ in line)
        x = (W - total) // 2
        y = pad_y + li * lh
        for wd, col in line:
            d.text((x, y), wd, font=f_title, fill=col)
            x += int(f_title.getlength(wd + " "))

    sw = int(f_sub.getlength(sub))
    d.text(((W - sw) // 2, pad_y + lh * len(lines) + 2), sub, font=f_sub,
           fill=(120, 120, 128, 255))
    return img


def _rank_row(rank: int, label: str, state: str, width: int = 660) -> Image.Image:
    """One ranking row. state: 'blank' | 'done' | 'active'."""
    f_num = font("anton", 54)
    f_lab = font("xbold", 36)
    h = 74
    img = Image.new("RGBA", (width, h), (0, 0, 0, 0))

    num_col = {"blank": (210, 210, 215, 230), "done": (255, 255, 255, 255),
               "active": (255, 196, 0, 255)}[state]
    lab_col = {"blank": (0, 0, 0, 0), "done": (255, 255, 255, 255),
               "active": (255, 240, 170, 255)}[state]
    stroke = 7 if state != "blank" else 6

    d = ImageDraw.Draw(img)
    txt = f"{rank}."
    d.text((6, 4), txt, font=f_num, fill=num_col, stroke_width=stroke,
           stroke_fill=(0, 0, 0, 235))
    x = 6 + int(f_num.getlength(txt)) + 18
    if state != "blank" and label:
        draw_rich(img, (x, 12), label, f_lab, fill=lab_col, stroke=6,
                  stroke_fill=(0, 0, 0, 235), emoji_px=46)
    return img


def leaderboard_track(duration: float, entries: list[dict], title_parts, sub: str,
                      cues_by_entry: list, mode: str, seed: int = 0):
    """`entries`: [{rank, label, t0, t1, beats, emoji}] in play order (5 -> 1)."""
    rnd = random.Random(seed)
    tr = Track(duration)
    sfx: list[tuple[float, str, float]] = []

    header = _header_tile(title_parts, sub)
    tr.add_static(header, 0, 0)

    list_x = 46
    list_y0 = header.height + 34
    row_h = 78
    n = len(entries)

    # scrim behind the ranking so white-on-white footage still reads
    tr.add_static(vertical_scrim(row_h * n + 70, width=740, top_alpha=120,
                                 bottom_alpha=70), 0, list_y0 - 24)
    tr.add_static(vertical_scrim(320, top_alpha=0, bottom_alpha=150), 0, H - 320)

    # Rows: blank until their clip starts, highlighted during it, white after.
    for i, e in enumerate(entries):
        y = list_y0 + i * row_h
        blank = _rank_row(e["rank"], "", "blank")
        tr.add(Sprite(blank, list_x + blank.width // 2, y + blank.height // 2,
                      0.0, e["t0"], pop=0.0))
        act = _rank_row(e["rank"], e["label"], "active")
        tr.add(Sprite(act, list_x + act.width // 2, y + act.height // 2,
                      e["t0"], e["t1"], pop=0.2))
        if i < n - 1:
            done = _rank_row(e["rank"], e["label"], "done")
            tr.add(Sprite(done, list_x + done.width // 2, y + done.height // 2,
                          e["t1"], duration, pop=0.0))

    # Per-entry stamp, flash, whoosh.
    for i, e in enumerate(entries):
        t0 = e["t0"]
        last = (i == n - 1)
        stamp_txt = f"#{e['rank']}"
        col = (255, 72, 72, 255) if last else (255, 210, 0, 255)
        stamp = caption_tile(stamp_txt, size=172 if last else 140, face="anton",
                             fill=col, stroke=16)
        tr.add(Sprite(stamp, W - 250, int(H * 0.30), t0, min(t0 + 1.5, e["t1"]),
                      pop=0.3, fade_out=0.45))
        if t0 > 0.05:
            tr.add(Flash(t0 - 0.06, t0 + 0.16, (255, 255, 255), 0.45))
        sfx.append((max(0.0, t0 - 0.30), "whoosh", 0.52))
        sfx.append((t0, "stinger" if not last else "airhorn", 0.6 if not last else 0.5))
        if last:
            sfx.append((max(0.0, t0 - 1.15), "drumroll", 0.42))
            sfx.append((t0, "bass_drop", 0.5))
        for b in e.get("beats", []):
            if e["t0"] + 0.2 < b < e["t1"] - 0.2:
                sfx.append((b, "boom", 0.52))

        if e.get("emoji"):
            tile = caption_tile(e["emoji"], size=150, face="anton", fill=WHITE,
                                stroke=0, shadow=True)
            et = min(t0 + 0.7, e["t1"] - 0.3)
            tr.add(Sprite(tile, W - 230, int(H * 0.30) + 190, et,
                          min(et + 1.3, e["t1"]), pop=0.26, fade_out=0.4,
                          drift=(0, -20)))

    # captions per entry
    cap_y = CAPTION_Y_COVER + 60 if mode == "cover" else CAPTION_Y_FIT + 40
    for cues in cues_by_entry:
        _caption_sprites(tr, cues, cap_y, size=92, sfx=sfx, accent_every=4)

    _progress_bar(tr, duration, color=(255, 196, 0, 255))
    _watermark(tr, duration, pos="bl")
    sfx.append((0.0, "riser", 0.34))
    return tr, sfx

"""
vidkit — the drawing kit behind MUTOSCOPE's shorts.

Everything that puts a pixel on the 1080x1920 canvas lives here: fonts, inline
colour-emoji text layout, outlined "meme" captions, rounded panels, scrims and the
little sprite compositor that the renderers animate.

Design notes
------------
* Noto Color Emoji is a CBDT bitmap font: it only rasterises at size 109. Any other
  size is a resample of the 109 strike, so emoji are rendered once at 109 and cached
  scaled. Asking FreeType for size 48 raises "invalid pixel size".
* Text is drawn with a stroke (outline) rather than a shadow because that is what the
  reference shorts use and it survives any background.
* Every expensive raster (a caption, a panel, an emoji) is cached by its parameters.
  The per-frame loop must only paste, never lay out.
"""

from __future__ import annotations

import functools
import os
import re
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30

_HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(os.path.dirname(_HERE), "assets", "fonts")

FONTS = {
    "anton": os.path.join(FONT_DIR, "Anton-Regular.ttf"),
    "black": os.path.join(FONT_DIR, "Montserrat-Black.ttf"),
    "xbold": os.path.join(FONT_DIR, "Montserrat-ExtraBold.ttf"),
    "bebas": os.path.join(FONT_DIR, "BebasNeue-Regular.ttf"),
    "emoji": os.path.join(FONT_DIR, "NotoColorEmoji.ttf"),
}

EMOJI_STRIKE = 109  # the only size the CBDT strike exists at

# Palette lifted from the reference shorts: hot yellow, cyan, white, kill-red.
YELLOW = (255, 222, 0, 255)
CYAN = (64, 236, 255, 255)
WHITE = (255, 255, 255, 255)
RED = (255, 54, 54, 255)
GREEN = (80, 255, 128, 255)
ORANGE = (255, 150, 20, 255)
BLACK = (0, 0, 0, 255)
INK = (16, 16, 20, 255)


@functools.lru_cache(maxsize=64)
def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONTS[name], size)


@functools.lru_cache(maxsize=4)
def _emoji_font() -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONTS["emoji"], EMOJI_STRIKE)


# A deliberately small, explicit emoji matcher. Matching "any symbol" also eats
# punctuation and arrows that the text font draws better.
_EMOJI_RE = re.compile(
    "([\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF"
    "\U00002190-\U000021FF\U00002B00-\U00002BFF\U0000FE0F\U0001F1E6-\U0001F1FF]+)"
)


def split_emoji(text: str) -> list[tuple[str, str]]:
    """Split a string into ('text'|'emoji', chunk) runs, in order."""
    out: list[tuple[str, str]] = []
    for part in _EMOJI_RE.split(text):
        if not part:
            continue
        out.append(("emoji" if _EMOJI_RE.fullmatch(part) else "text", part))
    return out


@functools.lru_cache(maxsize=512)
def emoji_image(ch: str, px: int) -> Image.Image:
    """One emoji glyph, rasterised at the CBDT strike then resampled to `px` tall."""
    pad = 16
    tile = Image.new("RGBA", (EMOJI_STRIKE + pad * 2, EMOJI_STRIKE + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    try:
        d.text((pad, pad), ch, font=_emoji_font(), embedded_color=True)
    except Exception:
        return Image.new("RGBA", (px, px), (0, 0, 0, 0))
    bbox = tile.getbbox()
    if not bbox:
        return Image.new("RGBA", (px, px), (0, 0, 0, 0))
    tile = tile.crop(bbox)
    scale = px / max(tile.height, 1)
    return tile.resize(
        (max(1, int(tile.width * scale)), max(1, int(tile.height * scale))), Image.LANCZOS
    )


def measure(text: str, fnt: ImageFont.FreeTypeFont, stroke: int = 0, emoji_px: int | None = None):
    """Width/height of a mixed text+emoji run as it will actually be drawn."""
    em = emoji_px or int(fnt.size * 1.0)
    w = 0
    asc, desc = fnt.getmetrics()
    h = asc + desc + stroke * 2
    for kind, chunk in split_emoji(text):
        if kind == "text":
            w += int(fnt.getlength(chunk)) + stroke * 2 * 0
        else:
            for ch in chunk:
                if ch == "\ufe0f":
                    continue
                w += int(emoji_image(ch, em).width * 1.06)
    return w + stroke * 2, max(h, em)


def draw_rich(
    img: Image.Image,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill=WHITE,
    stroke: int = 0,
    stroke_fill=BLACK,
    emoji_px: int | None = None,
    anchor_baseline: bool = False,
):
    """Draw mixed text + colour emoji starting at `xy` (top-left unless baseline)."""
    d = ImageDraw.Draw(img)
    x, y = xy
    em = emoji_px or int(fnt.size * 1.0)
    asc, _ = fnt.getmetrics()
    for kind, chunk in split_emoji(text):
        if kind == "text":
            d.text((x + stroke, y + stroke), chunk, font=fnt, fill=fill,
                   stroke_width=stroke, stroke_fill=stroke_fill)
            x += int(fnt.getlength(chunk))
        else:
            for ch in chunk:
                if ch == "\ufe0f":
                    continue
                g = emoji_image(ch, em)
                gy = y + stroke + asc - int(g.height * 0.82)
                img.alpha_composite(g, (int(x + stroke), int(gy)))
                x += int(g.width * 1.06)
    return x


@functools.lru_cache(maxsize=128)
def caption_tile(
    text: str,
    size: int = 96,
    face: str = "anton",
    fill: tuple = YELLOW,
    stroke: int = 12,
    stroke_fill: tuple = BLACK,
    shadow: bool = True,
    max_w: int = 960,
) -> Image.Image:
    """A centred, outlined caption with an optional soft drop shadow, auto-wrapped.

    Returned image is cropped tight so callers can position by its centre.
    """
    fnt = font(face, size)
    words = text.split()
    lines: list[str] = []
    cur = ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if measure(trial, fnt, stroke)[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)

    lh = int(size * 1.16)
    dims = [measure(ln, fnt, stroke) for ln in lines]
    tw = max([d[0] for d in dims] + [1]) + stroke * 2 + 8
    th = lh * len(lines) + stroke * 2 + int(size * 0.5)
    pad = 40 if shadow else 8
    img = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))

    for i, ln in enumerate(lines):
        lw = dims[i][0]
        draw_rich(img, (pad + (tw - lw) // 2, pad + i * lh), ln, fnt,
                  fill=fill, stroke=stroke, stroke_fill=stroke_fill,
                  emoji_px=int(size * 1.0))

    if shadow:
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        alpha = img.split()[3].filter(ImageFilter.GaussianBlur(14))
        glow.putalpha(alpha.point(lambda v: int(v * 0.75)))
        black = Image.new("RGBA", img.size, (0, 0, 0, 0))
        black.paste((0, 0, 0, 255), (0, 0), glow.split()[3])
        out = Image.alpha_composite(black, img)
    else:
        out = img
    bbox = out.getbbox()
    return out.crop(bbox) if bbox else out


def rounded_panel(size: tuple[int, int], radius: int, fill=(0, 0, 0, 140),
                  outline=None, outline_w: int = 0) -> Image.Image:
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=fill,
                        outline=outline, width=outline_w)
    return img


def vertical_scrim(height: int, width: int = W, top_alpha: int = 0,
                   bottom_alpha: int = 210, invert: bool = False) -> Image.Image:
    """A soft gradient wash so white text stays readable over any footage."""
    img = Image.new("RGBA", (1, height))
    px = img.load()
    for y in range(height):
        f = y / max(height - 1, 1)
        if invert:
            f = 1.0 - f
        a = int(top_alpha + (bottom_alpha - top_alpha) * (f ** 1.5))
        px[0, y] = (0, 0, 0, a)
    return img.resize((width, height))


# --------------------------------------------------------------------------- #
# sprite compositor
# --------------------------------------------------------------------------- #

def ease_out_back(t: float, overshoot: float = 1.9) -> float:
    t = min(max(t, 0.0), 1.0)
    c3 = overshoot + 1
    return 1 + c3 * (t - 1) ** 3 + overshoot * (t - 1) ** 2


def ease_out_cubic(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


@dataclass
class Sprite:
    """One timed, animatable raster on the overlay track.

    `cx, cy` are the *centre* in canvas pixels. `pop` gives the classic caption
    snap-in; `shake` is the small jitter used on impacts.
    """
    img: Image.Image
    cx: int
    cy: int
    t0: float
    t1: float
    pop: float = 0.14
    fade_out: float = 0.0
    shake: float = 0.0
    drift: tuple[float, float] = (0.0, 0.0)
    base_scale: float = 1.0
    opacity: float = 1.0
    scale_fn: Callable[[float], float] | None = None
    _cache: dict = field(default_factory=dict, repr=False)

    def active(self, t: float) -> bool:
        return self.t0 <= t < self.t1

    def _scaled(self, s: float) -> Image.Image:
        # Quantise hard: this box has 2 GB and a cache of near-identical rasters is
        # how the first leaderboard render got OOM-killed.
        key = round(s * 40) / 40
        hit = self._cache.get(key)
        if hit is None:
            if abs(key - 1.0) < 0.013:
                hit = self.img
            else:
                nw = max(1, int(self.img.width * key))
                nh = max(1, int(self.img.height * key))
                hit = self.img.resize((nw, nh), Image.BILINEAR)
            if len(self._cache) > 10:
                self._cache.clear()
            self._cache[key] = hit
        return hit

    def paste(self, canvas: Image.Image, t: float):
        if not self.active(t):
            return
        local = t - self.t0
        life = self.t1 - self.t0
        s = self.base_scale
        if self.scale_fn is not None:
            s *= self.scale_fn(local / max(life, 1e-6))
        elif self.pop > 0 and local < self.pop:
            s *= 0.55 + 0.45 * ease_out_back(local / self.pop)
        a = self.opacity
        if self.fade_out > 0 and local > life - self.fade_out:
            a *= max(0.0, (life - local) / self.fade_out)
        if a <= 0.01:
            return
        im = self._scaled(s)
        if a < 0.97:
            key = ("a", round(a * 12) / 12, round(s * 40) / 40)
            faded = self._cache.get(key)
            if faded is None:
                faded = im.copy()
                faded.putalpha(faded.split()[3].point(
                    lambda v, _a=key[1]: int(v * _a)))
                if len(self._cache) > 10:
                    self._cache.clear()
                self._cache[key] = faded
            im = faded
        dx = dy = 0
        if self.shake > 0:
            import math
            dx = int(math.sin(t * 61.0) * self.shake)
            dy = int(math.cos(t * 47.0) * self.shake)
        dx += int(self.drift[0] * local)
        dy += int(self.drift[1] * local)
        x = int(self.cx - im.width / 2 + dx)
        y = int(self.cy - im.height / 2 + dy)
        blit(canvas, im, x, y)


@dataclass
class Flash:
    """A full-frame colour wash, drawn in place.

    A white flash as a Sprite meant an 8.3 MB RGBA image per flash plus a fresh
    copy every frame to fade it. ImageDraw blends a rectangle straight into the
    canvas and allocates nothing.
    """
    t0: float
    t1: float
    color: tuple = (255, 255, 255)
    peak: float = 0.45

    def active(self, t: float) -> bool:
        return self.t0 <= t < self.t1

    def paste(self, canvas: Image.Image, t: float):
        if not self.active(t):
            return
        f = (t - self.t0) / max(self.t1 - self.t0, 1e-6)
        a = int(self.peak * 255 * (1.0 - f) ** 1.4)
        if a <= 2:
            return
        ImageDraw.Draw(canvas, "RGBA").rectangle(
            [0, 0, canvas.width, canvas.height], fill=(*self.color, a))


def blit(canvas: Image.Image, im: Image.Image, x: int, y: int):
    """alpha_composite refuses out-of-bounds, so crop the source instead.

    The old fallback allocated a full 1080x1920 RGBA scratch per offending sprite
    per frame — 8.3 MB a pop, and the reason this renderer first died at 2 GB.
    """
    cw, ch = canvas.size
    if x >= cw or y >= ch or x + im.width <= 0 or y + im.height <= 0:
        return
    sx = max(0, -x)
    sy = max(0, -y)
    ex = min(im.width, cw - x)
    ey = min(im.height, ch - y)
    if ex <= sx or ey <= sy:
        return
    if sx or sy or ex != im.width or ey != im.height:
        im = im.crop((sx, sy, ex, ey))
    canvas.alpha_composite(im, (x + sx, y + sy))


@dataclass
class ProgressBar:
    """Bottom fill, drawn in place — 64 sprites for one thin line was wasteful."""
    duration: float
    color: tuple = (255, 222, 0)
    y: int = H - 14
    thickness: int = 10

    def paste(self, canvas: Image.Image, t: float):
        f = min(max(t / max(self.duration, 1e-6), 0.0), 1.0)
        w = int(canvas.width * f)
        if w < 2:
            return
        ImageDraw.Draw(canvas, "RGBA").rectangle(
            [0, self.y, w, self.y + self.thickness], fill=(*self.color, 235))


class Track:
    """The overlay timeline: a bag of sprites rasterised on demand."""

    def __init__(self, duration: float, fps: int = FPS, size: tuple[int, int] = (W, H)):
        self.duration = duration
        self.fps = fps
        self.size = size
        self.sprites: list = []
        self.statics: list[tuple[Image.Image, int, int]] = []
        self._base: Image.Image | None = None
        self._canvas: Image.Image | None = None

    def add(self, sp):
        self.sprites.append(sp)
        return sp

    def add_static(self, img: Image.Image, x: int, y: int):
        self.statics.append((img, x, y))

    def nframes(self) -> int:
        return int(round(self.duration * self.fps))

    def _base_layer(self) -> Image.Image:
        """Statics never move: flatten them once and copy that each frame."""
        if self._base is None:
            base = Image.new("RGBA", self.size, (0, 0, 0, 0))
            for img, x, y in self.statics:
                blit(base, img, x, y)
            self._base = base
        return self._base

    def frame(self, i: int) -> Image.Image:
        t = i / self.fps
        canvas = self._base_layer().copy()
        for sp in self.sprites:
            sp.paste(canvas, t)
        return canvas

    def iter_raw(self) -> Iterable[bytes]:
        for i in range(self.nframes()):
            yield self.frame(i).tobytes()

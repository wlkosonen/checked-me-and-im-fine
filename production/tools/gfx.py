#!/usr/bin/env python3
"""The graphics base for Checked Me and I'm Fine. Kiln owns this file; the section agents build on it.

gfxrender.py calls scene() and top() for every frame of a shot. The order of one frame (film-1's flat layer is gone):

    the picture -> a section's picture() -> its world() layer -> beat kick and cut pulse -> transition -> over() layer
    -> the counter

So a thing on the wall or a full-frame graphic is in world() and takes the kick with the picture; type laid over the
film is in over() and holds still. Sections: production/tools/gfx_<section>.py, each with any of
picture(sid, t, frame), world(c, t, sid), over(c, t, sid) and CUTS = {"s012": ("flash", 2)} for the cuts inside it.
The cuts between sections are in production/edit/seams.md.

Drawing is Skia (media/cache/gfx-venv): subpixel text and paths, so moving type doesn't re-space (film 1's trouble with
PIL). All sizes and positions are in 1920x1080 units at any output size. Frames are numpy RGB uint8 arrays.

The rules behind the voices and colours are in production/style.md.
"""

import importlib
import json
import math
import re
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

import av
import cv2
import numpy as np
import skia
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[2]
FPS = 25

# ---- palette: green is a pass, clay is her and her words (style.md); the rest are the sets' colours

CLAY = (217, 119, 87)
GREEN = (46, 224, 128)
WHITE = (247, 245, 240)
INK = (20, 18, 28)
COBALT = (36, 64, 232)
MAGENTA = (226, 38, 170)
VIOLET = (124, 66, 232)
CYAN = (40, 208, 228)
YELLOW = (248, 226, 104)
TEAL = (36, 176, 176)
PINK = (244, 158, 196)

# ---- the two voices, and the two working faces

FACES = {
    "hook": "Anton-Regular.ttf",  # heavy caps: the hooks
    "serif": "Newsreader-LightItalic.ttf",  # light italic: the verse lines
    "mono": "IBMPlexMono-Medium.ttf",  # labels, stamps, the counter, screens
    "sans": "IBMPlexSans-SemiBold.ttf",  # UI: the call, the phone
}


@lru_cache(maxsize=None)
def _typeface(face):
    return skia.Typeface.MakeFromFile(str(ROOT / "media/cache/fonts" / FACES[face]))


@lru_cache(maxsize=None)
def _font(face, px):
    f = skia.Font(_typeface(face), px)
    f.setSubpixel(True)
    f.setLinearMetrics(True)
    f.setHinting(skia.FontHinting.kNone)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


@lru_cache(maxsize=4096)
def _blob(s, face, px):
    return skia.TextBlob.MakeFromShapedText(s, _font(face, px))


@lru_cache(maxsize=None)
def _hb(face):
    return hb.Font(hb.Face(hb.Blob.from_file_path(str(ROOT / "media/cache/fonts" / FACES[face]))))


@lru_cache(maxsize=4096)
def width(s, face, px):
    """The set width of s in units, kerned (a blob's own bounds are only an outer limit)."""
    if not s:
        return 0.0
    f = _hb(face)
    buf = hb.Buffer()
    buf.add_str(s)
    buf.guess_segment_properties()
    hb.shape(f, buf, {"kern": True})
    return sum(p.x_advance for p in buf.glyph_positions) * px / f.face.upem


# ---- time: the beat grid and the sung words

_beats = json.loads((ROOT / "media/song/analysis/checked-me-v1/beats.json").read_text())
BEATS, DOWNBEATS = np.array(_beats["beats"]), np.array(_beats["downbeats"])
BOARD = json.loads((ROOT / "production/board/board.json").read_text())
SHOTS = {s["id"]: s for s in BOARD["shots"]}
WORDS = sorted(({**w, "line": l["line"]} for l in BOARD["lyric_lines"] for w in l["words"]), key=lambda w: w["t0"])


def snap(t, div=1):
    """The nearest beat (div=1), eighth (2) or sixteenth (4). Graphics enter on this, not on the raw word time."""
    i = int(np.clip(np.searchsorted(BEATS, t), 1, len(BEATS) - 1))
    a, step = BEATS[i - 1], (BEATS[i] - BEATS[i - 1]) / div
    return float(a + round((t - a) / step) * step)


def word(w, after=0.0):
    """The first sung word w after song time `after`: {"w", "t0", "t1", "line"}."""
    return next(x for x in WORDS if x["w"].strip("!?,.—'\"").lower() == w and x["t0"] >= after)


def on(w, after=0.0, div=4):
    """When a graphic for that word enters: its start, snapped to the sixteenth."""
    return snap(word(w, after)["t0"], div)


def since_beat(t, div=1):
    i = int(np.searchsorted(BEATS, t, side="right")) - 1
    if i < 0:
        return 1e9
    step = (BEATS[min(i + 1, len(BEATS) - 1)] - BEATS[i]) / div
    return (t - BEATS[i]) % step


def pulse(t, div=1, tau=0.12):
    """1 on each beat, dying away: for anything that should breathe with the song."""
    return math.exp(-since_beat(t, div) / tau)


# ---- motion: everything is a function of song time, nothing keeps state between frames

def clamp(x, a=0.0, b=1.0):
    return min(max(x, a), b)


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def out_expo(x):
    x = clamp(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def out_back(x, over=1.7):
    x = clamp(x) - 1
    return 1 + (over + 1) * x ** 3 + over * x * x


def in_cubic(x):
    return clamp(x) ** 3


def ramp(t, a, b, e=smooth):
    """0 before a, 1 after b, shaped by e."""
    return e((t - a) / max(b - a, 1e-6))


def frames(n):
    return n / FPS


def slam(t, at, big=1.3, dur=0.14):
    """Scale of a thing that lands at `at`: oversized at once, settled in dur seconds. Before `at`, 0."""
    return 0.0 if t < at - 1e-6 else 1 + (big - 1) * (1 - ramp(t, at, at + dur, out_expo))


def rise(t, at, dy=26, dur=0.3):
    """(alpha, y offset) of a thing that floats up into place: the verse voice's entrance."""
    k = ramp(t, at, at + dur, out_expo)
    return k, dy * (1 - k)


def type_on(s, t, at, cps=40):
    """s as far as it has typed by t."""
    return s[: clamp(int((t - at) * cps) + 1, 0, len(s))] if t >= at else ""


def blink(t, at=0.0):
    """A cursor: on for an eighth, off for an eighth, on the song's grid."""
    i = int(np.searchsorted(BEATS, t, side="right")) - 1
    return i < 0 or since_beat(t, 2) < (BEATS[1] - BEATS[0]) / 4 or t < at


# ---- the canvas

def _paint(color, alpha=1.0, **kw):
    return skia.Paint(Color=skia.Color(*color, round(255 * clamp(alpha))), AntiAlias=True, **kw)


class Canvas:
    """A transparent layer of the output size, drawn in 1920x1080 units. self.a: premultiplied RGBA, h x w x 4."""

    def __init__(self, w, h, S=None):
        self.w, self.h, self.S = w, h, S or w / 1920
        self.a = np.zeros((h, w, 4), np.uint8)
        self.surface = skia.Surface(self.a, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
        self.k = self.surface.getCanvas()
        self.k.scale(self.S, self.S)

    def fill(self, color, alpha=1.0):
        self.k.drawPaint(_paint(color, alpha))

    def gradient(self, a, b, angle=0.0, box=None):
        """The whole canvas (or box x0, y0, x1, y1) in a linear gradient, angle in degrees from left to right."""
        x0, y0, x1, y1 = box or (0, 0, self.w / self.S, self.h / self.S)
        cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, math.hypot(x1 - x0, y1 - y0) / 2
        dx, dy = r * math.cos(math.radians(angle)), r * math.sin(math.radians(angle))
        shader = skia.GradientShader.MakeLinear([skia.Point(cx - dx, cy - dy), skia.Point(cx + dx, cy + dy)],
                                                [skia.Color(*a), skia.Color(*b)])
        self.k.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=shader, AntiAlias=True))

    def rect(self, x0, y0, x1, y1, color, alpha=1.0, r=0.0, stroke=0.0):
        p = _paint(color, alpha)
        if stroke:
            p.setStyle(skia.Paint.kStroke_Style)
            p.setStrokeWidth(stroke)
        self.k.drawRoundRect(skia.Rect(x0, y0, x1, y1), r, r, p)

    def line(self, x0, y0, x1, y1, color, alpha=1.0, w=2.0):
        self.k.drawLine(x0, y0, x1, y1, _paint(color, alpha, StrokeWidth=w))

    def circle(self, x, y, r, color, alpha=1.0):
        self.k.drawCircle(x, y, r, _paint(color, alpha))

    def text(self, s, x, y, face, px, color, alpha=1.0, anchor="l", scale=1.0, rot=0.0, blur=0.0, shadow=0.0):
        """One run of text, baseline at y. anchor l, c or r. scale and rot turn about the text's own centre."""
        if not s or alpha <= 0.003 or scale <= 0:
            return
        px = round(px, 2)
        blob = _blob(s, face, px)
        if blob is None:
            return
        w = width(s, face, px)
        top = y + _font(face, px).getMetrics().fAscent  # a shaped blob's origin is its top line, not its baseline
        dx = {"l": 0.0, "c": -w / 2, "r": -w}[anchor]
        self.k.save()
        cx, cy = x + dx + w / 2, y - px * 0.36
        self.k.translate(cx, cy)
        if rot:
            self.k.rotate(rot)
        if scale != 1:
            self.k.scale(scale, scale)
        self.k.translate(-cx, -cy)
        if shadow:  # a soft dark halo, so type holds over white shirts and bright light
            sh = _paint((0, 0, 0), alpha * shadow)
            sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, px * 0.06 + 3))
            self.k.drawTextBlob(blob, x + dx, top + 2, sh)
        p = _paint(color, alpha)
        if blur:
            p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
        self.k.drawTextBlob(blob, x + dx, top, p)
        self.k.restore()

    @contextmanager
    def layer(self, alpha=1.0, blur=0.0, shadow=None, at=None, scale=1.0, clip=None):
        """Draw a group as one: fade it, blur it, shadow it (dy, sigma, alpha), scale it about `at`, clip it to a box."""
        p = _paint((255, 255, 255), alpha)
        if blur:
            p.setImageFilter(skia.ImageFilters.Blur(blur * self.S, blur * self.S))
        if shadow:
            dy, sigma, a = shadow
            p.setImageFilter(skia.ImageFilters.DropShadow(0, dy * self.S, sigma * self.S, sigma * self.S,
                                                          skia.Color(0, 0, 0, round(255 * a))))
        self.k.save()
        if clip:
            self.k.clipRect(skia.Rect(*clip), doAntiAlias=True)
        if at and scale != 1:
            self.k.translate(*at)
            self.k.scale(scale, scale)
            self.k.translate(-at[0], -at[1])
        self.k.saveLayer(paint=p)
        yield self
        self.k.restore()
        self.k.restore()


def over(frame, rgba):
    """Premultiplied RGBA over an RGB frame."""
    a = rgba[..., 3:4].astype(np.uint16)
    if not a.any():
        return frame
    return ((frame.astype(np.uint16) * (255 - a) + 127) // 255 + rgba[..., :3]).clip(0, 255).astype(np.uint8)


# ---- the voices

def hook(c, t, s, at, x, y, px, clay=(), color=WHITE, anchor="c", end=None, big=1.28, shadow=0.0, alpha=1.0):
    """Hook voice: heavy caps, on the beat, one word in clay. s is cut into words, each drawn in turn; `clay` names the
    words in clay. It lands at `at` and goes at `end` on a cut, not a fade."""
    if t < at - 1e-6 or (end is not None and t >= end - 1e-6):
        return
    s = s.upper()
    sc = slam(t, at, big)
    words = s.split()
    gap = px * 0.2
    ws = [width(w, "hook", px) for w in words]
    total = sum(ws) + gap * (len(ws) - 1)
    x0 = x - {"l": 0.0, "c": total / 2, "r": total}[anchor]
    with c.layer(at=(x0 + total / 2, y - px * 0.36), scale=sc, alpha=alpha):
        for w, ww in zip(words, ws):
            col = CLAY if w.strip(",.!?") in {k.upper() for k in clay} else color
            c.text(w, x0, y, "hook", px, col, shadow=shadow)
            x0 += ww + gap


def verse(c, t, rows, x, y, px=54, key=2.1, anchor="l", end=None, shadow=0.75, leading=1.08):
    """Verse voice: the light italic serif beside her, the key word larger, in clay. rows: a list of rows, each a list
    of (text, at) or (text, at, True) for a key word. y is the first row's baseline. Each word floats up on its own
    time; the whole goes at `end`."""
    o = 1.0 if end is None else 1 - ramp(t, end, end + 0.14)
    if o <= 0:
        return
    for row in rows:
        sizes = [px * key if len(r) > 2 and r[2] else px for r in row]
        top = max(sizes)
        y += top * leading * 0.78
        sp = px * 0.26
        ws = [width(r[0], "serif", q) for r, q in zip(row, sizes)]
        total = sum(ws) + sp * (len(ws) - 1)
        xx = x - {"l": 0.0, "c": total / 2, "r": total}[anchor]
        for r, q, w in zip(row, sizes, ws):
            a, dy = rise(t, r[1])
            k = len(r) > 2 and r[2]
            c.text(r[0], xx, y + dy, "serif", q, CLAY if k else WHITE, alpha=a * o, shadow=shadow)
            xx += w + sp
        y += top * leading * 0.3


def line_words(n, first=0, last=None, keys=(), div=4):
    """A lyric line's words as (text, at[, True]) for verse(): the board's display text, entered on the sixteenth."""
    l = next(x for x in BOARD["lyric_lines"] if x["line"] == n)
    shown = [x for x in l["text"].split() if any(ch.isalnum() for ch in x)]  # a lone dash isn't sung
    if len(shown) != len(l["words"]):
        shown = [w["w"] for w in l["words"]]
    out = []
    for s, w in list(zip(shown, l["words"]))[first:last]:
        out.append((s, snap(w["t0"], div), True) if s.strip(",.!?—").lower() in keys else (s, snap(w["t0"], div)))
    return out


def stamp(c, t, at, s, x, y, px=44, color=GREEN, rot=-3.0, end=None, big=1.7):
    """The plain inspection stamp (CHECKED BY: ME): mono caps in a box, thumped on."""
    if t < at - 1e-6 or (end is not None and t >= end - 1e-6):
        return
    w = width(s, "mono", px) + px * 1.4
    h = px * 2.0
    sc = slam(t, at, big, 0.12)
    k = c.k
    k.save()
    k.translate(x, y)
    k.rotate(rot)
    k.scale(sc, sc)
    c.rect(-w / 2, -h / 2, w / 2, h / 2, color, r=6, stroke=px * 0.11)
    c.rect(-w / 2 + px * .2, -h / 2 + px * .2, w / 2 - px * .2, h / 2 - px * .2, color, alpha=0.55, r=4, stroke=px * 0.04)
    c.text(s, 0, px * 0.36, "mono", px, color, anchor="c")
    k.restore()


def star(c, x, y, r, color=CLAY, alpha=1.0, turn=0.0):
    """Her eight-pointed star clip: her mark in the film's screens, in place of any product's logo."""
    p = skia.Path()
    for i in range(16):
        a = math.radians(turn + i * 22.5 - 90)
        q = r if i % 2 == 0 else r * 0.42
        (p.moveTo if i == 0 else p.lineTo)(x + q * math.cos(a), y + q * math.sin(a))
    p.close()
    c.k.drawPath(p, _paint(color, alpha))


# ---- the counter: `first meetings: 1`, in every corner from "first time" on, rolling back to 1

def _phrases():
    """Each "first time, every time": (the "every", the last "time")."""
    out = []
    for i in range(len(WORDS) - 3):
        a = [WORDS[i + k]["w"].strip("!?,.—'\"").lower() for k in range(4)]
        if a == ["first", "time", "every", "time"]:
            out.append((snap(WORDS[i + 2]["t0"], 2), snap(WORDS[i + 3]["t0"], 2)))
    return out


ROLLS = _phrases()
COUNTER_ON = snap(word("first", 19.0)["t0"], 2)  # it arrives on the song's first "first time"
COUNTER_XY = (1856, 62)
COUNTER_OFF = ("s059",)  # the bar of black before the key change: pure black, the one shot without it


def counter_value(t):
    """How far the digit has rolled: 1, reaching for 2 on "every", thrown back to 1 on the last "time"."""
    for a, b in ROLLS:
        if a <= t < b:
            return 1 + 0.86 * ramp(t, a, b, out_expo)
        if b <= t < b + 0.34:
            return 1 + 0.86 * (1 - out_back((t - b) / 0.34, 2.2))
    return 1.0


def counter(c, t):
    if t < COUNTER_ON:
        return
    a = ramp(t, COUNTER_ON, COUNTER_ON + 0.2)
    px, x, y = 27, COUNTER_XY[0], COUNTER_XY[1]
    dw = width("0", "mono", px)
    lw = width("first meetings:", "mono", px)
    pad = 16
    x0, y0, x1, y1 = x - dw - lw - pad * 2 - 12, y - px - 8, x + pad - 4, y + 14
    c.rect(x0, y0, x1, y1, INK, alpha=0.62 * a, r=8)
    c.text("first meetings:", x0 + pad, y, "mono", px, WHITE, alpha=0.92 * a)
    v = counter_value(t)
    with c.layer(clip=(x - dw - 6, y0, x + 6, y1), alpha=a):  # the digit rolls in its own window
        h = px * 1.5
        for n in (1, 2):
            c.text(str(n), x - dw, y + (n - v) * h, "mono", px, GREEN if n == 1 else WHITE)


# ---- the LED wall: a graphic behind her, on the wall in the shot

def _has_matte(sid):
    return (ROOT / f"media/cache/gfx/matte-{sid}.mp4").exists()


@lru_cache(maxsize=4)
def _matte(sid):
    f = ROOT / f"media/cache/gfx/matte-{sid}.mp4"
    return [x.to_ndarray(format="gray") for x in av.open(str(f)).decode(video=0)]


def matte(sid, t, h, w):
    """Her matte at song time t, float 0-1 at h x w. Built by gfx_matte.py; dancers in silhouette aren't in it."""
    m = _matte(sid)
    a = m[int(clamp(round(t * FPS) - round(float(SHOTS[sid]["t0"]) * FPS), 0, len(m) - 1))]
    return (a if a.shape == (h, w) else cv2.resize(a, (w, h), interpolation=cv2.INTER_LINEAR)).astype(np.float32) / 255


@lru_cache(maxsize=4)
def _plane(sid):
    f = ROOT / f"media/cache/gfx/plane-{sid}.json"
    return json.loads(f.read_text()) if f.exists() else None


def plane(sid, t):
    """The wall's drift (gfx_wall.py), 3x3 in 1080p units, or identity."""
    p = _plane(sid)
    if not p:
        return np.eye(3)
    return np.array(p["H"][int(clamp(np.searchsorted(p["t"], t), 0, len(p["H"]) - 1))])


@lru_cache(maxsize=4)
def _led_mask(h, w, period):
    """The wall's pixels: faint rows and columns, so type reads as lit LEDs and not as a title on top of the film."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    g = (0.5 + 0.5 * np.cos(2 * np.pi * x / period)) * (0.5 + 0.5 * np.cos(2 * np.pi * y / period))
    return (0.8 + 0.2 * g)[..., None]


def wall(frame, draw, quad, sid, t, size=(1740, 600), bloom=0.3, gain=1.15, dim=0.62, led=True):
    """draw(c) draws in wall units (0, 0)-size; the result goes on the wall at `quad` (four corners in 1920 units,
    clockwise from top left), lit like LEDs, behind her matte, with the room's light still over it."""
    h, w = frame.shape[:2]
    S = w / 1920
    c = Canvas(round(size[0] * S), round(size[1] * S), S)
    draw(c)
    src = np.float32([[0, 0], [c.w, 0], [c.w, c.h], [0, c.h]])
    q = np.float32(quad)[None]
    dst = (cv2.perspectiveTransform(q, plane(sid, t))[0] if sid else q[0]) * S
    M = cv2.getPerspectiveTransform(src, np.float32(dst))
    rgba = c.a.astype(np.float32) / 255
    if led:
        rgba[..., :3] *= _led_mask(c.h, c.w, max(3.0, 5.5 * S))
        n = round(60 * S)
        rgba[:, :n] *= np.linspace(0, 1, n, dtype=np.float32)[None, :, None]  # the wall's ends fade into the dark
        rgba[:, -n:] *= np.linspace(1, 0, n, dtype=np.float32)[None, :, None]
    lay = cv2.warpPerspective(rgba, M, (w, h), flags=cv2.INTER_LINEAR)
    hold = (1 - matte(sid, t, h, w))[..., None] if sid and _has_matte(sid) else 1.0
    rgb, a = np.clip(lay[..., :3] * gain, 0, 1) * hold, lay[..., 3:4] * hold
    f = frame.astype(np.float32) / 255 * (1 - dim * a)  # sparks and beams pass over the type, held down so it reads
    out = 1 - (1 - f) * (1 - rgb)
    if bloom:
        out = 1 - (1 - out) * (1 - np.clip(cv2.GaussianBlur(rgb, (0, 0), 16 * S) * bloom, 0, 1))
    return (out * 255).astype(np.uint8)


def screen(frame, draw, quad, size=(1600, 900), sid=None, t=0.0, bloom=0.08):
    """draw(c) on a real screen in the shot (a laptop, a slide, a phone): its own picture, opaque, in perspective. Pass
    sid and t to keep it behind her matte and follow the shot's drift."""
    return wall(frame, draw, quad, sid, t, size=size, bloom=bloom, gain=1.0, dim=1.0, led=False)


# ---- transitions, from notes/reference-transitions.md. A is the outgoing shot's last frame, held; B is the incoming
# shot, live; k runs from 0 to 1 over the first frames of the incoming shot. Nothing moves before the cut, as measured.

def flash(A, B, k, t):
    """A white frame between two places."""
    return (B + (255 - B.astype(np.float32)) * (1 - k) ** 2).astype(np.uint8)


def whip(A, B, k, t, direction=1):
    """A motion-blur smear into the next shot."""
    src = A if k < 0.5 else B
    h, w = src.shape[:2]
    d = (1 - abs(2 * k - 1))  # strongest at the join
    n = max(3, int(w * 0.16 * d)) | 1
    kernel = np.ones((1, n), np.float32) / n
    shift = int(direction * w * 0.5 * (k - 1 if k >= 0.5 else k))
    return cv2.filter2D(np.roll(src, -shift, axis=1), -1, kernel)


def slide(A, B, k, t, direction=1):
    """A hard slide: the next shot pushes the last one off."""
    w = A.shape[1]
    x = int(w * out_expo(k))
    return np.concatenate([A[:, x:], B[:, :x]] if direction > 0 else [B[:, w - x:], A[:, :w - x]], axis=1)


@lru_cache(maxsize=4)
def _mosaic_order(rows, cols):
    return np.random.default_rng(7).random((rows, cols))


def mosaic(A, B, k, t, cols=24, color=CLAY):
    """KILL SWITCH's block peel: the frame breaks into squares that turn to `color`, then open onto the next shot."""
    h, w = A.shape[:2]
    rows = max(1, round(cols * h / w))
    o = _mosaic_order(rows, cols)
    grid = np.zeros((rows, cols), np.uint8)
    grid[o < k * 2] = 1  # block turned
    grid[o < k * 2 - 1] = 2  # block open
    g = cv2.resize(grid, (w, h), interpolation=cv2.INTER_NEAREST)
    out = A.copy()
    out[g == 1] = color
    out[g == 2] = B[g == 2]
    return out


TRANSITIONS = {"flash": flash, "whip": whip, "slide": slide, "mosaic": mosaic}


def _seams():
    """The cuts between sections, from the table in production/edit/seams.md: {t: (name, frames)}."""
    out = {}
    f = ROOT / "production/edit/seams.md"
    for l in f.read_text().splitlines() if f.exists() else []:
        m = re.match(r"\|\s*(s\d+)\s*→\s*(s\d+)\s*\|", l)
        if m:
            tr = l.split("|")[6].strip().split()
            if tr and tr[0] in TRANSITIONS:
                out[m[2]] = (tr[0], int(tr[1]))
    return out


# ---- the sections

SECTIONS = {
    "opening": [(1, 16)],
    "stage": [(17, 30), (43, 53), (60, 67)],
    "desk": [(31, 42)],
    "call": [(54, 59), (68, 73)],
}


def section_of(sid):
    n = int(sid[1:])
    return next(k for k, v in SECTIONS.items() if any(a <= n <= b for a, b in v))


def module(sid):
    return importlib.import_module(f"gfx_{section_of(sid)}")


def transition(sid):
    """The transition into shot sid, if it has one: a seam, or the section's own CUTS."""
    return _seams().get(sid) or getattr(module(sid), "CUTS", {}).get(sid)


def scene(sid, t, frame):
    """Everything under the kick."""
    m = module(sid)
    if hasattr(m, "picture"):
        frame = m.picture(sid, t, frame)
    if hasattr(m, "world"):
        c = Canvas(frame.shape[1], frame.shape[0])
        m.world(c, t, sid)
        frame = over(frame, c.a)
    return frame


def top(sid, t, frame):
    """Everything over the kick: the section's overlay, then the counter, which belongs to the whole film."""
    c = Canvas(frame.shape[1], frame.shape[0])
    m = module(sid)
    if hasattr(m, "over"):
        m.over(c, t, sid)
    if sid not in COUNTER_OFF:
        counter(c, t)
    return over(frame, c.a)

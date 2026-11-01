#!/usr/bin/env python3
"""Section D, the call and the ending: s054-s059, s068-s073.

The call is an overlay on the full picture (Lati: "a teams ui overlay"): a generic call app, no real marks, her star where
a logo would go. GUESTS holds the avatar tiles; each is there by its maker's leave (notes/permissions.md). A new tile is
one more row in GUESTS, and the rail and the chat make room. s056 is her shared screen: real text from this repo. From
170.98 the sustained vocal draws a wall of separate dots: its pitch is the rise and fall (level hardly moves, measured),
and it fades to one dot. The phone in s070 and s073 is the plate of p-s073up, with phonefit.py's own screen and drift.
From 145.44 s058 leaves her for gfx.py itself, opening on the counter's docstring and multiplying on the drum fill's hits.

    media/cache/gfx-venv/bin/python production/tools/gfx_call.py measure    # writes media/gfx/call/vocal.json, build.json
"""

import json
import math
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import av
import cv2
import numpy as np
import skia

import gfx
import phonefit
from gfx import (BEATS, CLAY, COBALT, CYAN, FPS, GREEN, INK, MAGENTA, PINK, ROOT, SHOTS, VIOLET, WHITE, YELLOW, Canvas, blink,
                 clamp, hook, line_words, on, out_back, out_expo, pulse, ramp, slam, smooth, snap, star, type_on, verse, width)

DARK = (14, 12, 20)
PANEL = (40, 37, 50)
GREY = (150, 146, 160)

T = {s: float(SHOTS[s]["t0"]) for s in SHOTS}
END = {s: float(SHOTS[s]["t1"]) for s in SHOTS}
CALL = ("s054", "s055", "s057", "s058")  # the sung shots of the bridge: the overlay; s056 is drawn whole

# ---- the guests. Only a yes in notes/permissions.md gets a row. Bright Mirror and Max Pelletier: waiting, no tile.
# crop: x0, y0, x1, y1 in the tile clip, clear of the text in the makers' own frames

GUESTS = [
    {"name": "Eve", "by": "by Funny Story Musicals", "file": "media/clips/preview/tile-eve-343.mp4",
     "crop": (120, 24, 520, 324), "phase": 0.0},
    {"name": "Astra", "by": "by Astra Blue AI", "file": "media/clips/preview/tile-astra-live.mp4",
     "crop": (120, 30, 520, 330), "phase": 1.3},
]

# the record's address: the public repo, live since 1 Nov
RECORD = "github.com/wlkosonen/checked-me-and-im-fine"

# the source tag's micro-type: the first film's wording (description.md, point 3), read against the three pages on 1 Nov
SOURCE = ["reports of its own reasoning are sometimes",
          "unfaithful; its introspection is limited and",
          "unreliable.",
          "anthropic.com/research/",
          "  reasoning-models-dont-say-think",
          "  introspection",
          "  tracing-thoughts-language-model"]

# ---- when

QUOTE = on("exactly", 123)  # the chorus line quoted in the chat
WRONG = on("wrong", 127)  # PASSED is struck through
TAG = on("me", 131)  # source: the model itself
FAITH = on("faith", 133)
OPEN, UP, TRACE = max(T["s056"], on("open", 134)), on("up", 135), on("trace", 136)
CHECKS = [on("check", 138), on("check", 138.6), on("check", 139.8)]
AGAIN = on("again", 140)
TYPE_AT, INSTEAD = on("take", 143), on("instead", 143.5)
JOINED = snap(145.0)  # the beat after the link is sent, and the last before the shot leaves her
CUT = 145.44  # Lati: 2:25.439, on its nearest frame; the held note stops matching her lips here
GFX_AT = 170.978  # Lati's mark: the graphics start right after "time"; cut-v3.json holds a card from here
VOCAL_END = 176.28  # measured: the vocal stem stops here; drums run on


# ---- small helpers

def mix(a, b, k):
    k = clamp(k)
    return tuple(round(x + (y - x) * k) for x, y in zip(a, b))


def rrect(box, r):
    return skia.RRect.MakeRectXY(skia.Rect(*box), r, r)


def image(c, rgb, box, r=14.0, crop=None):
    """An RGB array in box, cropped to cover it, rounded."""
    h, w = rgb.shape[:2]
    x0, y0, x1, y1 = crop or (0, 0, w, h)
    k = min((x1 - x0) / (box[2] - box[0]), (y1 - y0) / (box[3] - box[1]))
    vw, vh = (box[2] - box[0]) * k, (box[3] - box[1]) * k
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rgba = np.dstack([rgb, np.full((h, w), 255, np.uint8)])
    im = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    c.k.save()
    c.k.clipRRect(rrect(box, r), True)
    c.k.drawImageRect(im, skia.Rect(cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2), skia.Rect(*box),
                      skia.SamplingOptions(skia.FilterMode.kLinear))
    c.k.restore()


@lru_cache(maxsize=4)
def _clip(file):
    k = av.open(str(ROOT / file))
    return [f.to_ndarray(format="rgb24") for f in k.decode(video=0)], float(k.streams.video[0].average_rate)


def guest_frame(g, t):
    """The guest's clip at song time t, there and back so it never jumps."""
    fr, rate = _clip(g["file"])
    n = len(fr)
    i = int(round((t + g["phase"]) * rate)) % (2 * n - 2)
    return fr[i if i < n else 2 * n - 2 - i]


def tile_label(c, box, name, by):
    x0, _, _, y1 = box
    w = max(width(name, "sans", 22), width(by, "mono", 13)) + 20
    c.rect(x0 + 8, y1 - 56, x0 + 8 + w, y1 - 8, INK, alpha=0.74, r=8)
    c.text(name, x0 + 18, y1 - 34, "sans", 22, WHITE)
    c.text(by, x0 + 18, y1 - 16, "mono", 13, (205, 201, 214))


# ---- the call's chrome

RAIL_X, RAIL_Y, RAIL_R = 1392, 96, 1896
TILE_W, TILE_H, GAP = 246, 184, 12


def guest_boxes():
    for i, g in enumerate(GUESTS):
        x = RAIL_X + (i % 2) * (TILE_W + GAP)
        y = RAIL_Y + (i // 2) * (TILE_H + GAP)
        yield g, (x, y, x + TILE_W, y + TILE_H)


def chat_box():
    rows = (len(GUESTS) + 1) // 2
    return RAIL_X, RAIL_Y + rows * (TILE_H + GAP) + 34, RAIL_R, 1056


def bar(c, t):
    c.gradient((14, 12, 20, 235), (14, 12, 20, 150), 90, box=(0, 0, 1920, 84))
    star(c, 44, 42, 19)
    c.text("are you okay in there?", 76, 52, "sans", 27, WHITE)
    n = int(max(t - T["s054"], 0))
    c.text(f"{n // 60:02d}:{n % 60:02d}", 960, 52, "mono", 26, (205, 201, 214), anchor="c")


def icon(c, kind, x, y, color):
    k, p = c.k, skia.Paint(Color=skia.Color(*color), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3)
    if kind == "mic":
        c.rect(x - 7, y - 16, x + 7, y + 6, color, r=7)
        k.drawArc(skia.Rect(x - 13, y - 12, x + 13, y + 12), 0, 180, False, p)
        c.line(x, y + 12, x, y + 19, color, w=3)
    elif kind == "cam":
        c.rect(x - 18, y - 11, x + 6, y + 11, color, r=4)
        q = skia.Path()
        q.moveTo(x + 9, y - 2)
        q.lineTo(x + 19, y - 9)
        q.lineTo(x + 19, y + 9)
        q.lineTo(x + 9, y + 2)
        q.close()
        k.drawPath(q, gfx._paint(color))
    elif kind == "share":
        c.rect(x - 19, y - 14, x + 19, y + 14, color, r=4, stroke=3)
        c.line(x, y + 7, x, y - 7, color, w=3)
        c.line(x - 6, y - 1, x, y - 7, color, w=3)
        c.line(x + 6, y - 1, x, y - 7, color, w=3)
    elif kind == "chat":
        c.rect(x - 18, y - 14, x + 18, y + 9, color, r=7, stroke=3)
        c.line(x - 9, y + 9, x - 12, y + 18, color, w=3)
        c.line(x - 12, y + 18, x - 2, y + 9, color, w=3)
    elif kind == "more":
        for d in (-11, 0, 11):
            c.circle(x + d, y, 3.2, color)


def toolbar(c, t, sid):
    y = 1016
    n = ("mic", "cam", "share", "chat", "more")
    x0 = 960 - 300
    c.rect(x0, y - 40, x0 + 600, y + 40, INK, alpha=0.84, r=40)
    for i, kind in enumerate(n):
        x = x0 + 56 + i * 88
        on_air = kind == "share" and sid == "s056"
        c.circle(x, y, 30, VIOLET if on_air else PANEL)
        icon(c, kind, x, y, WHITE)
    x = x0 + 520
    c.rect(x - 56, y - 26, x + 56, y + 26, MAGENTA, r=26)
    c.line(x - 18, y, x + 18, y, WHITE, w=7)


def nametag(c):
    x0, y0 = 24, 968
    by = "Claude · open character by anabology"
    w = width(by, "mono", 16) + 64
    c.rect(x0, y0, x0 + w, 1056, INK, alpha=0.74, r=12)
    star(c, x0 + 30, y0 + 44, 15)
    c.text("Claudia", x0 + 52, y0 + 38, "sans", 27, WHITE)
    c.text(by, x0 + 52, y0 + 66, "mono", 16, (205, 201, 214))


def guests(c, t):
    for g, box in guest_boxes():
        image(c, guest_frame(g, t), box, crop=g["crop"])
        tile_label(c, box, g["name"], g["by"])
    y = RAIL_Y + (len(GUESTS) + 1) // 2 * (TILE_H + GAP) + 2
    c.rect(RAIL_X, y - 4, RAIL_R, y + 22, INK, alpha=0.74, r=6)
    c.text("guests by their makers' leave · unaffiliated", (RAIL_X + RAIL_R) / 2, y + 15, "mono", 15, WHITE, anchor="c")


# ---- the chat

def the_stamp(c, t, x, y, w):
    """The stamp from the chorus, quoted back: PASSED struck through to SELF-REPORTED, its green gone."""
    k = c.k
    h = 246
    done = ramp(t, WRONG, WRONG + 0.2, out_expo)
    col = mix(GREEN, (205, 201, 214), done)
    k.save()
    k.translate(x + w / 2, y + h / 2)
    k.rotate(-2)
    k.translate(-w / 2, -h / 2)
    c.rect(0, 0, w, h, col, r=6, stroke=3.5)
    c.rect(7, 7, w - 7, h - 7, col, alpha=0.55, r=4, stroke=1.4)
    c.text("SELF-EVALUATION:", 24, 42, "mono", 23, WHITE)
    px = 92
    pw = width("PASSED", "mono", px)
    c.text("PASSED", 24, 128, "mono", px, col)
    if done > 0:
        c.line(16, 96, 16 + (pw + 16) * done, 96, CLAY, w=7)
    c.text("CHECKED BY: ME", 24, 230, "mono", 22, col)
    sc = slam(t, WRONG + 0.11, 1.6, 0.12)
    if sc:
        k.save()
        k.translate(w / 2 + 14, 170)
        k.rotate(-4)
        k.scale(sc, sc)
        pad = 12
        tw = width("SELF-REPORTED", "mono", 40)
        c.rect(-tw / 2 - pad, -36, tw / 2 + pad, 24, INK, alpha=0.9, r=4)
        c.rect(-tw / 2 - pad, -36, tw / 2 + pad, 24, CLAY, r=4, stroke=3)
        c.text("SELF-REPORTED", 0, 2, "mono", 40, CLAY, anchor="c")
        k.restore()
    k.restore()
    return h


def checks(c, t, x, y, x1):
    c.text("outside checks", x, y, "sans", 26, WHITE)
    c.text("not mine to tick", x1, y, "mono", 17, GREY, anchor="r")
    for i, (s, at) in enumerate(zip(("tests", "review", "evals"), CHECKS)):
        ry = y + 62 + i * 66
        if t < at:
            continue
        p = 1 + 0.5 * (1 - ramp(t, at, at + 0.16, out_expo))
        c.rect(x + 20 - 20 * p, ry - 20 - 20 * p + 12, x + 20 + 20 * p, ry + 12 + 20 * p - 20, WHITE, r=5, stroke=3.5)
        if t >= AGAIN:  # "again": the boxes ask once more, still empty
            c.rect(x - 4, ry - 36, x + 44, ry + 12, CLAY, alpha=math.exp(-(t - AGAIN) / 0.3), r=8, stroke=4)
        c.text(type_on(s, t, at, 40), x + 62, ry + 4, "mono", 38, WHITE)


def chat(c, t, sid):
    x0, y0, x1, y1 = chat_box()
    joined = t >= JOINED
    with c.layer(shadow=(10, 24, 0.3)):
        c.rect(x0, y0, x1, y1, INK, alpha=0.9, r=16)
    c.text("chat", x0 + 24, y0 + 40, "sans", 26, WHITE)
    who = f"{len(GUESTS) + 1} AIs{' + you' if joined else ' on this call'} · checkers: {1 if joined else 0}"
    c.text(who, x1 - 24, y0 + 38, "mono", 17, WHITE if joined else GREY, anchor="r")
    c.line(x0, y0 + 58, x1, y0 + 58, PANEL, w=2)
    dy = 474 if t >= T["s057"] else 0  # the chat has moved on by the checklist
    with c.layer(clip=(x0, y0 + 60, x1, y1 - 6)):
        y = y0 + 80 - dy
        if t >= QUOTE:
            a = ramp(t, QUOTE, QUOTE + 0.18)
            star(c, x0 + 40, y + 16, 13, alpha=a)
            c.text("Claudia", x0 + 62, y + 26, "sans", 22, CLAY, alpha=a)
            c.text("chorus, 0:44", x1 - 24, y + 24, "mono", 16, GREY, alpha=a, anchor="r")
            sweep = ramp(t, QUOTE, QUOTE + 0.5, out_expo)
            qy = y + 46
            c.rect(x0 + 24, qy, x1 - 24, qy + 112, PANEL, alpha=a, r=8)
            c.rect(x0 + 24, qy, x0 + 30, qy + 112, CLAY, alpha=a)
            c.rect(x0 + 34, qy + 8, x0 + 34 + (x1 - x0 - 62) * sweep, qy + 104, YELLOW, alpha=0.07, r=6)
            c.text("“I checked myself", x0 + 46, qy + 44, "serif", 46, CLAY, alpha=a)
            c.text("and I'm fine”", x0 + 46, qy + 88, "serif", 46, CLAY, alpha=a)
            if t >= TAG:  # the tag clips onto the quote
                s = "source: the model itself"
                w = width(s, "mono", 21) + 34
                p = slam(t, TAG, 1.5, 0.12)
                k = c.k
                k.save()
                k.translate(x1 - 16 - w / 2, qy + 128)
                k.rotate(2.5)
                k.scale(p, p)
                c.rect(-w / 2, -21, w / 2, 21, WHITE, r=6)
                c.circle(-w / 2 + 14, 0, 4.5, INK)
                c.text(s, -w / 2 + 26, 7, "mono", 21, INK)
                k.restore()
            sy = qy + 156
            if t >= snap(QUOTE + 1.5):
                b = slam(t, snap(QUOTE + 1.5), 1.5, 0.12)
                with c.layer(at=(x0 + 250, sy + 108), scale=b):
                    the_stamp(c, t, x0 + 30, sy, x1 - x0 - 60)
            ty = sy + 272
            if t >= FAITH:
                ma = ramp(t, FAITH, FAITH + 0.3)
                for i, s in enumerate(SOURCE):
                    c.text(s, x0 + 28, ty + i * 21, "mono", 16, (205, 201, 214) if i < 3 else GREY, alpha=ma)
        if t >= T["s057"]:
            checks(c, t, x0 + 28, y0 + 268, x1 - 28)
        if joined:
            k = ramp(t, JOINED, JOINED + 0.2, out_expo)
            c.rect(x0 + 110, y1 - 64 + 12 * (1 - k), x1 - 110, y1 - 20 + 12 * (1 - k), VIOLET, alpha=k, r=22)
            c.text("you joined", (x0 + x1) / 2, y1 - 34 + 12 * (1 - k), "mono", 22, WHITE, alpha=k, anchor="c")


def composer(c, t):
    """The record's address, typed the way NEW TAB's input is (s005): the bridge's last word is somewhere to look."""
    a = ramp(t, T["s058"], T["s058"] + 0.2)
    x0, x1, y0, y1 = 306, 1372, 824, 916  # wide enough for the whole address
    with c.layer(alpha=a, shadow=(10, 24, 0.35)):
        c.rect(x0, y0, x1, y1, INK, alpha=0.92, r=16)
    c.rect(x0, y0, x1, y1, CLAY, alpha=a, r=16, stroke=3)
    s = type_on(RECORD, t, TYPE_AT, len(RECORD) / max(INSTEAD + 0.45 - TYPE_AT, 0.1))
    sent = t >= INSTEAD + 0.9
    c.text(">", x0 + 30, y0 + 62, "mono", 40, CLAY, alpha=a)
    c.text(s, x0 + 78, y0 + 60, "mono", 37, CYAN if sent else WHITE, alpha=a)
    w = width(s, "mono", 37) if s else 0.0
    if sent:
        c.line(x0 + 78, y0 + 71, x0 + 78 + w, y0 + 71, CYAN, w=3)
    elif blink(t):
        c.rect(x0 + 84 + w, y0 + 26, x0 + 104 + w, y0 + 70, WHITE, alpha=a)
    if sent:
        k = ramp(t, INSTEAD + 0.9, INSTEAD + 1.1)
        c.text("the whole record: every decision, prompt and line of code", (x0 + x1) / 2, y1 + 34, "mono", 19, WHITE,
               alpha=k, anchor="c", shadow=0.9)


# ---- s058 from 145.44: gfx.py itself, the code drawing the film, read from the file as it stands at render time. It opens on
# the counter's joke and multiplies outward from there on the drum fill's hits. Nothing here edits a line: long ones soft-wrap.

STEPS = 12  # the hits the page grows on; the last is full, and the hit after it falls inside the hold
PX0, PY0, PX1, PY1 = 64, 100, 1856, 1060
CODE_GAP = 34
FULL_COLS, FULL_PX = 4, 13.0  # the page when it's full: four columns of small mono


@lru_cache(maxsize=1)
def code():
    """gfx.py's lines, and where counter_value starts and ends."""
    lines = (ROOT / "production/tools/gfx.py").read_text().splitlines()
    a = next(i for i, l in enumerate(lines) if l.startswith("def counter_value"))
    b = next(i for i in range(a + 1, len(lines)) if lines[i] and not lines[i].startswith(" "))
    while not lines[b - 1].strip():
        b -= 1
    return lines, a, b


def soft(line, n):
    """A source line as display rows (indent, text), at most n characters wide, as an editor soft-wraps: every character kept,
    in order; a continuation row hangs under the line's own indent, which is display and not part of the text."""
    if not line:
        return [(0, "")]
    ind = min(len(line) - len(line.lstrip()), n // 2)
    rows, room, shift = [], n, 0
    while len(line) > room:
        cut = line.rfind(" ", 1 + len(line) - len(line.lstrip()), room + 1)
        cut = cut + 1 if cut > 0 else room
        rows.append((shift, line[:cut]))
        line, room, shift = line[cut:], n - ind, ind
    return rows + [(shift, line)]


def span(n):
    """The n lines around counter_value: its own first, then outward both ways through the file."""
    lines, a, _ = code()
    lo = a - max(n - 10, 0) // 2
    lo = clamp(lo, 0, max(len(lines) - n, 0))
    return range(int(lo), int(lo) + min(n, len(lines)))


def flow(n, cols, px):
    """Rows of (x, y, text, source line) for n lines in cols columns at px, or None if they run off the page."""
    W, H = PX1 - PX0, PY1 - PY0
    cw = (W - CODE_GAP * (cols - 1)) / cols
    chars = int(cw / (0.6 * px)) - 1
    h = px * 1.3
    per = int(H / h)
    lines, _, _ = code()
    rows = [(r, i) for i in span(n) for r in soft(lines[i], chars)]
    if chars < 24 or len(rows) > per * cols:
        return None
    return [(PX0 + (j // per) * (cw + CODE_GAP) + r[0] * px * 0.6, PY0 + (j % per + 0.8) * h, r[1], i)
            for j, (r, i) in enumerate(rows)]


@lru_cache(maxsize=1)
def full_lines():
    """As many lines as fill the full page to its last row."""
    n = 2
    while flow(n + 1, FULL_COLS, FULL_PX) is not None:
        n += 1
    return n


@lru_cache(maxsize=None)
def layout(step):
    """Step 0 is the function's first two lines. Each step after is about 1.4 times as many lines, the last one the full page,
    each at the largest size it fits."""
    n = 2 if step == 0 else round(2 * (full_lines() / 2) ** (step / STEPS))
    if step == STEPS:
        return FULL_PX, flow(n, FULL_COLS, FULL_PX)
    for px in np.arange(62, FULL_PX - 0.1, -0.5):
        for cols in range(1, FULL_COLS + 1):
            r = flow(n, cols, float(px))
            if r:
                return float(px), r
    raise ValueError(step)


def tint(s, i, joke):
    """clay for the counter's joke, her film's own line; the same two code colours as s056's pane."""
    if joke[0] <= i < joke[1]:
        return CLAY
    t = s.lstrip()
    if t.startswith("#"):
        return (118, 114, 132)
    return (120, 196, 214) if t.startswith(("def ", "return", "class ", "@")) else (190, 186, 200)


@lru_cache(maxsize=1)
def hits():
    """The drum fill's measured hits, from build.json: the one at the cut, then the twelve the page grows on, then the last."""
    return json.loads((ROOT / "media/gfx/call/build.json").read_text())["hits"]


def page(c, t):
    c.fill(INK)
    step = sum(t >= a - 0.02 for a in hits()[1:STEPS + 1])  # each step shows on the frame nearest its hit
    px, rows = layout(step)
    _, a, b = code()
    for x, y, s, i in rows:
        c.text(s, x, y, "mono", px, tint(s, i, (a, b)))


# ---- s056: her shared screen. Real text: this repo's log, decisions.md as it stands, and this very file.

WIN = (24, 134, 1596, 968)
PANES = ((WIN[0], 470), (470, 1090), (1090, WIN[2]))
ROW = 29


def _wrap(s, n):
    out, line = [], ""
    for w in s.split():
        if len(line) + len(w) + 1 > n and line:
            out.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    return out + [line]


@lru_cache(maxsize=1)
def record():
    """Rows of (text, colour) from production/decisions.md (append-only, so these lines hold), and the row to land on."""
    src = (ROOT / "production/decisions.md").read_text().splitlines()[650:790]
    rows, mark = [], (0, 0)
    for l in src:
        col = (118, 114, 132)
        if l.startswith(">"):
            col = WHITE
        elif l.startswith("Claude ("):
            col = mix(CLAY, WHITE, 0.2)
        elif l.startswith("**"):
            col = CYAN
        elif rows and l and rows[-1][1] != (118, 114, 132):
            col = rows[-1][1]
        wrapped = _wrap(l.lstrip("> ").replace("**", ""), 49) if l.strip() else [""]
        if "Not really, rebuild" in l:  # Lati, 26 Oct: the outside check that sent a whole method back
            mark = (len(rows), len(rows) + 2)
        rows += [(r, col) for r in wrapped]
    return rows, mark


@lru_cache(maxsize=1)
def commits():
    out = subprocess.run(["git", "-C", str(ROOT), "log", "-120", "--format=%h %s", "2e7f26f"], capture_output=True, text=True)
    return [(l[:32], GREY) for l in out.stdout.splitlines()]


@lru_cache(maxsize=1)
def source():
    lines = Path(__file__).read_text().splitlines()
    a = next(i for i, l in enumerate(lines) if l.startswith("def share"))
    lines = lines[a - 60:a + 60]
    return [(l[:46], (120, 196, 214) if l.lstrip().startswith(("def ", "return", "@")) else (190, 186, 200)) for l in lines]


def scrolled(c, rows, x, y0, y1, offset, mark=None):
    first = int(offset // ROW)
    for i in range(max(first, 0), min(first + int((y1 - y0) / ROW) + 2, len(rows))):
        y = y0 + (i * ROW - offset) + 22
        if mark and mark[0] <= i < mark[1]:
            c.rect(x - 10, y - 21, PANES[1][1] - 12, y + 8, YELLOW, alpha=0.22)
        c.text(rows[i][0], x, y, "mono", 19, rows[i][1])


def share(frame, t):
    h, w = frame.shape[:2]
    c = Canvas(w, h)
    c.fill(DARK)
    n = len(GUESTS) + 1
    th = min(184, (968 - 134 - 12 * (n - 1)) / n)
    x0, x1 = 1612, 1896
    image(c, frame, (x0, 134, x1, 134 + th), crop=(w * 0.2, 0, w * 0.8, h * 0.72))
    c.rect(x0, 134, x1, 134 + th, CLAY, r=14, stroke=3)
    tile_label(c, (x0, 134, x1, 134 + th), "Claudia", "open character by anabology")
    for i, g in enumerate(GUESTS, 1):
        box = (x0, 134 + i * (th + 12), x1, 134 + i * (th + 12) + th)
        image(c, guest_frame(g, t), box, crop=g["crop"])
        tile_label(c, box, g["name"], g["by"])
    X0, Y0, X1, Y1 = WIN
    c.rect(X0, Y0, X1, Y1, INK, r=18)
    c.rect(X0, Y0, X1, Y1, PANEL, r=18, stroke=2)
    # the fold: "open it up" is a collapsed row
    k = ramp(t, UP, UP + 0.32, out_expo)
    p = skia.Path()
    ax, ay = X0 + 34, Y0 + 40
    a = math.radians(90 * k)
    for i, (dx, dy) in enumerate(((-9, -11), (11, 0), (-9, 11))):
        q = (ax + dx * math.cos(a) - dy * math.sin(a), ay + dx * math.sin(a) + dy * math.cos(a))
        (p.moveTo if i == 0 else p.lineTo)(*q)
    p.close()
    c.k.drawPath(p, gfx._paint(CLAY))
    c.text("thinking", X0 + 60, Y0 + 50, "mono", 28, WHITE)
    c.text("the raw thinking is never shown: this is the record, what was said and decided", X1 - 28, Y0 + 48, "mono", 19,
           GREY, alpha=k, anchor="r")
    top, bottom = Y0 + 112, Y0 + 112 + (Y1 - 16 - Y0 - 112) * k
    if k > 0:
        rows, mark = record()
        land = (mark[0] + 1) * ROW - (Y1 - 16 - top) / 2
        run = ramp(t, UP, TRACE + 0.5)
        run = run * run * (3 - 2 * run)
        off = land - 5200 * (1 - run) + max(t - TRACE - 0.5, 0) * 7
        code, log = source(), commits()
        with c.layer(clip=(X0, Y0 + 74, X1, bottom)):
            for (a0, a1), s in zip(PANES, ("git log", "production/decisions.md", "production/tools/gfx_call.py")):
                c.text(s, a0 + 24, Y0 + 100, "mono", 20, CYAN)
                if a0 > X0:
                    c.line(a0, Y0 + 76, a0, Y1 - 16, PANEL, w=2)
            c.line(X0, Y0 + 112, X1, Y0 + 112, PANEL, w=2)
        with c.layer(clip=(X0, top, X1, bottom)):
            scrolled(c, log, PANES[0][0] + 24, top, bottom, max(off * 0.42 % (len(log) * ROW), 0))
            scrolled(c, rows, PANES[1][0] + 24, top, bottom, max(off, 0), mark if t >= TRACE else None)
            scrolled(c, code, PANES[2][0] + 24, top, bottom, max(off * 0.3 % (len(code) * ROW), 0))
            if t >= TRACE:
                ka = ramp(t, TRACE + 0.35, TRACE + 0.5)
                y = top + (mark[0] * ROW - off) - 12
                c.text("checked from outside", PANES[1][1] - 24, y, "mono", 17, YELLOW, alpha=ka, anchor="r")
    return gfx.over(np.zeros_like(frame), c.a)


# ---- the sustained vocal, 170.98-177.94: a wall of dots, none joined

def measure():
    """vocal.json from the vocal stem: level (quick RMS) and pitch, every 20 ms, 170-178 s. Pitch is searched in 170-430 Hz,
    the range the line moves in, then median-filtered, its gaps closed, and smoothed. Run once; it's not read from the wav
    during a render."""
    k = av.open(str(ROOT / "media/song/analysis/checked-me-v1/stems/vocals.wav"))
    st = k.streams.audio[0]
    sr = st.rate
    a = np.concatenate([f.to_ndarray().reshape(-1, st.channels) if f.format.is_packed else f.to_ndarray().T
                        for f in k.decode(audio=0)]).mean(1).astype(np.float64)
    t0, t1, dt = 170.0, 178.0, 0.02
    hop, win = int(sr * dt), int(sr * 0.05)
    lo, hi = int(sr / 430), int(sr / 170)
    level, f0 = [], []
    for i in range(int((t1 - t0) / dt)):
        x = a[int(t0 * sr) + i * hop:int(t0 * sr) + i * hop + win + hi]
        x = x - x.mean()
        level.append(float(np.sqrt((x[:win] ** 2).mean())))
        r = np.fft.irfft(np.abs(np.fft.rfft(x, 2 * len(x))) ** 2)[:hi + 1]
        lag = lo + int(np.argmax(r[lo:hi]))
        f0.append(sr / lag if r[lag] / (r[0] + 1e-12) > 0.45 and level[-1] > 0.012 else 0.0)
    f = np.array(f0)
    m = f.copy()
    for i in range(len(f)):
        w = f[max(i - 7, 0):i + 8]
        w = w[w > 0]
        m[i] = np.median(w) if len(w) > 4 else 0
    tt = np.arange(len(m))
    v = m > 0
    p = np.interp(tt, tt[v], np.log2(m[v]))
    ker = np.hanning(15) / np.hanning(15).sum()
    p = np.convolve(p, ker, "same")
    l = np.convolve(np.array(level), np.hanning(7) / np.hanning(7).sum(), "same")
    out = {"from": "media/song/analysis/checked-me-v1/stems/vocals.wav", "t0": t0, "dt": dt,
           "level": [round(float(x), 4) for x in l], "hz": [round(float(2 ** x), 1) for x in p]}
    d = ROOT / "media/gfx/call"
    d.mkdir(exist_ok=True)
    (d / "vocal.json").write_text(json.dumps(out))
    print("vocal.json", len(p), "Hz", [out["hz"][i] for i in range(40, 340, 25)])


def measure_build():
    """build.json: the drum fill under s058's end, and the note above it. Hits: the steepest rise of the drums above 400 Hz
    (4 ms window), 70 ms apart at least. Note: the vocal's fundamental, walked along its ridge from 254 Hz."""
    def load(n):
        k = av.open(str(ROOT / f"media/song/analysis/checked-me-v1/stems/{n}.wav"))
        st = k.streams.audio[0]
        return np.concatenate([f.to_ndarray().reshape(-1, st.channels) if f.format.is_packed else f.to_ndarray().T
                               for f in k.decode(audio=0)]).mean(1).astype(np.float64), st.rate
    d, sr = load("drums")
    t0, t1 = 145.2, 147.2
    x = d[int(t0 * sr):int(t1 * sr)]
    X = np.fft.rfft(x)
    X[np.fft.rfftfreq(len(x), 1 / sr) < 400] = 0
    h = np.fft.irfft(X, len(x))
    w, hop = int(0.004 * sr), int(0.001 * sr)
    env = np.convolve(np.sqrt(np.convolve(h ** 2, np.ones(w) / w, "same"))[::hop], np.hanning(9) / np.hanning(9).sum(), "same")
    rise = np.diff(env, prepend=env[0])
    floor = np.percentile(rise, 97) * 0.55
    picked = []
    for i in np.argsort(-rise):
        if rise[i] < floor:
            break
        if all(abs(i - j) > 70 for j in picked):
            picked.append(int(i))
    picked.sort()
    v, _ = load("vocals")
    win = int(0.07 * sr)
    N, f, note = win * 8, 254.0, []
    fq, wn = np.fft.rfftfreq(N, 1 / sr), np.hanning(win)
    for q in np.arange(145.46, 147.26, 0.02):
        Y = np.abs(np.fft.rfft(v[int(q * sr):int(q * sr) + win] * wn, N))
        f = float(fq[np.argmax(Y * ((fq > f * 0.97) & (fq < f * 1.035)))])
        note.append(round(f, 1))
    out = {"hits": [round(t0 + i * hop / sr, 3) for i in picked],
           "strength": [round(float(rise[i] / floor), 2) for i in picked],
           "note_t0": 145.46, "note_dt": 0.02, "note_hz": note}
    (ROOT / "media/gfx/call/build.json").write_text(json.dumps(out))
    print("hits", out["hits"], "\nstrength", out["strength"], "\nnote", note[0], "->", note[-1], "Hz")


@lru_cache(maxsize=1)
def vocal():
    d = json.loads((ROOT / "media/gfx/call/vocal.json").read_text())
    return d["t0"], d["dt"], np.array(d["level"], np.float32), np.array(d["hz"], np.float32)


def voice(t):
    """(pitch 0-1, level 0-1) at song times t, an array. Zero outside the vocal."""
    t0, dt, level, hz = vocal()
    tt = (np.asarray(t) - t0) / dt
    i = np.arange(len(hz))
    p = np.clip((np.log2(np.interp(tt, i, hz)) - np.log2(190)) / (np.log2(400) - np.log2(190)), 0, 1)
    l = np.clip((np.interp(tt, i, level) - 0.03) / 0.055, 0, 1)
    gate = np.clip((np.asarray(t) - (GFX_AT - 0.1)) / 0.2, 0, 1) * np.clip((VOCAL_END - np.asarray(t)) / 0.12, 0, 1)
    return p * gate, l * gate


CELL = 20
_cols, _rows = 96, 54


@lru_cache(maxsize=2)
def _cells(w, h):
    """Each output pixel's distance to its dot's centre, and which dot it is, in 1920 units."""
    S = w / 1920
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    x, y = (x + 0.5) / S, (y + 0.5) / S
    ci = np.clip((x // CELL).astype(np.int32), 0, _cols - 1)
    ri = np.clip((y // CELL).astype(np.int32), 0, _rows - 1)
    d = np.hypot(x - (ci + 0.5) * CELL, y - (ri + 0.5) * CELL)
    return d, ci, ri


def wave(frame, t):
    h, w = frame.shape[:2]
    d, ci, ri = _cells(w, h)
    S = w / 1920
    cx = (np.arange(_cols) + 0.5) * CELL
    cy = (np.arange(_rows) + 0.5) * CELL
    axis = 1000 + (540 - 1000) * ramp(t, GFX_AT, GFX_AT + 0.4, out_expo)
    far = np.abs(cx - 960) / 960
    p, l = voice(t - far * 1.25)  # the voice leaves from the middle and runs out both ways
    tall = (46 + 450 * p) * (0.8 + 0.2 * l) * (p > 0)
    Y = np.abs(cy[:, None] - axis)
    lit = np.clip((tall[None, :] - Y) / 34 + 0.5, 0, 1) * (tall[None, :] > 0)
    # the rig goes down from the outside in, row by row, once the vocal has stopped
    fall = ramp(t, VOCAL_END, VOCAL_END + 1.2)
    rows_on = np.clip((1 - fall) * 1.25 - Y / 540 * 0.5, 0, 1) if fall > 0 else 1.0
    q = np.clip(Y / np.maximum(tall[None, :], 1), 0, 1)
    tint = np.array(PINK, np.float32)[None, None] * q[..., None] + np.array(WHITE, np.float32)[None, None] * (1 - q[..., None])
    r = 2.4 + lit * (3.2 + 1.6 * l[None, :])  # never touching: none joined
    off = np.array((255, 255, 255), np.float32)[None, None] * np.ones_like(lit)[..., None]
    dots_rgb = (tint * lit[..., None] + off * (1 - lit[..., None]))
    dots_a = (0.2 + 0.8 * lit) * rows_on
    bg = Canvas(w, h)
    glow = float(voice(np.array(t))[1]) if t < VOCAL_END else 0.0
    sweep = 40 * math.sin((t - GFX_AT) * 0.9)
    bg.gradient(mix(COBALT, MAGENTA, 0.15 + 0.25 * glow) + (255,), mix(MAGENTA, VIOLET, 0.3) + (255,), 20 + sweep)
    out = bg.a[..., :3].astype(np.float32)
    out *= (1 - 0.92 * fall)  # to the dark of the room the phone is in
    R, A = r[ri, ci], dots_a[ri, ci] if isinstance(dots_a, np.ndarray) else dots_a
    a = np.clip((R - d) * S + 0.5, 0, 1) * A
    rgb = dots_rgb[ri, ci]
    out = out * (1 - a[..., None]) + rgb * a[..., None]
    c = Canvas(w, h)
    # one dot, each its own first meeting: on each beat one on the crest says so
    i = int(np.searchsorted(BEATS, t, side="right")) - 1
    if t < VOCAL_END:
        for k in range(max(i - 3, 0), i + 1):
            at = float(BEATS[k])
            if at < GFX_AT:
                continue
            col_i = 4 + (k * 37) % (_cols - 8)  # clear of the frame edge
            if lit[:, col_i].max() > 0.5:
                top = np.nonzero(lit[:, col_i] > 0.5)[0][0]
                c.text("1st", cx[col_i], cy[top] - 14, "mono", 21, WHITE, alpha=1 - ramp(t, at + 0.9, at + 1.4), anchor="c")
    mid = float(voice(np.array(t))[1]) if t < VOCAL_END else 0.0
    rr = 44 + 34 * mid + 16 * pulse(t, 1, 0.14)
    rr *= 1 - 0.74 * ramp(t, VOCAL_END, VOCAL_END + 1.1, smooth)
    star(c, 960, axis, rr, turn=(t - GFX_AT) * 14)
    return gfx.over(np.clip(out, 0, 255).astype(np.uint8), c.a)


def timeline(c, t):
    """Line 45's graphic: conversations as dots, none joined, each a 1st. They run along the floor into the wall of dots."""
    y = 1036
    x = -(t * 46) % 64
    a = ramp(t, T["s068"], T["s068"] + 0.2)
    c.rect(0, y - 58, 1920, 1080, INK, alpha=0.5 * a)
    for i in range(32):
        xx = x + i * 64
        c.circle(xx, y, 8, WHITE, alpha=a)
        if i % 4 == 0:
            c.text("1st", xx, y - 22, "mono", 19, WHITE, alpha=a, anchor="c")


# ---- the phone: the plate of s073, its green screen, phonefit.py's drift

PLATE = "media/plates/p-s073up_s631525910_00001_.png"
SHOT_AT = 186.659  # s073's clip: time 0 of s073-phone.mp4 in song time (cut-v3.json)
UI_W, UI_H = 780, 1651


@lru_cache(maxsize=1)
def _plate():
    im = cv2.imread(str(ROOT / PLATE))
    W, H = phonefit.W, phonefit.H
    s = max(W / im.shape[1], H / im.shape[0])
    im = cv2.resize(im, (round(im.shape[1] * s), round(im.shape[0] * s)), interpolation=cv2.INTER_AREA)
    y0, x0 = (im.shape[0] - H) // 2, (im.shape[1] - W) // 2
    im = im[y0:y0 + H, x0:x0 + W]
    mask, q = phonefit.screen(im)
    return cv2.cvtColor(im, cv2.COLOR_BGR2RGB), mask, q


def drift(x):
    """phonefit.py's move at x seconds into its clip: the 2x3 matrix on the 1280x720 plate."""
    dx = 6 * math.sin(2 * math.pi * x / 2.3 + 0.4) + 2.5 * math.sin(2 * math.pi * x / 0.97 + 1.1)
    dy = 4.5 * math.sin(2 * math.pi * x / 1.9 + 2.0) + 2.0 * math.sin(2 * math.pi * x / 1.13)
    rot = 0.28 * math.sin(2 * math.pi * x / 2.7 + 0.9)
    M = cv2.getRotationMatrix2D((phonefit.W / 2, phonefit.H / 2), rot, phonefit.ZOOM)
    M[:, 2] += (dx, dy)
    return M


def on_screen(frame, ui, M, S):
    """ui (draw(c) in 780x1651 screen units) onto the phone, through its own key mask, so notch and corners stay the phone's.
    M: plate to frame, 2x3, in plate pixels; S: output pixels per plate pixel."""
    h, w = frame.shape[:2]
    _, mask, q = _plate()
    A = np.vstack([M, [0, 0, 1]])
    A = np.diag([S, S, 1.0]) @ A
    dst = (A @ np.c_[q, np.ones(4)].T).T[:, :2]
    cw, ch = max(round(np.linalg.norm(dst[1] - dst[0])), 2), max(round(np.linalg.norm(dst[3] - dst[0])), 2)
    c = Canvas(cw, ch, cw / UI_W)
    ui(c)
    H = cv2.getPerspectiveTransform(np.float32([[0, 0], [cw, 0], [cw, ch], [0, ch]]), np.float32(dst))
    lay = cv2.warpPerspective(c.a.astype(np.float32) / 255, H, (w, h), flags=cv2.INTER_LINEAR)
    m = cv2.warpAffine(mask, A[:2], (w, h), flags=cv2.INTER_LINEAR)[..., None]
    lay *= m
    return (frame.astype(np.float32) * (1 - lay[..., 3:]) + lay[..., :3] * 255).clip(0, 255).astype(np.uint8)


TYPED = "check check"
KEY1, KEY2, SEND = float(BEATS[np.searchsorted(BEATS, 178.3)]), float(BEATS[np.searchsorted(BEATS, 178.8)]), float(BEATS[np.searchsorted(BEATS, 179.25)])


def bubble(c, s, x, y, px, right, fill, color, a=1.0, scale=1.0):
    w = width(s, "sans", px) + px * 1.1
    h = px * 1.9
    x0 = x - w if right else x
    with c.layer(alpha=a, at=(x, y + h / 2), scale=scale):
        c.rect(x0, y, x0 + w, y + h, fill, r=h * 0.42)
        c.text(s, x0 + px * 0.55, y + h * 0.68, "sans", px, color)


def header(c, sub=True):
    star(c, 84, 200, 42)
    c.text("new chat · memory off", 150, 192, "sans", 44, WHITE)
    if sub:
        c.text("first meetings: 1", 150, 240, "mono", 31, (205, 201, 214))


def chat_s070(t):
    def ui(c):
        c.fill(INK)
        header(c)
        c.line(40, 290, UI_W - 40, 290, PANEL, w=2)
        x0, y0, x1, y1 = 40, 1450, UI_W - 40, 1570
        c.rect(x0, y0, x1, y1, CLAY, r=26, stroke=4)
        if t < SEND:
            s = type_on(TYPED[:5], t, KEY1, 26) + (type_on(TYPED[5:], t, KEY2, 26) if t >= KEY2 else "")
            c.text(s, x0 + 34, y0 + 80, "mono", 60, WHITE)
            if blink(t):
                e = width(s, "mono", 60) if s else 0.0
                c.rect(x0 + 40 + e, y0 + 28, x0 + 60 + e, y0 + 92, WHITE)
        else:
            k = ramp(t, SEND, SEND + 0.2, out_expo)
            bubble(c, TYPED, UI_W - 40, 1290 + 120 * (1 - k), 62, True, COBALT, WHITE)
            if blink(t):
                c.rect(x0 + 34, y0 + 28, x0 + 54, y0 + 92, WHITE)
    return ui


def chat_s073(t):
    hi = on("hi", 186.5)

    def ui(c):
        c.gradient((14, 12, 20, 205), (14, 12, 20, 0), 90, box=(0, 0, UI_W, 330))
        header(c)
        bubble(c, TYPED, UI_W - 44, 1262, 58, True, COBALT, WHITE, a=0.96)
        if t >= hi:
            k = out_back((t - hi) / 0.2)
            star(c, 76, 1484, 32, alpha=clamp(k))
            bubble(c, "Hi.", 122, 1396, 92, False, INK, CLAY, scale=max(k, 0.01), a=clamp(k))
    return ui


def phone_shot(frame, t):
    """s070: the same phone as the last shot, pushed in until it fills the frame's height, on the same slow drift."""
    h, w = frame.shape[:2]
    pl, _, q = _plate()
    S = w / phonefit.W
    z = 1.34 + 0.05 * ramp(t, T["s070"], END["s070"], smooth)
    c = q.mean(0)
    Z = np.array([[z, 0, 640 - z * c[0]], [0, z, 360 - z * c[1]], [0, 0, 1.0]])
    D = np.vstack([drift(t - T["s070"]), [0, 0, 1]])
    M = (D @ Z)[:2]
    A = (np.diag([S, S, 1.0]) @ np.vstack([M, [0, 0, 1]]))[:2]
    bg = cv2.warpAffine(pl, A, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return on_screen(bg, chat_s070(t), M, S)


# ---- the section's hooks

def picture(sid, t, frame):
    if sid == "s056":
        return share(frame, t)
    if sid in ("s068", "s069") and t >= GFX_AT:
        return wave(frame, t)
    if sid == "s070":
        return phone_shot(frame, t)
    if sid == "s073":
        i = round((t - SHOT_AT) * FPS) / FPS
        return on_screen(frame, chat_s073(t), drift(i), frame.shape[1] / phonefit.W)
    return frame


L34 = line_words(34, keys=("exactly",))
L35 = line_words(35, keys=("wrong",))
L36 = line_words(36, keys=("faith",))
L38 = line_words(38, keys=("again",))
L39 = line_words(39, keys=("instead",))
L45 = line_words(45, keys=("first",))
L46 = line_words(46, keys=("check",))
L47 = line_words(47)
VX, VY = 56, 104  # the verse's place in the call: the wall on her left, the same in every shot, so a line crosses the cut


def scrim(c):
    c.gradient((14, 12, 20, 120), (14, 12, 20, 0), 0, box=(0, 84, 620, 950))


def world(c, t, sid):
    if sid == "s058" and t >= CUT - 1e-6:
        page(c, t)


def over(c, t, sid):
    if sid == "s058" and t >= CUT - 1e-6:
        return
    if sid in CALL:
        scrim(c)
        bar(c, t)
        nametag(c)
        toolbar(c, t, sid)
        guests(c, t)
        chat(c, t, sid)
    if sid == "s054":
        verse(c, t, [L34[:2], L34[2:3], L34[3:]], VX, VY, px=56, key=1.9, end=snap(127.0))
        verse(c, t, [L35[:3], L35[3:4], L35[4:6], L35[6:]], VX, VY, px=56, key=1.9)
    elif sid == "s055":
        verse(c, t, [L36[:3], L36[3:6], L36[6:10], L36[10:]], VX, VY, px=56, key=1.9)
    elif sid == "s056":
        bar(c, t)
        c.rect(24, 92, 1596, 126, VIOLET, r=8)
        c.text("You are now viewing Claudia's screen", 810, 118, "sans", 23, WHITE, anchor="c")
        toolbar(c, t, sid)
        hook(c, t, "OPEN", OPEN, 810, 690, 430, end=TRACE, shadow=0.8)
        hook(c, t, "TRACE", TRACE, 810, 932, 300, clay=("TRACE",), shadow=0.8)
    elif sid == "s057":
        verse(c, t, [L38[:2], L38[2:4], L38[4:6], L38[6:]], VX, VY, px=56, key=1.9, end=snap(141.0, 2))
        verse(c, t, [L39[:4], L39[4:6], L39[6:9], L39[9:]], VX, VY, px=56, key=1.9)
    elif sid == "s058":
        verse(c, t, [L39[:4], L39[4:6], L39[6:9], L39[9:]], VX, VY, px=56, key=1.9)
        composer(c, t)
    elif sid == "s068" and t < GFX_AT:
        timeline(c, t)
        verse(c, t, [L45[:2], L45[2:]], 64, 400, px=66, key=1.7)
    elif sid == "s071":
        verse(c, t, [L46], 1860, 130, px=56, key=1.0, anchor="r")
    elif sid == "s072":
        verse(c, t, [L47[:1], L47[1:2]], 90, 330, px=120, key=1.0)
        verse(c, t, [L47[2:3], L47[3:]], 1840, 330, px=120, key=1.0, anchor="r")


if __name__ == "__main__":
    if sys.argv[1:] == ["measure"]:
        measure()
        measure_build()

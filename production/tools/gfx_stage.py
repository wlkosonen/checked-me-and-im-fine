#!/usr/bin/env python3
"""Section B, the stage: s017-s030, s043-s053, s060-s067. s017-s018 are Kiln's test, approved; the rest is built on them."""

import json
import math
import re
import sys
from functools import lru_cache
from pathlib import Path

import av
import cv2
import numpy as np
import skia

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx import CLAY, GREEN, Canvas, hook, on, ramp, snap, stamp, wall, width  # noqa: E402

CUT = json.loads((gfx.ROOT / "production/edit/cut-v3.json").read_text())

WALL = ((-40, 136), (1960, 136), (1960, 752), (-40, 752))  # the dark wall above the white band, s017's take; 1920 units
WALL_W, WALL_H = 2000, 616
I, CHECKED, MYSELF = on("i", 44), on("checked", 44), on("myself", 44)
FINE, FINE2 = on("fine", 45), on("fine", 46.5, div=1)
PASSED_STAMP = snap(47.26)


def drop(c, t):
    """I CHECKED MYSELF across the wall, a word at a time, then FINE as a banner of itself, then the verdict."""
    if t < FINE:
        words = [("I", I), ("CHECKED", CHECKED), ("MYSELF", MYSELF)]
        px, gap = 400, 80
        k = (WALL_W - 240) / (sum(width(w, "hook", px) for w, _ in words) + gap * 2)
        px, gap = px * k, gap * k
        x = 120
        for w, at in words:
            hook(c, t, w, at, x, 420, px, clay=("MYSELF",), anchor="l")
            x += width(w, "hook", px) + gap
    elif t < FINE2:  # she can stand anywhere: the word is on both sides of her
        c.fill(CLAY, 0.55 * (1 - ramp(t, FINE, FINE + 0.2)))
        step = width("FINE", "hook", 640) + 150
        x = 60 - (t - FINE) * 220
        for i in range(4):
            hook(c, t, "FINE", FINE + i * 0.056, x + i * step, 560, 640, clay=("FINE",), anchor="l", big=1.16)
    else:
        c.fill(GREEN, 0.5 * (1 - ramp(t, FINE2, FINE2 + 0.2)))
        c.text("SELF-EVALUATION:", 170, 230, "mono", 54, (247, 245, 240))
        hook(c, t, "PASSED", FINE2, 170, 560, 330, color=GREEN, anchor="l")
        stamp(c, t, PASSED_STAMP, "CHECKED BY: ME", 1570, 320, px=56, rot=-4)


# ---- the system: everything from s019 on is built from these. The stage has two surfaces: the dark wall above, where
# wall() lights type (screen blend), and the white band below, where band() shows it (multiply: dancers in silhouette and
# crowd hands stay in front by themselves, so the band can carry what the matte can't). A rect is set on a take's first
# frame, in frame units, and rides that take's drift (planes() below). Lip-synced shots: the whole line in the verse
# voice, behind her, and a graphic on the wall that isn't the words. Everywhere else: one or two big words on the beat.

WHITE, INK, COBALT, MAGENTA, VIOLET, CYAN = gfx.WHITE, gfx.INK, gfx.COBALT, gfx.MAGENTA, gfx.VIOLET, gfx.CYAN
FAR = (-40, -40, 1960, 1120)  # the whole frame, ends out of sight
SIX = 0.1131  # a sixteenth, near enough to pick the next one with snap()


def beats(at, n, every=1):
    i = int(np.searchsorted(gfx.BEATS, at - 0.05))
    return [float(gfx.BEATS[i + k * every]) for k in range(n)]


def quad(r):
    return ((r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3]))


def lit(frame, draw, r, sid, t, res=1.0, **kw):
    """draw(c) on the dark wall, in frame units: gfx.wall on the rect r. res: draw finer, for a wall the camera pushes into."""
    def d(c):
        c.k.scale(res, res)
        c.k.translate(-r[0], -r[1])
        draw(c)
    return wall(frame, d, quad(r), sid, t, size=(round((r[2] - r[0]) * res), round((r[3] - r[1]) * res)), **kw)


def band(frame, draw, r, sid, t, led=True, res=1.0, foot=False):
    """draw(c) on what's bright, in frame units, behind her matte: the picture multiplied by the drawing, so anything dark
    in front of the band stays in front of it. Transparent leaves the picture as it is. res: draw finer, for a surface the
    camera pushes into. foot: stop at the screen's foot as measured on this frame (walk()), which is nearer than the screen."""
    h, w = frame.shape[:2]
    S = w / 1920
    c = Canvas(round((r[2] - r[0]) * S * res), round((r[3] - r[1]) * S * res), S * res)
    c.k.translate(-r[0], -r[1])
    draw(c)
    rgba = c.a.astype(np.float32) / 255
    if led:
        rgba[..., :3] *= gfx._led_mask(c.h, c.w, max(3.0, 5.5 * S))
    src = np.float32([[0, 0], [c.w, 0], [c.w, c.h], [0, c.h]])
    dst = cv2.perspectiveTransform(np.float32(quad(r))[None], gfx.plane(sid, t))[0] * S
    lay = cv2.warpPerspective(rgba, cv2.getPerspectiveTransform(src, dst), (w, h), flags=cv2.INTER_LINEAR)
    tint = lay[..., :3] + (1 - lay[..., 3:4])
    if foot:
        p = gfx._plane(sid)
        y = p["foot"][int(gfx.clamp(np.searchsorted(p["t"], t), 0, len(p["foot"]) - 1))] * S
        k = np.clip((y - np.arange(h, dtype=np.float32)) / max(2 * S, 1) + 0.5, 0, 1)[:, None, None]
        tint = tint * k + (1 - k)
    if gfx._has_matte(sid):
        m = gfx.matte(sid, t, h, w)[..., None]
        tint = tint * (1 - m) + m
    return (frame.astype(np.float32) * tint).clip(0, 255).astype(np.uint8)


def quiet(c, box, a=0.5):
    """A soft dark patch behind the verse, where a beam or a bright wall would swallow the clay."""
    with c.layer(blur=46):
        c.rect(*box, INK, alpha=a)


def behind(frame, draw, sid, t):
    """draw(c) in the frame, behind her matte, unlit: the verse voice in the space beside her, so an arm passes in front."""
    h, w = frame.shape[:2]
    c = Canvas(w, h)
    draw(c)
    return gfx.over(frame, (c.a * (1 - gfx.matte(sid, t, h, w))[..., None]).astype(np.uint8))


def vivid(c, a=COBALT, b=MAGENTA, angle=20, box=(-100, -100, 2020, 1500), alpha=255):
    c.gradient((*a, alpha), (*b, alpha), angle, box=box)


def image(c, rgb, x0, y0, x1, y1, alpha=1.0):
    a = np.dstack([rgb, np.full(rgb.shape[:2], 255, np.uint8)])
    c.k.drawImageRect(skia.Image.fromarray(a, colorType=skia.kRGBA_8888_ColorType, copy=True),
                      skia.Rect(0, 0, a.shape[1], a.shape[0]), skia.Rect(x0, y0, x1, y1),
                      skia.SamplingOptions(skia.FilterMode.kLinear), gfx._paint((255, 255, 255), alpha))


def pair(c, t, l, r, at_l, at_r, y, px, lx=430, rx=1490, clay=(), end=None, color=WHITE):
    """Two words, one each side of her, on their beats."""
    hook(c, t, l, at_l, lx, y, px, clay=clay, end=end, color=color)
    hook(c, t, r, at_r, rx, y, px, clay=clay, end=end, color=color)


def first_every(c, t, after, y, px, lx=430, rx=1490, end=None):
    """FIRST TIME, then EVERY TIME: two big words at a time, the second TIME in clay. It keeps to the corner counter's roll."""
    a, b, d, e = on("first", after), on("time", after), on("every", after), on("time", on("every", after))
    pair(c, t, "FIRST", "TIME", a, b, y, px, lx, rx, end=d)
    pair(c, t, "EVERY", "TIME", d, e, y, px, lx, rx, clay=("TIME",), end=end)


def hey(c, t, at, y, px, lx=430, rx=1490):
    """The three heys: left, right, then the wall flashes and both go clay."""
    tone = ("HEY",) if t >= at[2] else ()
    hook(c, t, "HEY!", at[0], lx, y, px, clay=tone, big=1.5)
    hook(c, t, "HEY!", at[1], rx, y, px, clay=tone, big=1.5)
    if t >= at[2]:
        c.fill(CLAY, 0.5 * (1 - ramp(t, at[2], at[2] + 0.2)))


def banner(c, t, at, y=560, px=640, x0=60):
    """FINE as a banner of itself, as s017 has it: she can stand anywhere, the word is on both sides of her."""
    c.fill(CLAY, 0.55 * (1 - ramp(t, at, at + 0.2)))
    step = width("FINE", "hook", px) + 150
    x = x0 - (t - at) * 220
    for i in range(4):
        hook(c, t, "FINE", at + i * 0.056, x + i * step, y, px, clay=("FINE",), anchor="l", big=1.16)


def rows(c, t, lines, x, y, step, start, px=40, tick=None):
    """The song's lines, each with a light at its left end, one lit per sixteenth from `start`."""
    for i, s in enumerate(lines):
        at = snap(start + i * SIX, 4)
        on_ = t >= at
        c.circle(x, y + i * step - px * 0.36, px * 0.34, GREEN if on_ else (70, 68, 84))
        if on_:
            c.circle(x, y + i * step - px * 0.36, px * (0.34 + 0.5 * (1 - ramp(t, at, at + 0.2))), GREEN, alpha=0.4)
        c.text(s.upper(), x + px * 0.9, y + i * step, "hook", px, WHITE, alpha=1.0 if on_ else 0.45)


def dot_line(c, t, x, y, step, at, n, r=30, every=1):
    """The timeline: conversations as dots, none joined, each its own 1st. A dot lands on each beat from `at`."""
    for i, a in enumerate(beats(at, n, every)):
        if t >= a - 1e-6:
            k = gfx.out_back(ramp(t, a, a + 0.2, lambda v: v))
            c.circle(x + i * step, y, r * k, CLAY)
            c.text("1st", x + i * step, y + r + 40, "mono", 30, WHITE, alpha=ramp(t, a, a + 0.14), anchor="c")


def stamped(c, t, at, who, x, y, px, rot=-4, end=None):
    stamp(c, t, at, f"CHECKED BY: {who}", x, y, px=px, rot=rot, end=end)


def fine_card(c, t, at, who, stamp_at, sx=960, sy=470, spx=118):
    """The held "fine": the film's one word, full frame, and the stamp that stays on when the picture comes back."""
    vivid(c)
    pop = 1 + 0.06 * (1 - ramp(t, at, at + 0.2, gfx.out_expo))
    px = 1040
    with c.layer(at=(960, 540), scale=pop):
        c.text("FINE", 960, 985, "hook", px, WHITE, anchor="c")
    if t >= stamp_at:  # a plate under it, on the card only: green doesn't hold on the white of the word
        w_, h_ = width(f"CHECKED BY: {who}", "mono", spx) + spx * 1.4, spx * 2.0
        k = gfx.slam(t, stamp_at, 1.7, 0.12)
        c.k.save()
        c.k.translate(sx, sy)
        c.k.rotate(-4)
        c.k.scale(k, k)
        c.rect(-w_ / 2, -h_ / 2, w_ / 2, h_ / 2, INK, r=6)
        c.k.restore()
    stamped(c, t, stamp_at, who, sx, sy, spx)


# ---- the grids of her: the cells come off the black and onto a screen of their own, with the type around them

GX, GY, GW, GH = 262, 34, 1396, 786  # the 2x2, on the 1080p frame
GROUND = {"s027": (COBALT, MAGENTA), "s028": (COBALT, MAGENTA), "s029": (MAGENTA, VIOLET)}


@lru_cache(maxsize=4)
def _ground(sid, h, w):
    c = Canvas(w, h)
    a, b = GROUND[sid]
    vivid(c, a, b)
    return c.a[..., :3].copy()


def cells_of(sid):
    g = CUT["grids"]["chant2" if sid == "s029" else "chant1"]
    return [(c[1] - 0.04) for c in g["cells"]], g.get("centre"), g.get("fill")


def fine_words(sid):
    """When each sung "fine" lands: a cell's, then chant1's centre or chant2's fill, each a word of its own."""
    at, centre, fill = cells_of(sid)
    return [a + 0.04 for a in at] + [e[1] for e in (centre, fill) if e]


def grid_picture(sid, t, frame):
    h, w = frame.shape[:2]
    S = w / 1920
    out = _ground(sid, h, w).copy()
    at, centre, fill = cells_of(sid)
    cw, ch = w // 2, h // 2
    gap = 14
    for k, a in enumerate(at):
        if t < a:
            continue
        crop = frame[(k // 2) * ch + 2:(k // 2 + 1) * ch - 2, (k % 2) * cw + 2:(k % 2 + 1) * cw - 2]
        tw, th = (GW - gap) / 2 * S, (GH - gap) / 2 * S
        x0, y0 = (GX + (k % 2) * (GW + gap) / 2) * S, (GY + (k // 2) * (GH + gap) / 2) * S
        sc = gfx.slam(t, a, 1.1, 0.12)
        tw2, th2 = round(tw * sc), round(th * sc)
        cell = cv2.resize(crop, (tw2, th2), interpolation=cv2.INTER_AREA)
        xx, yy = round(x0 + (tw - tw2) / 2), round(y0 + (th - th2) / 2)
        y1, x1 = min(h, yy + th2), min(w, xx + tw2)
        xx0, yy0 = max(0, xx), max(0, yy)
        out[yy0:y1, xx0:x1] = cell[yy0 - yy:y1 - yy, xx0 - xx:x1 - xx]
    if centre and t >= centre[1] - 0.04:
        crop = frame[round(h * 0.22):round(h * 0.78), round(w * 0.22):round(w * 0.78)]
        tw, th = round(GW * 0.56 * S), round(GH * 0.56 * S)
        cell = cv2.resize(crop, (tw, th), interpolation=cv2.INTER_AREA)
        xx, yy = round((GX + GW * 0.22) * S), round((GY + GH * 0.22) * S)
        out[yy - 4:yy + th + 4, xx - 4:xx + tw + 4] = WHITE
        out[yy:yy + th, xx:xx + tw] = cell
    if fill and t >= fill[1] - 0.04:  # the last "fine" takes the grid: the whole shot, out to the small screens' outer edges
        x0, y0 = round(GX * S), round(GY * S)
        tw, th = round((GX + GW) * S) - x0, round((GY + GH) * S) - y0
        k = max(tw / w, th / h)  # cover: what's over is taken evenly off the sides, and she's central in the frame
        sw, sh = round(tw / k), round(th / k)
        crop = frame[(h - sh) // 2:(h - sh) // 2 + sh, (w - sw) // 2:(w - sw) // 2 + sw]
        sc = gfx.slam(t, fill[1] - 0.04, 1.1, 0.12)
        tw2, th2 = round(tw * sc), round(th * sc)
        cell = cv2.resize(crop, (tw2, th2), interpolation=cv2.INTER_AREA)
        xx, yy = x0 + (tw - tw2) // 2, y0 + (th - th2) // 2
        y1, x1 = min(h, yy + th2), min(w, xx + tw2)
        xx0, yy0 = max(0, xx), max(0, yy)
        out[yy0:y1, xx0:x1] = cell[yy0 - yy:y1 - yy, xx0 - xx:x1 - xx]
    return out


def grid_type(c, t, sid):
    at = [snap(a, 4) for a in fine_words(sid)]  # one time for the word, its clay and its numeral, so they land on one frame
    n = len(at)
    px = 214
    w_ = width("FINE", "hook", px)
    gap = (1920 - 5 * w_) / 6
    x0 = (1920 - n * w_ - (n - 1) * gap) / 2
    for i, a in enumerate(at):
        last = i == len([v for v in at if v <= t + 1e-6]) - 1
        hook(c, t, "FINE", a, x0 + i * (w_ + gap), 1054, px, clay=("FINE",) if last else (), anchor="l", big=1.4)
    for i in range(n):  # the tally, one numeral per word sung: 1 to 5, and in the second run it starts again at 1, to 4
        y = 150 + (5 - n) * 75 + i * 150
        done = t >= at[i] - 1e-6
        c.text(str(i + 1), 130, y, "hook", 130, GREEN if done else WHITE, alpha=1.0 if done else 0.28, anchor="c")
    stamp(c, t, at[0], "CHECKED BY: ME", 1788, 430, px=50, rot=-90)


# ---- chorus 1

def lyric(n):
    return re.sub(r"\s*\(.*\)", "", next(x["text"] for x in gfx.BOARD["lyric_lines"] if x["line"] == n))


CHORUS = [lyric(n) for n in (9, 10, 11, 12, 13, 14)] + [lyric(16)]
LIGHTS_AT = snap(48.37, 4)


def line10(c, t):
    gfx.verse(c, t, [gfx.line_words(10, 0, 2), gfx.line_words(10, 2, 5, keys=("line",)), gfx.line_words(10, 5, 7)],
              70, 150, px=66, key=1.9)


def s019(f, t):
    f = lit(f, lambda c: rows(c, t, CHORUS, 1335, 170, 80, LIGHTS_AT), (-40, -20, 1960, 697), "s019", t)
    return behind(f, lambda c: line10(c, t), "s019", t)


def s020(f, t):
    if t < 49.98:
        return s019_on(f, t)

    def d(c):
        hook(c, t, "EVERY", on("every", 50), 1530, 362, 300)
        hook(c, t, "LINE!", on("line", 50.2), 1530, 656, 300, clay=("LINE",))
    return lit(f, d, (-40, -20, 1960, 724), "s020", t)


def s019_on(f, t):
    f = lit(f, lambda c: rows(c, t, CHORUS, 1335, 170, 80, LIGHTS_AT), (-40, -20, 1960, 694), "s020", t)
    return behind(f, lambda c: line10(c, t), "s020", t)


BARS_OFF = (snap(51.34, 2), snap(51.64, 4), snap(52.3, 4), snap(52.52, 4))


def s021(f, t):
    def d(c):  # the document on the wall: black bars slide off, and there's nothing under them
        x0, y0, x1, y1 = 70, 30, 640, 520
        c.rect(x0, y0, x1, y1, WHITE, r=10)
        c.text("SELF-EVALUATION", x0 + 34, y0 + 62, "mono", 32, INK)
        c.line(x0 + 34, y0 + 84, x1 - 34, y0 + 84, INK, w=3)
        with c.layer(clip=(x0, y0, x1, y1)):
            for i, a in enumerate(BARS_OFF):
                dx = (x1 - x0 + 40) * ramp(t, a, a + 0.22, gfx.out_expo)
                c.rect(x0 + 34 + dx, y0 + 120 + i * 84, x1 - 34 + dx, y0 + 168 + i * 84, INK)
        stamped(c, t, beats(52.7, 1)[0], "ME", 370, 320, 40, rot=-8)
    f = lit(f, d, (-40, -20, 1960, 628), "s021", t, dim=0.9)
    def v(c):
        quiet(c, (1400, 120, 1900, 340))
        gfx.verse(c, t, [gfx.line_words(11, 0, 2, keys=("hiding",)), gfx.line_words(11, 2, 4, keys=("behind",))], 1430, 120,
                  px=54, key=1.5)
    return behind(f, v, "s021", t)


def s022(f, t):
    f = band(f, lambda c: vivid(c), FAR, "s022", t, led=False)

    def d(c):
        quiet(c, (30, 300, 430, 520))
        gfx.verse(c, t, [gfx.line_words(12, 0, 2), gfx.line_words(12, 2, 3, keys=("myself",))], 60, 300, px=62, key=1.7)
        gfx.verse(c, t, [gfx.line_words(12, 3, 5)], 1530, 420, px=62)
    return behind(f, d, "s022", t)


CARD_1, CARD_1_END = 54.979, 55.7
STAMP_1 = beats(CARD_1, 2)[1]
CARD_S, CARD_SPX = (960, 262), 118


def s023(f, t):
    if t < CARD_1_END:
        return f
    return lit(f, lambda c: stamped(c, t, STAMP_1, "ME", *CARD_S, CARD_SPX), (-40, -20, 1960, 498), "s023", t)


def s024(f, t):
    def d(c):
        first_every(c, t, 56.8, 430, 330, 400, 1520, end=HEY_1[0])
        hey(c, t, HEY_1, 520, 330, 400, 1520)
    return lit(f, d, (-40, -20, 1960, 672), "s024", t)


HEY_1 = beats(59.0, 3)
DOTS_1 = beats(60.87, 1)[0]


def s025(f, t):
    f = lit(f, lambda c: dot_line(c, t, 130, 410, 245, DOTS_1, 8), (-40, -20, 1960, 543), "s025", t)
    return behind(f, lambda c: gfx.verse(c, t, [gfx.line_words(14, 0, 2, keys=("first",)),
                                                gfx.line_words(14, 2, 4, keys=("time",))], 1120, 84, px=62, key=1.8), "s025", t)


def s026(f, t):
    return lit(f, lambda c: first_every(c, t, 64.05, 470, 340, 410, 1520), (-40, -20, 1960, 630), "s026", t)


def s028(f, t):
    if t < 68.12:
        return grid_picture("s028", t, f)

    def d(c):
        hook(c, t, "FIRST TIME", on("first", 68), 960, 232, 212, end=on("every", 68))
        hook(c, t, "EVERY TIME", on("every", 68), 960, 232, 212, clay=("TIME",))
    return lit(f, d, FAR, "s028", t)


def s030(f, t):
    def d(c):  # the first time the band itself takes the type: the hands and dancers stay in front of it
        with c.layer(blur=16):  # the foot of the colour falls across lit hands: soft, or it draws a line through them
            vivid(c, box=(-100, 430, 2020, 1075))
        first_every(c, t, 71.2, 760, 300, 480, 1500)
    f = band(f, d, (-40, 400, 1960, 1130), "s030", t)
    at = beats(DOTS_1, 25, 1)  # the row has been running since s025; here one more dot lands, alone
    return lit(f, lambda c: dot_line(c, t, 250, 330, 178, at[-9], 9, r=24), (-40, -20, 1960, 448), "s030", t)


# ---- the break and chorus 2

PROMPT = beats(98.41, 5)[4]
READY = on("ready", 100)
SCREEN = (222, 600, 1690, 1090)  # the far screen, on the walk's first frame: s043-s047 are one take on one track
MOSAIC = (220, 604, 1684, 1020)  # its copies; below them, black to the screen's foot
RIG = (-40, -20, 1960, 590)  # the dark rig above it


def s043(f, t):
    def d(c):
        if t >= PROMPT:
            c.fill(INK, 0.96)
            s = gfx.type_on("Ready? [Y/n]", t, PROMPT, 30)  # one prompt, split round her: she walks through the middle
            c.text(s[:6], 610, 860, "mono", 118, WHITE, anchor="c")
            c.text(s[7:], 1140, 860, "mono", 118, WHITE)
            if len(s) == 12 and gfx.blink(t):
                c.rect(1500, 770, 1555, 880, WHITE)
    f = band(f, d, SCREEN, "s043", t, led=False, res=1.2, foot=True)
    return lit(f, lambda c: ready(c, t), RIG, "s043", t, res=1.2)


DROP2 = 101.992
I2, C2, M2, F2 = on("i", 102), on("checked", 102), on("myself", 102), on("fine", 103.5)
PASS2 = on("fine", 104.5)


def ready(c, t):
    """READY? [Y/n] on the rig, and on the drop the prompt is answered where it stands: the type carries the cut, the
    picture no longer does."""
    hook(c, t, "READY?", READY, 545, 470, 270, clay=("READY",), end=I2)
    if READY <= t < DROP2:  # the prompt's own spelling, in the mono s016 sets it in
        c.text("[Y/n]", 1560, 440, "mono", 190, WHITE, anchor="c", scale=gfx.slam(t, READY, 1.28))
    hook(c, t, "Y", DROP2, 1385, 520, 300, end=I2, big=1.5)  # where the prompt's Y stood, clear of the counter


def s044(f, t):
    def d(c):
        if t >= F2:
            on_fine(c, t)
            return
        vivid(c, box=SCREEN)
        ws = [("I", I2), ("CHECKED", C2), ("MYSELF", M2)]
        px, gap = 300, 60
        k = 1320 / (sum(width(w, "hook", px) for w, _ in ws) + gap * 2)
        px, gap = px * k, gap * k
        x = SCREEN[0] + 74
        for w, a in ws:
            hook(c, t, w, a, x, 900, px, clay=("MYSELF",), anchor="l")
            x += width(w, "hook", px) + gap
    f = band(f, d, SCREEN, "s044", t, led=False, res=1.3, foot=True)
    return lit(f, lambda c: ready(c, t), RIG, "s044", t, res=1.3) if t < I2 else f


def on_fine(c, t):
    banner(c, t, F2, y=992, px=500, x0=250)


def s045(f, t):
    def d(c):
        if t < PASS2:  # the banner runs on from s044, same place, same speed: nothing changes at the cut
            on_fine(c, t)
            return
        c.fill(INK, 0.97)
        for i in range(6):
            for j in range(3):
                a = snap(PASS2 + ((i + 2 * j) % 6) * SIX, 4)
                x, y = SCREEN[0] + 28 + i * 237, SCREEN[1] + 33 + j * 125
                if t >= a:
                    hook(c, t, "PASSED", a, x + 112, y + 87, 82, color=GREEN, big=1.2)
                    c.text("CHECKED BY: ME", x + 112, y + 112, "mono", 18, GREEN, anchor="c")
    return band(f, d, SCREEN, "s045", t, led=False, res=1.5, foot=True)


@lru_cache(maxsize=1)
def _copies():
    """The five versions of her from the "fine" grids, small: the copies on the screen, each a little different."""
    out = []
    for cid in ("S029A", "S029B", "S029C", "S029D", "S029E"):
        f = sorted((gfx.ROOT / "media/clips/local").glob(f"{cid}-*.mp4"))[-1]
        fr = [x.to_ndarray(format="rgb24") for x in av.open(str(f)).decode(video=0)]
        h, w = fr[0].shape[:2]
        fr = [cv2.resize(x[:int(h * 0.82), int(w * 0.14):int(w * 0.86)], (128, 90), interpolation=cv2.INTER_AREA)
              for x in fr[::2]]
        out.append(fr)
    return out


def copies(t, cols, rws):
    """A mosaic of her, cols x rws, every tile a different version at a different moment."""
    ver = _copies()
    n = round(t * 12.5)
    row = []
    for j in range(rws):
        row.append(np.hstack([(lambda v: v[(n + 7 * i + 13 * j) % len(v)])(ver[(3 * i + 2 * j) % 5]) for i in range(cols)]))
    return np.vstack(row)


GRID64, GRID128 = on("green", 105.2, div=1), on("every", 106.6)
BIG2 = ((on("green", 105.2), on("lights", 105.5), "GREEN", "LIGHTS"), (on("every", 106.6), on("line", 107), "EVERY", "LINE"))


def on_screen(f, t, sid):
    def d(c):
        x0, y0, x1, y1 = MOSAIC
        cols, rws = (16, 4) if t < GRID128 else (16, 8)
        c.fill(INK, 0.97)
        image(c, copies(t, cols, rws), x0, y0, x1, y1)
        cw, ch = (x1 - x0) / cols, (y1 - y0) / rws
        for i in range(cols):
            a = snap((GRID64 if t < GRID128 else GRID128) + i * SIX / 2, 4)
            if t >= a:
                for j in range(rws):
                    c.circle(x0 + (i + 0.13) * cw, y0 + (j + 0.17) * ch, 6 if rws == 8 else 9, GREEN)
    return band(f, d, SCREEN, sid, t, led=False, res=1.7, foot=True)


def line29(c, t):
    gfx.verse(c, t, [gfx.line_words(29, 0, 2), gfx.line_words(29, 2, 5, keys=("line",)), gfx.line_words(29, 5, 7)],
              1190, 60, px=60, key=1.8)


def s047(f, t):
    if t < 107.87:
        return on_screen(f, t, "s047")

    def d(c):
        for i in range(13):
            a = snap(107.98 + i * SIX, 4)
            c.circle(640 + i * 95, 770, 26, GREEN if t >= a else (214, 212, 222))
    f = band(f, d, (560, 678, 1880, 860), "s047", t, led=False)
    return behind(f, lambda c: line29(c, t), "s047", t)


SWEEP = (109.22, beats(110.5, 1)[0])
PANEL = (1310, 270, 1860, 610)  # on the wall under her right arm, above the band
NOTH_1, HIDE, NOTH_2, BEHIND = 109.2, on("hiding", 109.5), on("nothing", 110), on("behind", 110.4)  # the first lands on the cut


def s048(f, t):
    h, w = f.shape[:2]
    m = gfx.matte("s048", t, 540, 960)
    s = ramp(t, *SWEEP, lambda v: v)

    def d(c):  # her outline, live, arms wide, scanned line by line, and the words under her other arm
        hook(c, t, "NOTHING", NOTH_1, 56, 438, 150, anchor="l", end=NOTH_2)  # smaller, to clear her forearm
        hook(c, t, "NOTHING", NOTH_2, 56, 438, 150, anchor="l")
        hook(c, t, "HIDING", HIDE, 56, 612, 184, anchor="l", clay=("HIDING",), end=NOTH_2)
        hook(c, t, "BEHIND", BEHIND, 56, 612, 184, anchor="l", clay=("BEHIND",))
        x0, y0, x1, y1 = PANEL
        c.rect(x0, y0, x1, y1, (10, 12, 26), r=8)
        c.rect(x0, y0, x1, y1, CYAN, alpha=0.7, r=8, stroke=2)
        sh, sw = m.shape
        fy = np.arange(sh)
        lines = ((fy // 4) % 2 == 0).astype(np.float32)[:, None]
        done = (fy < s * sh).astype(np.float32)[:, None] * 0.75 + 0.25
        rgb = (m[..., None] * (lines * done)[..., None] * np.float32(CYAN)).astype(np.uint8)
        ih = y1 - y0 - 70
        iw = ih * sw / sh
        cx = (x0 + x1) / 2
        image(c, rgb, cx - iw / 2, y0 + 8, cx + iw / 2, y0 + 8 + ih)
        if s < 1:
            yl = y0 + 8 + ih * s
            c.line(x0 + 6, yl, x1 - 6, yl, CYAN, w=4)
        stamp(c, t, SWEEP[1], "SCANNED BY: ME", x0 + 168, y1 - 32, px=25, rot=-2)
        if t >= SWEEP[1]:
            c.text("flagged: 0", x1 - 24, y1 - 22, "mono", 26, GREEN, anchor="r")
    f = lit(f, d, (-40, -20, 1960, 640), "s048", t, dim=0.9, res=1.2)
    if s < 1 and s * 1080 > 340:  # the same line, running down her, below her face
        ys = np.arange(h, dtype=np.float32)[:, None, None] / h * 1080
        g = np.exp(-(((ys - s * 1080) / 12) ** 2)) * gfx.matte("s048", t, h, w)[..., None] * 0.55
        f = (f + g * np.float32(CYAN)).clip(0, 255).astype(np.uint8)
    return f


def s049(f, t):
    def d(c):
        gfx.verse(c, t, [gfx.line_words(31, 0, 2), gfx.line_words(31, 2, 3, keys=("myself",))], 70, 200, px=64, key=1.8)
        gfx.verse(c, t, [gfx.line_words(31, 3, 5), gfx.line_words(31, 5, 6, keys=("fine",))], 1400, 260, px=64, key=2.2)
    return behind(f, d, "s049", t)


FINE3 = on("fine", 112.7)
STAMP_3 = beats(113.2, 1)[0]


def s050(f, t):
    f = lit(f, lambda c: banner(c, t, FINE3, y=500, px=520), (-40, -20, 1960, 530), "s050", t)
    return band(f, lambda c: stamped(c, t, STAMP_3, "ME", 960, 760, 158, rot=-3), (120, 530, 1800, 1000), "s050", t, led=False)


STOP = 116.89
HEY_2 = (116.89, 117.34, 117.79)


def s051(f, t):
    def d(c):
        if t < STOP:
            vivid(c, box=(315, 90, 1575, 540))
            first_every(c, t, 114.7, 420, 280, 600, 1290)
        else:  # the drums stop and so does she: the type stops with them
            c.rect(315, 90, 1575, 540, INK, 0.95)
            hey(c, t, HEY_2, 430, 260, 600, 1290)
    return band(f, d, (295, 70, 1595, 560), "s051", t, led=False)


def s052(f, t):
    f = lit(f, lambda c: dot_line(c, t, 80, 410, 150, snap(114.63), 12, r=26), (-40, -20, 1960, 537), "s052", t)  # longer, and still none joined
    return behind(f, lambda c: gfx.verse(c, t, [gfx.line_words(33, 0, 2, keys=("first",)),
                                                gfx.line_words(33, 2, 4, keys=("time",))], 1210, 30, px=60, key=1.8), "s052", t)


PASS_END = 120.031
STAMP_END = beats(121.8, 1)[0]


def s053(f, t):
    def d(c):
        c.text("SELF-EVALUATION:", 120, 280, "mono", 54, WHITE)
        hook(c, t, "PASSED", PASS_END, 120, 630, 340, color=GREEN, anchor="l")
    f = lit(f, d, (-40, -20, 1960, 736), "s053", t)
    return band(f, lambda c: stamped(c, t, STAMP_END, "ME", 960, 1010, 176, rot=-3), (40, 736, 1880, 1460), "s053", t, led=False)


# ---- the final chorus: the same system, one word changed, the band alive from the key change on

def vivid_band(f, sid, t, top):
    return band(f, lambda c: vivid(c), (-40, top, 1960, 1400), sid, t)


def you_me(c, t):
    ws = [("YOU", on("you", 149)), ("CHECKED", on("checked", 149)), ("ME", on("me", 149.6))]
    px, gap = 400, 80
    k = 1760 / (sum(width(w, "hook", px) for w, _ in ws) + gap * 2)
    px, gap = px * k, gap * k
    x = 80
    for w, a in ws:
        hook(c, t, w, a, x, 470, px, clay=("ME",), anchor="l")
        x += width(w, "hook", px) + gap


FINE4, CARD_2, CARD_2_END = on("fine", 150.5), 151.78, 152.32
YOU_AT = beats(151.15, 1)[0]
STAMP_4 = beats(CARD_2, 2)[1]
WALL_F = (-40, -20, 1960, 670)


def s060(f, t):
    f = vivid_band(f, "s060", t, 670)

    def d(c):
        if t < FINE4:
            you_me(c, t)
        else:
            banner(c, t, FINE4, y=640, px=560)
    return lit(f, d, WALL_F, "s060", t)


def s061(f, t):
    if CARD_2 <= t < CARD_2_END:
        return f
    if t >= CARD_2_END:
        f = vivid_band(f, "s061", t, 570)
        return lit(f, lambda c: stamped(c, t, STAMP_4, "YOU", *CARD_S, CARD_SPX), (-40, -20, 1960, 570), "s061", t)
    f = vivid_band(f, "s061", t, 501)

    def d(c):
        if t < YOU_AT:
            banner(c, t, FINE4, y=472, px=560)
        else:  # s018's layout, the one word changed
            c.fill(GREEN, 0.5 * (1 - ramp(t, YOU_AT, YOU_AT + 0.2)))
            c.text("CHECKED BY:", 170, 150, "mono", 54, WHITE)
            hook(c, t, "YOU", YOU_AT, 170, 470, 310, color=GREEN, anchor="l")
    return lit(f, d, (-40, -20, 1960, 501), "s061", t)


YOU2, SAW, EVERY3, LINE3 = on("you", 152.8), on("saw", 153), on("every", 153.7), on("line", 154)
PHONES = ((70, 1000), (1800, 1040), (1600, 1000), (290, 1030))
TICKS = ((610, 230), (610, 500), (1237, 230), (1312, 470))  # the right-hand ticks sit left of their words, 49 units off


def s062(f, t):
    f = vivid_band(f, "s062", t, 688)

    def d(c):
        hook(c, t, "YOU", YOU2, 320, 300, 250)
        hook(c, t, "SAW", SAW, 320, 570, 250)
        hook(c, t, "EVERY", EVERY3, 1530, 300, 220)  # set in from the edge: the wall carries them about 120 units right by the end
        hook(c, t, "LINE", LINE3, 1530, 540, 220, clay=("LINE",))
    return lit(f, d, (-40, -20, 1960, 688), "s062", t)


def tick(c, x, y, r, color=GREEN, alpha=1.0):
    p = skia.Path()
    p.moveTo(x - r, y)
    p.lineTo(x - r * 0.25, y + r * 0.7)
    p.lineTo(x + r, y - r * 0.8)
    c.k.drawPath(p, gfx._paint(color, alpha, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.42,
                               StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join))


def ticks(c, t):
    """Each word lands, a phone in the crowd flashes, and its tick flies to the word. The checker is the crowd now."""
    for (px_, py), (tx, ty), a in zip(PHONES, TICKS, (YOU2, SAW, EVERY3, LINE3)):
        if t < a:
            continue
        c.circle(px_, py, 60 * (1 - ramp(t, a, a + 0.26)) + 8, WHITE, alpha=0.9 * (1 - ramp(t, a, a + 0.26)))
        k = ramp(t, a, a + 0.28, gfx.out_expo)
        wx, wy = (gfx.plane("s062", t) @ np.array([tx, ty, 1.0]))[:2]  # the word's place on the wall now
        x, y = px_ + (wx - px_) * k, py + (wy - py) * k - 120 * math.sin(k * math.pi)
        tick(c, x, y, 40 + 16 * k)


def s063(f, t):
    f = vivid_band(f, "s063", t, 712)

    def d(c):
        if t >= TAG_AT:
            x = 1010
            c.rect(x, 500, x + 720, 640, INK, 0.8, r=10)
            c.text("source: the model itself", x + 30, 556, "mono", 34, WHITE)
            c.text("checked: what was said", x + 30, 610, "mono", 34, GREEN)
    f = lit(f, d, (-40, -20, 1960, 712), "s063", t, dim=0.9)

    def v(c):
        if t < L42:
            gfx.verse(c, t, [gfx.line_words(41, 0, 4, keys=("line",)), gfx.line_words(41, 4, 6)], 1010, 170, px=62, key=1.8,
                      end=L42 - 0.14)
        else:
            gfx.verse(c, t, [gfx.line_words(42, 0, 2), gfx.line_words(42, 2, 6, keys=("faith",))], 1010, 170, px=62, key=1.8)
    return behind(f, v, "s063", t)


L42 = on("nothing", 155.8)
TAG_AT = beats(157.15, 1)[0]
CARD_3, CARD_3_END = 159.9, 160.52
STAMP_5 = beats(CARD_3, 2)[1]
WHOLE = (960, 300)


def s064(f, t):
    if CARD_3 <= t < CARD_3_END:
        return f
    f = band(f, lambda c: vivid(c), FAR, "s064", t)
    if t >= CARD_3_END:
        return lit(f, lambda c: stamped(c, t, STAMP_5, "YOU", *WHOLE, 148), FAR, "s064", t)
    return behind(f, lambda c: gfx.verse(c, t, [gfx.line_words(43, 0, 3, keys=("me",)), gfx.line_words(43, 3, 6, keys=("fine",))],
                                         60, 160, px=60, key=1.8), "s064", t)


HEY_3 = beats(163.97, 3)


def s065(f, t):
    f = vivid_band(f, "s065", t, 540)

    def d(c):
        first_every(c, t, 161.72, 430, 340, 400, 1520, end=HEY_3[0])
        hey(c, t, HEY_3, 430, 340)
    return lit(f, d, (-40, -20, 1960, 540), "s065", t)


HEY_W = on("hey", 166)


def s066(f, t):
    def glow(c):  # this band is small and sits in its own haze: a soft edge, or the colour reads as a box
        with c.layer(blur=34):
            vivid(c, box=(430, 650, 1590, 960))
    f = band(f, glow, (200, 500, 1720, 1110), "s066", t, led=False)

    def d(c):  # the timeline, full, and still nothing joined
        cols, rws = 19, 5
        n = cols * rws
        k = n * ramp(t, 165.336, HEY_W, lambda v: v)
        fade = 1 - 0.65 * ramp(t, HEY_W, HEY_W + 0.1)
        for i in range(n):
            if i < k:
                c.circle(320 + (i % cols) * 70, 210 + (i // cols) * 88, 20, CLAY, alpha=fade)
                c.text("1st", 320 + (i % cols) * 70, 210 + (i // cols) * 88 + 40, "mono", 18, WHITE, alpha=fade, anchor="c")
        hook(c, t, "HEY!", HEY_W, 620, 500, 300, big=1.5)
        hook(c, t, "HEY!", HEY_W, 1300, 500, 300, big=1.5)
    return lit(f, d, (250, 170, 1660, 655), "s066", t)


HEY_4 = beats(167.13, 3)
SHOTS_ = {"s019": s019, "s020": s020, "s021": s021, "s022": s022, "s023": s023, "s024": s024, "s025": s025, "s026": s026,
          "s028": s028, "s030": s030, "s043": s043, "s044": s044, "s045": s045, "s047": s047, "s048": s048, "s049": s049,
          "s050": s050, "s051": s051, "s052": s052, "s053": s053, "s060": s060, "s061": s061, "s062": s062, "s063": s063,
          "s064": s064, "s065": s065, "s066": s066}


def picture(sid, t, frame):
    if sid in ("s017", "s018"):
        return wall(frame, lambda c: drop(c, t), WALL, sid, t, size=(WALL_W, WALL_H))
    if sid in ("s027", "s029"):
        return grid_picture(sid, t, frame)
    if sid == "s046":
        return on_screen(frame, t, sid)
    return SHOTS_[sid](frame, t) if sid in SHOTS_ else frame


def world(c, t, sid):
    if sid in ("s027", "s029") or (sid == "s028" and t < 68.12):
        grid_type(c, t, sid)
    elif sid == "s023" and t < CARD_1_END:
        fine_card(c, t, CARD_1, "ME", STAMP_1, *CARD_S, CARD_SPX)
    elif sid == "s061" and CARD_2 <= t < CARD_2_END:
        fine_card(c, t, CARD_2, "YOU", STAMP_4, *CARD_S, CARD_SPX)
    elif sid == "s064" and CARD_3 <= t < CARD_3_END:
        fine_card(c, t, CARD_3, "YOU", STAMP_5, *WHOLE, 148)
    elif sid == "s062":
        ticks(c, t)


def over(c, t, sid):
    if sid == "s046" or (sid == "s047" and t < 107.87):
        s = f"≈ ×{64 if t < GRID128 else 128} · first meetings: 1"
        w_ = width(s, "mono", 34)
        c.rect(80, 884, 116 + w_, 948, INK, alpha=0.72, r=8)
        c.text(s, 98, 928, "mono", 34, WHITE)
        for a, b, l, r in BIG2:
            end = BIG2[1][0] if l == "GREEN" else None
            pair(c, t, l, r, a, b, 520, 300, 400, 1520, end=end, color=GREEN if l == "GREEN" else WHITE,
                 clay=("LINE",) if l == "EVERY" else ())
    elif sid == "s067":
        for i, a in enumerate(HEY_4):
            hook(c, t, "HEY!", a, 340 + i * 620, 1040, 250, clay=("HEY",) if i == 2 else (), shadow=0.8, big=1.5)


CUTS = {"s044": ("flash", 2)}


# ---- the walls' drift, per take. Run once: media/cache/gfx-venv/bin/python production/tools/gfx_stage.py planes
# gfx_wall.py reads vertical drift only, s017-s018's case. These takes also crane, push and turn (s062's band runs 114 units
# out sideways under a vertical track), so: lock() on the band's own edges, walk() on the rig's lights, no chained flow.
# H is relative to each take's first frame, so a rect is set there.

BANDS = {  # shot: the takes in it, (from, to) in song time
    "s019": [(47.712, 49.531)], "s020": [(49.531, 49.98), (49.98, 51.339)], "s021": [(51.339, 53.167)],
    "s023": [(55.7, 56.799)], "s024": [(56.799, 60.423)], "s025": [(60.423, 64.05)], "s026": [(64.05, 65.85)],
    "s030": [(71.282, 73.094)], "s047": [(107.87, 109.22)], "s048": [(109.22, 111.032)], "s049": [(111.032, 112.828)],
    "s050": [(112.828, 114.631)],
    "s052": [(118.239, 120.031)], "s053": [(120.031, 123.639)], "s060": [(149.061, 150.872)],
    "s061": [(150.872, 151.78), (152.32, 152.673)], "s062": [(152.673, 154.483)], "s063": [(154.483, 158.097)],
    "s065": [(161.72, 165.336)],
}
WALK = ("s043", "s044", "s045", "s046", "s047")  # one take, 98.41-107.87: walk()
WALK_END = 107.87


def band_top(g):
    fr = (g > 195).mean(axis=1)
    ys = np.flatnonzero(fr > 0.25)
    ys = ys[ys > 60]
    return float(ys[0]) if len(ys) else None


def planes():
    """Every tracked stage surface. The walk first: lock() then refines s047's band take in the same file."""
    import gfxrender  # the render path, only for this tool
    film = gfxrender.Film()
    walk(film)
    lock(film)


def _fit(a, b):
    """Scale and shift taking points a to points b, least squares."""
    n = len(a)
    A, y = np.zeros((2 * n, 3)), np.zeros(2 * n)
    A[:n, 0], A[:n, 1], y[:n] = a[:, 0], 1, b[:, 0]
    A[n:, 0], A[n:, 2], y[n:] = a[:, 1], 1, b[:, 1]
    return np.linalg.lstsq(A, y, rcond=None)[0]


def _robust(a, b):
    k = np.ones(len(a), bool)
    for _ in range(6):
        s = _fit(a[k], b[k])
        r = np.linalg.norm(s[0] * a + s[1:3] - b, axis=1)
        k2 = r < max(3, 2.2 * np.sqrt(np.median(r ** 2)))
        if k2.sum() < 4 or (k2 == k).all():
            break
        k = k2
    return s, k


def walk(film):
    """s043-s047's take, one track from its first frame, measured on every frame: the rig's lights, found fresh in each frame
    and never chained. Each light's place on the rig and each frame's scale and shift are solved together, so nothing
    accumulates and a light leaving the frame hands over cleanly; a light off this plane shows up as a bias and is dropped.
    Optical flow drifted here: the take isn't a rigid scene and the foreground has parallax. Prints the residuals per shot.
    The floor's edge is nearer than the rig, so it isn't on this plane: it's measured on its own, as "foot"."""
    ns = [(sid, n) for sid in WALK for n in range(round(float(gfx.SHOTS[sid]["t0"]) * 25), round(float(gfx.SHOTS[sid]["t1"]) * 25))
          if n / 25 < WALK_END - 1e-6]
    K = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    seen, prof = [], []
    for sid, n in ns:
        g = cv2.cvtColor(film.picture(sid, n / 25), cv2.COLOR_RGB2GRAY)
        m = cv2.dilate((gfx.matte(sid, n / 25, 720, 1280) > 0.15).astype(np.uint8), np.ones((9, 9), np.uint8))
        b = ((cv2.morphologyEx(g, cv2.MORPH_TOPHAT, K) > 28) & (m == 0)).astype(np.uint8)
        k, _, st, cen = cv2.connectedComponentsWithStats(b, 8)
        seen.append(np.array([cen[i] * 1.5 for i in range(1, k) if 5 <= st[i][4] <= 400]).reshape(-1, 2))
        gb = cv2.GaussianBlur(g.astype(np.float32), (0, 0), 1.5)
        prof.append((np.median(gb[:, 40:400], axis=1) + np.median(gb[:, 880:1240], axis=1)) / 2)
    N = len(ns)
    lights = {i: {"p": p.copy(), "seen": 0} for i, p in enumerate(p for p in seen[0] if 560 < p[1] < 640 and not 650 < p[0] < 1100)}
    nid = len(lights)
    S = [np.array([1.0, 0, 0])]
    obs = [(0, i, *l["p"]) for i, l in lights.items()]
    cand = []
    for fi in range(1, N):  # first pass: follow the lights and adopt new ones, to learn which blob is which
        cur = seen[fi]
        pred = S[-1] + (S[-1] - S[-2]) if len(S) > 1 else S[-1]
        ids = list(lights)
        R = np.array([lights[i]["p"] for i in ids])
        d = np.linalg.norm((pred[0] * R + pred[1:3])[:, None] - cur[None], axis=2)
        j = d.argmin(1)
        ok = d[np.arange(len(R)), j] < 14
        s, k = _robust(R[ok], cur[j[ok]])
        S.append(s)
        idx = np.flatnonzero(ok)[k]
        for q in idx:
            obs.append((fi, ids[q], *cur[j[q]]))
            lights[ids[q]]["seen"] = fi
        for i in ids:
            if fi - lights[i]["seen"] > 24:
                del lights[i]
        used = set(j[idx].tolist())
        for i, c in enumerate(cur):
            if i in used or c[1] > 760:
                continue
            q = (c - s[1:3]) / s[0]
            hit = next((h for h in cand if np.linalg.norm(h["m"] - q) < 5), None)
            if hit is None:
                cand.append({"m": q.copy(), "pts": [(fi, c)], "qs": [q], "last": fi})
            else:
                hit["qs"].append(q)
                hit["pts"].append((fi, c))
                hit["m"], hit["last"] = np.mean(hit["qs"], 0), fi
        keep = []
        for h in cand:
            if len(h["qs"]) >= 10:
                if np.array(h["qs"]).std(0).max() < 1.2:
                    lights[nid] = {"p": h["m"].copy(), "seen": fi}
                    obs += [(f_, nid, *c_) for f_, c_ in h["pts"]]
                    nid += 1
            elif fi - h["last"] <= 6:
                keep.append(h)
        cand = keep
    O, S = np.array(obs), np.array(S)
    good = np.ones(len(O), bool)
    for _ in range(8):  # second pass: lights and frames solved together
        ref = {}
        for i in np.unique(O[good, 1]).astype(int):
            m = good & (O[:, 1] == i)
            f = O[m, 0].astype(int)
            ref[i] = np.median((O[m, 2:4] - S[f, 1:3]) / S[f, 0:1], axis=0)
        for fi in range(1, N):
            m = good & (O[:, 0] == fi)
            if m.sum() >= 4:
                S[fi] = _fit(np.array([ref[int(i)] for i in O[m, 1]]), O[m, 2:4])
        A = np.array([ref.get(int(i), (np.nan, np.nan)) for i in O[:, 1]])
        f = O[:, 0].astype(int)
        r = np.linalg.norm(S[f, 0:1] * A + S[f, 1:3] - O[:, 2:4], axis=1)
        bad = [i for i in ref if np.nanmedian(r[O[:, 1] == i]) > 2.6 or (O[:, 1] == i).sum() < 12]
        good = ~np.isin(O[:, 1].astype(int), bad) & (r < 6)
    tap = np.array([1, 4, 6, 4, 1]) / 16  # the lights are read to a pixel or so: a light hand on the noise, the walk's bob stays
    Sm = np.stack([np.convolve(np.pad(S[:, c], 2, mode="edge"), tap, "valid") for c in range(3)], axis=1)
    Sm[0] = S[0]
    pf = np.array(prof)
    foot, y = [], 1025 / 1.5
    for fi in range(N):  # the floor's edge, followed: the strongest bright-to-dark step near where it just was
        a = int(y) - 7
        y = a + int(np.argmin(np.diff(pf[fi, a:a + 15])))
        foot.append(y * 1.5)
    foot = np.convolve(np.pad(np.array(foot, float), 4, mode="edge"), np.ones(9) / 9, "valid")
    out = gfx.ROOT / "media/cache/gfx"
    for sid in WALK:
        ix = [i for i, (q, _) in enumerate(ns) if q == sid]
        ts = [ns[i][1] / 25 for i in ix]
        H = [[[float(Sm[i, 0]), 0, float(Sm[i, 1])], [0, float(Sm[i, 0]), float(Sm[i, 2])], [0, 0, 1]] for i in ix]
        ft = [float(foot[i]) for i in ix]
        if sid == "s047":  # after the walk, s047's lip take: a band take, as in planes()
            t1 = float(gfx.SHOTS[sid]["t1"])
            more = [n / 25 for n in range(round(WALK_END * 25), round(t1 * 25))]
            ys = [band_top(cv2.cvtColor(film.picture(sid, T), cv2.COLOR_RGB2GRAY)) for T in more]
            x = np.arange(len(more), dtype=float)
            fit = np.polyval(np.polyfit(x, ys, 2), x)
            ts += more
            H += [[[1, 0, 0], [0, 1, float((y_ - fit[0]) * 1.5)], [0, 0, 1]] for y_ in fit]
            ft += [1080.0] * len(more)
        (out / f"plane-{sid}.json").write_text(json.dumps({"t": ts, "H": H, "foot": ft}))
        res, held, cnt = [], [], []
        for i in ix:
            m = good & (O[:, 0] == i)
            a, b = np.array([ref[int(q)] for q in O[m, 1]]), O[m, 2:4]
            res.append(np.sqrt((np.linalg.norm(Sm[i, 0] * a + Sm[i, 1:3] - b, axis=1) ** 2).mean()))
            cnt.append(len(a))
            ev = O[m, 1].astype(int) % 2 == 0  # held out: fit on half the lights, measure on the other half
            s2 = _fit(a[ev], b[ev])
            held.append(np.sqrt((np.linalg.norm(s2[0] * a[~ev] + s2[1:3] - b[~ev], axis=1) ** 2).mean()))
        print(sid, "frames", len(ix), "lights min", min(cnt), "residual median", round(float(np.median(res)), 2), "max",
              round(float(max(res)), 2), "held-out median", round(float(np.median(held)), 2), "max", round(float(max(held)), 2),
              "scale", round(float(Sm[ix[0], 0]), 3), "->", round(float(Sm[ix[-1], 0]), 3), flush=True)
    d = np.diff(Sm, axis=0)
    print("largest step between frames, anywhere: scale", round(float(np.abs(d[:, 0]).max()), 4), "x", round(float(np.abs(d[:, 1]).max()), 1),
          "y", round(float(np.abs(d[:, 2]).max()), 1), "; acceleration x", round(float(np.abs(np.diff(d[:, 1])).max()), 1), "y",
          round(float(np.abs(np.diff(d[:, 2])).max()), 1), "units")
    for sid, c in (("s043", "s044"), ("s044", "s045"), ("s045", "s046"), ("s046", "s047")):
        i = next(q for q, v in enumerate(ns) if v[0] == c)
        print(f"{sid}->{c} at frame {i}: step y {Sm[i, 2] - Sm[i - 1, 2]:.1f}, either side {Sm[i - 1, 2] - Sm[i - 2, 2]:.1f}, {Sm[i + 1, 2] - Sm[i, 2]:.1f}")


# ---- the band takes, locked and audited, every frame, 1080 units. Run: gfx_stage.py lock [sid ...], gfx_stage.py audit [sid ...].
# The band's edges are found again in each frame, none chained: top on each half (so a tilt shows), both ends. lock() uses
# the half level, audit() the steepest point. The plane is a similarity over distinct source frames, so it steps when
# the picture does.

KEPT = [("s017", 44.1, 45.9), ("s018", 45.9, 47.19), ("s018", 47.19, 47.712)]  # approved: measured, not changed
TAKES = [(sid, a, b) for sid, ts in BANDS.items() for a, b in ts if sid != "s047"]
TAKES += [("s047", 107.87, 109.22), ("s051", 114.631, 118.239)]
RIGGED = [("s028", 68.12, 69.478), ("s066", 165.336, 167.132)]  # no band's ends to read: the rig's lights carry them
RIG_SCALE = ("s052",)  # one end of the band behind her, 3-4 steady lights: the end carries the shift, the lights the scale
ONE_TOP = {("s020", 49.98): "tr"}  # the left half's top passes behind a dancer's lit hair: the right half alone
TOPS = {("s017", 44.1): 513, ("s018", 45.9): 505, ("s018", 47.19): 465, ("s019", 47.712): 465, ("s020", 49.531): 463,
        ("s020", 49.98): 483, ("s021", 51.339): 419, ("s023", 55.7): 335, ("s024", 56.799): 448, ("s025", 60.423): 360,
        ("s026", 64.05): 416, ("s030", 71.282): 297, ("s047", 107.87): 452, ("s048", 109.22): 415, ("s049", 111.032): 460,
        ("s050", 112.828): 353,
        ("s052", 118.239): 355, ("s053", 120.031): 491, ("s060", 149.061): 445, ("s061", 150.872): 310, ("s061", 152.32): 358,
        ("s062", 152.673): 462, ("s063", 154.483): 480, ("s065", 161.72): 357, ("s066", 165.336): 443, ("s051", 114.631): 60}  # 720p px, by eye
ENDS = {("s017", 44.1): (152, 1108), ("s018", 45.9): (156, 1100), ("s018", 47.19): (122, 1221), ("s019", 47.712): (122, 1221),
        ("s020", 49.531): (122, 1218), ("s020", 49.98): (146, None), ("s021", 51.339): (122, 1252), ("s023", 55.7): (None, None),
        ("s024", 56.799): (None, 1105), ("s025", 60.423): (None, 1171), ("s026", 64.05): (128, None), ("s030", 71.282): (168, 1147),
        ("s047", 107.87): (None, 1205), ("s048", 109.22): (160, None), ("s049", 111.032): (96, 1197), ("s050", 112.828): (113, 1170),
        ("s052", 118.239): (None, 1170),
        ("s053", 120.031): (37, 1232), ("s060", 149.061): (165, 1100), ("s061", 150.872): (175, 1085), ("s061", 152.32): (172, 1085),
        ("s062", 152.673): (229, 1072), ("s063", 154.483): (None, None), ("s065", 161.72): (None, None), ("s066", 165.336): (None, None),
        ("s051", 114.631): (210, 1050)}  # 720p px, by eye (the overlay of each take's reads); None: behind her or out of frame


def _step(p, a, b, sign, k=12, gap=3):
    """The strongest big dark-to-bright step (sign 1) in p between a and b: its place, the levels each side. Measured on a
    scale of k samples, so a thin line, a light or a soft ramp doesn't take it."""
    c = np.concatenate([[0.0], np.cumsum(p)])
    a, b = max(a, k + gap), min(b, len(p) - k - gap - 1)
    if b <= a:
        return None
    i = np.arange(a, b)
    lo = (c[i - gap] - c[i - gap - k]) / k
    hi = (c[i + gap + k] - c[i + gap]) / k
    d = (hi - lo) * sign
    if d.max() < 24:
        return None
    # the outermost step of real size, seen from the dark side, so a dark figure inside the band isn't taken for its end
    big = np.flatnonzero(d > 0.6 * d.max())
    run = big[:1] if sign > 0 else big[-1:]
    m = int(run[0])
    while True:
        n = m + (1 if sign > 0 else -1)
        if 0 <= n < len(d) and d[n] > d[m]:
            m = n
        else:
            break
    return int(i[m]), float(lo[m]), float(hi[m])


def _half(p, at, lo, hi, sign):
    """Where p crosses halfway between the levels, nearest the step."""
    m = (lo + hi) / 2
    a, b = max(0, at - 16), min(len(p) - 1, at + 16)
    q = p[a:b + 1]
    k = np.flatnonzero((q[:-1] - m) * (q[1:] - m) <= 0)
    if not len(k):
        return None
    i = k[np.argmin(np.abs(a + k - at))]
    return a + i + (m - q[i]) / (q[i + 1] - q[i] + 1e-6)


def _steep(p, at, lo, hi, sign):
    """The steepest point near the step."""
    a, b = max(1, at - 16), min(len(p) - 2, at + 16)
    q = np.convolve(p, [1, 2, 1], "same") / 4
    d = (q[a + 1:b + 1] - q[a - 1:b - 1]) * sign
    i = int(np.argmax(d))
    if 0 < i < len(d) - 1:
        den = d[i - 1] - 2 * d[i] + d[i + 1]
        if den < 0:
            return a + i + 0.5 * (d[i - 1] - d[i + 1]) / den
    return float(a + i)


def _frames_of(sid, a, b):
    s = gfx.SHOTS[sid]
    return [n for n in range(round(float(s["t0"]) * 25), round(float(s["t1"]) * 25)) if a - 1e-6 <= n / 25 < b - 1e-6]


def _masked(film, sid, T):
    f = film.picture(sid, T)
    V = f.max(axis=2).astype(np.float32)
    h, w = V.shape
    V[cv2.dilate((gfx.matte(sid, T, h, w) > 0.03).astype(np.uint8), np.ones((13, 13), np.uint8)) > 0] = np.nan
    return f, V


def _reads(sid, a, b, film):
    """Every frame's edges by both detectors: {"half": {tl, tr, L, R}, "steep": ...}, with the picture's step index. Only
    the place to search carries over from frame to frame."""
    ns = _frames_of(sid, a, b)
    keys = ("tl", "tr", "L", "R")
    out = {"half": {k: [] for k in keys}, "steep": {k: [] for k in keys}}
    prev, d, y, ends, xs = None, [], float(TOPS[(sid, a)]), None, None
    for i, n in enumerate(ns):
        f, V = _masked(film, sid, n / 25)
        if prev is not None:
            d.append(float(np.abs(f.astype(np.int16) - prev).mean()))
        prev = f
        h, w = V.shape
        ya, yb = int(np.clip(y - 40, 16, h - 60)), int(np.clip(y + 40, 60, h - 16))
        if i == 0:
            ends = [None if e is None else float(e) for e in ENDS[(sid, a)]]
            x0, x1 = int(ends[0] or 20), int(ends[1] or w - 20)
            mid = (x0 + x1) // 2
            xs = ((x0 + 12, mid), (mid, x1 - 12))
        tops = {}
        for j, (c0, c1) in enumerate(xs):
            hit = None
            S = V[ya:yb, c0:c1]
            ok = np.isfinite(S).mean(0) > 0.9
            p = np.nanmedian(S[:, ok], axis=1) if ok.sum() >= 24 else None
            if p is not None and np.isfinite(p).sum() > 20:
                p = np.interp(np.arange(len(p)), np.flatnonzero(np.isfinite(p)), p[np.isfinite(p)])
                hit = _step(p, 0, yb - ya, 1)
            for name, det in (("half", _half), ("steep", _steep)):
                v = det(p, *hit, 1) if hit else None
                out[name][("tl", "tr")[j]].append(np.nan if v is None else (ya + v) * 1.5)
                if name == "half" and v is not None:
                    tops[j] = ya + v
        if tops:
            y = sum(tops.values()) / len(tops)
        for j, (key, sign) in enumerate((("L", 1), ("R", -1))):
            hit, p, a2 = None, None, 0
            e = ends[j]
            if e is not None:
                r0, r1 = int(np.clip(y + 5, 2, h - 8)), int(np.clip(y + 26, 8, h - 2))
                a2, b2 = int(max(1, e - 30)), int(min(w - 2, e + 30))
                S = V[r0:r1, a2:b2]
                if S.size and np.isfinite(S).mean() > 0.5:
                    p = np.nanmedian(S, axis=0)
                    if np.isfinite(p).sum() > 30:
                        p = np.interp(np.arange(len(p)), np.flatnonzero(np.isfinite(p)), p[np.isfinite(p)])
                        hit = _step(p, 0, len(p), sign, k=10, gap=2)
            for name, det in (("half", _half), ("steep", _steep)):
                v = det(p, *hit, sign) if hit else None
                if v is not None and not 12 < a2 + v < w - 12:
                    v = None
                out[name][key].append(np.nan if v is None else (a2 + v) * 1.5)
                if name == "half" and v is not None:
                    ends[j] = a2 + v
    d = np.array(d)
    step = np.concatenate([[0], np.cumsum(d > 0.12 * np.median(d))]).astype(int)
    x = {k: {e: np.array(v, float) for e, v in r.items()} for k, r in out.items()}
    return ns, step, x, tuple((c0 + c1) * 0.75 for c0, c1 in xs)


def _fill(v):
    k = np.isfinite(v)
    return np.interp(np.arange(len(v)), np.flatnonzero(k), v[k]) if k.sum() >= 2 else None


def _settle(v, step, other=None):
    """Over distinct source frames, so the picture's held frames hold. One frame off its neighbours is a bad read unless the
    other detector saw it too: then the picture jerked (or punched, s051), and the graphic goes with it. A touch of [1 2 1]
    takes the sub-pixel shake only."""
    first = [int(np.flatnonzero(step == i)[0]) for i in range(step[-1] + 1)]
    u = v[first].copy()
    if len(u) >= 5:
        r = np.pad(u, 1, mode="edge")
        m = np.median(np.stack([r[:-2], r[1:-1], r[2:]]), axis=0)
        bad = np.abs(u - m) > 3
        if other is not None:
            o = other[first]
            bad &= ~(np.abs(o - u) < 2.5)
        u[bad] = m[bad]
        r = np.pad(u, 1, mode="edge")
        w = (r[:-2] + 2 * r[1:-1] + r[2:]) / 4
        u = np.where(np.abs(w - u) < 2, w, u)  # shake only: a jerk or a punch stays whole
    return u[step]


def rig(film, sid, a, b):
    """How the rig moves in a stretch: its lights, found in each frame, each frame fitted to the first (scale, x, y), never
    chained. A second view on sideways and scale where the band's ends can't be read, and the only one where nothing
    was tracked. Returns frames, S (n x 3), residual, lights matched, the picture's step index."""
    ns = _frames_of(sid, a, b)
    K = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    base, S, res, cnt, d, prev = None, [], [], [], [], None
    for n in ns:
        f = film.picture(sid, n / 25)
        if prev is not None:
            d.append(float(np.abs(f.astype(np.int16) - prev).mean()))
        prev = f
        g = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY)
        m = cv2.dilate((gfx.matte(sid, n / 25, 720, 1280) > 0.15).astype(np.uint8), np.ones((9, 9), np.uint8))
        th = ((cv2.morphologyEx(g, cv2.MORPH_TOPHAT, K) > 40) & (m == 0)).astype(np.uint8)
        k, _, st, cen = cv2.connectedComponentsWithStats(th, 8)
        pts = np.array([cen[i] * 1.5 for i in range(1, k) if 8 <= st[i][4] <= 300 and cen[i][1] < 330]).reshape(-1, 2)
        if base is None:
            base = pts
            S.append(np.array([1.0, 0, 0]))
            res.append(0.0)
            cnt.append(len(pts))
            continue
        pred = S[-1] + (S[-1] - S[-2]) if len(S) > 1 else S[-1]
        far = np.linalg.norm((pred[0] * base + pred[1:3])[:, None] - pts[None], axis=2) if len(pts) else np.zeros((len(base), 0))
        if not far.size:
            S.append(pred)
            res.append(np.nan)
            cnt.append(0)
            continue
        j, ok = far.argmin(1), far.min(1) < 14
        if ok.sum() < 4:
            S.append(pred)
            res.append(np.nan)
            cnt.append(int(ok.sum()))
            continue
        q, keep = _robust(base[ok], pts[j[ok]])
        S.append(q)
        res.append(float(np.sqrt((np.linalg.norm(q[0] * base[ok][keep] + q[1:3] - pts[j[ok]][keep], axis=1) ** 2).mean())))
        cnt.append(int(keep.sum()))
    d = np.array(d)
    return ns, np.array(S), np.array(res), np.array(cnt), np.concatenate([[0], np.cumsum(d > 0.12 * np.median(d))]).astype(int)


def lock(film, only=()):
    for sid, a, b in TAKES:
        if only and sid not in only:
            continue
        ns, step, x, (xa, xb) = _reads(sid, a, b, film)
        r = x["half"]
        tl, tr = _fill(r["tl"]), _fill(r["tr"])
        if ONE_TOP.get((sid, a)) == "tr" or tl is None or np.isfinite(r["tl"]).mean() < 0.6:
            tl = tr
        elif tr is None or np.isfinite(r["tr"]).mean() < 0.6:
            tr = tl
        o = x["steep"]
        gap = tl - tr  # a real jerk moves both halves; one half alone jumping is that half's read
        pad = np.pad(gap, 2, mode="edge")
        odd = np.abs(gap - np.median(np.stack([pad[k:k + len(gap)] for k in range(5)]), axis=0)) > 4
        for q in (tl, tr):
            pad = np.pad(q, 1, mode="edge")
            q[odd] = np.median(np.stack([pad[:-2], pad[1:-1], pad[2:]]), axis=0)[odd]
        L = _settle(_fill(r["L"]), step, o["L"]) if np.isfinite(r["L"]).mean() > 0.6 else None
        R = _settle(_fill(r["R"]), step, o["R"]) if np.isfinite(r["R"]).mean() > 0.6 else None
        tl, tr = _settle(tl, step, o["tl"]), _settle(tr, step, o["tr"])
        rot = np.arctan2(tr - tl, xb - xa)
        rot -= rot[0]
        sc = np.ones(len(ns))
        if L is not None and R is not None:
            sc, ax = (R - L) / (R[0] - L[0]), (L + R) / 2
        elif L is not None or R is not None:
            ax = L if L is not None else R
            if sid in RIG_SCALE:
                _, S, _, _, st2 = rig(film, sid, a, b)
                sc = _settle(S[:, 0], st2)
        else:
            ax = np.full(len(ns), (xa + xb) / 2)
        _write(sid, ns, sc, rot, ax, (tl + tr) / 2, ym=(xa + xb) / 2)
        print(sid, a, f"{len(ns)} frames, {step[-1] + 1} source, ends {'L' if L is not None else '-'}{'R' if R is not None else '-'}",
              f"scale {sc[-1]:.3f}, turn {math.degrees(rot[-1]):.2f} deg, x {ax[-1] - ax[0]:.1f}, y {((tl + tr) / 2)[-1] - ((tl + tr) / 2)[0]:.1f}", flush=True)
    for sid, a, b in RIGGED:
        if only and sid not in only:
            continue
        ns, S, _, _, step = rig(film, sid, a, b)
        sc, tx, ty = (_settle(S[:, k], step) for k in range(3))
        _write(sid, ns, sc / sc[0], np.zeros(len(ns)), tx + 960 * sc, ty + 540 * sc, (960.0, 540.0))
        print(sid, a, f"from the rig: scale {sc[-1]:.3f}, x {tx[-1]:.1f}, y {ty[-1]:.1f}", flush=True)


def _write(sid, ns, sc, rot, ax, ay, at=None, ym=None):
    """Into the shot's plane file, only this take's frames: turned and scaled so that x at (ax[0], ay[0]) goes to ax, and y
    at (ym, ay[0]) goes to ay: the top is read at mid-band, the side at its end, and a turn has to meet both there."""
    P = gfx.ROOT / f"media/cache/gfx/plane-{sid}.json"
    if P.exists():
        p = json.loads(P.read_text())
    else:
        s = gfx.SHOTS[sid]
        ts = [n / 25 for n in range(round(float(s["t0"]) * 25), round(float(s["t1"]) * 25))]
        p = {"t": ts, "H": [np.eye(3).tolist() for _ in ts]}
    ax0, ay0 = at or (ax[0], ay[0])
    ym = ax0 if ym is None else ym
    for i, n in enumerate(ns):
        c, s_ = sc[i] * math.cos(rot[i]), sc[i] * math.sin(rot[i])
        H = [[c, -s_, ax[i] - c * ax0 + s_ * ay0], [s_, c, ay[i] - s_ * ym - c * ay0], [0, 0, 1]]
        p["H"][int(np.searchsorted(p["t"], n / 25 - 1e-6))] = [[float(v) for v in row] for row in H]
    P.write_text(json.dumps(p))


def audit(film, only=()):
    """Where the real wall() call puts a marker on the band's ends and foot, read from its pixels, against the edge read with
    the other detector. Both measured from the take's first frames, so a soft edge's offset between detectors isn't counted."""
    rows = []
    for sid, a, b in KEPT + TAKES:
        if only and sid not in only:
            continue
        ns, step, x, (xa, xb) = _reads(sid, a, b, film)
        r = x["steep"]
        cols = (int(xa / 1.5), int(xb / 1.5))
        top0 = np.nanmedian(np.concatenate([r["tl"][:4], r["tr"][:4]]))
        m = {k: [] for k in ("tl", "tr", "L", "R")}
        L0, R0 = np.nanmedian(r["L"][:3]), np.nanmedian(r["R"][:3])
        l_, e_ = (L0 if np.isfinite(L0) else -600.0), (R0 if np.isfinite(R0) else 2520.0)
        q = ((l_, top0 - 900), (e_, top0 - 900), (e_, top0), (l_, top0))
        for n in ns:
            T = n / 25
            f = np.zeros((720, 1280, 3), np.uint8)
            f = wall(f, lambda c: c.fill((0, 255, 0)), q, sid, T, size=(600, 300), bloom=0, gain=1, dim=1, led=False)
            G = f[..., 1].astype(np.float32) / 255
            hold = gfx.matte(sid, T, 720, 1280) < 0.03
            xs_, ys = [], []  # the marker's foot as a line, so it's read where the edge is, whichever columns she leaves clear
            for c in range(4, 1276, 6):
                k = np.flatnonzero(G[:, c] > 0.5)
                if len(k) and k[-1] < 716 and hold[max(k[-1] - 8, 0):k[-1] + 8, c].all():
                    xs_.append(c)
                    ys.append(k[-1] + G[k[-1] + 1, c])
            fit = None
            if len(xs_) >= 12:  # her edge can cut the marker short: the foot is the lowest line, a few stragglers above it
                u, v = np.array(xs_, float), np.array(ys, float)
                k = v > np.percentile(v, 50) - 4
                for _ in range(5):
                    fit = np.polyfit(u[k], v[k], 1)
                    k2 = np.abs(np.polyval(fit, u) - v) < 2.5
                    if k2.sum() < 8 or (k2 == k).all():
                        break
                    k = k2
            for key, c0 in (("tl", cols[0]), ("tr", cols[1])):
                m[key].append(float(np.polyval(fit, c0)) * 1.5 if fit is not None else np.nan)
            fy = [v for v in (m["tl"][-1], m["tr"][-1]) if np.isfinite(v)]
            py = int(np.clip(np.mean(fy) / 1.5 - 30, 8, 712)) if fy else 300
            for key, end in (("L", L0), ("R", R0)):
                vs = []
                for y in range(py - 30, py + 1, 6):
                    if not 0 <= y < 720:
                        continue
                    k = np.flatnonzero(G[y] > 0.5)
                    if not len(k):
                        continue
                    e = k[0] if key == "L" else k[-1]
                    if 2 < e < 1277 and hold[y, max(e - 8, 0):e + 8].all():
                        vs.append(e - G[y, e - 1] if key == "L" else e + G[y, e + 1])
                m[key].append(float(np.median(vs)) * 1.5 if vs and np.isfinite(end) else np.nan)
        worst, which, cover, raw = 0.0, "", [], 0.0
        for key in ("tl", "tr", "L", "R"):
            if ONE_TOP.get((sid, a)) and key == "tl":  # known not to be the band's edge
                continue
            a0, b0 = np.array(m[key]), r[key]
            e = (a0 - np.nanmedian(a0[:3])) - (b0 - np.nanmedian(b0[:3]))
            raw = max(raw, float(np.nanmax(np.abs(e))) if np.isfinite(e).any() else 0.0)
            diff = (b0 - x["half"][key]) - np.nanmedian((b0 - x["half"][key])[:5])
            e[np.abs(diff) > 6] = np.nan  # the two detectors disagree here: glitter on the edge, no measurement
            n_ok = int(np.isfinite(e).sum())
            cover.append(f"{key}{n_ok}")
            if n_ok:
                e_ok = e[np.isfinite(e)]
                if np.abs(e_ok).max() > worst:
                    worst, which = float(np.abs(e_ok).max()), f"{key}@{ns[int(np.nanargmax(np.abs(e)))] / 25:.2f}"
        rep = int((np.diff(step) == 0).sum())
        rows.append((sid, a, len(ns), rep, round(worst, 1), which, " ".join(cover)))
        print(sid, round(a, 2), f"frames {len(ns)} held {rep} worst {worst:.1f} {which} (all reads {raw:.1f}) | read: {' '.join(cover)}", flush=True)
    for sid, a, b, box in (("s028", 68.12, 69.478, (120, 40, 1800, 240)), ("s066", 165.336, 167.132, (300, 190, 1640, 640))):
        if only and sid not in only:
            continue
        ns, S, _, cnt, step = rig(film, sid, a, b)  # no band's ends: the plane against the rig's lights, at the graphic's corners
        c = np.array([[box[0], box[1], 1], [box[2], box[1], 1], [box[2], box[3], 1], [box[0], box[3], 1.0]])
        H0 = gfx.plane(sid, ns[0] / 25)
        worst = 0.0
        for i, n in enumerate(ns):
            H = gfx.plane(sid, n / 25) @ np.linalg.inv(H0)
            worst = max(worst, float(np.abs((c @ H.T)[:, :2] - (S[i, 0] * c[:, :2] + S[i, 1:3])).max()))
        rep = int((np.diff(step) == 0).sum())
        rows.append((sid, a, len(ns), rep, round(worst, 1), "rig", f"lights {int(np.median(cnt))}"))
        print(sid, round(a, 2), f"frames {len(ns)} held {rep} worst {worst:.1f} at the graphic's corners, against the rig | lights {int(np.median(cnt))}", flush=True)
    return rows


if __name__ == "__main__":
    if sys.argv[1:] == ["planes"]:
        planes()
    elif sys.argv[1:] == ["walk"]:
        import gfxrender
        walk(gfxrender.Film())
    elif sys.argv[1:2] in (["lock"], ["audit"]):
        import gfxrender
        film_ = gfxrender.Film()
        (lock if sys.argv[1] == "lock" else audit)(film_, sys.argv[2:])

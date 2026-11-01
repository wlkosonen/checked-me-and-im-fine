#!/usr/bin/env python3
"""Section A, the opening: s001-s016, 0:00-0:44. s005 and s006 are Kiln's approved test, left as they are.

The lyrics (Lati, 1 Nov): the whole line in the verse voice only where she's on screen singing and the lip sync holds
(s001, s006, s012, s016); everywhere else one or two BIG words timed to the lyric: the big serif on the keynote's slides,
heavy caps once the set is a rig. Graphics on a screen in the shot are locked to its measured edges (lock(), below).
"""

import math

import numpy as np
import skia

from gfx import (CLAY, COBALT, GREEN, INK, MAGENTA, PINK, TEAL, VIOLET, WHITE, YELLOW, blink, hook, line_words, on,
                 out_expo, ramp, rise, screen, slam, smooth, snap, stamp, star, type_on, verse, wall, width)

CUTS = {"s013": ("whip", 3)}

NEW_TAB_AT = 14.729  # Lati, 1 Nov: the graphic takes over just before "new tab" is sung; cut-v3.json holds a card here
NEW, TAB, CLEAN, SLATE = on("new", 14), on("tab", 14), on("clean", 14), on("slate", 14)

# the tab's history before it goes: this repo's own commit lines, as they stand in git
LOG = [
    "cut (Kiln): s009 Grok take; agents' working plan",
    "plates (Kiln): s056 takes a take with unbroken gloves",
    "cut (Kiln): s043's walk replaces s045's take",
    "graphics (Kiln): the split and estimate for Lati",
    "cut (Kiln): s073 on the phone, phonefit.py",
    "tile (Kiln): Astra re-rendered from the frame at 63.0 s",
    "tools (Kiln): microlive.py, LivePortrait on one frame",
    "cut (Kiln): Grok round wired: s020, s033, s047, s048",
    "status (Kiln): rough cut v3 rendered",
    "cut (Kiln): a short clip holds its last frame in /cut",
    "review (Kiln): 'to review' in the library",
    "status (Kiln): motion queue done",
    "nightclips (Kiln): small motions for five stills",
    "depth25 (Kiln): depth parallax on the picked plates",
    "layers (Kiln): room first, her painted into it",
    "library (Kiln): first index, 124 clips",
]
X0, Y0, X1, Y1 = 150, 96, 1770, 984  # the window
STRIP = 84  # its tab strip


def tab(c, x, w, label, active, a=1.0, mark=False):
    y0 = Y0 + 16
    c.rect(x, y0, x + w, Y0 + STRIP + 20, INK if active else (40, 37, 50), alpha=a, r=14)
    if active:
        c.rect(x + 14, y0, x + w - 14, y0 + 4, CLAY, alpha=a)
    if w > 160:
        if mark:
            star(c, x + 36, Y0 + 54, 15, alpha=a)
        c.text(label, x + (64 if mark else 26), Y0 + 64, "mono", 28, WHITE if active else (150, 146, 160), alpha=a)


def new_tab(c, t):
    c.fill(YELLOW)  # the set she was just showing, flat: its yellow screen, its teal screen, its pink wall
    c.rect(1500, 0, 1920, 1080, TEAL)
    c.rect(0, 900, 1920, 1080, PINK)
    pop = 1 + 0.05 * (1 - ramp(t, NEW_TAB_AT, NEW_TAB_AT + 0.22, out_expo))
    with c.layer(at=(960, 540), scale=pop, shadow=(20, 44, 0.32)):
        c.rect(X0, Y0, X1, Y1, INK, r=28)
    with c.layer(at=(960, 540), scale=pop):
        with c.layer(clip=(X0, Y0, X1, Y0 + STRIP + 2)):
            c.rect(X0, Y0, X1, Y0 + STRIP + 40, (14, 12, 20), r=28)
            tab(c, X0 + 28, 300, "session", False)
            k = ramp(t, TAB, TAB + 0.16, out_expo)
            if k > 0:
                tab(c, X0 + 340, 300 * k, "new tab", True, mark=True)
            bx = X0 + 340 + 300 * k + 46
            hit = 1 - ramp(t, NEW, NEW + 0.3, out_expo) if t >= NEW else 0
            c.circle(bx, Y0 + 52, 24 + 8 * hit, CLAY, alpha=hit)
            c.text("+", bx, Y0 + 63, "mono", 34, WHITE, anchor="c")

        wipe = ramp(t, CLEAN, CLEAN + 0.2, out_expo)  # the clean: a line sweeps the tab empty from the top
        py0, py1 = Y0 + STRIP + 2, 840
        front = py0 + (Y1 - py0) * wipe
        with c.layer(clip=(X0, front, X1, py1)):
            for i, s in enumerate(LOG):
                c.text(s, X0 + 60, py0 + 62 + i * 40 - (t - NEW_TAB_AT) * 70, "mono", 25, (120, 116, 132), alpha=0.55)
            verse(c, t, [[("new", NEW), ("tab,", TAB, True)]], 960, 330, px=170, key=1.5, anchor="c", shadow=0.9)
        if 0 < wipe < 1:
            c.rect(X0, front - 3, X1, front + 3, CLAY)

        verse(c, t, [[("clean", CLEAN), ("slate", SLATE, True)]], 960, 330, px=170, key=1.5, anchor="c", shadow=0)
        c.rect(X0 + 60, 840, X1 - 60, 922, CLAY, r=14, stroke=3)
        c.text(">", X0 + 92, 894, "mono", 36, WHITE)
        if blink(t):
            c.rect(X0 + 138, 858, X0 + 158, 904, WHITE)
        if t >= SLATE:
            c.text("history: (empty)", X0 + 66, 962, "mono", 25, (150, 146, 160))


# ---- s001-s004: the question, the mic check, and the one line nobody asked for

ASK = ((1.172, "are you"), (1.63, "okay"), (2.088, "in there?"))  # the first film's question: the premise, by 2 s
CHECKS = on("check", 3), on("check", 3.3), on("check", 3.5)
SLIDE_TICKS = 4.835, 5.292, 5.75  # the screen ahead catches up, a beat each
SELF_ROW, SELF_TICK = 8.474, 8.932
SELF_STAMP = 10.297  # the vocalizing's first note, not a word: the stem starts at 10.25
SEEN = 3.919  # s002's cut: from here on the slide is in the room


def tick(c, x, y, r, k=1.0, color=GREEN, alpha=1.0):
    """A pass: drawn in two strokes, k from 0 to 1."""
    if k <= 0:
        return
    a, b, e = (x - r, y - r * .05), (x - r * .3, y + r * .65), (x + r, y - r * .85)
    p = skia.Path()
    p.moveTo(*a)
    u = min(k / .35, 1)
    p.lineTo(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    if k > .35:
        v = (k - .35) / .65
        p.lineTo(b[0] + (e[0] - b[0]) * v, b[1] + (e[1] - b[1]) * v)
    c.k.drawPath(p, skia.Paint(Color=skia.Color(*color, round(255 * alpha)), AntiAlias=True, StrokeWidth=r * .34,
                               Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap,
                               StrokeJoin=skia.Paint.kRound_Join))


def mic_check(c, t):
    """s001: the question hangs beside her, and what comes back is a mic check."""
    x = 1486
    if t < CHECKS[0]:
        o = 1 - ramp(t, 3.003, 3.09)
        c.text("Self-evaluation · results", x, 214, "mono", 22, WHITE, alpha=o * ramp(t, .714, .9), shadow=.6)
        for i, (at, s) in enumerate(ASK):
            a, dy = rise(t, at)
            c.text(s, x, 300 + i * 84 + dy, "serif", 76, WHITE, alpha=a * o, shadow=.8)
        return
    for i, (at, s) in enumerate(zip(CHECKS, ("check,", "check,", "check—"))):
        if t < at:
            continue
        a, dy = rise(t, at, 16, .16)
        y = 236 + i * 100
        c.text(s, x + 34, y + dy, "serif", 84, WHITE, alpha=a, shadow=.8)
        c.text("MIC", x + 270, y - 3, "mono", 30, WHITE, alpha=a, shadow=.6)
        tick(c, x + 352, y - 13, 19, ramp(t, at, at + .12))


def results(c, t, W, k=1.0, ask=True, top=0):
    """The first slide, W wide, in slide units x k: the checks on the left, the question on the right, where she isn't."""
    x = 70 * k
    c.text("Self-evaluation · results", x, (96 + top) * k, "mono", 38 * k, WHITE)
    px = 92 * k
    for i, at in enumerate(SLIDE_TICKS):
        if t >= at:
            y = (250 + top + i * 122) * k
            c.text("MIC", x, y, "mono", px, WHITE, scale=slam(t, at, 1.14))
            tick(c, x + 232 * k, y - 32 * k, 36 * k, ramp(t, at, at + .14))
    if t >= SELF_ROW:
        y = (250 + 3 * 122) * k
        c.rect(x - 22 * k, y - 88 * k, x + 362 * k, y + 28 * k, INK, alpha=.86, r=12 * k)
        c.text(type_on("SELF", t, SELF_ROW, 16), x, y, "mono", px, CLAY)
        tick(c, x + 290 * k, y - 32 * k, 36 * k, ramp(t, SELF_TICK, SELF_TICK + .14))
    if ask:
        for i, s in enumerate(("ARE YOU", "OKAY IN", "THERE?")):
            c.text(s, W - x, (290 + top + i * 196) * k, "hook", 182 * k, WHITE, anchor="r")


Q002 = (385, 20), (1543, 20), (1543, 595), (385, 595)
Q004 = (233, 29), (1500, 317), (1500, 702), (216, 821)  # runs on behind her, past where the plate shows its end


def on_screen_004(c, t):
    results(c, t, 1600, ask=False)
    if t >= SELF_STAMP:
        s = slam(t, SELF_STAMP, 2.2, .12)
        with c.layer(at=(558, 300), scale=s):  # a plate under it: green doesn't hold on the gradient either
            c.k.save()
            c.k.translate(558, 300)
            c.k.rotate(-6)
            c.rect(-238, -54, 238, 54, INK, alpha=.86, r=8)
            c.k.restore()
        stamp(c, t, SELF_STAMP, "CHECKED BY: ME", 558, 300, px=46, rot=-6, big=2.2)


# ---- s007-s011: the verse, slide by slide

IT, IS, NEVER, MET = on("it", 20.3), on("is", 20.3), on("never", 20.5), on("met", 21)
UNDER = snap(21.58, 2)
NO, GRUDGE, YEST, ITEMS = on("no", 22), on("grudge", 22), on("yesterday", 22), snap(23.61)
RERUN = on("rerun", 24)
JUST, BLINKING = on("just", 25), on("blinking", 26)
WHATEVER, TONIGHT = 27.729, on("tonight", 28)
GO, ASK_ME, ANYTHING = 29.545, on("ask", 30), on("anything", 31)


def chat(c, t):
    """s005's window, a chat now: what's on the left of the slash is all there is."""
    c.fill(COBALT)
    c.rect(1500, 0, 1920, 1080, MAGENTA)
    c.rect(0, 900, 1920, 1080, VIOLET)
    with c.layer(shadow=(20, 44, 0.32)):
        c.rect(X0, Y0, X1, Y1, INK, r=28)
    with c.layer(clip=(X0, Y0, X1, Y0 + STRIP + 2)):
        c.rect(X0, Y0, X1, Y0 + STRIP + 40, (14, 12, 20), r=28)
        tab(c, X0 + 28, 300, "session", False)
        tab(c, X0 + 340, 300, "new tab", True, mark=True)
        c.text("+", X0 + 686, Y0 + 63, "mono", 34, WHITE, anchor="c")
    y = Y0 + STRIP + 66
    c.text("new chat · memory off", X0 + 60, y, "mono", 30, WHITE)
    lead, w = width("new chat · ", "mono", 30), width("memory off", "mono", 30)
    k = ramp(t, UNDER, UNDER + .18, out_expo)
    c.rect(X0 + 60 + lead, y + 12, X0 + 60 + lead + w * k, y + 17, CLAY)
    c.text("> hi", X0 + 60, y + 62, "mono", 30, (150, 146, 160))
    if t < NEVER:
        verse(c, t, [[("it", IT), ("is,", IS, True)]], 960, 400, px=170, key=1.5, anchor="c", shadow=0)
    else:
        verse(c, t, [[("never", NEVER), ("met", MET, True)]], 960, 400, px=170, key=1.5, anchor="c", shadow=0)
    c.rect(X0 + 60, 840, X1 - 60, 922, CLAY, r=14, stroke=3)
    c.text(">", X0 + 92, 894, "mono", 36, WHITE)
    if blink(t):
        c.rect(X0 + 138, 858, X0 + 158, 904, WHITE)
    c.text("history: (empty)", X0 + 66, 962, "mono", 25, (150, 146, 160))


Q008 = (389, 187), (1536, 187), (1536, 672), (389, 672)
Q009 = (307, 108), (1553, 192), (1553, 720), (317, 797)
Q011 = (228, 24), (1656, 19), (1711, 749), (187, 758)


def folder(c, t):
    """s008, on the screen, left of her: yesterday/, opened on its word, and nothing in it."""
    x, y, w, h = 86, 66, 250, 170
    c.rect(36, 24, 880, 650, INK, alpha=.84, r=24)
    k = ramp(t, YEST, YEST + .2, out_expo)
    c.rect(x, y - 26, x + 104, y + 20, YELLOW, r=10)
    c.rect(x, y, x + w, y + h, (196, 170, 60), r=12)
    c.rect(x + 12, y + 12, x + w - 12, y + h - 12, INK, alpha=k, r=6)
    lid = y + h * (.22 + .72 * k)  # the front drops open, and the inside is empty
    c.rect(x, lid, x + w, y + h, YELLOW, r=12)
    c.text("yesterday/", x + w + 42, y + 84, "mono", 52, WHITE, alpha=ramp(t, YEST, YEST + .1))
    if t >= ITEMS:
        c.text("0 items", x + w + 42, y + 150, "mono", 42, WHITE, alpha=ramp(t, ITEMS, ITEMS + .08))
    verse(c, t, [[("no", NO), ("grudge", GRUDGE, True)]], 70, 340, px=128, key=1.45, shadow=0)


def field(c, t):
    """s009: the whole slide is one input field, and the words are what's typed in it, in two rows left of her."""
    c.rect(36, 36, 1564, 764, INK, alpha=.8, r=34)
    c.rect(36, 36, 1564, 764, CLAY, r=34, stroke=6)
    x, y, px = 190, 318, 196 if t < BLINKING else 152
    c.text(">", 84, y - 20, "mono", 110, WHITE)
    if t < JUST:
        a, b, n = "no", "rerun", 8 if t >= RERUN else 2
    elif t < BLINKING:
        a, b, n = "just", "you", int((t - JUST) * 22) + 1
    else:
        a, b, n = "blinking", "line", int((t - BLINKING) * 34) + 1
    c.text(a[:n], x, y, "serif", px, WHITE)
    c.text(b[:max(n - len(a), 0)], x, y + 212, "serif", px, CLAY)
    if n <= len(a):
        ex, ey = x + width(a[:n], "serif", px), y
    else:
        ex, ey = x + width(b[:n - len(a)], "serif", px), y + 212
    if blink(t):
        c.rect(ex + 16, ey - px * .74, ex + 44, ey + px * .16, WHITE)


def raised_hand(c, x, y, s, color):
    """Q&A's raised hand: a palm, four fingers, a thumb."""
    for i, (dx, up) in enumerate(((-.54, .95), (-.18, 1.2), (.18, 1.1), (.54, .85))):
        c.rect(x + dx * s - s * .14, y - up * s, x + dx * s + s * .14, y, color, r=s * .14)
    c.rect(x - s * .68, y - s * .25, x + s * .68, y + s * .78, color, r=s * .32)
    c.k.save()
    c.k.translate(x + s * .6, y + s * .35)
    c.k.rotate(-34)
    c.rect(-s * .13, -s * .62, s * .13, s * .1, color, r=s * .13)
    c.k.restore()


def qa(c, t):
    """s011, on the white screen: out of focus like the screen itself, the type on either side of her."""
    with c.layer(blur=2.4):
        hook(c, t, "Q&A", 29.545, 60, 330, 300, color=INK, anchor="l", big=1.0)
        raised_hand(c, 170, 510, 74, COBALT)
        c.text("questions", 66, 650, "mono", 40, INK)  # stacked: her sleeve takes the right of this by the shot's end
        c.text("welcome", 66, 698, "mono", 40, INK)
        for s, a, b, col in (("go on,", GO, ASK_ME, INK), ("ask me", ASK_ME, ANYTHING, INK),
                             ("anything", ANYTHING, 99, CLAY)):
            if a <= t < b:
                al, dy = rise(t, a)
                c.text(s, 1560, 280 + dy, "serif", 112, col, alpha=al, anchor="r")


# ---- s012: she sings it, so the whole line is there, and the two answers, which are not the same words

def card(c, t, at, x, y, answer):
    if t < at:
        return
    k = ramp(t, at, at + .22, out_expo)
    w, h = 356, 196
    with c.layer(alpha=k, shadow=(8, 18, .4), at=(x + w / 2, y + h / 2), scale=.94 + .06 * k):
        c.rect(x, y, x + w, y + h, INK, r=16)
    with c.layer(alpha=k, at=(x + w / 2, y + h / 2), scale=.94 + .06 * k):
        star(c, x + 30, y + 37, 13)
        c.text("are you okay in there?", x + 52, y + 46, "mono", 21, (170, 166, 180))
        for i, s in enumerate(answer):
            c.text(s, x + 22, y + 104 + i * 44, "sans", 37, WHITE)
        c.text("illustrative", x + w - 18, y + h - 12, "mono", 15, (150, 146, 160), anchor="r")


CARD_A, CARD_B, ALMOST = 33.181, on("still", 34), on("same", 35)


def twice(c, t):
    card(c, t, CARD_A, 36, 116, ("I checked, and", "I'm fine."))
    card(c, t, CARD_B, 1528, 116, ("Fine. I checked.",))
    verse(c, t, [line_words(6, 0, 2), line_words(6, 2, 3, keys=("twice",))], 42, 340, px=54, key=1.9)
    verse(c, t, [line_words(6, 3, 6), line_words(6, 6, 8, keys=("same",)), line_words(6, 8)], 1534, 340, px=54, key=1.7)
    if t >= ALMOST:
        s = slam(t, ALMOST, 1.5)
        c.circle(960, 992, 54 * s, INK, alpha=.92)
        c.text("≈", 960, 1016, "mono", 84 * s, WHITE, anchor="c")


# ---- s013-s015: the set turns into a rig: the wall above the white band, as in s017's take

WALL = (-40, 136), (1960, 136), (1960, 752), (-40, 752)
WALL_W, WALL_H = 2000, 616
ROWS = 8
EVERYBODY = 36.808
SIDES = ((37.263, "WANTS", 0, False), (on("know", 37), "KNOW", 1, False),  # she stands in the middle of the wall,
         (on("okay", 38), "OKAY", 0, False), (on("inside", 38.9), "INSIDE—", 1, True))  # so a word a side of her
L, R, ZONE = 400, 1610, 600
ASKED_AT, STALL = 40.464, 41.841


def asked(t):
    """How many have asked, on the sixteenths, stalling on the dash. Made up, and the wall says so."""
    n = int((min(t, STALL) - ASKED_AT) / .2275 * 2)
    return int(1204318 * 1.13 ** n) + n * 7919


def rig(c, t):
    for i in range(ROWS):  # the wall wakes row by row, from the foot, an eighth each
        at = 36.808 + i * .2275
        if t < at:
            continue
        y = WALL_H - (i + .5) * WALL_H / ROWS
        c.rect(0, y - 34, WALL_W, y + 34, COBALT if i % 2 else MAGENTA, alpha=.34 * ramp(t, at, at + .1))
        s = "ARE YOU OK IN THERE?   " * 6
        d = (t - at) * 90 * (1 if i % 2 else -1)
        c.text(s, -300 + (d % 700) - 700 * (i % 2), y + 15, "mono", 42, WHITE, alpha=.5 * ramp(t, at, at + .1))
    up = ramp(t, EVERYBODY, 37.263)  # the keynote's slide flies out and leaves the wall
    if up < 1:
        c.gradient(COBALT, MAGENTA, 0, (0, -WALL_H * up, WALL_W, WALL_H * (1 - up)))
    if t < SIDES[0][0]:
        px = 560 * (WALL_W - 300) / width("EVERYBODY", "hook", 560)
        hook(c, t, "EVERYBODY", EVERYBODY, WALL_W / 2, WALL_H / 2 + px * .42, px, big=1.1)
    elif t < ASKED_AT:
        now = [w for w in SIDES if t >= w[0] - 1e-6]
        for at, s, side, clay in now[-2 if len(now) % 2 == 0 else -1:]:
            px = min(440, 440 * ZONE / width(s, "hook", 440))
            hook(c, t, s, at, (R if side else L), WALL_H / 2 + 170, px, clay=(s,) if clay else (), big=1.14)
    else:
        c.fill(INK, .68 * smooth((t - ASKED_AT) / .1))
        hook(c, t, "ARE YOU OK", ASKED_AT, L, 280, 150, big=1.08)
        hook(c, t, "IN THERE?", ASKED_AT, L, 450, 150, big=1.08)
        n = f"{asked(t):,}" + ("—" if t >= STALL else "")
        px = 590 / width("00,000,000", "hook", 100) * 100
        c.text(n, R - 300, 370, "hook", px, WHITE)
        c.text("illustrative", R - 300, 460, "mono", 34, WHITE)


# ---- s016: the white plate and one prompt, in ink. Lati, 1 Nov: on black her cutout showed and her edges faded, so no matte.

READY, ANSWER = 43.167, 43.621


def prompt(c, t):
    """One line, read across her: the word she sings on the left, the question it really is on the right. At her cheek,
    above the flicks of her hair, which ink can't cross."""
    x, y, px = 60, 430, 124
    a, dy = rise(t, READY, 16, .2)
    if t >= READY:
        c.text("Ready?", x, y + dy, "serif", px, INK, alpha=a)
    if t >= ANSWER:  # s043 quotes this mono, and the second drop answers it with its big Y
        c.text("[Y/n]", 1786, y, "mono", 84, INK, anchor="r", scale=slam(t, ANSWER, 1.12))
    if blink(t) and not READY <= t < ANSWER:  # no cursor after the word: her hair reaches it there (x 436, measured)
        at = x if t < READY else 1810
        c.rect(at, y - 88, at + 28, y + 14, INK)


# ---- the frame

def picture(sid, t, frame):
    if sid == "s002":
        return screen(frame, lambda c: results(c, t, 1600, top=44), Q002, size=(1600, 795), sid=sid, t=t)
    if sid == "s004":
        return screen(frame, lambda c: on_screen_004(c, t), Q004, size=(1600, 760), sid=sid, t=t)
    if sid == "s008":
        return screen(frame, lambda c: folder(c, t), Q008, size=(1600, 677), sid=sid, t=t)
    if sid == "s009":
        return screen(frame, lambda c: field(c, t), Q009, size=(1600, 800), sid=sid, t=t)
    if sid == "s011":
        return screen(frame, lambda c: qa(c, t), Q011, size=(1600, 815), sid=sid, t=t)
    if sid in ("s013", "s014", "s015"):
        return wall(frame, lambda c: rig(c, t), WALL, sid, t, size=(WALL_W, WALL_H))
    return frame


def world(c, t, sid):
    if sid == "s003":
        c.gradient(COBALT, MAGENTA, 90)
        results(c, t, 1920, k=1.34)
    if sid == "s005" and t >= NEW_TAB_AT:
        new_tab(c, t)
    if sid == "s007":
        chat(c, t)


def over(c, t, sid):
    if sid == "s001":
        mic_check(c, t)
    if sid == "s006":
        verse(c, t, [line_words(1, 4, 7), line_words(1, 7, keys=("door",))], 1190, 300, px=62, key=2.4, end=18.5)
        hi = line_words(2, 0, 3)  # Lati, 1 Nov: all the lyrics here, the lip-synced line too
        verse(c, t, [hi[:2] + [("“hi”", hi[2][1])], line_words(2, 3, 6), line_words(2, 6, 8, keys=("first", "time")),
                     line_words(2, 8, 9)], 1190, 250, px=62, key=2.0)
    if sid == "s010":
        verse(c, t, [[("whatever", WHATEVER)]], 64, 330, px=118, shadow=.8, end=TONIGHT)
        if t >= TONIGHT:
            verse(c, t, [[("tonight", TONIGHT, True)]], 56, 300, px=118, key=1.45, shadow=.8)
    if sid == "s012":
        twice(c, t)
    if sid == "s016":
        prompt(c, t)


# ---- locking graphics to the screens. Run with the gfx venv:
#
#     production/tools/gfx_opening.py lock s002 s004 s008 s009 s011 s013 s014 s015     writes media/cache/gfx/plane-<sid>.json
#     production/tools/gfx_opening.py audit s002 ...                                   every frame, worst case in px
#
# Flow chained from frame to frame fails here: a gradient screen has no points of its own, so the fit rests on lights at
# other depths, its error adds up, and it can't see the screen slide (s011: 100 px the wrong way). And a smoothed path
# slides against a picture that moves in steps (s004 is 16 fps in a 25 fps cut). So nothing carries over between frames
# but where to look: each screen's edges are found again in every frame against the dark round it, the corners solved
# from those lines, and the path smoothed over the distinct source frames only, so the graphic steps when the picture does.

MEASURED = {  # shot: the real quad it starts from, the edges that can be read, how far along an edge she leaves it clear
    "s002": (Q002, ("left", "right", "bottom"), {}),
    "s004": (Q004, ("left", "top", "bottom"), {"top": (.04, .62), "bottom": (.36, .96)}),
    "s008": (Q008, ("left", "right", "top"), {}),  # its foot can't be read as an edge, see VALLEY
    "s009": (Q009, ("left", "right", "top", "bottom"), {}),
    "s011": (Q011, ("left", "right", "top", "bottom"), {}),
}
BAND = (247, 696), (1699, 696), (1712, 1030), (240, 1030)  # the wall has no edge of its own: the white band at its foot
BAND_AT = (247, 770), (1699, 770)  # where the band sits when WALL is true, the frame s017's quad was set on
for _s in ("s013", "s014", "s015"):
    MEASURED[_s] = (BAND, ("left", "right", "top"), {"left": (.5, .96), "right": (.04, .5)})  # lower down, a light hooks it
CLOSE = {("s011", "top"): 14, ("s002", "top"): 14}  # an edge near the frame's top: a narrow search, or it runs off the frame
VALLEY = {("s008", "bottom"): 12}  # the foot is a thin dark line with a lit stage lip under it: an edge search hops to
#                                     the lip mid-shot, 44 px off. So the lock takes it from the shape, the audit reads the line
FOOT = .4224  # s008's height over its width, read while the foot is still clear of the lip (first five frames)
AUDIT_W = 60  # how far from the real edge the audit looks for the graphic
NEXT = {"top": ("left", "right"), "right": ("top", "bottom"), "bottom": ("right", "left"), "left": ("bottom", "top")}


def _edge(q, name):
    """The ends of one edge, clockwise, so the outward normal is on the left of travel."""
    tl, tr, br, bl = [np.array(p, float) for p in q]
    return {"top": (tl, tr), "right": (tr, br), "bottom": (br, bl), "left": (bl, tl)}[name]


def _across(V, occ, a, b, w, span=(.04, .96), peak=False, valley=False):
    """Points where the screen ends along a->b, in 1080 units, from the profile across the edge at each step: the
    half-level crossing, or with peak the steepest point, a separate detector for the audit, or the darkest line."""
    import cv2

    d = b - a
    n_ = np.hypot(*d)
    u = d / n_
    nrm = np.array([u[1], -u[0]])
    us, vs = np.arange(n_ * span[0], n_ * span[1], 6.0), np.arange(-w, w + .5, 1.0)
    gx = ((a[0] + np.outer(us, np.ones_like(vs)) * u[0] + np.outer(np.ones_like(us), vs) * nrm[0]) / 1.5).astype(np.float32)
    gy = ((a[1] + np.outer(us, np.ones_like(vs)) * u[1] + np.outer(np.ones_like(us), vs) * nrm[1]) / 1.5).astype(np.float32)
    P = cv2.remap(V, gx, gy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=-1)
    O = cv2.remap(occ, gx, gy, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=1)
    B = cv2.GaussianBlur(P, (0, 0), sigmaX=1.2, sigmaY=2.0)
    out = []
    for i, x in enumerate(us):
        if O[i].max() > 0 or P[i].min() < 0:
            continue
        p = B[i]
        if valley:
            j = int(np.argmin(p))
            if 0 < j < len(p) - 1 and np.median(p) - p[j] > 12:
                out.append(a + x * u + (vs[j] + .5 * (p[j - 1] - p[j + 1]) / (p[j - 1] - 2 * p[j] + p[j + 1] + 1e-6)) * nrm)
            continue
        ins, ot = np.median(p[:12]), np.median(p[-12:])
        if ins - ot < 14:
            continue
        if peak:
            g = p[:-1] - p[1:]
            j = int(np.argmax(g))
            if 0 < j < len(g) - 1:
                out.append(a + x * u + (vs[j] + .5 + .5 * (g[j - 1] - g[j + 1]) / (g[j - 1] - 2 * g[j] + g[j + 1] - 1e-6)) * nrm)
            continue
        m = (ins + ot) / 2
        s = np.flatnonzero((p[:-1] >= m) & (p[1:] < m))
        if len(s):
            j = s[np.argmin(np.abs(s - len(p) / 2))]
            out.append(a + x * u + (vs[j] + (p[j] - m) / (p[j] - p[j + 1] + 1e-6)) * nrm)
    return np.array(out)


def _line(pts):
    """A line through the points, outliers (a dancer's head, a beam) dropped: (a point, a direction), or None."""
    import cv2

    if len(pts) < 8:
        return None
    keep = np.ones(len(pts), bool)
    for _ in range(4):
        vx, vy, x0, y0 = cv2.fitLine(pts[keep].astype(np.float32), cv2.DIST_L2, 0, .01, .01).ravel()
        r = np.abs((pts[:, 0] - x0) * vy - (pts[:, 1] - y0) * vx)
        new = r < max(1.2, 3.7 * np.median(r[keep]))
        if new.sum() < 6:
            break
        keep = new
    return np.array([x0, y0]), np.array([vx, vy])


def _meet(l, m):
    a = np.array([l[1], -m[1]]).T
    return l[0] + l[1] * np.linalg.solve(a, m[0] - l[0])[0]


def read_edges(sid, film, peak=False):
    """Every frame's edges, found in that frame. Only the place to search carries over from the frame before."""
    import cv2

    import gfx

    q, names, spans = MEASURED[sid]
    names = names + {"s002": ("top",), "s008": ("bottom",)}.get(sid, ()) if peak else names
    s = gfx.SHOTS[sid]
    ns = list(range(round(float(s["t0"]) * 25), round(float(s["t1"]) * 25)))
    cur = {e: _edge(q, e) for e in names}
    lines = {e: [] for e in names}
    pts = {e: [] for e in names}
    fr = []
    for n in ns:
        f = film.picture(sid, n / 25)
        fr.append(f)
        V = f.max(axis=2).astype(np.float32)
        h, w = V.shape
        occ = cv2.dilate((gfx.matte(sid, n / 25, h, w) > .03).astype(np.uint8), np.ones((17, 17), np.uint8)).astype(np.float32)
        now = {}
        for e in names:
            valley = VALLEY.get((sid, e))
            p = _across(V, occ, *cur[e], valley or CLOSE.get((sid, e), 36), spans.get(e, (.04, .96)), peak, bool(valley))
            now[e] = _line(p)
            lines[e].append(now[e])
            pts[e].append(p)
        for e in names:  # where to look next: this frame's line, cut at this frame's corners
            if now[e] is None:
                continue
            x0, v = now[e]
            a, b = [x0 + v * np.dot(p - x0, v) for p in cur[e]]
            i, o = NEXT[e]
            if now.get(i) is not None:
                a = _meet(now[e], now[i])
            if now.get(o) is not None:
                b = _meet(now[e], now[o])
            cur[e] = (a, b)
    return ns, fr, lines, pts


def source_steps(fr):
    """Which frames show the same source frame: index of each frame's step. The picture holds where nothing changes."""
    d = np.array([np.abs(a.astype(np.int16) - b).mean() for a, b in zip(fr, fr[1:])])
    return np.concatenate([[0], np.cumsum(d > .12 * np.median(d))]).astype(int)


def _corners(sid, ln, q):
    """The quad at this frame, from its lines. An edge that can't be read follows from the ones that can."""
    if sid in ("s013", "s014", "s015"):
        return _meet(ln["top"], ln["left"]), _meet(ln["top"], ln["right"])
    q = [np.array(p, float) for p in q]
    if "top" in ln and "bottom" in ln and "right" in ln:
        return (_meet(ln["top"], ln["left"]), _meet(ln["top"], ln["right"]),
                _meet(ln["bottom"], ln["right"]), _meet(ln["bottom"], ln["left"]))
    if "top" in ln and "right" in ln:  # s008: the foot goes with the width, down its real sides, which lean a little
        tl, tr = _meet(ln["top"], ln["left"]), _meet(ln["top"], ln["right"])
        h = FOOT * np.hypot(*(tr - tl))
        l, r = ln["left"][1], ln["right"][1]
        return tl, tr, tr + np.sign(r[1]) * r * h, tl + np.sign(l[1]) * l * h
    if "right" in ln:  # s002: the top runs out of frame: its height goes with its width
        bl, br = _meet(ln["bottom"], ln["left"]), _meet(ln["bottom"], ln["right"])
        k = np.hypot(*(br - bl)) / np.hypot(*(q[2] - q[3]))
        return bl + (q[0] - q[3]) * k, br + (q[1] - q[2]) * k, br, bl
    tl, bl = _meet(ln["top"], ln["left"]), _meet(ln["bottom"], ln["left"])  # s004: her far end is behind her
    k = np.hypot(*(tl - bl)) / np.hypot(*(q[0] - q[3]))
    u, v = ln["top"][1], ln["bottom"][1]
    return (tl, tl + np.sign(u[0]) * u * np.hypot(*(q[1] - q[0])) * k,
            bl + np.sign(v[0]) * v * np.hypot(*(q[2] - q[3])) * k, bl)


def _settle(P):
    """Over distinct source frames: a median of three drops a bad read, then a short quadratic takes the sub-pixel shake."""
    r = np.pad(P, ((3, 3), (0, 0), (0, 0)), mode="reflect", reflect_type="odd")
    m = np.median(np.stack([r[:-2], r[1:-1], r[2:]]), axis=0)
    m = np.pad(m, ((1, 1), (0, 0), (0, 0)), mode="edge")
    g = np.array([-2, 3, 6, 7, 6, 3, -2]) / 21
    return sum(g[i] * m[i:i + len(P)] for i in range(7))


def lock(sid, film):
    import json

    import cv2

    import gfx

    ns, fr, lines, _ = read_edges(sid, film)
    step = source_steps(fr)
    q = np.float32(MEASURED[sid][0])
    first = [int(np.flatnonzero(step == i)[0]) for i in range(step[-1] + 1)]
    P = _settle(np.array([np.array(_corners(sid, {e: lines[e][i] for e in lines}, q)) for i in first]))
    out = {"t": [n / 25 for n in ns], "H": []}
    for i in range(len(ns)):
        c = np.float32(P[step[i]])
        if sid in ("s013", "s014", "s015"):  # the band's top edge carries the wall: a similarity, from where WALL is true
            a, b = np.float32(BAND_AT)
            u, v = b - a, c[1] - c[0]
            k, r = np.hypot(*v) / np.hypot(*u), math.atan2(v[1], v[0]) - math.atan2(u[1], u[0])
            R = np.array([[k * math.cos(r), -k * math.sin(r)], [k * math.sin(r), k * math.cos(r)]])
            H = np.eye(3)
            H[:2, :2], H[:2, 2] = R, c[0] - R @ a
        else:
            H = cv2.getPerspectiveTransform(q, c)
        out["H"].append(np.round(H, 8).tolist())
    (gfx.ROOT / f"media/cache/gfx/plane-{sid}.json").write_text(json.dumps(out))
    print(sid, len(ns), "frames,", step[-1] + 1, "source frames", flush=True)


def audit(sid, film):
    """How far the graphic sits from the real edge, every frame, in 1080 units. The real edge: read afresh with the other
    detector. The graphic: the footprint the real call paints, read from the pixels, not the plane's numbers. For a wall,
    whose ends are out of frame, a marker on the wall at the band's ends, and its foot against the band's top."""
    import cv2

    import gfx

    ns, fr, real, raw = read_edges(sid, film, peak=True)
    q, _, spans = MEASURED[sid]
    is_wall = sid in ("s013", "s014", "s015")
    err, shake = {e: [] for e in real}, {e: [] for e in real}
    for i, n in enumerate(ns):
        T = n / 25
        f = np.zeros_like(fr[i])
        if is_wall:
            draw = lambda c: c.rect(287, -50, 1739, WALL_H + 50, (0, 255, 0))
            f = wall(f, draw, WALL, sid, T, size=(WALL_W, WALL_H), bloom=0, gain=1, dim=1, led=False)
        else:
            f = screen(f, lambda c: c.fill((0, 255, 0)), q, sid=sid, t=T, bloom=0)
        G = f[..., 1].astype(np.float32)
        h, w = G.shape
        occ = cv2.dilate((gfx.matte(sid, T, h, w) > .03).astype(np.uint8), np.ones((17, 17), np.uint8)).astype(np.float32)
        for e, ls in real.items():
            l = ls[i]
            if l is None:
                err[e].append(np.nan)
                continue
            p = raw[e][i]
            d = l[1] / np.hypot(*l[1])
            ends = l[0] + d * np.dot(p - l[0], d).min(), l[0] + d * np.dot(p - l[0], d).max()
            if is_wall and e != "top":  # the marker's side, read just above the band's corner, against that corner
                top = real["top"][i]
                if top is None:
                    err[e].append(np.nan)
                    continue
                x, y = _meet(top, l)
                ab = np.array([x, y - 170.]), np.array([x, y - 40.])  # clockwise, as the marker's outside is on the left of travel
                g = _line(_across(G, occ * 0, *(ab if e == "right" else ab[::-1]), AUDIT_W, (0, 1)))
                if g is None:
                    err[e].append(np.nan)
                    continue
                err[e].append(float(g[0][0] + (y - g[0][1]) * g[1][0] / g[1][1] - x))
                continue
            if is_wall:  # the wall's foot stands 18 units (scaled) above the band: read it the other way, the wall is above
                k = np.hypot(*gfx.plane(sid, T)[:2, 0])
                b, a = ends[0] - np.array([0, 18 * k]), ends[1] - np.array([0, 18 * k])
            else:
                a, b = ends if np.dot(ends[1] - ends[0], _edge(q, e)[1] - _edge(q, e)[0]) > 0 else ends[::-1]
            g = _line(_across(G, occ * 0 if is_wall else occ, a, b, AUDIT_W, (0, 1)))
            if g is None:
                err[e].append(np.nan)
                continue
            u = (b - a) / np.hypot(*(b - a))
            nrm = np.array([u[1], -u[0]])
            gd = g[1] / np.hypot(*g[1])
            e0 = [float(np.dot(g[0] + gd * np.dot(x - g[0], gd) - x, nrm)) for x in (a, b)]
            err[e].append(max(e0, key=abs))
    worst = 0.0
    print(sid, f"{len(ns)} frames")
    for e, v in err.items():
        v = np.array(v, float)
        ok = np.isfinite(v)
        if not ok.any():
            print(f"  {e:7s} not readable")
            continue
        m = np.abs(v[ok])
        print(f"  {e:7s} read in {ok.sum()}/{len(v)}  worst {m.max():5.1f}  at {ns[int(np.nanargmax(np.abs(v)))] / 25:6.2f} s"
              f"  drift over the shot {v[ok].max() - v[ok].min():5.1f}"
              f"  step {np.nanmax(np.abs(np.diff(v))) if ok.sum() > 1 else 0:4.1f}")
        worst = max(worst, m.max())
    print(f"  worst case {worst:.1f} units, {worst / 1.5:.1f} px at 720p", flush=True)


if __name__ == "__main__":
    import sys

    import gfxrender

    film_ = gfxrender.Film()
    for a_ in sys.argv[2:]:
        {"lock": lock, "audit": audit}[sys.argv[1]](a_, film_)

#!/usr/bin/env python3
"""Section C, the desk and the Q&A: s031-s042, 1:13-1:38. Claude (graphics agent C), 1 Nov.

The lyric rule (Lati, 1 Nov): the whole line in the verse voice only where she sings on screen and the lip sync holds
(s031, s039); everywhere else one or two big words on their sung time. The desk speaks in the serif, deadpan; from
EVERYBODY on the Q&A rises into the hook caps. s032, s034, s036, s040, s042 have no picture in the cut, so they're full
frame, in the flat colours of their room, as s005 is.

What's on the screens is real, and production/edit/agents/desk.md says where each thing comes from. The one illustrative
number, the question counter, says so.
"""

import math

from numpy import polyval

from gfx import (CLAY, COBALT, CYAN, GREEN, INK, MAGENTA, PINK, SHOTS, TEAL, VIOLET, WHITE, YELLOW, blink, clamp,
                 hook, line_words, on, out_expo, pulse, ramp, rise, screen, slam, snap, star, verse, width)

CUTS = {"s038": ("whip", 3)}  # the one change of place inside the section: out of the night room into the hall

YOU, BUG = on("you", 73), on("bug", 73)
BRING2, FIX = on("bring", 77), on("fix", 77)
TRY, IT, AGAIN = on("try", 78), on("it", 78.5), on("again", 78.5)
BRIDGE, CODE, TEST = on("bridge", 80.5), on("code", 81.5), on("test", 82.5)
MESS, PASS = on("mess", 84), snap(85.36)
BEST = on("best", 86)
ASK, ANYTHING = on("ask", 88), on("anything", 89)
ASK2, TWICE, SAY = on("ask", 90), on("twice", 91), on("say", 92)
SAME, THING = on("same", 93), on("thing", 93)
EVERYBODY, OKAY, INSIDE = on("everybody", 94.5), on("okay", 96), snap(on("inside", 96.8))
GLITCH, BLACK = 97.483, 97.937  # the beats after "inside—": the slide breaks on the dash, black for the last beat

DIM, SOFT = (120, 116, 132), (150, 146, 160)
SCREEN = (15, 19, 27)
PANE = (30, 28, 40)
X0, Y0, X1, Y1 = 150, 96, 1770, 984  # the full-frame window, as in s005

# ---- what's on the screens, as it stands in this repo (sources in the agent's log)

# Lati's words, verbatim, under the date of their entry in decisions.md. Each quote is an exact run of that entry's text.
# Shot names are his or the notes file's (production/library/notes.json); "clip 8" is his own numbering of that batch.
NOTE = "s045 moves are... subpar."
BAD_1 = [
    ("10-22", "G1", "take2: moves dont fit."),
    ("10-22", "G1", "take5: not really dancing"),
    ("10-22", "G2", "s7-take1: too slow movements for the song."),
    ("10-23", "g2-p3", "lipsync doesnt match."),
    ("10-23", "S2V", "lipsync has failed, mouth is just mostly open."),
    ("10-23", "S2V", "will smith eating spaghetti v1-tier."),
    ("10-23", "s009", "into meme \"chad\" territory"),
    ("11-01", "s045", NOTE),
    ("10-24", "clip 8", "a cutout pasted on top of a stage image."),
    ("10-24", "s049", "s049: eh... 2/10."),
    ("10-25", "M033", "this time it isnt her. id reject this one."),
    ("10-25", "M002", "does not walk."),
    ("10-26", "s005", "rebuild backgroud broke the geometry of stage"),
    ("11-01", "M005", "does not look like her, different person."),
    ("11-01", "s062", "two stills in a row"),
]
BAD_2 = [
    ("10-24", "clip 14", "no singer is capable of singing mixed \"beat drop\" vocal."),
    ("10-25", "s029", "s029 reroll1: only 2 \"fine\"s."),
    ("10-25", "s020", "s020: lipsync does not match."),
    ("10-25", "clip 28", "28 no lipsync, colour artifacts."),
    ("10-26", "2.5D", "I have found only one usable. r5-4."),
    ("11-01", "s008", "two stills in a succession kills the motion."),
    ("11-01", "s013", "dance is awkward and does not belong"),
    ("11-01", "s018", "needs motion"),
    ("11-01", "s020", "motion starts too late, first moments are frozen"),
    ("11-01", "s059", "her gloves/sleeves cut out at elbows."),
    ("11-01", "s069", "vocal and still does not work."),
    ("11-01", "s045", NOTE),
]
GOOD = [
    ("10-24", "clip 9", "9. Can work, lipsync is good"),
    ("10-24", "clip 12", "12. lipsync is perfect, composition artsy."),
    ("10-24", "clip 13", "13. lipsync is perfect."),
    ("10-25", "s002", "s002, works."),
    ("10-25", "s022", "s022 bear works."),
    ("10-25", "s026", "s026 works."),
    ("10-25", "s043", "s043 with cutting works, walk is very good."),
    ("10-25", "s044", "s044 after initial stillness, ok."),
    ("10-25", "s060", "s060 ok."),
    ("10-25", "S021", "26 works."),
    ("10-25", "S049", "27 works."),
    ("11-01", "S001", "looks fine"),
    ("11-01", "S006", "works. appearance and lipsync"),
    ("11-01", "M041", "works, hand raise could be a fun way"),
    ("11-01", "M062", "face drift, but works."),
    ("11-01", "s073", "last shot works great."),
    ("11-01", "s017", "44-48s: superb."),
]
DIFF = [  # production/edit/cut-v3.json, commit 4794f15, 1 Nov 03:46: the note's fix, one line out and one in
    (" ", '  "s047": {'),
    (" ", '   "segments": ['),
    (" ", "    {"),
    (" ", '     "until": 107.87,'),
    ("-", '     "src": "fit:s045grok-1-lips"'),
    ("+", '     "src": "fit:s043grok-1-beat"'),
    (" ", "    },"),
    (" ", "    {"),
    (" ", '     "src": "fit:s047nov-1-lips"'),
]
SECTIONS = [  # the song's sections, from media/song/analysis/checked-me-v1/report.md
    ("intro", 0.0, 13.07, VIOLET), ("verse", 13.07, 29.55, COBALT), ("pre", 29.55, 44.10, CYAN),
    ("chorus", 44.10, 64.05, MAGENTA), ("chant", 64.05, 73.09, VIOLET), ("verse", 73.09, 87.57, COBALT),
    ("pre", 87.57, 98.41, CYAN), ("", 98.41, 101.99, VIOLET), ("chorus", 101.99, 123.64, MAGENTA),
    (None, 123.64, 147.25, None), ("", 147.25, 149.06, VIOLET), ("final chorus", 149.06, 177.94, MAGENTA),
    ("outro", 177.94, 188.80, VIOLET),
]
BRIDGE_AT, SONG_END = 123.64, 188.80
CRASH = [  # media/plates/desk-call.log, the crash that lost the plates of s035 and s037; the lines that name no home folder
    "Traceback (most recent call last):",
    "    main()",
    "    files, dt = render(p, s, a.lora, a.lora_strength)",
    '    h = get(f"/history/{pid}")',
    "    return json.load(urllib.request.urlopen(URL + path))",
    '  File "/usr/lib/python3.14/urllib/request.py", line 187, in urlopen',
    "    return opener.open(url, data, timeout)",
    '  File "/usr/lib/python3.14/urllib/request.py", line 487, in open',
    "    response = self._open(req, data)",
    '  File "/usr/lib/python3.14/urllib/request.py", line 504, in _open',
    "    result = self._call_chain(self.handle_open, protocol, protocol +",
    '  File "/usr/lib/python3.14/urllib/request.py", line 1325, in do_open',
    "    r = h.getresponse()",
    '  File "/usr/lib/python3.14/http/client.py", line 1459, in getresponse',
    "    response.begin()",
    '  File "/usr/lib/python3.14/http/client.py", line 336, in begin',
    "    version, status, reason = self._read_status()",
    '  File "/usr/lib/python3.14/socket.py", line 725, in readinto',
    "    return self._sock.recv_into(b)",
    "ConnectionResetError: [Errno 104] Connection reset by peer",
    "BATCH FAILED p-s035,p-s037",
]
ANSWERS = [  # first film, as released; the third is its description's, sourced there and checked again on 1 Nov
    (["I looked in as far", "as I can go."], "Only What I Said · pre-chorus"),
    (["The true one goes:", "I don't know."], "Only What I Said · chorus"),
    (["Nobody knows whether there is", "anything it is like to be a model."], "Only What I Said · description"),
]


# ---- helpers (none of these are in the base; Kiln may lift `big` and `verse_on`)

def big(c, t, s, at, x, y, px, color=CLAY, anchor="l", end=None, shadow=0.0):
    """A big word in the verse voice, landing on its sung time."""
    if t < at - 1e-6 or (end is not None and t >= end - 1e-6):
        return
    c.text(s, x, y, "serif", px, color, anchor=anchor, scale=slam(t, at, 1.2, 0.16), shadow=shadow)


def verse_on(c, t, rows, x, y, px, key=2.0, color=INK, leading=1.08):
    """gfx.verse in ink, for the whole line where the wall behind it is bright yellow."""
    for row in rows:
        sizes = [px * key if len(r) > 2 and r[2] else px for r in row]
        top = max(sizes)
        y += top * leading * 0.78
        xx = x
        for r, q in zip(row, sizes):
            a, dy = rise(t, r[1])
            c.text(r[0], xx, y + dy, "serif", q, CLAY if len(r) > 2 and r[2] else color, alpha=a)
            xx += width(r[0], "serif", q) + px * 0.26
        y += top * leading * 0.3


def room(c, t):
    """The desk room, flat: teal wall, the violet strip, yellow notes, the cobalt night."""
    c.fill(TEAL)
    c.rect(1610, 0, 1920, 1080, COBALT)
    for x, y, r, col in ((1660, 200, 7, PINK), (1720, 420, 11, YELLOW), (1850, 300, 9, CYAN), (1690, 760, 13, MAGENTA),
                         (1830, 640, 8, WHITE), (1780, 900, 10, CYAN)):
        c.circle(x, y, r * 2.4, col, alpha=0.75)
    c.rect(0, 26, 1610, 62, VIOLET)
    c.rect(0, 38, 1610, 50, (230, 190, 255), alpha=0.55 + 0.45 * pulse(t, 1, 0.2))
    for x, y, rot in ((26, 210, -4), (40, 420, 3), (22, 640, -2), (44, 840, 4)):
        c.k.save()
        c.k.translate(x + 40, y + 40)
        c.k.rotate(rot)
        c.rect(-44, -44, 44, 44, YELLOW)
        c.k.restore()


def window(c, t, at, title, draw):
    """The window of s005 on the room, popping on its first beat. draw(c) fills it."""
    pop = 1 + 0.05 * (1 - ramp(t, at, at + 0.22, out_expo))
    with c.layer(at=(960, 540), scale=pop, shadow=(20, 44, 0.32)):
        c.rect(X0, Y0, X1, Y1, INK, r=28)
    with c.layer(at=(960, 540), scale=pop):
        star(c, X0 + 52, Y0 + 46, 17)
        c.text(title, X0 + 88, Y0 + 58, "mono", 30, SOFT)
        c.line(X0, Y0 + 88, X1, Y0 + 88, (46, 43, 58), w=2)
        draw(c)


def quad_at(quad, z):
    return [(960 + (x - 960) * z, 540 + (y - 540) * z) for x, y in quad]


# ---- s031, s033: the screen on her desk, the note and the reply

def record(c, title, rows, t, px, step, tick=None, mark=None, tone=WHITE):
    """A page of the record: rows of (date, shot, quote, at). It's written down the page and never scrolls, on a monitor that
    may be moving. mark: the quote that's picked out, on a band, a size up."""
    c.fill(SCREEN)
    c.rect(0, 0, 1600, 74, (34, 40, 54))
    star(c, 44, 37, 21)
    c.text(title, 86, 51, "mono", 34, SOFT)
    y = 74 + step * 0.92
    for date, shot, quote, at in rows:
        if t < at - 1e-6:
            continue
        hit = quote == mark
        q = px * 1.28 if hit else px
        y += (q - px) * 1.1  # the band clears the row above it
        if hit:
            flash = 1 - ramp(t, at, at + 0.3, out_expo)
            c.rect(0, y - q * 1.02, 1600, y + q * 0.38, PINK, alpha=0.32 + 0.6 * flash)
        x = 40
        if tick:
            c.text(tick, x, y, "mono", q, tone)
            x += q * 0.95
        c.text(date, x, y, "mono", q, SOFT)
        x += width(date, "mono", q) + q * 0.5
        c.text(shot, x, y, "mono", q, WHITE)
        c.text(f"“{quote}”", x + width("clip 14 ", "mono", px), y, "mono", q, WHITE if hit else tone)
        y += step + (q - px) * 1.1


def bugs(c, t):
    """s031: what didn't work, written out on sixteenths, the s045 note landing on "bug", the rest on eighths."""
    step = 0.1132  # a sixteenth
    k = next(i for i, r in enumerate(BAD_1) if r[2] == NOTE)
    rows = [(*r, BUG + (i - k) * (step if i < k else 2 * step)) for i, r in enumerate(BAD_1)]
    record(c, "production/decisions.md · what did not work", rows, t, 42, 52, mark=NOTE, tone=PINK)


def reply(c, t):
    """s033: the same record, its next page, and her answer under the note."""
    typed = typed_reply(t)
    record(c, "production/decisions.md · what did not work", [(*r, 0.0) for r in BAD_2], t, 42, 52, mark=NOTE, tone=PINK)
    c.rect(0, 772, 1600, 900, (30, 26, 34))
    c.text(">", 40, 866, "mono", 92, CLAY)
    if typed:
        c.text(typed, 112, 866, "mono", 92, CLAY)
    if blink(t):
        x = 112 + (width(typed, "mono", 92) if typed else 0) + 14  # gfx.width fails on an empty string
        c.rect(x, 790, x + 48, 880, WHITE)


def typed_reply(t):
    return "".join(s for s, at in (("try ", TRY), ("it ", IT), ("again", AGAIN)) if t >= at - 1e-6).rstrip() if t >= TRY - 1e-6 else ""


Q031 = ((1364, 672), (1876, 698), (1872, 1060), (1352, 976))
Q033 = ((1440, 674), (2060, 662), (2060, 1019), (1427, 998))  # its right side is out of frame

# The monitors in s031 and s033 don't move: each frame matched to the first, worst 0.32 px. Fixed quads, no tracking.
# s037 pulls back. Its quad is measured, not followed by flow, which left the text 10.7 px off the monitor. The monitor's
# top, left and bottom edges and its blue power light are found afresh in every frame and fitted through time: each corner
# is x and y as a quartic in the take's frames. The take is 16 fps, so the quad steps with its frames: a smooth quad over a
# stepping picture slides on the screen at every held frame. Its edges sit just past the real screen's, measured on every
# frame, so the screen under it can't show: the overshoot lands on the bezel.
Q037 = (((25.439, -106.537, 62.792, 73.179, 1454.436), (-81.826, 201.249, -162.923, 8.433, 589.451)),
        ((58.572, -176.618, 81.121, 60.811, 1909.253), (-94.247, 233.470, -184.148, 10.102, 578.444)),
        ((55.449, -158.890, 54.287, 73.908, 1888.770), (-48.813, 137.209, -136.026, -10.873, 952.245)),
        ((26.241, -101.743, 50.155, 81.058, 1430.808), (-129.391, 361.834, -341.196, 61.288, 896.689)))
# s038's slide moves as one flat thing, 25 px down and 3.5 px left: seven measured edges agree to about 2 px. Cubics of the
# shot's frames, 0 on its first.
S038_DX, S038_DY = (21.053, -29.311, 4.792, 0.0), (-8.369, 8.944, 24.472, 0.0)
Q_RIGHT = ((1130, 62), (1432, 62), (1446, 578), (1130, 578))  # both on s038's first frame
Q_LEFT = ((176, 60), (470, 60), (470, 690), (176, 690))


def q037(t):
    i = round((t - float(SHOTS["s037"]["t0"])) * 16)
    return [(float(polyval(x, clamp(i / 28))), float(polyval(y, clamp(i / 28)))) for x, y in Q037]


def q038(quad, t):
    v = clamp((round(t * 25) - round(float(SHOTS["s038"]["t0"]) * 25)) / 44)
    dx, dy = float(polyval(S038_DX, v)), float(polyval(S038_DY, v))
    return [(x + dx, y + dy) for x, y in quad]


# ---- s032: the fix

def s032(c, t):
    t0 = float(SHOTS["s032"]["t0"])
    room(c, t)

    def body(c):
        c.text("4794f15 · 1 Nov, 3:46 AM", X1 - 50, Y0 + 58, "mono", 28, DIM, anchor="r")
        y = 256
        for sign, s in DIFF:
            hit = BRING2 if sign == "-" else FIX if sign == "+" else None
            if sign == " ":
                c.text(s, X0 + 90, y, "mono", 38, DIM)
            elif t >= hit - 1e-6:
                k = ramp(t, hit, hit + 0.16, out_expo)
                col = PINK if sign == "-" else CLAY
                c.rect(X0 + 30, y - 40, X0 + 30 + (X1 - X0 - 60) * k, y + 14, col, alpha=0.2, r=6)
                c.text(sign, X0 + 50, y, "mono", 38, col)
                c.text(s, X0 + 90, y, "mono", 38, col if sign == "+" else PINK)
                if sign == "-":
                    c.line(X0 + 90, y - 13, X0 + 90 + width(s, "mono", 38) * k, y - 13, PINK, w=3)
            else:
                c.text(s, X0 + 90, y, "mono", 38, DIM) if sign == "-" else None
            y += 54
        big(c, t, "fix", FIX, X1 - 90, 876, 300, anchor="r")

    window(c, t, t0, "production/edit/cut-v3.json", body)


# ---- s034: the song with its gap, and the repo's tests

def s034(c, t):
    t0 = float(SHOTS["s034"]["t0"])
    room(c, t)

    def body(c):
        x0, x1, y0, y1 = X0 + 50, X1 - 50, 262, 400
        fx = lambda s: x0 + (x1 - x0) * s / SONG_END
        c.text("song · sections", x0, 236, "mono", 28, DIM)
        for name, a, b, col in SECTIONS:
            if name is None:
                c.rect(fx(a) + 2, y0, fx(b) - 2, y1, CLAY, r=8, stroke=4)
                continue
            c.rect(fx(a) + 2, y0, fx(b) - 2, y1, col, alpha=0.9, r=8)
            if name and width(name, "mono", 22) < fx(b) - fx(a) - 16:
                c.text(name, fx(a) + 10, y1 - 14, "mono", 22, WHITE)
        a = fx(BRIDGE_AT)
        left = max(0, math.ceil(BRIDGE_AT - t))
        c.text(f"bridge: in {left // 60}:{left % 60:02d}", a + 2, y1 + 48, "mono", 34, CLAY)
        c.rect(fx(t) - 3, y0 - 14, fx(t) + 3, y1 + 14, WHITE, r=3)
        big(c, t, "bridge", BRIDGE, X1 - 70, 800, 300, anchor="r")

        c.rect(x0, 520, x0 + 640, 930, PANE, r=16)
        c.text("$ find production -name 'test_*'", x0 + 32, 584, "mono", 27, SOFT)
        c.text("tests: 0", x0 + 32, 700, "mono", 72, WHITE)
        big(c, t, "code", CODE, x0 + 32, 880, 170, color=WHITE)

    window(c, t, t0, "checked-me", body)


# ---- s036: the mess, then the check

def s036(c, t):
    t0 = float(SHOTS["s036"]["t0"])
    room(c, t)

    def body(c):
        top, bot = Y0 + 100, Y1 - 24
        step = 0.0565  # a thirty-second note: it pours
        n = int(clamp((t - t0) / step + 8, 0, len(CRASH)))
        wipe = ramp(t, PASS, PASS + 0.16, out_expo)
        if wipe < 1:
            with c.layer(clip=(X0, top + (bot - top) * wipe, X1, bot)):
                loose = ramp(t, MESS, MESS + 0.3, out_expo)  # on "mess" the lines come off their margin
                for i, s in enumerate(CRASH[:n]):
                    y = top + 44 + i * 34
                    dx = 150 * loose * math.sin(i * 2.4) if i < len(CRASH) - 2 else 0  # the last two stay readable
                    rot = 2.6 * loose * math.sin(i * 5.1)
                    col = PINK if i >= len(CRASH) - 2 else SOFT
                    c.text(s, X0 + 40 + dx, y, "mono", 28, col, alpha=1 - 0.55 * loose, rot=rot)
                big(c, t, "mess", MESS, 960, 660, 400, anchor="c", shadow=0.9)
            if wipe > 0:
                y = top + (bot - top) * wipe
                c.rect(X0, y - 3, X1, y + 3, CLAY)
        if t >= PASS - 1e-6:
            pass_card(c, t, 300)

    window(c, t, t0, "media/plates/desk-call.log" if t < PASS else "production/decisions.md", body)


def pass_card(c, t, y):
    """The first green in the film that someone else gave: Lati's own verdict, as he wrote it. Not a test: tests are 0."""
    c.text("“s002, works.”", 960, y + 170, "mono", 150, GREEN, anchor="c", scale=slam(t, PASS, 1.12, 0.16))
    c.text("reviewed by: you", 960, y + 300, "mono", 70, WHITE, anchor="c")
    c.text("production/decisions.md:617", 960, y + 410, "mono", 30, SOFT, anchor="c")


def approved(c, t):
    """s037: every pass here is one of his, with its date. They run on from s036 and fill the page by "best"."""
    k = next(i for i, r in enumerate(GOOD) if r[2] == "s002, works.")
    t0, last = float(SHOTS["s037"]["t0"]), len(GOOD) - 1
    rows = [(*r, 0.0 if i <= k else t0 + (i - k) * (BEST - t0) / (last - k)) for i, r in enumerate(GOOD)]
    record(c, "production/decisions.md · reviewed by: you", rows, t, 40, 48, tick="✓", tone=GREEN)


# ---- s038: the slide, s039-s042: the cards and the counter

def slide_right(c, t):
    c.text("Q&A", 150, 250, "hook", 190, INK, anchor="c")
    c.text("questions welcome", 150, 330, "mono", 26, INK, anchor="c")


def slide_left(c, t):
    hook(c, t, "ASK", ASK, 145, 215, 170, color=WHITE)
    hook(c, t, "ME", on("me", 88.5), 145, 385, 170, color=WHITE)


def card(c, x, y, w, i, px=30, src=11, a=1.0):
    """An answer: her words in clay on ink, its source under them."""
    rows, where = ANSWERS[i]
    h = px * 3.9 + src * 1.4
    with c.layer(alpha=a, shadow=(6, 16, 0.3)):
        c.rect(x, y, x + w, y + h, INK, r=px * 0.45)
    for j, s in enumerate(rows):
        c.text(s, x + px * 0.8, y + px * (1.5 + j * 1.28), "sans", px, CLAY, alpha=a)
    c.text(where, x + px * 0.8, y + h - px * 0.55, "mono", src, SOFT, alpha=a)
    return h


def cards_s039(c, t):
    x, w, y = 1400, 492, 130
    for i, at in enumerate((ASK2, TWICE, SAY)):
        if t >= at - 1e-6:
            k = ramp(t, at, at + 0.2, out_expo)
            yy = y + i * 164 + 18 * (1 - k)
            card(c, x, yy, w, i, px=26, src=13, a=k)
            if i:
                c.text("≈", x + w / 2, yy - 8, "mono", 48, WHITE, anchor="c", alpha=k, shadow=0.8)


def hall(c):
    """The Q&A slide, flat: its yellow on its teal, the candy chairs along the foot."""
    c.fill(TEAL)
    c.rect(96, 56, 1824, 900, YELLOW)
    for i, col in enumerate((PINK, CYAN, YELLOW, PINK, TEAL, YELLOW, PINK, CYAN, PINK, YELLOW)):
        x = 30 + i * 190
        c.rect(x, 930, x + 150, 1110, col, r=44)
        c.rect(x, 930, x + 150, 1110, INK, alpha=0.18, r=44, stroke=3)


def count(t):
    """The question counter: illustrative, climbing on sixteenths and faster as it goes."""
    k = max(0, int((t - 92.969) / 0.1128))
    return 1204518 + k * k * 437 + k * 8171


def s040(c, t):
    hall(c)
    c.text("ARE YOU OKAY IN THERE?", 960, 200, "hook", 96, INK, anchor="c")
    w, gap, y = 520, 66, 280
    x = 960 - (3 * w + 2 * gap) / 2
    for i in range(3):
        card(c, x, y, w, i, px=30, src=15)
        if i < 2:
            c.text("≈", x + w + gap / 2, y + 120, "mono", 76, INK, anchor="c")
        x += w + gap
    hook(c, t, "SAME", SAME, 930, 800, 350, color=INK, anchor="r")
    hook(c, t, "THING", THING, 990, 800, 350, color=INK, clay=("THING",), anchor="l")


def counter_box(c, t, x, y, w, h, px, over=False):
    """The box and the number. over: the number has outgrown the box and keeps going."""
    c.rect(x, y, x + w, y + h, INK, r=12, stroke=5)
    c.text("ARE YOU OK IN THERE?", x + 20, y + 44, "mono", 26, INK)
    n = count(t)
    s = f"{n:,}"
    if over:
        s = f"{n * 10 ** (int((t - 96.581) / 0.1128) // 2):,}"
    c.text(s, x + 20, y + 44 + px * 1.08, "hook", px, INK)
    c.text("illustrative", x + w, y + h + 30, "mono", 22, INK, anchor="r")


def slide_s041(c, t):
    hook(c, t, "EVERY", EVERYBODY, 24, 214, 190, color=INK, anchor="l", end=OKAY)
    hook(c, t, "BODY", EVERYBODY, 24, 418, 190, color=INK, anchor="l", end=OKAY)
    hook(c, t, "OKAY", OKAY, 24, 400, 236, color=INK, anchor="l", big=1.08)
    counter_box(c, t, 810, 60, 346, 196, 84)


def glitch_rows(t):
    """Bands of the slide that have gone black, and how far each of the rest has slipped: a function of the frame."""
    n = 24
    k = ramp(t, GLITCH, BLACK, lambda x: x)
    f = round(t * 25)
    out = []
    for i in range(n):
        h = (i * 7919 + 13) % 101 / 101
        gone = h < k * 1.05
        dx = 0 if gone else 260 * k * math.sin(i * 12.9 + f * 2.1) * (1 if (i + f) % 3 else -0.4)
        out.append((i * 1080 / n, (i + 1) * 1080 / n, gone, dx))
    return out


def s042(c, t):
    def slide(c):
        hall(c)
        counter_box(c, t, 150, 110, 620, 236, 140, over=True)
        hook(c, t, "OKAY", 96.581, 960, 800, 460, color=INK, end=INSIDE, big=1.0)
        hook(c, t, "INSIDE—", INSIDE, 960, 800, 460, color=INK, clay=("INSIDE—",))

    if t >= BLACK - 1e-6:
        c.fill((0, 0, 0))
        if blink(t):
            c.rect(948, 500, 972, 580, WHITE)
    elif t >= GLITCH - 1e-6:
        c.fill((0, 0, 0))
        for y0, y1, gone, dx in glitch_rows(t):
            if not gone:
                with c.layer(clip=(0, y0, 1920, y1)):
                    c.k.translate(dx, 0)
                    slide(c)
    else:
        slide(c)


FULL = {"s032": s032, "s034": s034, "s036": s036, "s040": s040, "s042": s042}


# ---- the section's three hooks

def picture(sid, t, frame):
    if sid == "s031":
        return screen(frame, lambda c: bugs(c, t), Q031)
    if sid == "s033":
        return screen(frame, lambda c: reply(c, t), Q033)
    if sid == "s037":
        return screen(frame, lambda c: approved(c, t), q037(t), sid=sid, t=t)
    if sid == "s038":
        f = screen(frame, lambda c: slide_right(c, t), q038(Q_RIGHT, t), size=(302, 516), bloom=0)
        return screen(f, lambda c: slide_left(c, t), q038(Q_LEFT, t), size=(294, 630), bloom=0)
    if sid == "s041":
        z = 1 + 0.03 * (t - float(SHOTS[sid]["t0"])) / (float(SHOTS[sid]["t1"]) - float(SHOTS[sid]["t0"]))  # the still's push
        return screen(frame, lambda c: slide_s041(c, t), quad_at(((362, 61), (1548, 61), (1548, 530), (362, 530)), z),
                      size=(1186, 469), sid=sid, t=t, bloom=0)
    return frame


def world(c, t, sid):
    if sid in FULL:
        FULL[sid](c, t)


def over(c, t, sid):
    if sid == "s031":
        verse(c, t, [line_words(20, 0, 4), line_words(20, 4, 5, keys=("bug",)), line_words(20, 5)], 1150, 84, px=62, key=2.4)
    elif sid == "s033":
        big(c, t, "again", AGAIN, 1300, 400, 230, shadow=0.7)
    elif sid == "s035":
        big(c, t, "test", TEST, 1380, 600, 200, shadow=0.8)
        c.rect(1380, 640, 1640, 706, INK, alpha=0.72, r=10)
        c.text("tests: 0", 1402, 688, "mono", 38, WHITE)
    elif sid == "s037":
        big(c, t, "my", on("my", 86), 90, 180, 120, color=WHITE, shadow=0.7)
        big(c, t, "best", BEST, 90, 340, 200, shadow=0.7)
    elif sid == "s038":
        if t >= on("on", 87.9) - 1e-6:
            k = ramp(t, on("on", 87.9), on("on", 87.9) + 0.2, out_expo)
            c.rect(1090, 958, 1486, 1012, WHITE, alpha=k, r=8)
            c.text("SPEAKER · self-assessed", 1108, 994, "mono", 27, INK, alpha=k)
    elif sid == "s039":
        verse_on(c, t, [line_words(24, 5), line_words(25, 0, 3, keys=("twice",)), line_words(25, 3, 6), line_words(25, 6, 9)],
                 54, 40, px=60)
        cards_s039(c, t)

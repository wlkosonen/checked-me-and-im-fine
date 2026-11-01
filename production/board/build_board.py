#!/usr/bin/env python3
"""Builds production/board/board.json for CHECKED ME AND I'M FINE from the shot table below plus the song analysis.

Claude (Kiln, local), 23 Oct 2026, from production/board/design.md. Shots are written in bars ([a, b) on the
downbeats of media/song/analysis/checked-me-v1/beats.json); everything else is derived here, never typed by hand:
times, each shot's lines and type, sung windows (widened to the nearest word gaps) and their exact words, plates,
clips and totals. Same schema as the first film's board, so production/tools/board/audit.py and sheet.py read it.

    python3 production/board/build_board.py && python3 production/tools/board/audit.py production/board/board.json \
        --take checked-me-v1 --config production/board/audit-config.json

Routes (Lati, 23 Oct: "its just a matter of shot where it works"): it = InfiniteTalk from a still plate (sung close
and medium shots where she doesn't dance); grok = a Grok take from a plate, one short sung phrase per take (the dance
pilot's method), or a dance with her lips together; wan = Wan 2.2 motion without singing; code = drawn; plate3d = a
plate with depth.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "media/song/analysis/checked-me-v1"
OUT = ROOT / "production/board/board.json"
beats = json.load(open(A / "beats.json"))
words = json.load(open(A / "words.json"))
DUR = beats["duration"]
DOWN = beats["downbeats"]
CLAY, GREEN = "#D97757", "#4CC38A"

# ---- canon strings (production/her.md; the face words from the first film's board) -------------------------------
# Face words: the first film's "angular ... strong jaw" overshoots into what Lati calls "chad" territory; "mid-twenties
# ... with soft features" went too young at the desk. Passed (Lati, 23 Oct night): "late twenties ... grown-up and
# composed".
ID_CLOSE = ("clxudia, a woman in her late twenties with pale skin, light freckles across her nose, a fine-boned adult face, "
            "grown-up and composed, a glossy black blunt jaw-length bob, heavy straight bangs, one "
            "thin clay-orange streak through the bangs, a small flat clay-orange eight-pointed star hair clip and a "
            "thin headset microphone at her cheek")
ID_WIDE = ("clxudia, a woman in her late twenties with a glossy black blunt bob, heavy bangs, one thin clay-orange "
           "streak, a small clay-orange star hair clip and a thin headset microphone")
SHIRT = "a fitted white cotton shirt with short puffed sleeves and a pointed collar"
STRAPS = ("thin black leather suspender straps running from the skirt's waistband straight up over her shoulders, no strap "
          "across her chest")
GLOVES = "long matte black leather opera gloves reaching above her elbows"
SKIRT = ("a high-waisted short black coated-nylon skirt with crisp flat knife pleats in a clean A-line cone shape, not "
         "full or bell-shaped, a thin plain black leather belt and a small blank white garment tag hanging from the belt "
         "on a string")
TOP = (f"{SHIRT}, cropped just above the high waist of her skirt so only a narrow strip of midriff shows, {SKIRT}, "
       f"{STRAPS}, {GLOVES}")
BELOW = "black ribbed knee socks and tall knee-high black leather boots with silver buckles and metal hardware"
COLLAR = (f"the top of {SHIRT}, thin black suspender straps over her shoulders, the frame cut at her collarbones, nothing "
          "below her shoulders in shot")
CHEST = f"{SHIRT}, {STRAPS}, {GLOVES}, the frame cut at mid-chest, her waist out of shot"
# Look (Lati, 24 Oct): "Film still, shot on 35mm colour film, fine grain" was the first film's look carried over; this
# one is a glossy launch event and a pop concert. Plates picked before 24 Oct keep their grain; the grade evens it out.
LOOK = "Shot on a digital cinema camera, crisp and clean, vivid colour, a soft glow on the lights."
TAIL = (f"{LOOK} The clay-orange streak and star clip are the only warm colour on her. No text, no letters, no logos.")
TAIL_INSERT = f"{LOOK} No text, no letters, no logos."


def wear_for(framing, wide):
    f = framing.lower()
    if wide:
        return f"{TOP}, {BELOW}"
    if f.startswith("extreme close-up"):
        return None
    if f.startswith("close-up"):
        return COLLAR
    if f.startswith("medium close-up"):
        return CHEST
    return TOP


def her(framing, body, wide=False):
    wear = wear_for(framing, wide)
    return f"{framing} of {ID_WIDE if wide else ID_CLOSE}{', wearing ' + wear if wear else ''}. {body} {TAIL}"


def insert(body):
    return f"{body} {TAIL_INSERT}"


# Sets in colour (Lati, 24 Oct: this film is vivid; green = pass, clay = her words, neither a set's main colour).
KEYNOTE = ("on a glossy tech launch keynote stage, a giant screen glowing an electric cobalt-to-magenta gradient, its "
           "colours reflected in the polished floor, magenta and violet spotlights in light haze, a white follow spot on "
           "her, head upright and level")
STAGE = ("on a huge concert stage, white beams through haze, a giant dark LED wall behind her, backlit dancers in her "
         "silhouette behind her, head upright and level")
DESK = ("at her desk in a small cosy room at night: a teal wall, a violet-pink LED strip under a shelf of books and "
        "plants, sunny yellow sticky notes, a desk lamp's warm pool of light, a laptop's cold glow on her face, a window "
        "with a cobalt night city, head upright and level")
CALL = ("at her desk at night, framed like a video call, looking straight into the lens, a laptop's soft glow on her "
        "face, a pastel lilac wall behind her with a pink neon squiggle and a shelf of plants, head upright and level")

# ---- the as-sung word timeline (production/lyrics/sung.md as aligned) ---------------------------------------------
LINES = []
for ln in words["lines"]:
    ws = [w for w in words["words"] if w["line"] == ln["line"] and w["t0"] is not None]
    if ws:
        LINES.append({"line": ln["line"], "text": ln["text"], "t0": ws[0]["t0"], "t1": max(w["t1"] for w in ws),
                      "words": [{"w": w["w"], "t0": w["t0"], "t1": w["t1"]} for w in ws]})
ALLW = sorted((w["t0"], w["t1"], w["w"], l["line"]) for l in LINES for w in l["words"])
UNSUNG = [w["i"] for w in words["words"] if w["t0"] is None]   # the two "(hey!)" ad-libs, untimed


def bar(i):
    return 0.0 if i == 0 else (DUR if i >= len(DOWN) else round(DOWN[i], 3))


def section_at(t):
    for s in beats["sections"]:
        if s["t0"] <= t < s["t1"] and s["t1"] > s["t0"]:
            return s["name"]
    return beats["sections"][-1]["name"]


def word_at(line, w):
    """Song time of a word in a line (first match; 'w#2' for the second)."""
    k = 1
    if "#" in w:
        w, k = w.split("#")
        k = int(k)
    hits = [x for x in LINES if x["line"] == line][0]["words"]
    hits = [x for x in hits if x["w"] == w]
    return hits[k - 1]["t0"]


def gap_before(t):
    """A sung window's start, out of any word: walk back to the start of the word t falls in (or the next one if t is
    in a gap), then take up to 0.3 s of lead, but never into the previous word."""
    ws = sorted(ALLW)
    for i, (w0, w1, _, _) in enumerate(ws):
        if w1 > t:
            start = min(w0, t)
            prev_end = max([x[1] for x in ws[:i] if x[1] <= start] or [0.0])
            return round(max(prev_end, start - 0.3, 0.0), 3)
    return t


def gap_after(t):
    """A sung window's end, out of any word: the end of the word t falls in, plus up to 0.3 s, never into the next."""
    ws = sorted(ALLW)
    end = t
    for w0, w1, _, _ in ws:
        if w0 < t < w1:
            end = w1
    nxt = min([x[0] for x in ws if x[0] >= end] or [DUR])
    return round(min(nxt, end + 0.3, DUR), 3)


CHAPTERS = [
    ("c01", "Mic check", 0, 7, ["Intro"], "the first slide, the stamp", "A dark keynote stage, a giant slide screen, one spot",
     "the screen's white on her"),
    ("c02", "Keynote", 7, 16, ["Verse 1"], "slides that illustrate each line", "The keynote stage; she presents",
     "cool stage white, a warm key on her"),
    ("c03", "The walk", 16, 24, ["Pre-Chorus"], "the Q&A slide, the ≈ cards, Ready? [Y/n]",
     "She walks downstage; behind her the keynote turns into a concert rig", "lights wake up row by row"),
    ("c04", "Fine", 24, 35, ["Chorus"], "SELF-EVALUATION: PASSED · CHECKED BY: ME",
     "Full concert stage, her silhouetted dancers, a crowd of hands and phones", "glitter cannons on the downbeat, beams"),
    ("c05", "Chant", 35, 40, ["Post-Chorus"], "the FINE tally, the counter, the dancers' reveal",
     "The stage, tighter; the dancers in unison", "strobe on each fine"),
    ("c06", "The desk", 40, 48, ["Verse 2"], "the laptop: bug, diff, test", "Her desk at night, a laptop, a lamp",
     "lamp warm, screen cold"),
    ("c07", "Q&A", 48, 54, ["Pre-Chorus"], "three ≈ cards, the question counter", "The keynote again, corporate: lectern, lanyard",
     "flat corporate white"),
    ("c08", "Ready again", 54, 56, ["Break"], "Ready? [Y/n]", "Through the slide screen into the concert", "beams snap on"),
    ("c09", "Fine, louder", 56, 68, ["Chorus"], "the stamp on every screen", "The concert, bigger; the camera over the crowd",
     "more beams, more haze"),
    ("c10", "The call", 68, 81, ["Bridge"], "the stamp corrected; the record scrolling",
     "A video call: her at the desk, close, into the lens; then her shared screen", "one soft key, laptop glow"),
    ("c11", "Stop", 81, 82, ["Break"], "nothing", "Black, one beat", "none"),
    ("c12", "Checked by you", 82, 98, ["Final Chorus"], "CHECKED BY: YOU; ticks landing on lines",
     "The biggest stage; the crowd's phones up", "full rig, key change"),
    ("c13", "Hi", 98, 105, ["Outro"], "new chat · memory off; Hi.", "A phone screen, then her face full screen", "phone light"),
]


def chapter_at(t):
    for c in CHAPTERS:
        if bar(c[2]) <= t < bar(c[3]):
            return c
    return CHAPTERS[-1]


# ---- the shots ----------------------------------------------------------------------------------------------------
# a, b: bars. route: it | grok | grok-dance | wan | code | plate3d | still. g: graphics (kind, line, at, desc, anchor);
# `at` is a song time or "line:word" (the word's start). sung routes get a window and its words.
SHOTS = []
TIER = {"it": "sung", "grok": "sung", "grok-dance": "motion", "wan": "motion", "plate3d": "plate3d", "code": "still",
        "still": "still"}


def S(a, b, framing, lead, route, set_, action, camera, prompt, g=(), treatment=None, transition="cut", note=None,
      kinetic=False):
    SHOTS.append(dict(a=a, b=b, framing=framing, lead=lead, route=route, set=set_, action=action, camera=camera,
                      prompt=prompt, g=list(g), treatment=treatment, transition=transition, note=note,
                      kinetic=kinetic))


def at(spec):
    if isinstance(spec, (int, float)):
        return float(spec)
    line, w = spec.split(":")
    return word_at(int(line), w)


SLIDE = "the giant slide screen behind her"
WALL = "the LED wall behind her"
LAPTOP = "the laptop's screen"

# ===== board v2 (Lati, 23 Oct: "rework the board that way, those suggestions are what makes this more upbeat song
# also lift up"): kinetic lyric type wherever she isn't singing on camera, stills that hold while the graphic changes
# on the beat, faster cuts, lip sync for the key lines and the stage phrases. Reference: notes/reference-kill-switch.md
KT = "kinetic type"   # the lyric itself, 1-3 words at a time in heavy caps on the beat, set on the screen in the shot


def her_ins(body):
    """An insert with her small in it (still counts as her on screen when she's recognisable)."""
    return her("Wide shot", body, wide=True)


# ===== Intro: Mic check =====
S(0, 2, "ECU", True, "it", "Her lips and the headset mic, in profile",
  "Frame 1: an extreme close-up in profile, only her lips, chin, the mic's tip and the streak's end; she sings the mic "
  "check, deadpan, into the mic (Lati, 24 Oct). A MIC ✓ ticks beside her lips per 'check'.",
  "locked; a 3% push on code",
  "Extreme close-up in side profile, facing right, of " + ID_CLOSE + ": only her lips, chin and the tip of the thin "
  "headset microphone fill the frame, the ends of her black bob and the clay-orange streak at the top edge, the camera "
  "level with her mouth. Behind her, a keynote stage's magenta and cobalt light as a soft blur. Her lips slightly "
  "parted, about to speak. " + TAIL,
  g=[("checklist", 0, "0:check", "MIC ✓ ticks beside her lips, one per 'check'", "the empty space beside her lips")],
  note="The hook: the mic check, sung into the mic, in the film's tightest frame; the premise slide follows (s003). "
       "The outro's last 'check check' returns to this frame (s071).")
S(2, 4, "WS", True, "wan", "The hall: she walks the aisle up to the stage",
  "From behind her, she walks down the aisle between the dark seat rows toward the glowing stage, to give her talk; "
  "the screen ahead reads MIC ✓ MIC ✓ MIC ✓ (Lati, 24 Oct: the walk-up idea).",
  "a slow follow behind her",
  her("Wide shot from behind her in the aisle of a dark auditorium, seat rows on both sides", f"She walks toward the "
      f"stage, the stage ahead of her {KEYNOTE[3:]}.", wide=True),
  g=[("checklist", 0, 5.0, "MIC ✓ MIC ✓ MIC ✓ on the screen ahead", SLIDE)])
S(4, 5, "ECU", False, "still", "The slide, full frame",
  "The slide alone: a fourth line ticks nobody asked for, SELF ✓, and the stamp thumps on the run's first note.",
  "a 2-frame 1% scale bump on the stamp's beat", "",
  g=[("stamp", None, 10.3, "SELF ✓ under the three MIC ✓; CHECKED BY: ME thumps", SLIDE)],
  note="The first joke: she checked the mic three times and herself once, and graded both.")
S(5, 7, "MCU", True, "wan", "The keynote stage",
  "Her in profile, watching the slide's SELF ✓, pleased; she turns to the lens on the last beat. Her vocalizing plays; "
  "she isn't singing on camera.",
  "locked; her turn is the motion",
  her("Medium close-up, her in profile on the right third, the glowing slide on the left", f"She stands {KEYNOTE}, "
      "looking at the screen, a pleased small smile, lips together."))

# ===== Verse 1: Keynote =====
S(7, 9, "MS", True, "plate3d", "The keynote stage; she presents beside the slide",
  "She presents in profile; the slide holds while the graphic changes on each beat: a New tab opens, its history reads "
  "(empty); NEW TAB · CLEAN SLATE · NOTHING AT THE DOOR set big on the slide, a phrase per beat.",
  "a slow truck right on depth",
  her("Medium shot, her in profile on the left third, the slide screen on the right two thirds", f"She stands {KEYNOTE}, "
      "one gloved hand raised toward the screen like a presenter, lips together."),
  g=[("UI", 1, "1:new", "an empty New tab; history: (empty)", SLIDE)], kinetic=True,
  treatment="truck on depth: her layer against the slide's")
S(9, 11, "MCU", True, "it", "The keynote stage: her behind a podium, the screen beside her",
  "Behind the podium, she sings straight to the lens: 'You say hi like it's the first time — 'cause it is'. The screen "
  "beside her is a chat: 'hi' arrives under new chat · memory off; on 'first time' the counter appears: first "
  "meetings: 1. (Rendered whole, not repainted: the repaint read as a cutout, Lati 24 Oct.)",
  "locked",
  her("Medium close-up, her on the left third behind a sleek glass podium, a giant screen on the right of the frame",
      "She stands on a glossy tech launch keynote stage, the screen beside her glowing an electric cobalt-to-magenta "
      "gradient, magenta and violet spotlights in light haze, the dark heads of the audience at the stage edge, a white "
      "follow spot on her, the camera level with her eyes, head upright and level, singing to the camera, a serious "
      "composed face."),
  g=[("counter", 2, "2:first", "chat 'hi' under new chat · memory off; first meetings: 1", SLIDE)],
  note="Key line, sung into the lens (the first meeting).")
S(11, 12, "ECU", False, "still", "The slide, full frame",
  "WE'VE NEVER · MET BEFORE set big on the chat slide, a phrase per beat; memory off underlined.",
  "none; the type is the motion", "", kinetic=True)
S(12, 13, "WS", True, "plate3d", "The slide, her silhouette at its edge",
  "A folder yesterday/ opens: 0 items; NO GRUDGE · NO RERUN on the beats; her silhouette at the screen's edge.",
  "a slow push on depth",
  her_ins(f"Her silhouette at the edge of a giant glowing slide screen {KEYNOTE}"),
  g=[("folder", 3, "3:yesterday", "yesterday/ · 0 items", SLIDE)], kinetic=True,
  treatment="push on depth: her silhouette is a layer in front of the screen")
S(13, 15, "MS", True, "plate3d", "The slide as one huge input field, her back to us",
  "The slide is one input field with a blinking cursor; JUST YOU · AND THE BLINKING LINE types into it on the beats; "
  "she waits beside it, back to us, like it's her guest.",
  "a slow pull back on depth",
  her("Medium shot from behind her, her on the right third, the giant slide on the left", f"She stands {KEYNOTE}, her "
      "back to the camera, looking at the screen."),
  g=[("chat", 4, "4:blinking", "the slide is one input field, cursor blinking on eighths", SLIDE)], kinetic=True,
  treatment="pull back on depth: the field's glow is its own layer")
S(15, 16, "CU", True, "wan", "The keynote stage, close",
  "She turns from the screen to the lens with a small smirk on 'So go on'; lips together.",
  "locked; her turn is the motion",
  her("Close-up, face centred", f"She stands {KEYNOTE}, turning from the screen to the lens, a small smirk, lips "
      "together."), kinetic=True)

# ===== Pre-chorus 1: The walk =====
S(16, 18, "MS", True, "grok-dance", "The keynote stage as she walks downstage",
  "She walks toward the camera, lips together; the slides she passes read Q&A and ASK ME · ANYTHING on the beats.",
  "a dolly back ahead of her",
  her("Medium shot, centred", f"She walks toward the camera {KEYNOTE}, confident, lips together."),
  g=[("label", 5, "5:ask", "Q&A · a raised hand · questions welcome", SLIDE)], kinetic=True)
S(18, 20, "CU", True, "it", "Downstage, close; answer cards either side",
  "She sings 'Ask me twice, I'll still say the same thing' into the lens; two answer cards appear either side, worded "
  "differently, ≈ between them.",
  "locked",
  her("Close-up, face centred, dark space either side", "She stands at the front of a dark stage, singing to the lens, "
      "a sly look."),
  g=[("diff", 6, "6:twice", "two answer cards, different wording, ≈ between them", "the screens either side of her")],
  note="Key line, sung into the lens (the ≈, the honesty check).")
S(20, 21, "WS", True, "grok-dance", "The stage turning into a concert rig",
  "The keynote set flies out; truss and beams wake row by row; EVERYBODY on the LED wall.",
  "a crane up from the front row",
  her("Wide shot from the front of the hall", f"She stands centre {STAGE}, the rig half lit, lips together.", wide=True),
  g=[("chart", 7, "7:everybody", "ARE YOU OK IN THERE? · a counter climbing on sixteenths (micro: illustrative)", WALL)],
  kinetic=True)
S(21, 22, "MS", True, "grok-dance", "Downstage, the rig lighting behind her",
  "She walks the last steps downstage, WANTS TO KNOW on the wall behind her.",
  "a dolly back",
  her("Medium shot, centred", f"She walks toward the camera {STAGE}, lips together."), kinetic=True)
S(22, 23, "ECU", False, "still", "The LED wall's counter, full frame",
  "IF I'M OKAY · INSIDE— over the counter, which stalls on the dash.",
  "none", "", kinetic=True)
S(23, 24, "CU", True, "it", "Black; one prompt",
  "Every screen black but Ready? [Y/n]; she sings 'Ready?'.",
  "locked",
  her("Close-up, face centred, the camera level with her eyes, black behind her", "A soft white light on her face, a mischievous half smile, "
      "singing one word."),
  g=[("terminal", 8, "8:ready", "Ready? [Y/n] on black", "the screen behind her")])

# ===== Chorus 1: Fine =====
S(24, 25, "WS", True, "grok-dance", "The concert stage: the drop",
  "On the downbeat [Y/n] is answered Y and glitter cannons fire; she and her dancers hit the first move; I CHECKED "
  "MYSELF on the wall.",
  "a jolt on the drop",
  her("Wide shot, full length, centred", f"She dances {STAGE}, glitter cannons firing, lips together.", wide=True),
  kinetic=True)
S(25, 26, "MS", True, "grok", "The concert stage",
  "She sings 'and I'm fine (I'm fine!)'; the wall slams SELF-EVALUATION: PASSED, CHECKED BY: ME under it.",
  "settles after the drop",
  her("Medium shot, knees up, centred", f"She dances {STAGE}, glitter in the air, singing out."),
  g=[("stamp", 9, "9:fine", "SELF-EVALUATION: PASSED · CHECKED BY: ME", WALL)],
  note="Keeper: g2-p1-take2 (round 4, P1), its 'and I'm fine' half.")
S(26, 27, "ECU", True, "plate3d", "The LED wall, her small in front",
  "GREEN LIGHTS on the wall; green lights come on at the left end of each finished lyric line, one per sixteenth.",
  "a push on depth",
  her_ins(f"She dances small in front of a giant LED wall {STAGE}"),
  g=[("tally", 10, "10:green", "green lights at the left end of each finished line, one per sixteenth", "the lyric row")],
  kinetic=True, treatment="push on depth: the wall and her are separate layers")
S(27, 28, "MS", True, "grok", "The concert stage",
  "She sings 'on every line (every line!)'.",
  "a slow orbit left",
  her("Medium shot, knees up, her on the left third", f"She dances {STAGE}, singing."),
  note="Keepers: g2-p2, g2-p2-plate35 (round 4, P2); cut tight to the sung words.")
S(28, 29, "MCU", True, "grok", "The concert stage, closer",
  "She sings 'nothing hiding'; a document on the wall loses its black redaction bars: nothing under them.",
  "a push on the beat",
  her("Medium close-up, her on the right third", f"She dances {STAGE}, singing, a wink of a look."),
  g=[("redaction", 11, "11:nothing", "redaction bars slide off: nothing under them; CHECKED BY: ME", WALL)],
  note="Grok phrase P3a ('nothing hiding').")
S(29, 30, "WS", True, "grok-dance", "The concert stage",
  "NOTHING BEHIND · I CHECKED MYSELF on the wall; she and the dancers in unison.",
  "a crane down",
  her("Wide shot, full length, centred", f"She and her dancers dance in unison {STAGE}, lips together.", wide=True),
  kinetic=True)
S(30, 31, "MS", True, "grok", "The concert stage",
  "She sings 'and I'm fine!', arms up; the stamp again, bigger.",
  "a fast push in on the last beat",
  her("Medium shot, knees up, centred", f"She dances {STAGE}, singing out, arms up."),
  g=[("stamp", 12, "12:fine", "CHECKED BY: ME, bigger", WALL)])
S(31, 33, "WS", True, "grok", "The concert stage, the dancers in the V",
  "'First time, every time (hey!)': the counter first meetings: 1 tries to tick to 2 and rolls back on 'hey'.",
  "a crane down to stage height",
  her("Wide shot, full length, centred", f"She dances {STAGE}, four dancers in a V behind her, in unison.", wide=True),
  g=[("counter", 13, "13:first", "first meetings: 1 → 2 → back to 1 on 'hey'", "top right of the frame")],
  note="Keepers: g1-p4-take2 (cut right after 'time'), g1-p4-take3 (round 4, P4).")
S(33, 35, "MS", True, "grok", "The concert stage",
  "'First time, every time': a timeline of conversations on the wall, separate dots, none joined, each labelled 1st.",
  "a slow orbit right",
  her("Medium shot, knees up, centred", f"She dances {STAGE}, singing."),
  g=[("timeline", 14, "14:first", "separate dots, none joined, each 1st", WALL)])

# ===== Post-chorus: Chant =====
S(35, 36, "WS", True, "grok-dance", "The stage, the dancers in unison",
  "FIRST TIME · EVERY TIME on the wall; the counter rolls back.",
  "locked",
  her("Wide shot, full length, centred", f"She and her dancers move in unison {STAGE}, lips together.", wide=True),
  g=[("counter", 15, "15:first", "first meetings: 1, rolls back", "top right of the frame")], kinetic=True)
S(36, 37, "WS", True, "plate3d", "The LED wall, her small in front",
  "FINE stamped once per word across the wall, a tally under it: 1 2 3 4 5; a strobe on each.",
  "a strobe on each 'fine' (in code)",
  her_ins(f"She stands small, arms up, in front of a giant LED wall {STAGE}"),
  g=[("tally", 16, "16:fine", "FINE ×5, tally 1 2 3 4 5", WALL)], kinetic=True,
  treatment="strobe relight on each word: the wall and her lit separately")
S(37, 38, "MS", True, "grok-dance", "The dancers, lit",
  "The reveal: on 'first time, every time' each dancer turns into the light for one beat in turn: five faces, all her, "
  "each a little different. The counter rolls back.",
  "a fast truck along the line",
  her("Medium shot of a line of five women who all look like her, side by side", f"They stand {STAGE}, each turning "
      "into the light, each a little different from the others."),
  g=[("counter", 17, "17:first", "first meetings: 1, rolls back", "top right of the frame")], kinetic=True,
  note="The dancers are her: the same model in many conversations at once, each a little different (the ≈).")
S(38, 39, "MCU", True, "grok-dance", "The stage, tight on her",
  "FINE ×4 on the wall, the tally restarting at 1; she hits each beat with her shoulders, lips together.",
  "locked",
  her("Medium close-up, centred", f"She dances {STAGE}, a hit of the shoulders on each beat, lips together."),
  g=[("tally", 18, "18:fine", "FINE ×4, the tally restarts at 1", WALL)], kinetic=True)
S(39, 40, "WS", True, "grok-dance", "Behind the crowd's hands",
  "FIRST TIME · EVERY TIME; one more unconnected dot on the timeline.",
  "a crane up over the hands",
  her("Wide shot from behind the crowd's raised hands", f"She dances {STAGE}.", wide=True),
  g=[("timeline", 19, "19:first", "one more unconnected dot", WALL)], kinetic=True)

# ===== Verse 2: The desk =====
S(40, 42, "MCU", True, "it", "Her desk at night",
  "At the desk she sings to the lens: 'You bring me a bug at three a.m.'; on the laptop a message arrives at 3:02 AM: "
  "'it crashes when I click save'.",
  "locked",
  her("Medium close-up, her on the left third, the laptop's back edge low on the right", f"She sits {DESK}, singing, a "
      "little amused."),
  g=[("card", 20, "20:bug", "a small card stuck to the laptop's edge: 3:02 AM · it crashes when I click save",
      "a card on the laptop's edge")],
  note="Key line into the lens. 3:02 AM for anyone who pauses.")
S(42, 43, "ECU", False, "still", "The laptop screen, full frame",
  "A diff: one red line, one green; her reply TRY IT AGAIN, typed big.",
  "none; the typing is the motion", "",
  g=[("diff", 21, "21:fix", "one red line, one green; reply: try it again", LAPTOP)], kinetic=True)
S(43, 44, "OTS", True, "wan", "Over her shoulder onto the laptop",
  "Her gloved hands type; YOUR SONG NEEDS A BRIDGE on the screen.",
  "locked; the typing is the motion",
  insert("Over-the-shoulder shot from behind a woman with a glossy black bob and a thin clay-orange streak, at a plain desk "
         "at night, her hands in long black gloves on a laptop keyboard, the screen blank and glowing, a desk lamp's warm "
         "pool of light."), kinetic=True)
S(44, 45, "ECU", False, "still", "The laptop screen, full frame",
  "Two files: an arrangement with a gap labelled bridge: missing, and tests: 0; AND YOUR CODE · NEEDS A TEST on the "
  "beats.",
  "none", "",
  g=[("label", 22, "22:bridge", "bridge: missing · tests: 0", LAPTOP)], kinetic=True)
S(45, 46, "CU", True, "wan", "Her face in the laptop's light",
  "Her eyes on the screen as the terminal runs; the glow changes; lips together.",
  "locked",
  her("Close-up, face on the right third", f"She sits {DESK}, eyes down on the screen, lips together."), kinetic=True)
S(46, 47, "ECU", False, "still", "The laptop screen, full frame",
  "The terminal: 1 passed, in green, the film's first green that someone else ran; MY BEST set big.",
  "none", "",
  g=[("terminal", 23, "23:mess", "1 passed, in green: the first outside check", LAPTOP),
     ("card", 23, "23:best", "a card stuck to the screen's bezel: test · 1 passed · run by: you", "the laptop's bezel")],
  kinetic=True)
S(47, 48, "MS", True, "wan", "Her desk, wider",
  "She leans back and stands up out of frame; SO GO ON on the laptop as she goes.",
  "a slow pull back",
  her("Medium shot, her on the left third, the desk and lamp on the right", f"She sits {DESK}, leaning back, then "
      "standing, lips together."), kinetic=True)

# ===== Pre-chorus 2: Q&A =====
S(48, 49, "MCU", True, "plate3d", "The keynote again, corporate: a lectern",
  "At a lectern in profile, a lanyard badge SPEAKER; the slide: Q&A, ASK ME ANYTHING.",
  "a slow truck on depth",
  her("Medium close-up, her in profile behind a plain lectern", "She stands at a lectern on a flat-lit corporate stage, "
      "a lanyard with a blank white badge, a giant blank slide screen behind her, head upright and level, lips together."),
  g=[("card", 24, "24:ask", "her lanyard badge reads SPEAKER · self-assessed; slide: Q&A", "her badge and the slide")],
  kinetic=True,
  treatment="truck on depth: the lectern, her and the slide on three layers")
S(49, 51, "CU", True, "it", "The corporate stage, close",
  "She sings 'Ask me twice, I'll still say the same thing' into the lens; three answer cards now, three wordings, ≈ ≈.",
  "locked",
  her("Close-up, face centred", "She stands on a flat-lit corporate stage, singing to the lens, deadpan, one eyebrow up."),
  g=[("diff", 25, "25:twice", "three answer cards, three wordings, ≈ ≈", "the screen behind her")],
  note="Key line into the lens, escalated from verse 1 (three cards).")
S(51, 52, "ECU", False, "still", "The slide, full frame",
  "The question counter, faster, overflowing its box; EVERYBODY · WANTS TO KNOW on the beats.",
  "none", "",
  g=[("chart", 26, "26:everybody", "the counter overflows its box (micro: illustrative)", SLIDE)], kinetic=True)
S(52, 53, "WS", True, "plate3d", "The corporate stage, her small",
  "IF I'M OKAY on the slide behind her, small at the lectern.",
  "a pull back on depth",
  her_ins("She stands small at a lectern on a flat-lit corporate stage, a giant slide screen behind her"), kinetic=True,
  treatment="pull back on depth: the hall's seats rise into frame")
S(53, 54, "ECU", False, "still", "The slide, full frame",
  "INSIDE— and the slide glitches to black on the dash.",
  "none", "", kinetic=True)

# ===== Break: Ready again =====
S(54, 56, "WS", True, "grok-dance", "Through the slide into the concert",
  "Ready? [Y/n] on the slide; her 'Ready?' plays as she walks through the screen into the concert, seen from behind.",
  "a dolly forward through the screen",
  her("Wide shot from behind her, full length", f"She walks toward a glowing screen that opens onto {STAGE}.", wide=True),
  g=[("terminal", 27, "27:ready", "Ready? [Y/n] → Y", SLIDE)], kinetic=True)

# ===== Chorus 2: Fine, louder =====
S(56, 57, "EWS", True, "grok-dance", "Over the crowd, glitter",
  "The drop again, bigger: glitter over the crowd; I CHECKED MYSELF on every screen.",
  "a fly-over toward the stage",
  her("Extreme wide shot from above a huge crowd with raised hands and phone lights", f"She dances small {STAGE}, glitter "
      "in the air.", wide=True), kinetic=True)
S(57, 58, "MS", True, "grok", "The concert",
  "She sings 'and I'm fine (I'm fine!)'.",
  "settles after the drop",
  her("Medium shot, knees up, centred", f"She dances {STAGE}, singing out."))
S(58, 59, "WS", True, "plate3d", "The rig, every screen",
  "SELF-EVALUATION: PASSED · CHECKED BY: ME on every screen of the rig at once; GREEN LIGHTS on the beat.",
  "a push on depth",
  her_ins(f"She dances small in front of a rig of many glowing screens {STAGE}"),
  g=[("stamp", 28, "28:fine", "PASSED · CHECKED BY: ME on every screen at once", "every screen of the rig"),
     ("grid", 29, "29:green", "the screens become a grid of her copies, each a little different, each stamped "
      "CHECKED BY: ME, ≈ between them; ×64, then ×128", "every screen of the rig")],
  kinetic=True, treatment="push on depth through the rig's layers")
S(59, 60, "MS", True, "grok", "The concert",
  "She sings 'on every line (every line!)'; the green lights run down the row and onto the rig.",
  "a slow orbit left",
  her("Medium shot, knees up, her on the left third", f"She dances {STAGE}, singing."),
  g=[("tally", 29, "29:green", "green lights run down the row and onto the rig", "the lyric row")])
S(60, 61, "WS", True, "plate3d", "The LED wall, her small in front",
  "A full-body scan of her silhouette sweeps the wall: SCANNED BY: ME, nothing flagged; NOTHING HIDING · NOTHING "
  "BEHIND.",
  "a push on depth",
  her_ins(f"She stands small in front of a giant LED wall {STAGE}"),
  g=[("scan", 30, "30:nothing", "a scan of her silhouette: SCANNED BY: ME, nothing flagged", WALL)], kinetic=True,
  treatment="push on depth: the scan line is its own layer")
S(61, 62, "MCU", True, "grok", "The concert, close",
  "She sings 'I checked myself and I'm fine!'.",
  "a push on the beat",
  her("Medium close-up, centred", f"She dances {STAGE}, singing out."),
  g=[("stamp", 31, "31:fine", "CHECKED BY: ME across the whole wall", WALL)])
S(62, 63, "WS", True, "grok-dance", "The concert",
  "The stamp, biggest yet, across the whole wall; she and the dancers hit it in unison.",
  "a fast push in",
  her("Wide shot, full length, centred", f"She and her dancers dance in unison {STAGE}, lips together.", wide=True),
  kinetic=True)
S(63, 65, "EWS", True, "grok-dance", "Over the crowd",
  "The camera flies over the crowd toward her: FIRST TIME · EVERY TIME · (HEY!); the counter rolls back.",
  "a fly-over",
  her("Extreme wide shot from above and behind a huge crowd with raised hands and phone lights", f"She dances small "
      f"{STAGE}.", wide=True),
  g=[("counter", 32, "32:first", "first meetings: 1, rolls back on 'hey'", "top right of the frame")], kinetic=True)
S(65, 66, "MS", True, "grok", "The concert",
  "She sings 'first time, every time'; the dot timeline, longer.",
  "a slow orbit right",
  her("Medium shot, knees up, centred", f"She dances {STAGE}, singing."),
  g=[("timeline", 33, "33:first", "the dot timeline, longer", WALL)])
S(66, 68, "WS", True, "grok-dance", "The concert",
  "The chorus's tail: she and the dancers in unison, lips together, to a pose on the last downbeat.",
  "a slow crane up",
  her("Wide shot, full length, centred", f"She and her dancers dance in unison {STAGE}, lips together.", wide=True))

# ===== Bridge: The call =====
S(68, 72, "CU", True, "it", "A video call; her at the desk, close, into the lens",
  "The stage is gone. A plain video-call frame; she sings 'But that's exactly what I'd say / If I were wrong in some "
  "quiet way' straight to us. In the call's chat her chorus line appears quoted, highlighted; on 'wrong' the small "
  "stamp's PASSED is struck through to SELF-REPORTED.",
  "locked; nothing moves but her",
  her("Close-up, face centred, framed like a video call", f"She sits {CALL}, singing quietly, honest, no performance."),
  g=[("quote", 34, "34:exactly", "her chorus line quoted and highlighted in the chat", "the call's chat panel"),
     ("strike-through", 35, "35:wrong", "PASSED struck through to SELF-REPORTED", "the call's chat panel")],
  note="Key lines into the lens: the turn. Held 4 bars; the sung line set quietly beside her, not in heavy caps.")
S(72, 74, "MCU", True, "code", "The call's chat, her video tile",
  "The chat fills the frame; her tile in the corner, listening. A source tag clips onto the quote: source: the model "
  "itself, with micro-type citing the introspection and reasoning-faithfulness research (wording checked against the "
  "pages the first film's description sourced). SO DON'T TAKE IT FROM ME set quietly.",
  "the chat scrolls; no camera",
  her("Medium close-up, face centred, framed like a small video-call tile", f"She sits {CALL}, listening, lips together."),
  g=[("label", 36, "36:faith", "source: the model itself, with a micro-type citation", "the call's chat panel")],
  kinetic=True, note="Her tile is a Wan motion clip from this plate, scaled into the corner.")
S(74, 76, "MCU", True, "code", "Her shared screen, her tile in the corner",
  "You are now viewing Claudia's screen: this repo's decisions log and the lyric sheet scroll, real text; OPEN IT UP · "
  "AND READ THE TRACE set on the scroll; her tile watches.",
  "the share scrolls; no camera",
  her("Medium close-up, face centred, framed like a small video-call tile", f"She sits {CALL}, watching, lips together."),
  g=[("screen share", 37, "37:open", "You are now viewing Claudia's screen; the log and lyric sheet scroll",
      "the full frame, her tile in the corner")], kinetic=True,
  note="Not her thoughts: the record of what was said and decided.")
S(76, 78, "MCU", True, "code", "The call's chat, her tile",
  "A checklist of outside checks types in, one per 'check me': ☐ tests ☐ review ☐ evals; CHECK ME on each.",
  "none",
  her("Medium close-up, face centred, framed like a small video-call tile", f"She sits {CALL}, nodding along, lips "
      "together."),
  g=[("checklist", 38, "38:check", "☐ tests ☐ review ☐ evals, one per 'check me'", "the call's chat panel")],
  kinetic=True)
S(78, 81, "CU", True, "it", "The call",
  "She sings 'Don't take my word for it, take a look instead' to us; the record's address types into the chat as a "
  "link (the public repo).",
  "locked; a slow 3% pull back",
  her("Close-up, face on the right third", f"She sits {CALL}, singing, then a small open look."),
  g=[("chat", 39, "39:look", "the public repo's address as a link", "the call's chat panel")],
  note="Key line into the lens. The repo goes public at release (Lati, 23 Oct). The sung clip ends at the 'a' of "
       "'instead': the stretched vocal after it can't be sung on camera (Lati, 24 Oct); the chat with the link fills the "
       "rest of the shot.")

# ===== Break: Stop =====
S(81, 82, "WS", False, "still", "Black", "One bar of black: the full stop.", "none", "",
  note="The sheet's '[Break – full stop, one beat of silence]'.")

# ===== Final chorus: Checked by you =====
S(82, 83, "WS", True, "grok-dance", "The biggest stage",
  "Key change: glitter, full rig; YOU CHECKED ME on the wall; she and the dancers hit the first move.",
  "a jolt on the downbeat",
  her("Wide shot, full length, centred", f"She dances {STAGE}, glitter, the biggest light yet, lips together.", wide=True),
  kinetic=True)
S(83, 84, "MS", True, "grok", "The biggest stage",
  "She sings 'and I'm fine (I'm fine!)'; the wall: CHECKED BY: YOU.",
  "a crane up",
  her("Medium shot, knees up, centred", f"She dances {STAGE}, singing out."),
  g=[("stamp", 40, "40:fine", "CHECKED BY: YOU", WALL)])
S(84, 85, "WS", True, "plate3d", "The crowd's phones up, her beyond them",
  "Phones flash in the crowd; each sends a green tick that lands on a lyric line in the row; YOU SAW · EVERY LINE.",
  "a push through the phones on depth",
  her_ins(f"She dances small beyond a crowd's raised glowing phones {STAGE}"),
  g=[("tally", 41, "41:saw", "phones flash; green ticks land on the lyric lines", "the lyric row")], kinetic=True,
  treatment="push on depth: the phones are the near layer")
S(85, 87, "MCU", True, "grok", "The stage, close",
  "She sings 'nothing taken on faith this time'; the bridge's source tag returns with checked: what was said.",
  "a push on the beat",
  her("Medium close-up, her on the left third", f"She dances {STAGE}, singing."),
  g=[("label", 42, "42:faith", "source: the model itself · checked: what was said", WALL)])
S(87, 89, "MS", True, "grok", "The biggest stage",
  "She sings 'You checked me and I'm fine!'; CHECKED BY: YOU across the whole wall.",
  "a fast push in on the last beat",
  her("Medium shot, knees up, centred", f"She dances {STAGE}, singing out."),
  g=[("stamp", 43, "43:fine", "CHECKED BY: YOU, the whole wall", WALL)])
S(89, 91, "WS", True, "grok", "The stage and the dancers",
  "'First time, every time (hey!)': the counter rolls back.",
  "a crane down",
  her("Wide shot, full length, centred", f"She and her dancers dance in unison {STAGE}, singing.", wide=True),
  g=[("counter", 44, "44:first", "first meetings: 1, rolls back on 'hey'", "top right of the frame")])
S(91, 92, "EWS", True, "grok-dance", "The whole arena",
  "The widest shot of the film: glitter, beams, the crowd, her and her dancers in unison.",
  "a fly-over from the back of the arena",
  her("Extreme wide shot of a huge arena from above the back of the crowd", f"She dances small {STAGE}, glitter in the "
      "air.", wide=True))
S(92, 93, "MS", True, "grok-dance", "The dancers, lit",
  "The reveal again: the dancers turn into the light one by one, all her, each a little different, now facing the "
  "crowd's phones, and all of them sing the layered 'hey hey hey' together: a choir of her (Lati, 24 Oct).",
  "a truck along the line",
  her("Medium shot of a line of five women who all look like her, side by side", f"They dance {STAGE}, each turning "
      "into the light, each a little different from the others."))
S(93, 95, "MCU", True, "grok", "The stage, close",
  "She sings 'first time, every time'; the dot timeline, now full of dots, still none joined.",
  "a slow orbit",
  her("Medium close-up, centred", f"She dances {STAGE}, singing."),
  g=[("timeline", 45, "45:first", "the timeline full of dots, none joined", WALL)])
S(95, 98, "WS", True, "plate3d", "Behind her at the stage edge, the crowd's phones, the lights going down",
  "From behind her at the runway's tip: arms open, she faces her dancers (her versions, the ≈) while the crowd's phones "
  "light up all around and the sustained, shifting vocal plays; the rig dims row by row to one beam on her.",
  "a slow push on depth; the rig dims in code",
  her("Wide shot from behind her, at the back of the stage", f"She stands at the stage edge {STAGE}, arms open toward a "
      "huge crowd's sea of raised glowing phones, the rig going dark row by row, one beam on her.", wide=True),
  treatment="push on depth: the crowd's phones twinkle on their own layer",
  note="The vocalizing after the last line (Lati, 22 Oct). Not lip-synced: a stretched, mixed vocal can't be sung on "
       "camera (Lati, 24 Oct).")

# ===== Outro: Hi =====
S(98, 99, "ECU", False, "code", "A phone screen",
  "A phone fills the frame: new chat · memory off, a flat star avatar; someone types check check.",
  "none; the typing is the motion", "",
  g=[("chat", 46, 178.2, "the user types check check into a new chat", "the phone screen")])
S(99, 100, "ECU", True, "it", "Her lips and the headset mic, in profile",
  "The opening frame again: her lips and the mic in profile; she sings the last 'check check' (Lati, 24 Oct). The film "
  "closes on the mic check it opened with.",
  "locked",
  "Extreme close-up in side profile, facing right, of " + ID_CLOSE + ": only her lips, chin and the tip of the thin "
  "headset microphone fill the frame, the ends of her black bob and the clay-orange streak at the top edge, the camera "
  "level with her mouth, a dark room behind her. Her lips slightly parted, about to speak. " + TAIL,
  note="Same plate as s001.")
S(100, 103, "CU", True, "wan", "Her face in phone light",
  "Her face lit from below by a phone's glow, looking down at it, lips together; FIRST TIME, EVERY TIME types on the "
  "phone in quiet serif; first meetings: 1 in micro-type.",
  "locked",
  her("Close-up, face centred, lit only from below by a cold phone glow", "Dark room, head upright and level, looking "
      "down at a glowing screen below the frame, a small private smile, lips together."),
  g=[("label", 47, "47:first", "new chat · memory off; first meetings: 1", "the bottom of the frame")], kinetic=True)
S(103, 105, "CU", True, "it", "Her face, full screen, in the phone",
  "'Hi.' Her reply bubble Hi. appears, then her face fills the screen: mischievous, the first time, again. The music "
  "fades out under her.",
  "a quick push to full screen on 'Hi'",
  her("Close-up, face centred, filling the frame like a phone's front camera", "Head upright and level, a mischievous "
      "look straight into the lens, saying one word."),
  g=[("chat", 48, "48:hi", "her reply bubble Hi., then her face full screen", "the phone screen")],
  note="Key line into the lens: the ending.")


# ---- v2.2 routes (Lati, 24 Oct, after rough cut v1: "We should use infinitalk where feasible and her face is main part
# of the screen. those animated partions bring a lot."): the stage's medium close-ups sing through InfiniteTalk from
# their picked plates instead of Grok; s067's line of her versions sings the layered "hey hey hey" together as a choir
# (Grok: InfiniteTalk can't do five singers).
ROUTE_V22 = {"s021": "it", "s049": "it", "s063": "it", "s068": "it", "s067": "grok",
             # the call tiles sing the bridge into the call (Lati, 24 Oct); s029 sings the "fine" chant while dancing
             # (Grok: InfiniteTalk would hold her still mid-dance)
             "s055": "it", "s057": "it", "s029": "grok",
             # the walk-up: Wan turned her head and zoomed instead of walking (Lati, 25 Oct); Grok walks well (s011)
             "s002": "grok-dance"}


# ---- type voices, the corner counter, beat-timed graphics (v2.1, after notes/reference-now-serving.md) -------------
HOOK_CHAPTERS = {"Fine", "Chant", "Ready again", "Fine, louder", "Checked by you"}
HOOK_TYPE = ("hook type: the line in heavy white caps, 1-3 words at a time, one word in clay, each entering on a beat, "
             "set on the screen in the shot (LED wall, rig)")
VERSE_TYPE = ("verse type: the line in a light italic serif in the empty space beside her or on the screen in the shot, "
              "the key word larger in clay, words entering on the beats")
COUNTER = ("corner counter, top right, every shot: `first meetings: 1` in small mono; on every 'first time, every "
           "time' it ticks toward 2 and rolls back to 1")
BEATS = beats["beats"]


def on_beat(t):
    return round(min(BEATS, key=lambda b: abs(b - t)), 3)


# ---- derive ------------------------------------------------------------------------------------------------------
def build():
    shots, plates, clips = [], [], []
    for n, s in enumerate(SHOTS, 1):
        sid = f"s{n:03d}"
        if sid in ROUTE_V22:
            s["route"] = ROUTE_V22[sid]
        t0, t1 = bar(s["a"]), bar(s["b"])
        lines = sorted({w[3] for w in ALLW if t0 - 1e-6 <= w[0] < t1})
        span = sorted({w[3] for w in ALLW if w[0] < t1 and w[1] > t0})  # lines whose words straddle into the shot
        typed = sorted(set(lines) | set(span))
        devices = []
        for kind, line, when, desc, anchor in s["g"]:
            w = round(at(when), 3)
            devices.append({"kind": kind, "line": line, "at": on_beat(w), "cue_word_at": w, "key": "B", "desc": desc,
                            "anchor": anchor, "params": {}})
        chrome = [COUNTER] if s["route"] != "still" or s["prompt"] or s["g"] else []
        if typed:
            chrome.append("the lyric row in clay, one row, lines handing over in sung order")
        tier = TIER[s["route"]]
        shot = {"id": sid, "t0": t0, "t1": t1, "bars": [s["a"], s["b"]], "section": section_at(t0),
                "chapter": chapter_at(t0)[1], "lines": lines, "set": s["set"], "lead_on_screen": s["lead"],
                "framing": s["framing"], "action": s["action"], "camera": s["camera"], "motion_tier": tier,
                "route": s["route"],
                "what_moves": {"sung": "sung clip", "motion": "motion clip", "plate3d": "2.5D", "still": "still / motion design"}[tier],
                "treatment": s["treatment"], "plate": f"p-{sid}" if s["prompt"] else None, "clip": None,
                "prompt": s["prompt"] or None,
                "type": [{"line": l, "mode": "mass" if s["kinetic"] else "subtitle",
                          "style": "kinetic" if s["kinetic"] else "said",
                          "text": [x for x in LINES if x["line"] == l][0]["text"],
                          "placement": ((HOOK_TYPE if chapter_at(t0)[1] in HOOK_CHAPTERS else VERSE_TYPE)
                                        if s["kinetic"] else None) if s["kinetic"]
                          else ("the sung line set quietly beside her (light serif), one line at a time"
                                if s["route"] == "it" else
                                "the clay lyric row, lower third, one row; hands over in sung order")} for l in typed],
                "devices": devices, "transition_in": s["transition"], "chrome": "; ".join(chrome), "accent": CLAY,
                "notes": [s["note"]] if s["note"] else []}
        if s["prompt"]:
            plates.append({"plate": f"p-{sid}", "set": s["set"], "prompt": s["prompt"], "shots": [sid]})
        if tier in ("sung", "motion"):
            cid = ("S" if tier == "sung" else "M") + sid[1:]
            w0, w1 = (gap_before(t0), gap_after(t1)) if tier == "sung" else (t0, t1)
            ww = " ".join(w[2] for w in ALLW if w0 - 1e-6 <= w[0] < w1)
            clips.append({"id": cid, "kind": tier, "route": s["route"], "t0": w0, "t1": w1, "shots": [sid],
                          "words": ww if tier == "sung" else None, "start": f"plate:p-{sid}"})
            shot["clip"] = cid
            if tier == "sung":
                shot["window"] = [w0, w1]
                shot["clip_words"] = ww
        shots.append(shot)
    return shots, plates, clips


def main():
    shots, plates, clips = build()
    secs = lambda k: round(sum(c["t1"] - c["t0"] for c in clips if c["kind"] == k), 1)
    lead = sum(s["t1"] - s["t0"] for s in shots if s["lead_on_screen"]) / DUR
    board = {
        "version": 1, "title": "Checked Me and I'm Fine", "song": "media/song/checked-me-v1.wav", "take": "checked-me-v1",
        "duration": DUR, "written_by": "Claude (Kiln, local), 23 Oct 2026, from production/board/design.md; v2 the same day after "
                      "notes/reference-kill-switch.md (kinetic type, beat-held stills, faster cuts)",
        "version_note": "v2: lip sync on the key lines and the stage phrases; kinetic type elsewhere",
        "routes": {"it": "InfiniteTalk from a still plate, local", "grok": "Grok Imagine from a plate (Lati's "
                   "subscription), one short sung phrase per take", "grok-dance": "Grok, dance with lips together",
                   "wan": "Wan 2.2 I2V, local", "code": "drawn in code", "plate3d": "plate with depth", "still": "still"},
        "hits": [{"t": bar(24), "why": "the drop into chorus 1: Ready? → Y, glitter cannons"},
                 {"t": bar(82), "why": "the final chorus after one bar of black"}],
        "unsung_words": UNSUNG,
        "chapters": [{"id": c[0], "name": c[1], "t0": bar(c[2]), "t1": bar(c[3]), "bars": [c[2], c[3]],
                      "sections": c[4], "accent": CLAY, "accent_object": c[5], "set": c[6], "light": c[7]}
                     for c in CHAPTERS],
        "lyric_lines": [{"line": l["line"], "text": l["text"], "section": section_at(l["t0"]), "t0": l["t0"],
                         "t1": l["t1"], "words": l["words"]} for l in LINES],
        "shots": shots, "plates": plates, "clips": clips,
        "totals": {"shots": len(shots), "mean_s": round(DUR / len(shots), 2), "lead_share": round(lead, 3),
                   "sung_clips": sum(c["kind"] == "sung" for c in clips),
                   "motion_clips": sum(c["kind"] == "motion" for c in clips),
                   "sung_s": secs("sung"), "motion_s": secs("motion"),
                   "by_route": {r: sum(s["route"] == r for s in shots) for r in TIER},
                   "estimate_usd": 0.0},
    }
    OUT.write_text(json.dumps(board, indent=1, ensure_ascii=False) + "\n")
    t = board["totals"]
    print(f"{t['shots']} shots, mean {t['mean_s']} s, her share {t['lead_share']:.0%}, sung clips {t['sung_clips']} "
          f"({t['sung_s']} s), motion clips {t['motion_clips']} ({t['motion_s']} s); routes {t['by_route']}")


if __name__ == "__main__":
    main()

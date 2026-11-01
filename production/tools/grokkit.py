#!/usr/bin/env python3
"""The Grok farming kit: every stage shot's picked plate and its exact prompt, numbered in farming order.

    python3 production/tools/grokkit.py        # -> media/grok-kit/NN-sXXX-kind.png + production/motion/grok-kit.md

Order (plan-b.md, the stage caveat): dance takes first (lips together; every stage shot needs one in either plan),
then sung phrases, closest framings first. Sung prompts follow the pilot's round 4: one short phrase per take, its
words timed from 0.5 s, tempo 132, Lati's subtitle gate; a shot gets one take per sub-phrase (split at commas, the
echoes in parentheses left out), whole even where the shot cuts inside it: the edit trims, Grok needs the phrase.
Lines already kept from chorus 1 (P1 "I checked myself and I'm fine", P2 "Green lights on every line", P4 "First
time, every time") are marked: try the keeper first. Plates are copied as picked (the edit mirrors where the clip
sits on the other side; mirror the plate first if you want the take to carry it).
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "media/grok-kit"
# Lati's version (25 Oct): with "This is crucial:", "All words must be present and lip synced." and "Tight lip sync
# pass." Grok sang whole phrases almost every take; before, a whole phrase came by luck around take 3.
TEMPLATE_SUNG = ("Upbeat pop concert at 132 BPM. She dances to the beat and sings into her headset microphone. This is "
                 "crucial: word by word on this timing: {phrase}. All words must be present and lip synced. She sings "
                 "out with energy, her mouth clearly shaping each word, then keeps dancing, her lips closed. "
                 "{extra}{crew}{camera}Keep her face, hair, streak, star clip, headset microphone and clothes as in the "
                 "image. Gate: if subtitles or text appear on screen, redo. Tight lip sync pass. video starts into "
                 "motion. no music is necessary")  # Lati: Grok's agent otherwise makes 6 s of music too
TEMPLATE_DANCE = ("Upbeat pop concert at 132 BPM. She dances to the beat, her lips gently closed. {extra}{crew}{camera}"
                  "Keep her face, hair, streak, star clip, headset microphone "
                  "and clothes as in the image. Gate: if subtitles on screen, redo.")
CHOIR = ("Upbeat pop concert at 132 BPM. A line of five women who all look like her, side by side, dance in unison and "
         "all shout one word together into their headset microphones, on the beat: {phrase}. Their mouths open wide on "
         "each 'hey' and close between. {camera}Keep each woman's face, hair, streak, star clip, headset microphone and clothes "
         "as in the image. Gate: if subtitles on screen, redo.")
OWN = {  # shots whose take isn't a concert dance
    "s002": ("Seen from behind, she walks steadily down the aisle of a dark auditorium between the seat rows, toward the "
             "glowing cobalt-and-magenta keynote stage ahead, confident and unhurried, her arms relaxed. The camera "
             "follows behind her at walking pace. She walks alone between the dark, quiet seat rows. Keep her face, hair, streak, star "
             "clip, headset microphone and clothes as in the image. Gate: if subtitles on screen, redo."),
    "s028": ("Upbeat pop concert at 132 BPM. Five women who all look like her, side by side, dance in unison to the beat "
             "with their lips closed. The camera holds steady at chest height in front of the five of them. "
             "Keep each woman's face, hair, streak, star clip, headset microphone "
             "and clothes as in the image. Gate: if subtitles on screen, redo."),  # the plate is her five versions
}
# Say only what the plate holds and what should happen, in positive words (Lati, 25 Oct, from Skybrows' lessons in
# ~/workshop/references/skybrows-lessons.md: a negative tends to make the thing it names appear). Lati's subtitle
# gate stays: it worked in round 4.
CREW = "Behind her, her backing dancers dance as dark silhouettes against the bright screen. "
SOLO = {"s011": "She is alone in front of the bright screen. "}  # plates without dancers
# What moves in each dance take, motion only (25 Oct). The board's action lines also carry the graphics (words on the
# wall, [Y/n], the counter); in a Grok prompt those get painted as garbled text, and the type is ours to add.
DANCE_EXTRA = {
    "s011": "She walks toward the camera on the beat. ",
    "s013": "The stage lights sweep across the stage. ",
    "s014": "She strides the last steps downstage toward the camera. ",
    "s017": "On the downbeat glitter cannons fire. ",
    "s022": "Beams sweep across the stage on the beat. ",
    "s026": "",
    "s030": "The crowd's hands wave in the foreground. ",
    "s043": "Seen from behind, she dances on the runway, facing the stage. ",
    "s044": "Glitter falls over the crowd. ",
    "s050": "The lights flash on the beat. ",
    "s051": "Seen from behind, she dances at the end of the runway, facing the crowd. ",
    "s053": "She and the dancers move in unison and hit a pose on the last downbeat. ",
    "s060": "Glitter falls and the full light rig flashes. ",
    "s066": "Glitter, sweeping beams, the crowd, her and her dancers in unison. ",
}
# Where the camera is and what it does, pinned to something physical (Skybrows' lessons: left free, it drifts
# somewhere dull; an effect brings its side effects, so say the camera stays steady through them). Lati, 25 Oct: yes.
CAMERA_BY_FRAMING = {
    "MCU": "The camera holds steady at her face, just below her eye line. ",
    "MS": "The camera holds steady, low and close at the stage edge, looking up at her. ",
    "WS": "The camera holds steady, low at the front of the stage, looking up at her. ",
    "EWS": "The camera holds steady and wide, low in the crowd, looking up at the stage. ",
}
CAMERA = {
    "s011": "The camera holds at her chest height as she walks toward it. ",
    "s014": "The camera holds low at the stage edge as she strides toward it. ",
    "s017": "The camera stays steady, low at the front of the stage, as the glitter cannons fire. ",
    "s030": "The camera holds steady, low in the crowd behind the raised hands, looking up at her. ",
    "s043": "The camera follows low behind her along the runway. ",
    "s044": "The camera holds steady, low in the crowd at the end of the runway, looking up at her. ",
    "s051": "The camera rises slowly behind her, over the crowd. ",
    "s067": "The camera holds steady at chest height in front of the five of them. ",
}
KEEPERS = {"i checked myself and i'm fine": "P1 (g2-p1-take2)", "green lights on every line": "P2 (g2-p2, g2-p2-plate35)",
           "first time every time": "P4 (g1-p4-take2, g1-p4-take3)"}
CLOSE = {"MCU": 0, "MS": 1, "WS": 2, "EWS": 3}


def norm(t):
    return " ".join("".join(ch for ch in t.lower() if ch.isalnum() or ch in " '").split())


def subphrases(line):
    """A lyric line's sung words split at commas and dashes; parenthesised echoes ("(I'm fine!)") are dropped: they're
    layered backing vocals, not hers to sing on camera. Each part is one Grok take (P3 only came whole once split)."""
    text, parts, cur, depth = line["text"], [], [], 0
    toks = text.replace("—", " , ").replace(",", " , ").replace("(", " ( ").replace(")", " ) ").split()
    ws, wi = line["words"], 0
    for t in toks:
        if t == "(":
            depth += 1
        elif t == ")":
            depth -= 1
        elif t == ",":
            if cur:
                parts.append(cur)
            cur = []
        else:
            if not any(ch.isalnum() for ch in t) or wi >= len(ws):
                continue
            if depth == 0:
                cur.append(ws[wi])
            wi += 1
    if cur:
        parts.append(cur)
    parts = [p for p in parts if p]
    whole = [w for p in parts for w in p]
    if any(norm(" ".join(w["w"] for w in whole)) == k for k in KEEPERS):  # "first time, every time" was kept whole (P4)
        return [whole]
    if all(len(p) == 1 for p in parts):  # a chant ("Fine, fine, fine, fine, fine"): one take, all on the beat
        return [whole]
    return parts


def main():
    b = json.loads((ROOT / "production/board/board.json").read_text())
    picks = json.loads((ROOT / "production/board/picks.json").read_text())
    W = [w for w in json.loads((ROOT / "media/song/analysis/checked-me-v1/words.json").read_text())["words"]
         if w.get("t0") is not None and w.get("t1")]
    dance = [s for s in b["shots"] if s["route"] == "grok-dance"]
    sung = sorted([s for s in b["shots"] if s["route"] == "grok"], key=lambda s: (CLOSE.get(s["framing"], 9), s["t0"]))
    if KIT.exists():
        shutil.rmtree(KIT)
    KIT.mkdir(parents=True)
    out = ["# Grok farming kit", "",
           "Claude (Kiln, local), 24 Oct 2026. Made by `production/tools/grokkit.py`; the plates are in "
           "`media/grok-kit/` with the same numbers. Dance takes first, then sung phrases, closest framings first "
           "(plan-b.md, the stage caveat). Four takes per phrase at most; no keeper after four, the shot takes its "
           "fallback (its dance take with the line in hook type).", ""]
    n = 0
    for kind, shots in (("dance", dance), ("sung", sung)):
        out += [f"## {'Dance takes (lips together)' if kind == 'dance' else 'Sung phrases'}", ""]
        for s in shots:
            pk = picks.get(s["plate"] or "")
            if not pk:
                out += [f"- {s['id']}: no picked plate", ""]
                continue
            extra = DANCE_EXTRA.get(s["id"], "") if kind == "dance" else ""
            cam = CAMERA.get(s["id"]) or CAMERA_BY_FRAMING.get(s["framing"], CAMERA_BY_FRAMING["WS"])
            if s["id"] == "s067":  # the choir (Lati, 24 Oct): four backing "hey"s, found by ear and in the 'other' stem
                takes = [[{"w": "hey", "t0": t, "t1": t + 0.2} for t in (167.45, 167.90, 168.32, 168.80)]]
            elif kind == "dance":
                takes = [None]
            else:  # every sub-phrase of the shot's lines that's sung inside the shot's window, whole
                takes = [p for i in s["lines"] for p in subphrases(b["lyric_lines"][i])
                         if any(s["t0"] - 0.05 <= w["t0"] < s["t1"] - 0.15 for w in p)]  # not a phrase starting at the cut
            for k, ws in enumerate(takes):
                n += 1
                tag = f"{n:02d}-{s['id']}-{kind}" + (chr(97 + k) if len(takes) > 1 else "")
                shutil.copy(ROOT / pk["file"], KIT / f"{tag}.png")
                head = f"### {n:02d} · {s['id']} · {s['framing']} · {s['chapter']} · {s['t0']:.2f}-{s['t1']:.2f} s"
                if kind == "dance":
                    out += [head, "", f"Plate `{tag}.png`. Take length: at least {s['t1'] - s['t0'] + 1:.0f} s.", "",
                            "```text", OWN.get(s["id"]) or TEMPLATE_DANCE.format(extra=extra, crew=SOLO.get(s["id"], CREW), camera=cam), "```", ""]
                else:
                    t0 = ws[0]["t0"] - 0.5
                    phrase = ", ".join(f"\"{w['w']}\" at {w['t0'] - t0:.1f} s" for w in ws)
                    if ws[-1]["t1"] - ws[-1]["t0"] > 0.45:  # a held last word: s023/s064 dropped the held "fine"
                        phrase += f", held as a long open note until {ws[-1]['t1'] - t0:.1f} s"
                    line = norm(" ".join(w["w"] for w in ws))
                    keep = KEEPERS.get(line)
                    out += [head, "", f"Plate `{tag}.png`. Phrase starts at {ws[0]['t0']:.2f} s in the song "
                            f"(take time 0.5 s). Words: *{' '.join(w['w'] for w in ws)}*."
                            + (f" **Kept already: {keep}; try it first.**" if keep else ""), "",
                            "```text", (CHOIR.format(phrase=phrase, camera=cam) if s["id"] == "s067" else
                                         TEMPLATE_SUNG.format(phrase=phrase, extra="", crew=SOLO.get(s["id"], CREW), camera=cam)), "```", ""]
    (ROOT / "production/motion/grok-kit.md").write_text("\n".join(out) + "\n")
    print(n, "takes ->", KIT.relative_to(ROOT))


if __name__ == "__main__":
    main()

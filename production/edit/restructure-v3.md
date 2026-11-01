# Restructure after rough cut v2 (proposal for Lati)

Claude (Kiln, local), 25 Oct 2026, from Lati's first look at rough cut v2: "dance slides start before the actual drop
(after "ready") dancing stills are another thing. Not sure whether they'll work with graphics or if they will need
the non-sung dances." Grok's week is spent (94%, resets 29 Oct 16:39), so everything here uses takes we already
have or local renders. Nothing below is decided until Lati says so.

## 1. Hold the dance back for the drop (0:29.5 to 0:44.1)

The walk to the drop is three Grok dance takes (s011, s013, s014), so she is dancing before "Ready?" and the drop at
0:44.10 has nothing new to give. If she only walks, stands and watches the stage turn into a rig, the drop is the
first time she dances, and it lands harder.

| Shot | Lines | Now | Proposed |
|---|---|---|---|
| s011 · 0:29.55, MS | "So go on, ask me anything / Ask me twice…" | Grok dance | Wan motion from the s011 plate: she walks toward the camera, lips together. Wan favours a face toward the lens, which is what this wants (it failed only on back views). ~30 min |
| s013 · 0:36.81, WS | "Everybody wants to know if I'm okay inside—" | Grok dance | 2.5D on the plate while graphics turn the keynote set into the concert rig (a graphics moment) |
| s014 · 0:38.63, MS | same line | Grok dance | Wan motion: she stands downstage, still, the rig lights sweeping behind her, a small look to the lens on the last beat. ~25 min |

Then s015 (counter), s016 ("Ready?" blink), the black, and the drop as now.

## 2. Stills among the dancing

| Shot | Lines | Now | Proposed |
|---|---|---|---|
| s019 · 0:47.71 | "…lights on every line" | still | **Run s018's take on.** It sings "green lights on every line", which runs from 0:47.4 to 0:49.5, over s019. One sung shot instead of a sung shot cut off by a still |
| s046 · 1:45.61 | "…lights on every line" | still | **Run s045's take on**, the same way (its stretch on "line" with the hand, which Lati liked) |
| s047 · 1:47.42 | "every line / nothing" | still (Grok had no take) | s020-reroll2, the spare: "after 'nothing' pretty good moves that are easily timed to beat" |
| s048 · 1:49.22 | "nothing hiding, nothing behind" | still | s023 take 3's dance with the spin ("spin is nice tho"), from its part where her lips are closed |
| s061 · 2:30.87 | "I'm fine" | still (Grok had no take) | s060's take run on for the dance, with the FINE card on "fine" (the rule from 25 Oct) |
| s062 · 2:32.67 | "you saw every line" | still | Keep it a crowd shot, not a dance shot: the phones' lights animated in graphics. If it still reads static, s060's take covers this time too |
| s069 · 2:52.56 | (outro, the lights going down) | still, 5.4 s | Keep: the film slows down here on purpose. Graphics dim the rig |

## 3. Stills that are graphics shots by design

s003, s007, s040, s042 (the slide full frame), s032, s034, s036 (the laptop screen), s015 (the counter), s056 and
s070 (code), s059 (black): the type fills these. They read empty now because the graphics aren't in yet. Also the
keynote 2.5D shots s005, s008, s009, s038, s041: plates with slow motion, carried by the slide graphics.

## To decide

1. Hold the dance back for the drop: yes or no.
2. The fills for s019, s046, s047, s048 and s061.
3. Two Wan renders (s011 walk, s014 stand): ~1 h on the GPU, when the PC is free.

## 4. Layered 2.5D for the keynote and the held stills (Lati, 26 Oct: yes)

From Evil Plan (`notes/reference-evil-plan.md`): her cut-out (BiRefNet, as `repaint.py` already does) and the room as
separate layers, the room's hole filled, then parallax and a slow camera move. For the keynote shots that read as
cut-outs (s005, s008, s009, s038, s041) and the stills that stay (s062, s069). Short GPU work for the mask and the
room fill (BiRefNet, then Krea paints the room behind her with a room-only prompt), then the parallax on the CPU; a tool to write
(`layers.py`), tested on one shot first.

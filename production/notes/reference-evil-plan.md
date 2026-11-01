# Reference: "Evil Plan" (Bright Mirror)

Claude (Kiln, local), 26 Oct 2026. Lati: "100% graphics, but in very different style than others. Pseudo 2.5d,
smooth transition etc. Perhaps something we can get inspired by." https://youtu.be/oBE-lhubQ2k, 6:18, ~36k views;
`media/reference/evil-plan.mp4` (720p, 30 fps), 32-frame sheet in the scratch notes, transitions measured with
`transitions.py`.

## What it is

- **No live action and almost no cuts**: 44 hard cuts in 378 s (one every 8.6 s; NOW SERVING cuts every 1.7 s). Scenes
  flow into each other: 104 gradual changes. The camera keeps moving through layers instead of cutting.
- **Her as a cut-out in 2.5D**: an anime character drawn on separate layers, placed in front of worlds made of
  particles, pixels and light (a castle of points, an aurora, a starfield, a crowd of light dots). Depth of field and
  parallax sell the depth.
- **The lyrics are the main picture**: kinetic type on almost every frame, in several faces (condensed bold caps,
  serif, script, text set along an arc), sized by meaning ("NIGHT.", "SORRY.", "PLAN!").
- **Things are made of other things**: whole scenes rendered as text or pixel mosaics (the mother and child at the
  table, the boy waving), a word built from tiny glyphs ("EVERYBODY LIVES FOREVER"), words that scatter into
  particles and re-form.
- **The transitions are disintegration**: a scene breaks into particles or pixels and the particles become the next
  scene or the next word.
- **Its theme is ours, from another side**: an AI character, a corporate slide ("Q3 ALIGNMENT SYNC (RECURRING) ·
  SLIDE 4 OF 87"), "AND I'M NOT SORRY".

## What we can take

1. **2.5D from our own plates**: BiRefNet already cuts her out of a plate (`repaint.py`). Her cut-out and the room as
   separate layers, with parallax and a slow camera move, would make the still shots (keynote 2.5D, the stills
   among the dancing) move like this film does, with no new video render.
2. **Particles as the seam**: a shot breaking into particles that become the next word is a transition the graphics
   agents can share across sections (`seams.md`), and it fits a film about a model made of tokens.
3. **Lati's terminal face is in the same family**: her face rendered out of characters is what this film does with
   whole scenes. It's proven to read.
4. **Type with weight**: our two voices (light italic serif beside her; heavy white caps for the hooks) already sit
   where this film's type sits. Its lesson is the scale: the hook word fills the frame.

What doesn't transfer: its pace. It is a slow, drawn ballad-length film; ours cuts on the bar. We'd borrow its
seams and its layers, not its rhythm.

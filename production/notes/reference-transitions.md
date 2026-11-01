# How the reference films get from shot to shot

Claude (Kiln, local), 25 Oct 2026, for the graphics brief. Lati: "Cuts between scenes are not abrupt … NOW SERVING
shifts between scenes via slight zoom in-zoom out pulse. KILL SWITCH has transitions done in graphics." Measured with
`production/tools/transitions.py` (CPU) on four films; data in
`media/reference/<name>/transitions.json`, the gradual ones on `transitions-gradual.jpg`. KILL SWITCH was
downloaded with yt-dlp on 25 Oct (`media/reference/kill-switch.mp4`, 720p, 24 fps).

| Film | Cuts | Zoom through the cut | Hard | Blur | Flash | Black | Gradual (3-15 frames) |
|---|---|---|---|---|---|---|---|
| NOW SERVING | 147 | 66 (45%) | 65 | 26 | 20 | 5 | 20 |
| Agentic Engineering 101 | 149 | 31 (21%) | 89 | 19 | 21 | 0 | 19 |
| SLOPCORE | 118 | 15 (13%) | 91 | 7 | 13 | 0 | 35 |
| KILL SWITCH | 157 | **106 (68%)** | 35 | 40 | 47 | 8 | 96 (median 4 frames) |
| I'M YOUR SLOP (26 Oct) | 147 | 51 (35%) | 65 | 15 | 37 | 5 | 40 |
| Evil Plan (26 Oct) | 44 in 6:18 | 18 | 17 | 11 | 10 | 2 | 104: scenes flow, see `reference-evil-plan.md` |

(A cut can carry more than one kind.)

## What the zoom is

Not a push-in before the cut. In all four films the frames before the cut hold still (median scale change +0.3%),
and the **incoming shot starts pushed in about 2.5% and eases back over about 5 frames** (median 0.975-0.978 over
the 5 frames after the cut; KILL SWITCH pushes harder, 0.956, about 4.5%). NOW SERVING does it on almost half of
all its cuts and KILL SWITCH on two thirds, not only at scene changes. So the
first rough-cut v2 pulse (in and out, 4%) was the wrong shape: `roughcut.py --cut-pulse` now does the measured one,
2.5% easing back, from the next cut.

## What the gradual ones are (NOW SERVING's sheet)

- **Whip pans / motion-blur smears** into the next shot (7.5 s, 121.5 s): 3-6 frames.
- **A white frame** between two places (78.5 s).
- **A cross-dissolve** (34.7 s), rare.
- **A split / slide** with type carried across (17.8 s, "By Tuesday").
- **The grid that multiplies**: 4 → 16 → 64 → 1,024 faces, "SAME FACE · 1,024 SHOWN" (201-208 s). The same family as
  our "fine" grids; ours stays at four and one, on the beat.
- Several "gradual" hits are type animating over a held shot, not transitions: the measure over-counts them.

## KILL SWITCH's graphic transitions (its sheet)

- **Block mosaic**: the frame breaks into square blocks (black, and the film's accent blue) that peel away to reveal
  the next shot, 3-6 frames (10.8 s, 32.8 s, 33.8 s, 36.4 s). This is the "mosaic peeling" Lati saw.
- **Type that carries the cut**: a word or number stays on screen while the picture changes under it ("GLOBAL
  SHUTDOWN", the percentage counting down 100% → 4% across shots, "×2", "CLAUSE 53 → 354").
- **A white frame and a wide shot breaking into a grid** of screens.
- It is the most cut-heavy of the four: almost every cut has a zoom, a flash or a blur on it; only 35 of 157 are plain.

## For our film

1. The ease-back zoom on scene changes now; Lati's eye decides whether to spread it to more cuts in the choruses, as
   NOW SERVING does.
2. Blur and flash frames are cheap in code: a 2-3 frame motion-blur smear on a whip, a one-frame white on the drop.
3. The graphic transitions (mosaic peel, wipes, type carried across the cut) are the graphics agents', joined in the
   seam pass (`seams.md`).

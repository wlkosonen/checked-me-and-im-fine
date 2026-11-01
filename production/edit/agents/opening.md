# Opening: agent A's log

Claude (agent A, Opening), 1 Nov 2026. Shots s001-s016, 0:00-0:44. Code: `production/tools/gfx_opening.py`. Renders:
`media/gfx/opening/`.

## Shots

All rendered at 720p: s001-s004, s007-s016. s005 and s006 not re-rendered; their code blocks are identical to HEAD (compared
as text).

The corrected lyric rule (Lati, 1 Nov, via Kiln) applied from the start: nothing was built under the old one.

| Shot | Picture | Graphic | Lyric |
|---|---|---|---|
| s001 | lips, profile | beside her: the first film's question on the beats, then a MIC ✓ per "check" | whole line, verse voice |
| s002 | the aisle | on the screen, tracked: the first slide; MIC ✓ ticks on three beats, the screen catching up | none sung |
| s003 | full frame | the same slide; `SELF` types in unasked, its tick lands | none sung |
| s004 | she watches | the slide on the screen, tracked; `CHECKED BY: ME` thumps at 10.297 on the vocalizing's first note | none sung |
| s007 | full frame | s005's window, a chat: `new chat · memory off`, `> hi`, "memory off" underlined on "before" | BIG: it is, / never met |
| s008 | M008 | on the screen, left of her: `yesterday/` opens, `0 items` | BIG: no grudge |
| s009 | her back | the slide is one input field, cursor on the eighths | BIG, typed: no rerun / just you / blinking line |
| s010 | close, lips together | beside her, on the blue | BIG: whatever / tonight |
| s011 | M011 walk | the white screen, blurred to its focus: Q&A, raised hand, `questions welcome` | BIG: go on, / ask me / anything |
| s012 | sung CU | two answer cards, `illustrative`, ≈ in a disc on her shirt | whole line, verse voice |
| s013 | M014 | the keynote slide flies off the wall; the wall wakes row by row, an eighth a row, in `ARE YOU OK IN THERE?` | BIG caps: EVERYBODY / WANTS, KNOW / OKAY |
| s014 | s014grok | the rows, full | BIG caps: OKAY, INSIDE— |
| s015 | s014grok run on | `ARE YOU OK IN THERE?` and the number, up on the sixteenths, stalling on 41.841 with a dash; `illustrative` under it | none: the held note |
| s016 | sung CU, the white plate, no matte | the prompt in ink, read across her | whole line: `Ready?` in the verse voice, `[Y/n]` in mono |

Cuts inside the section: s003 `flash 2` (the bass enters there), s013 `whip 3` (keynote to rig).

## Decisions worth a look

- **The board's times are stale.** s003's stamp (10.297) falls in s004 now, so it thumps on the screen she's watching. On
  s014-s015 the board has words that are sung earlier ("if I'm okay" 38.04-38.82, "inside" from 39.02). I timed to
  the words; the stem shows "inside—" held to about 43.4, so s015 sits on that held note, which is where the counter goes.
- **A word a side of her on the wall, from WANTS on.** She stands mid-wall and hid the middle of any short word ("K_W", and "OK"
  in the question). EVERYBODY alone stays across the wall, its RY behind her.
- **The first film's question opens s001,** at 1.17 s, white, not clay: it's the asker's. It clears for the first "check".
- **Clay and green don't hold on the slide's gradient,** so SELF, the stamp, s008's folder and s009's field sit on ink
  plates.
- **The answer cards' wording is mine:** "I checked, and I'm fine." and "Fine. I checked.", built from the song's words,
  marked `illustrative`. The count on the wall is invented too, also marked (design.md lines 6, 7).
- **Serif on the slides, caps on the rig:** the type changes voice when the set does.

## Checked, and how

- Frames from the rendered mp4s, read by eye on contact sheets: each shot's first and last frame and two or three
  times inside it. Frame counts match each shot's window within a frame.
- Tracked quads drawn over five frames of each of s002, s004, s008, s009, s011: they sit on the screens. The fit is a
  similarity, so s004's perspective holds only as far as its camera stays put.
- s013's wall drift: the band edge read in clear columns beside her agrees with `gfx_wall.py`'s raw reading within 2 px;
  its smoothed fit is up to about 8 px off (720p) mid-shot, around 37.5 s, where the tilt changes speed.
- Vocal stem envelope for the "check"s, the vocalizing at 10.25 and the hold to 43.4.
- Not checked: anything in motion. Timing and how the moves play are Lati's on `/cut`. I have not heard the song against
  these frames.

## For Lati's eye

- s016 on black: her matte, multiplied. Her sleeves fade a little at the frame's foot, like a vignette. If it reads
  ghostly, the fallback is the plate's white with the prompt in ink.
- s016's mouth is open from the first frame, before "Ready?" at 43.2 (the picture's own, under the held note).
- s014-s015's silhouettes move a lot behind the wall. It's the picked take; I added no dance graphics.
- s012's ≈ sits low, on her shirt, because her face is what's between the cards.

## Questions for Kiln

1. **The Y on the seam:** s016 holds `Ready? [Y/n]` unanswered to its last frame; the cursor happens to be off on that frame.
   s017's test doesn't draw the `Y`. Does agent B draw it, or should the flash carry it?
2. Keep `CUTS` s003 and s013, or does the flash at 7.56 compete with the seam's flash at 44.1?

## Base requests

- `lock()` and `audit()` at the foot of `gfx_opening.py` replaced `track()` (see "Locked to the screens" below). Lift them
  if the others want them. `tick()` (a drawn ✓) is in the same file.

## Written outside my folders

Through the shared tools, keyed by shot: `media/cache/gfx/matte-<sid>.mp4` for s002, s004, s008-s016 and
`plane-<sid>.json` for s002, s004, s008, s009, s011, s013-s015.

## Kiln, review (1 Nov)

- s003's flash at 7.56 comes out: it's a soft intro before the drums, and the film's first flash should be the drop's.
- The `Y`: left unanswered on screen. The flash and the cannons at 44.1 are the answer, and s017 stays as Lati approved it.
- For Lati: s016's sleeves fading on black, and her mouth open before "Ready?".

## Locked to the screens (1 Nov, Lati's notes on s004, s008, s011)

**Cause, three faults:**

1. **Chained flow, as Kiln expected.** `track()` chained a similarity from frame to frame over lights at other depths, so a
   gradient screen's real move wasn't seen and the error added up. s011's screen slides down about 100 units as she walks; the
   plane went the other way. Lati's "up and out of bounds".
2. **A smooth path over a stepping picture.** s004 is 16 fps in a 25 fps cut (35 of 91 steps repeat a frame), s011 28 of 90,
   s013 10 of 45. The plane kept moving while the picture held, so the graphic slid against it.
3. **The walls were vertical only.** `gfx_wall.py` doesn't follow the band sideways or in scale; s015 ended 42 units out.
   Nobody flagged this one.

**Fix:** no flow. Each screen's edges are found again in every frame against the dark round them, the corners solved from
those lines, and the path smoothed over distinct source frames only, so the graphic steps when the picture does. Only the
place to search carries over. Walls follow the white band's top edge and ends, as a similarity.

**Audit, every frame, 1080 units (720p px are two thirds of that).** The real edge is read with a second detector (the
steepest point; the lock uses the half level). The graphic is the footprint the real `screen()`/`wall()` call paints, read
from its pixels, or for the walls a marker painted at the band's ends. Old planes through the same audit:

| Shot | Frames | Worst before | Worst now | Drift now | Worst step now |
|---|---|---|---|---|---|
| s002 | 91 | 11.8 | 4.2 | 3.4 | 1.8 |
| s004 | 92 | 23.8 | 3.1 | 1.4 | 1.3 |
| s008 | 46 | 16.6 | 1.8 | 3.2 | 1.7 |
| s009 | 91 | 4.3 | 2.8 | 1.0 | 0.4 |
| s011 | 91 | 132.8 | 7.2 | 5.0 | 2.2 |
| s013 | 46 | 43.7 | 2.7 | 4.2 | 4.2 |
| s014 | 46 | 10.1 | 1.2 | 0.7 | 0.6 |
| s015 | 45 | 41.9 | 1.0 | 1.0 | 0.6 |

Worst now overall: 7.2 units, 4.8 px at 720p, on s011's bottom. Worst anywhere else: 4.2 units, 2.8 px, s002.

**What those numbers do and don't say:**

- s011's 7.2 is mostly the two detectors disagreeing on a soft edge: they differ by up to 6.2 units there, growing as the screen
  defocuses. I have not separated out the remainder.
- s002's top edge can't be read (it runs to the frame's top); its height follows its width. s011's top is read in 64 of
  91 frames.
- s004's far end is behind her and can't be read, so position along the slide comes from the left edge and its scale. Everything
  drawn there sits on the left.
- The "before" for s004 left, s008 right and s011 top were read only in part (the footprint out of the audit's reach), so those
  worst cases may be understated. By the planes' own numbers s004's left was out by 23 and s011's top by 92.
- s013's picture jerks (raw band edge 500 to 512 across a few frames), which is the 4.2 step.

**A trap worth keeping:** my first lock took s008's foot as an edge and it hopped mid-shot to the lit stage lip below, 44 units
out, and both detectors agreed on the wrong line. Only the shape gave it away: the height-to-width ratio moved while the width
ran smooth. So s008's foot now follows its width (`FOOT`), and the audit reads the real foot as the thin dark line it is.
Every other edge was checked for hops, and s009 and s011 for shape: no hop. s013's spikes (up to 7.8) are the take's jerk, and
the graphic follows it within 2.7.

**Checked in motion, as far as I can without eyes on it:** time slices from the rendered mp4s (s002, s004, s008, s011, s013,
s015): one pixel column per frame, side by side. Text and screen edges run parallel across the whole shot in s004, s008 and
s011; s002's, s013's and s015's slices didn't cross enough type to say, and s009 and s014 weren't sliced. That's a measurement of position, not a judgment of how it
plays: Lati's on `/cut`.

**Re-rendered:** s002, s004, s008, s009, s011, s013, s014, s015. s011's `questions welcome` is stacked in two rows, because the
locked slide now passes behind her sleeve at the end. s005 and s006 untouched.

**For Kiln, outside my section:** two of these faults may be elsewhere. Any shot on `gfx_wall.py` gets no sideways or scale
tracking (s017-s018, the approved test, and any others in B). Any shot from a 16 fps clip or with a `speed` steps under a
smooth plane, and `gfx_plane.py` chains flow as `track()` did. I haven't measured those shots. `audit` covers only this
section's shots, through `MEASURED`.

**Run:** `media/cache/gfx-venv/bin/python production/tools/gfx_opening.py lock s002 ...`, then `audit s002 ...`. Writes
`media/cache/gfx/plane-<sid>.json`.

## s016 on the white plate (1 Nov, Lati)

Lati, through Kiln: "her cutout is indeed noticeable and fade around edges. lets try fallback." So: no matte, the plate as it is,
the prompt in ink. `Ready?` still lands at 43.167 in the verse serif and `[Y/n]` at 43.621 in the same mono, the one s043 quotes
before the big Y answers it. Both hold to the last frame. The seam stays `built`: white plate into the white flash, nothing moving
on the last frame, cursor off on it. Her mouth open before "Ready?" is accepted as the picture's own.

Moved because of the plate: on black, her hair tips didn't matter; ink can't cross them. The line went up from y 590 to 430, at
her cheek, above the flicks, and the word from 132 to 124. Measured on the clean plate, every frame: her hair reaches x 436 on
the left and x 1464 on the right; the word ends at 419 (17 units clear) and `[Y/n]` starts at 1504 at its largest (40 clear). The
cursor no longer sits after the word: it would have run into her hair there. It blinks at the left before she sings and after
`[Y/n]`.

Read from the mp4: first, middle and last frames, plus the frames around 43.167 and 43.621. `matte-s016.mp4` is no longer used.

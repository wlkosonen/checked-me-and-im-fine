# Graphics agent B: the stage

s017-s030, s043-s053, s060-s067. Code: `production/tools/gfx_stage.py`. Renders: `media/gfx/stage/`. s017 and s018 are as
Lati approved them: `drop()` and their branch of `picture()` are unchanged and they were not re-rendered.

## The system

The stage has two surfaces, and every shot uses them the same way.

- **The dark wall above:** `lit()`, gfx.wall on a rect, type behind her matte, as s017 does it.
- **The white band below:** `band()`, new. It multiplies the picture by the drawing, so anything dark in front of the
  band stays in front: dancers in silhouette and crowd hands hold by themselves, with no matte. This also turns a white
  screen into a colour. It's the answer to "dancers aren't in the matte".
- **Words:** lip-synced shots carry the whole line in the verse voice, behind her (`behind()`), and the wall shows a
  graphic that isn't the words. Everywhere else, one or two big words on the wall, on the beat.
- **Escalation:** chorus 1 keeps the white band and only the dark wall takes type; s022 and the FINE card are the first
  colour. s030 is the first time the band takes type. Chorus 2 fills the far screen. From the key change (s060) the band
  stays cobalt-to-magenta.

## Shots

| Shot | Picture | Graphic | Words |
|---|---|---|---|
| s019 | lips | the song's lines on the wall, a green light per sixteenth | whole line, verse |
| s020 | lips, then s020nov | lights finish; second take: wall | verse, then BIG: EVERY / LINE! |
| s021 | S021 lips | a document: black bars slide off nothing, stamped | whole line, verse |
| s022 | lips | the pale screen turned cobalt-magenta | whole line, verse |
| s023 | card, then take | FINE card made real; the stamp carries the cut onto the wall, same place on screen | BIG: FINE |
| s024 | dance | counter in the corner | BIG: FIRST / TIME, EVERY / TIME, then HEY! x3 |
| s025 | sung take | the dot timeline, none joined, each 1st | whole line, verse |
| s026 | dance | | BIG: as s024 |
| s027, s029 | the "fine" grids | the cells moved onto a vivid ground; tally at the left, 1-5, then 1-4 in s029; chant 1's centre, chant 2's fill on the fourth word; stamp at the right; the corner counter still reads 1 | BIG: FINE on each word |
| s028 | grid, then five of her | the fifth cell in the centre | BIG: FIRST TIME, EVERY TIME behind their heads |
| s030 | dance, crowd hands | band goes vivid, one more dot on the wall | BIG on the band |
| s043 | the walk | far screen goes black on a beat, the prompt types, split round her | BIG: READY? [Y/n] on "ready" |
| s044 | the walk, s043's take (Lati, 1 Nov: crowd slice out) | flash in; READY? stays and the prompt's Y lands where it stood, far screen opens to vivid on the drop; the line on the screen | I CHECKED MYSELF, FINE banner |
| s045 | the walk | the FINE banner runs on from s044 unchanged, then PASSED + CHECKED BY: ME in a grid of screens | BIG: FINE, PASSED |
| s046 | the walk | the far screen is a mosaic of her, x64 then x128, green lights by column; chip `≈ x64 · first meetings: 1` | BIG: GREEN LIGHTS, EVERY LINE |
| s047 | walk, then lips | mosaic; green lights along the band | BIG, then whole line, verse |
| s048 | s020-reroll2 (Lati, 1 Nov), arms wide, no lip sync | her outline scanned live on a wall panel under her right arm, the line runs down her below the face, SCANNED BY: ME, `flagged: 0` | BIG: NOTHING, HIDING, then NOTHING, BEHIND |
| s049 | S049 lips | quiet, on purpose, before s050 | whole line, verse |
| s050 | dance | stamp across the band, biggest yet | BIG: FINE banner |
| s051 | crowd, holds at 116.89 | the upper screen vivid; at 116.89 it goes black and the type stops with her | BIG: FIRST / TIME, EVERY / TIME, then HEY! on 116.89, 117.34, 117.79 |
| s052 | sung take | the dot timeline, longer | whole line, verse |
| s053 | tail | SELF-EVALUATION: PASSED on the wall as s018 has it; the crane brings CHECKED BY: ME up on the band | none sung |
| s060 | dance | band vivid from the first frame | YOU CHECKED ME, FINE banner |
| s061 | take, card, take | s018's layout, one word changed; FINE card; stamp carries the cut | BIG: YOU, FINE |
| s062 | M062 | a phone flashes for each word, its green tick flies to the word | BIG: YOU SAW, EVERY LINE |
| s063 | S063 lips | the bridge's tag back, `source: the model itself` / `checked: what was said`, at "faith" | whole lines, verse |
| s064 | lips, card, lips | disc vivid; FINE card; CHECKED BY: YOU across the wall | whole line, verse; BIG: FINE |
| s065 | dance | band vivid | BIG: as s024, HEY! x3 |
| s066 | widest | the wall fills with unjoined dots, each 1st | BIG: HEY! |
| s067 | five of her | | BIG: HEY! x3, over their skirts |

## What I built outside the brief's list

- `planes()` in `gfx_stage.py` (`python production/tools/gfx_stage.py planes`): replaced on 1 Nov by `lock()` and `walk()`,
  see "Audit" below. The first version, vertical only with chained flow, was out by up to 114 units.
- `band()`, `lit()`, `behind()`, `quiet()`, `image()`. Kiln may want `band()` in the base.
- `CUTS = {"s044": ("flash", 2)}`: the second drop, as s017 has the first.

## What I checked, and how

Frame checks only, read as JPEGs: 2-6 frames per shot from `--check`, every shot in the section. I looked for type
over her face, type under the counter, band edges and word timing against `on()`. Motion, the band's lock in motion, and
timing by ear are Lati's. The hey times come from the stems: chorus 1 near 59.06, 59.52, 59.97 (vocals and drums);
s051's from cut-v3 (the vocal stem is silent there, so they follow the beat grid); s065's from the beat grid.

## Renders and seams

All 31 shots rendered at 720p to `media/gfx/stage/` (s017, s018 untouched). After the batch: s043 re-rendered (the prompt
keeps s016's spelling, `[Y/n]`, in mono) and s030, s066 re-rendered (band tints). Seam frames read from the mp4s: s030, s053
and s067's last frames, s043 and s060's first. Each outgoing shot holds still type to its last frame; each incoming shot's
first frame is clean, with s060's band already vivid. Cells set to `built`; Transition left as it was.

## The walk: s043-s047 as one take (Lati's note, 1 Nov)

s044's crowd slice is out and s043's take runs 98.41-107.87 through five shots. s044 has a new matte. All five shots now
share one track and one screen rect, set on the walk's first frame, so nothing can step at a cut.

**The track:** `walk()` in `gfx_stage.py` (`python production/tools/gfx_stage.py walk`), measured on all 237 frames. It finds
the rig's lights fresh in every frame, not chained from frame to frame, and solves each light's place and each frame's
scale and shift together, so error can't accumulate. Lights off the plane are dropped. A 5-tap filter takes the noise and
leaves the walk's bob. The old chained flow was mixing in the foreground's parallax.

Measured, 1920 units (1 unit = 0.67 px at 720p):

| Shot | Frames | Fewest lights | Residual median / max | Held-out median / max | Scale |
|---|---|---|---|---|---|
| s043 | 90 | 21 | 1.43 / 2.32 | 1.53 / 2.67 | 1.000-1.097 |
| s044 | 45 | 30 | 2.44 / 2.79 | 2.56 / 3.08 | 1.099-1.230 |
| s045 | 45 | 38 | 2.31 / 2.78 | 2.35 / 3.03 | 1.233-1.408 |
| s046 | 45 | 69 | 1.80 / 2.33 | 1.86 / 2.57 | 1.414-1.669 |
| s047, walk | 12 | 54 | 2.02 / 2.90 | 2.20 / 2.86 | 1.676-1.752 |

- **Held-out:** fit on half the lights, measured on the other half.
- **Independent check:** the screen's top edge, read per frame from the picture, not used in the fit, against the track:
  median 1.8 / 2.5 / 0.0 and max 4.4 / 6.3 / 4.5 on s043 / s044 / s045. s046-s047 weren't checked this way: the edge
  leaves the search range.
- **Across the cuts, y step per frame, before / at / after:** s043→s044 -3.8 / -3.5 / -3.4, s044→s045 -5.2 / -5.0 / -5.1,
  s045→s046 -6.5 / -6.7 / -6.7, s046→s047 -7.6 / -7.6 / -7.7. Largest frame-to-frame change in velocity anywhere: 1.7 units.
- **The floor's edge is nearer than the rig** and leaves the plane by up to about 30 units late in the walk, so it's
  measured per frame as `foot` in the plane files, and `band()` stops the colour there.

**The cuts:** s043→s044, READY? stays put, the prompt's Y lands where it stood, the screen opens on the flash. s044→s045,
the FINE banner runs through unchanged. Frames either side of each cut read from the mp4s: the graphic holds its place.
s046's look is kept (Lati liked it): same mosaic box, now on the new track. Re-rendered: s043-s047.

Not judged: the lock in motion, which is Lati's on `/cut`. The numbers say the track follows the lights to about 2 px at
720p at worst; the take itself isn't perfectly rigid. `gfxrender.py`'s 2.5% cut pulse fires on this take only at 101.992, on the
drop, measured from the board's places, so there's no stray pulse at the other cuts.

## Audit: every tracked stage surface, every frame (Kiln's request, 1 Nov)

**Faults found:** the same three A found. The old band planes were vertical only and fitted a threshold read; s051 and s066
were chained flow. Only s017 and s018 are on `gfx_wall.py`; my other band planes came from my own vertical `planes()`, the
same fault. s062's band ends 114 units out sideways: the camera pushes in and pans, and only the height was tracked.
Stepping pictures: s062 holds 16 of 44 steps, s048 18, s051 13 (it holds from 116.89), s017, s018, s025, s047 and s049 4-7.

**Fix:** `lock()`: the band's top on each half and both ends, found in every frame, nothing chained. Each take's plane is a
scale, turn and shift over distinct source frames, so the graphic holds when the picture holds. A one-frame jump is kept
only if both detectors and, for the top, both halves saw it (s051's punches, jerks in s047). s028 and s066 follow the
rig's lights (`rig()`), 7 and 25 lights, fitted to the first frame.

**Audit:** `audit()`. The graphic is a marker painted through the real `wall()` call, read from its pixels. The real edge is
read by the steepest point; the lock uses the half level. Both are measured from the take's first frames, so a soft
edge's constant offset between detectors isn't counted. Frames where the two detectors differ by over 6 units are left
out of "Worst" (glitter on the edge, no measurement); "All reads" keeps them. s028, s048 and s066 have no readable band
ends: the plane against the rig at the graphic's corners. Units are 1080p; 720p px are two thirds of that.

| Take | Frames | Held | Worst before | Worst after | All reads, after | Edges read |
|---|---|---|---|---|---|---|
| s017 (approved) | 45 | 5 | 16.7 | not changed | 21.1 | top, L, R part |
| s018 to 47.19 (approved) | 32 | 4 | 32.6 | not changed | 32.6 | top, L, R |
| s018 from 47.19 (approved) | 13 | 3 | 2.1 | not changed | 2.1 | top, L, R |
| s019 | 45 | 2 | 3.9 | 0.9 | 0.9 | top, L, R |
| s020 first take | 11 | 0 | 3.1 | 1.0 | 1.0 | top, L, R |
| s020 second take | 33 | 0 | 11.9 | 6.0 | 6.0 | top right, L |
| s021 | 45 | 0 | 50.5 | 1.3 | 1.3 | top, L, R |
| s023 | 27 | 1 | 3.1 | 2.1 | 2.1 | top only |
| s024 | 91 | 0 | 19.3 | 1.7 | 1.7 | top, R |
| s025 | 90 | 4 | 9.5 | 2.3 | 2.3 | top right, R |
| s026 | 44 | 2 | 3.7 | 1.8 | 1.8 | top, L |
| s028 | 34 | 0 | 6.0 | 0.4 | | rig |
| s030 | 44 | 2 | 11.1 | 5.3 | 5.3 | top, L, R |
| s047 lip take | 33 | 5 | 19.5 | 7.1 | 13.3 | top, R |
| s048, old take (replaced) | 45 | 18 | 3.9 | left alone | | rig |
| s048, new take | 45 | 1 | new | 8.0 | 29.3 | top, L |
| s049 | 45 | 7 | 0.5 | 0.4 | 0.4 | top, L, R |
| s050 | 45 | 1 | 64.7 | 3.0 | 3.0 | top, L, R |
| s051 | 90 | 13 | 7.3 | 1.9 | 1.9 | top, L, R |
| s052 | 45 | 0 | 16.4 | 1.9 | 1.9 | top, R; scale from the rig |
| s053 | 90 | 0 | 51.4 | 7.9 | 9.3 | top, L, R |
| s060 | 45 | 0 | 46.6 | 5.8 | 19.9 | top, L, R |
| s061 first take | 23 | 0 | 18.4 | 5.0 | 21.1 | top, L, R |
| s061 last take | 9 | 0 | 10.1 | 9.4 | 12.2 | top, L, R |
| s062 | 45 | 16 | 114.4 | 2.5 | 2.5 | top, L, R |
| s063 | 89 | 0 | 5.2 | 0.6 | 0.6 | top right only |
| s065 | 90 | 3 | 5.0 | 5.2 | 5.2 | top only |
| s066 | 44 | 1 | 12.8 | 0.3 | | rig |

**What's still over 5, and why.** In s030, s047, s053, s060, s061 and s065 the plane is within 6.0 of the edge by its own
detector, and over 3 on at most one frame per edge; what's left is the two detectors disagreeing on a soft or glittered edge,
by up to 20 units. I can't separate more than that. s020's 6.0 is on the left end; the plane is within 0.6 of it by the
half level, and the detectors differ by up to 3.0 there. s065 got no better because it was already still: the band doesn't move.

**Not measured, so not claimed:**
- s023, s063, s065 have no readable band end: sideways is unread, and s063's scale too. s023 and s065's band runs out of frame.
- s064 has no plane and no edge the audit could use; the stamp sits on the dark wall after the card. The disc's top moved about 9 units.
- s022 is a full-frame tint with no edge. s027 and s029 are grids, untracked.
- The band's foot isn't read: tints run past it.
- `band()` uses the same `plane()` as `wall()`, but its footprint wasn't read separately.
- s043-s047's walk wasn't re-audited, as asked, so its filter over held frames hasn't been checked against fault 2.
- Rig scale on s052 rests on 3-4 lights. Rig reads on s024 (3 lights) and s065 diverged, so I didn't use them.

**Traps:** the first end reads followed a beam beside the band on s024 and on s066 walked off the band. The overlay of each
take's reads showed it, and s024's left, s066's and s047's left are now not used. s020's second take has its left top read
off a dancer's lit hair (a 9-unit step the right half didn't have): excluded. s066 and the first s024 read both agreed
with themselves, so only the overlay caught them.

**s017, s018 (approved, not changed):** s018's 32.6 is one frame: at 47.16 the render already takes the next take's plane (-61 against -31), a frame
before the picture cuts at 47.19. gfx_wall.py's times sit 0.02 s off the 25 fps grid, and `plane()` rounds up. Its second take is 2.1. s017's 16.7 is the band's right end, read on 25 of 45 frames, on sideways drift
the vertical plane doesn't follow. Lati's call whether to fix them.

**Other change from this:** s062's EVERY and LINE ran off the frame once the wall followed its real move (about 120 units right
by the end): set in from the edge, smaller, and their ticks moved. s062's ticks now use the full plane.

**Re-rendered:** s019, s020, s021, s023, s024, s025, s026, s028, s030, s047, s050, s051, s052, s053, s060, s061, s062, s063, s065,
s066. Frames read after: last frames of s021, s024, s028, s030, s047, s053, s060, s061, s066, plus s051 and s062 inside the
shot. Lock in motion is Lati's on `/cut`.

**Run:** `media/cache/gfx-venv/bin/python production/tools/gfx_stage.py lock [sid ...]`, then `audit [sid ...]`.

## s029's centre (Lati's note, 1 Nov)

"s029 is missing the 5th "fine" center frame." Kiln's spec now brings S029E up large on the fourth "fine" (70.86), over all
four cells. `grid_picture` draws it as in s028, white frame included, from the rebuilt shot; the fourth cell doesn't pop, since
the centre lands on it. `fine_words()` counts words sung, not pictures: 5 in chant1, 4 here, so s029's tally is 1-4 with no
fifth numeral, centred in its column, and its FINE row stays four.

The word, its clay and its numeral now share one snapped time. Before, the numeral and the clay came a frame after the word.
That's in shared code, so s027 and s028 are re-rendered too.

Frames read from the mp4s: s029 at 70.80 (three cells, 3 lit), 70.84 (fourth word, 4 lit, centre up), 70.88 and the last, 71.24;
s027's last and s028's second. s027's last frame (67.64) has the centre up a frame before its fifth word, which lands in s028:
the spec's "a frame early", and it's across the cut. Left as it is.

## s029's fill (Lati's note, 1 Nov, replaces the centre above)

"okay, s029 need another pass, 5th screent was wrong move by me since that 5th "fine" is just "fi". I suggest that screens pop
in on "fine" as before, but 4th "fine" fills the the area, overlapping smaller screens fully, but staying in bounds what are
smaller screens outer edges." Kiln's spec: three cells and `fill` (S029D, 70.86). `grid_picture` puts the whole shot frame
into GX, GY, GW, GH on the fourth "fine", with the usual slam (1.1, settled in 0.12 s). `fine_words()` counts cells plus
centre or fill. s027 and s028 keep their centre and weren't re-rendered.

Measured from the mp4's pixels, 720p px, left / top / right / bottom: the small screens at 70.80 are 174 / 22 / 1105 / 547, and
the fill from 70.92 to the last frame is the same. At 70.84 and 70.88 it's still settling from the slam. Word, clay, numeral
4 and the fill all land on frame 70.84. Frames read: 70.80, 70.84, 70.88, 70.92, 70.96, 71.24.

## s062's tick (Lati's note, 1 Nov)

"otherwise good, but the checkmark above "every" is not like the others. it would be more symmetrical if that checkmark is left
of that word, like it is with "line"". EVERY's tick now sits left of the word, 49 units off its left edge like LINE's, at the same
height above its baseline and the same size. Same phone, same timing. To keep it clear of her, EVERY and LINE moved 40 units
right, and LINE's tick with them.

Checked per frame against her matte and the plane: after landing the tick stays at least 17 units clear of her, and EVERY's right
edge ends at 1896 of 1920. Frames read from the mp4: 153.88, 153.96, 154.04 (landed), 154.16, 154.32, 154.44 (last). In flight the
tick crosses the corner of the E, and LINE's crosses her, as before: only their landings changed.

## Accepted by Lati (1 Nov, through Kiln)

s023, s061, s064 (the FINE cards), s025, s052, s046, s047 and s060's flash, as they are. The walk with the crowd shot gone is what
he wanted. This settles questions 1 and 3 below.

## s048's new take (Lati, 1 Nov)

"option 1, reserved take works, since it also carries thematically over to s050, as if this was a montage of the concert." The picture is
`fit:s020-reroll2-beat`, arms wide, dancers in a V, no lip sync. New matte and a new `lock()` take: top and left end; the right end is out
of frame. Under her right arm, the scan panel, now landscape to hold her wide arms; under her left, BIG NOTHING / HIDING, then
NOTHING / BEHIND, on the words, in clay on the second. The band stays white, as s049 and s050 have it.

**Measured, every frame:** worst 8.0 by the audit (top, right half, at 110.96), 29.3 with all reads, left end 0.9. Against the lock's own
detector the plane is within 5.5 (one frame over 3 per edge). The two detectors disagree by up to 29 on 20 frames, which I take to be
the dancers' raised hands crossing the band's top; I haven't confirmed that. The camera rises 156 units and shifts 15; the band's
last frame reads 23 units lower on the right half on both detectors, unexplained, and the plane follows it.

**Base bug, Kiln, please:** `gfxrender.Film.picture` rounds `(T - at) * rate`. When `at` falls on a half frame, Python rounds to even, so
frames alternate repeat and skip (12.5 fps in stretches). Measured on every 25 fps shot: s017 and s018 (6 repeats each), s039 (19), s048 (19),
s049 (7), s058 (14). So part of the "held" counts in the audit above for s017, s018 and s049, and the old s048's 18, are this, not
the source. For s048 I worked round it in my own file: `_steady()` reads its frames from the file, and the matte (built with `at` set to
109.2 in a one-off script), `lock` and `audit` read the same frames. After a base fix: delete `_steady()` and the `at` line in
`__main__`, then rebuild the mattes of the shots listed and re-render them. s017 and s018 are approved, so that's your call with Lati.

Joins read from the mp4s: s047's last to s048's first, s048's last to s049's first, both clean cuts on the type.

## Questions for Kiln

1. **Does the lip sync hold on s025 and s052?** They're dance takes that sing the phrase, not lips fits. I gave them the
   verse voice. If it doesn't hold, they become BIG words: one line of code each. s020's second take I treated as not
   holding (cut-v3: "slide by eye").
2. **s043 and s046 say `[Y/n]` and `×64`.** The tile count is what's drawn on the far screen, though the camera has pushed
   past some of it by then.
3. **s023, s061, s064's cards are one word and a stamp for about 0.6 s**, her off screen. Lati may prefer the word over her.
4. Seam suggestion, your call: `flash 2` on s059 → s060, as on the first drop. It's the film's biggest hit and is `hard` now.

## Kiln, review (1 Nov)

- s018's one early frame fixed in `gfx_wall.py`: its times now sit on the 25 fps grid. s017 and s018 re-rendered; only that frame's wall position should change.
- `band()`, `big()` and the audits stay in the sections for now; lifted to the base only if a later round needs them.


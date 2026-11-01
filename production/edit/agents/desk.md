# Section C, the desk and the Q&A: s031-s042, 73.094-98.408

Claude (graphics agent C), 1 Nov 2026. First pass. Code: `production/tools/gfx_desk.py`. Renders: `media/gfx/desk/`.
Built to the corrected lyric rule (Lati, 1 Nov): nothing was built under the old one.

## Shots

All twelve are rendered at 720p. Together they run 633 frames, which is the section's span on the 25 fps grid.

| Shot | Picture | Graphics | Words on screen |
|---|---|---|---|
| s031 | S031, sung | his note arrives on the desk monitor on "bug" | whole line 20, verse voice, in the night sky |
| s032 | none, full frame | the diff: one line out, one in | "fix" |
| s033 | s033 Grok take | `> try it again` typed on the monitor, word by word on the sung words | "again" |
| s034 | none, full frame | the song's real sections, a playhead, the bridge gap counting down; `tests: 0` | "bridge", "code" |
| s035 | M035 | `tests: 0` card carried over | "test" |
| s036 | none, full frame | the real crash log pours in and comes loose on "mess"; swept clean to `1 passed` | "mess" |
| s037 | M037 | `1 passed · run by: you` on the monitor, tracked, behind her matte | "my best" |
| s038 | M038 | slide `Q&A · questions welcome`, tracked; `SPEAKER · self-assessed` by her badge | "ASK ME" |
| s039 | S039, sung | three answer cards land on "ask", "twice" and "say", with ≈ between them | end of line 24, then line 25 up to "the", verse voice in ink |
| s040 | none, full frame | the three cards, ≈ ≈, under the question | "SAME THING" |
| s041 | Lati's r5-4, the push | the counter on the slide, climbing on sixteenths, `illustrative` | "EVERY / BODY", "OKAY" |
| s042 | none, full frame | the counter outgrows its box; the slide breaks from 97.483, black from 97.937 with a cursor | "OKAY", "INSIDE—" |

Cuts: one inside the section, s037→s038 `whip 3`, the change of place from the night room to the hall. The rest are hard.
Seams: both set to `built`, Transition left as `hard`.

## Where the on-screen text comes from

| Text | Source |
|---|---|
| `s045 moves are... subpar.` | `decisions.md:890`, Lati, verbatim. Dated `11-01` on the monitor now (the `3 AM` stamp went in round 3) |
| the monitors in s031, s033, s037 | `production/decisions.md`, Lati's words, verbatim: see round 3 |
| the diff, `4794f15 · 1 Nov, 3:46 AM` | `production/edit/cut-v3.json` in that commit: the fix for that note, exactly one line out and one in. The context lines are the file's |
| song sections | `media/song/analysis/checked-me-v1/report.md` |
| `bridge: in 0:44` | computed from song time; true while the bridge stays at 123.64 |
| `tests: 0` | `find production -name 'test_*' -o -name '*_test.py' -o -name 'tests'` returns nothing, run 1 Nov. The screen shows the shorter `test_*` form |
| the log in s036 | `media/plates/desk-call.log`, the crash that lost the plates of s035 and s037. Lines naming the home folder are left out; the others are in order |
| “s002, works.” / `reviewed by: you` | `decisions.md:617`, Lati, cited on s036. Kiln's wording, replacing my `1 passed · run by: you` |
| the three answers | first film: pre-chorus and chorus (`~/Claudia/production/lyrics/v2.md`), and its description, point 2. Each card names its source |
| the question counter | invented, and marked `illustrative` on s041 and s042 |

Claim check for "Nobody knows whether there is anything it is like to be a model": read against
`https://github.com/wlkosonen/only-what-i-said/blob/main/production/release/description.md`, and against https://www.anthropic.com/research/exploring-model-welfare on
1 Nov, through a page summary. The page calls it "an open question" and says "no scientific consensus". "Nobody knows"
is the first film's plainer wording of that. See question 4.

## What I checked, and how

Frame checks only. I read JPEGs and I have not watched any of this move or heard it against the song.

- 26 check frames across the section at 1080p, then re-checks of the ones I changed.
- Crops of the monitors: s031 at two times, s033 at one, s037 at three. These showed the old taskbar and title bar peeking
  out, and I moved the quads. Re-cropped from the final renders (s031 frame 70; s037 frames 0, 22, 44): none of it shows now.
- The first and last frame of all twelve renders, plus frames 2-3 of s038 (the whip) and s033's opening prompt.
- s037's track (67 px of drift) was looked at on those three crops; s038's (16 px) on three frames. Neither was checked
  frame by frame, and both turned out to be wrong: see Round 2. At 85.8 her glove stays in front of the monitor.
- Faults the frames caught, now fixed: SAME and THING overlapping, OKAY off the left edge, the counter out of its box too
  early, EVERYBODY running behind her, the note cut off in s033, "1 passed" cut off in s037, the log's last lines clipped.
- A fault the frames missed: s033 crashed on its opening frames in the full render (see Base requests). Fixed.
- "The lip sync holds" on s031 and s039 is taken from the record, not from my eyes: neither has a note against it in
  `v3-notes.md`, `STATUS.md` or the marks files. The only mark in this section is s038's, and M038 answered it.

Not judged: timing, motion, how long the small cards in s039 stay readable, and whether "twice" in clay on yellow is strong
enough in motion. Those are Lati's.

## Choices that differ from the board

- **s032, s034, s036, s040, s042 have no picture in the cut** (`kind: none`, black), so there's nothing to set a quad on.
  They're full frame, in the room's flat colours, as s005 is, and as the board says ("full frame"). `gfx.screen()` is used
  on the real screens: s031, s033, s037 (monitors), s038, s041 (slides).
- **The + line in the diff is clay, not green; the − line is pink.** Green is only for a pass, and the board wants s036's to
  be the film's first green someone else ran. An unchecked fix shouldn't get there first. It's also her line.
- **`3 AM`, not `3:02 AM`, and his real note, not "it crashes when I click save".** Real beats invented here.
- **`bridge: in 0:44`, not `bridge: TODO`.** It counts down to the real bridge as the film plays, and pays off the plant.
- **The answers are real ones, so they carry sources and no `illustrative`.** Only the counter does.
- **`1 passed` lands on "I'll", at 85.298,** not 84.851 as on the board: "mess" now needs that beat.
- **The board's SO GO ON, MY BEST on s036 and IF I'M OKAY are gone or moved,** under the new rule and the new cut.
- **Voices:** the desk speaks in the big serif, deadpan. From EVERYBODY the Q&A climbs into hook caps, towards the drop.

## s041: does it need motion?

I've made the graphics carry it, and I don't think I should ask for motion on this evidence. His note says the same thing
conditionally: "s041 makes me think about motion too, but if graphics overlay is good then maybe its not necessary." The
counter ticks on sixteenths, EVERY/BODY lands, then OKAY, all on the slide behind a still woman, under the 3% push. Whether
that's enough is his call on `/cut`. If it isn't, it needs a new take, which I haven't tried to make.

## Questions for Kiln

1. **His note on screen.** s031 and s033 show Lati's own words about a take, and name s045. OK with him? It's the same
   record the bridge shows.
2. **s042's last half-second.** It's black with a cursor from 97.937 to the cut. The stems show vocal energy carrying on past
   97.4, though the aligned word ends at 97.38, and I can't hear which is right. If "inside—" really runs to the cut,
   Lati should say, and the break moves later.
3. **`1 passed` is my reading of a review verdict, not a test run.** `tests: 0` is true, so the only passing "test" here is his
   eye, which is the film's point. s036 cites the line, but s037's monitor doesn't, at that size. If that's too loose, I'd
   mark it `illustrative`.
4. **"Nobody knows" is a little stronger than the page it rests on,** which says no scientific consensus and "deeply uncertain".
   It's the released first film's sentence, verbatim. Keep it, or swap the third card for "Nobody knows" with a softer line?
5. **The web read.** I fetched that one page to do the claim check. The brief says no downloads, and I took that to mean files.

## Base requests

- `gfx.width("")` raises a TypeError (`glyph_positions` is None on an empty string). Guarded in my file; worth fixing in the base.
- `big()` (a big word in the verse voice, on its sung time) and `verse_on()` (`gfx.verse` in ink, for bright walls) are in
  `gfx_desk.py`. Other sections working to the new rule may want `big()`.
- `Canvas.layer` nesting with a translate works for the glitch, but it's slow; s040 rendered at 4.4 fps, probably because the
  render was sharing the CPU or because of the card shadows. Not looked into.

## Files outside my list

Written with the base's own tools, as `gfx.screen()` expects: `media/cache/gfx/matte-s037.mp4`, `matte-s041.mp4`. CPU runs;
the mattes took the render lock. `plane-s037.json` and `plane-s038.json` were mine too and are gone from the cache: see
below. If either comes back, s037's would apply on top of the measured quad.

## Round 2: s037, "text on monitor drifts and moves" (Lati, 86.98)

**Status:** fixed in the render and measured on every frame. Lati hasn't seen it yet, so whether the motion is right is
still his to say.

**Cause, measured. There were two faults, and the first frame checks could see neither.**

1. **The take is 16 fps; the graphic moved at 25.** On 16 of s037's 45 cut frames the picture is identical to the frame
   before. The old graphic still moved on those frames, 1.77 px on average and 2.33 at worst, so the text swam on a monitor
   that was standing still. Each still frame hides this.
2. **Flow had no points where the text was.** It held the real text at the top of the screen (within 3.5 px) but not my text
   lower down: 10.7 px off the monitor by frame 12, and it stayed about 9 px off. My quad was also wrong from frame 0: I'd
   put the right side out of frame at x=1990, and the screen's real right edge is on frame at about x=1905.

Kiln's suspicion was half right. Flow did not walk off the whole screen; the fault was uneven, and the stepping was a
separate cause that no choice of tracker would have fixed unless it stepped with the source.

**Fix.**

- **s037:** the quad is now a curve in `gfx_desk.py` (`q037`), with no flow and no file behind it. It comes from the
  monitor's top, left and bottom edges and its blue power light, found afresh in each frame, then fitted as a quartic in the
  take's own frames. It steps with the 16 fps source.
- **s038:** the same fault, unflagged. The old flow was run on the slide's right side only and extrapolated: Q&A was 13.5 px
  off and ASK ME 62.8 px off. The slide moves as one flat thing, 25 px down and 3.5 px left, so it's now one translation
  curve (`q038`). s038's file is 25 fps, so no stepping is needed.
- **s031, s033, s041:** no change, and no re-render. The audit says they were sound.

**Audit, every frame.** Drift is how far the graphic's edge moves against the real edge, about its median, in 1080p pixels.
The graphic's edge is read from what `gfx.screen` actually drew (a solid fill through the section's code), and the real edge
is found absolutely in each bare frame.

| Shot | Method | Frames | Worst drift, before | Worst drift, now | Static gap to the line measured |
|---|---|---|---|---|---|
| s031 | fixed quad | 91 | same | **0.44** | up to 12.0 |
| s033 | fixed quad | 45 | same | **0.35** | up to 24.9 |
| s037 | measured curve, stepped | 45 | 10.7 (text on monitor) | **2.60** (edges), **2.23** (real screen text) | up to 29.3 |
| s038 | translation curve | 45 | 13.5 Q&A, 62.8 ASK ME | **1.99** | up to 11.3 |
| s041 | analytic push | 45 | same | **1.85** | up to 3.4 |

- **Graphic motion on s037's 16 held frames:** 2.33 px before, **0.00 now.** Output before the kick, whole frame: 14 of the 16 are
  identical to the frame before, one changes by 1/255, and one by 7/255 on 20 pixels, centred on her glove's matte edge.
- **Independent checks:** s031 and s033 matched to frame 0 at their corners: worst 0.32 and 0.18 px. For s037, the real screen
  text unwarped through the quad stays within 2.23 px, against 3.52 for the old path. A smooth quad can't follow more than that
  if the generated text itself wobbles; that's my reading, not measured separately.
- **Held-out checks:** s037's right edge predicted at 1905, 1910, 1915 against 1905, 1910, 1917 read by eye. s038's three
  edges not used in the fit stay within 2.4 px.

**Limits of these numbers.**

- The static gap isn't an error figure on its own: the measured lines are the bezel's or title bar's, so it's mostly bezel
  width, and it doesn't move. The real screen's own edge is only checked by eye, on crops.
- Drift is partly measurement noise, about 0.5 px rms on these edges.
- s037's bottom edge: 1.50 px at the station with a real edge. Its left end has no measurable edge (band strength 5), so the
  7.05 in the raw audit output is that non-edge, not the graphic. It's unaudited there; the real taskbar text in that area is
  the check (within 2.23 px).
- s037's bottom and s041's top edges were readable on 42 and 39 of 45 frames; the other edges on all.
- s038's text and s041's graphic have no drawn edge of their own, so I audited the quad that carries them.
- The kick and cut pulse zoom picture and graphic together, after both are drawn, so they aren't in these numbers.
- The first measurement rounds gave wrong readings, which I threw out: edge-hopping on s031 and s033, spurious phase
  correlation, and a mask that read the whole frame as drawn. The "before" of 16.6 px by edges on s037 was inflated by the
  wrong quad; 10.7 is the fair figure.

**Left on purpose (overruled by Lati, round 3):** I left the real taskbar and title edge showing at s037's monitor edges. That was
wrong: see round 3.

**Also rendered:** s036, with s037 and s038. I wasn't sure the render had Kiln's wording; it does now. Kiln's text (“s002,
works.” / `reviewed by: you`) is kept, which closes question 3 above. Lati's yes on the s045 note closes question 1.

**For Agent A and the base.**

- Any tracked surface on a source that isn't 25 fps can swim this way. The only other one in the film is **s004, at 16 fps.**
- The quick test for any shot: find the cut frames whose picture equals the last one, and measure whether the graphic moved.
- Base request: `gfx.plane()` could take the source's frame, not song time, so stepping is handled once for everyone.

Measurement scripts are in my scratchpad, not the repo. Say if you want them lifted into a tool.

## Kiln, review (1 Nov)

- `1 passed` changed to Lati's own words, `“s002, works.”`, `reviewed by: you`: it wasn't a test run, and `tests: 0` stands four seconds earlier. Real text, and still the first green someone else gave.
- "Nobody knows…" stays: it's the released first film's wording, labelled with its source on the card.
- Your page read for the claim check was fine: "no downloads" meant files.
- `gfx.width("")` fixed in the base. For Lati: his s045 note on screen, and where "inside—" really ends.

## Round 3: the monitors (Lati, 1 Nov)

"s037: screen overlay is misaligned. at the bottom, original screen is peeking. For this shot perhaps we should make font smaller
and and graphics itself more "code-like" with more lines from when I approved this or that shot. similar idea to s031: smaller
font on monitor, more lines about what did not work, variety is preferred."

**Status:** rendered: s031, s033, s037, and s038, whose whip takes s037's last frame. Measured on every frame. Lati hasn't seen it.

**Cause of the misalignment: mine, twice over.**

- I set s037's frame-0 bottom-left corner by subtracting a guess from the bezel line: y=856. The screen's real bottom edge is at about
  y=893 there, so about 38 px of original screen was left uncovered at the left, tapering to nothing at the right.
- Round 2's audit couldn't catch it. It measured how much the graphic moved against an edge, never whether it reached the edge, and I
  called the constant gap "mostly bezel width". Then I saw the taskbar and wrote it off as "left on purpose". Both calls were wrong.

**The fit.** Each monitor's real inner screen edge, where blue-grey meets bezel, is measured on a lifted picture on every frame. Each
quad edge now sits just past it, so the overshoot lands on the bezel. s037's camera curve is unchanged; only its frame-0 corners moved.
s033's width is now true to the monitor, which leaves more of the log on frame, and its bottom no longer overshoots by about 15 px.

**Coverage audit, every frame.** Px at 1080p past the real screen edge, read from what `gfx.screen` actually drew; negative would mean
original screen showing.

| Shot | Frames | Top | Right | Bottom | Left | Screen-coloured pixels below the bottom edge, worst frame |
|---|---|---|---|---|---|---|
| s031 | 91 | +5.2 to +11.2 | +0.2 to +3.2 | +3.5 to +6.8 | +1.2 to +8.5 | **0** of 1800 |
| s033 | 45 | +4.0 to +5.5 | off frame | +2.2 to +13.0 | +1.2 to +5.0 | **0** of 1422 |
| s037 | 45 | +1.2 to +4.0 | +2.8 to +5.1 | +1.2 to +9.0 | +1.5 to +4.8 | **0** of 1800 |

- The last column is the direct test for what Lati saw: pixels of the real screen's blue-grey, in a strip 1-6 px below the graphic's
  bottom edge, along its length. Zero on every frame of all three shots. The power light is excluded by position.
- The 16 fps stepping from round 2 holds: 0.000 px of quad motion on s037's 16 held frames.
- **Crops I read, from the rendered files, lifted so dark detail shows:** the bottom edge of s031 and s033 at first and last frames; s037
  at frames 0, 22, 30, 44. No taskbar, no strip of original screen. Her glove stays in front in s037.

**Limits.**

- One s037 bottom reading was −9.2, at frame 3 near the left corner. That's on her glove: her matte is 1.0 there, and the glove is meant to
  be in front. It's the only negative reading.
- Those stations can't read everywhere: s037's bottom edge read at 122 of 225 stations, and s037's top at 207, s033's top and bottom at
  180. The bottom strip test covers those gaps along the bottom, and all frames. s037's right edge is measured only while it's on frame
  (frames 0-7), with a separate profile; after that it's out of the picture.
- s031's right edge has the thinnest margin, +0.2 px at worst. It's positive on every reading, but that's about the noise.
- My first ring test was invalid (it reached past the thin bezel onto the wall), and my first strip test counted the bezel's logo and her
  glove. Both are replaced; the numbers above are the colour-based strip.

**The content.** Small type, many rows, written down the page. It never scrolls, because Lati's last note was text moving on the monitor.

- **s031 (15 rows, `what did not work`):** rows arrive on sixteenths and `s045 moves are... subpar.` lands on its band on the sung "bug". The
  rest follow on eighths.
- **s033 (12 rows, the next page):** the note sits directly above `> try it again`, which types on the sung words in clay.
- **s037 (17 rows, `reviewed by: you`):** Kiln's wording is kept as the header. Green ticks and quotes; the page fills by "best".
  “s002, works.” is among them. s036 is unchanged.
- Sources: G1, S2V, Wan, the 2.5D failure, the cut notes, from 22 Oct to 1 Nov, so it's his whole record and not one complaint repeated.

**Nothing invented.** A script checks all 44 rows (43 distinct quotes) against `decisions.md`: each quote must be an exact run of his quoted
words, in an entry with that date. No misses. Limits of that check:

- Some quotes are cut short, always a verbatim run, marked by nothing but the closing quote.
- It proves the words and the date, not the shot label. Those I took by reading: `M002`, `S021`, `S049` from `notes.json`; `s073` for "last
  shot"; `s017` for "44-48s: superb.", which spans s017-s018; `clip 8` and the like are his own numbering.

**Legibility.** On the 720p render a row reads in close-up, and at full frame it reads as a mass, with the s045 band and `> try it again` standing
out. In s037 some glyphs break up at 720p: it's narrow, in perspective. I haven't checked a 1080p render, and whether it reads at a glance
in motion is Lati's call.

**For Kiln:** the drift audit in round 2 is not a fit audit. A surface can pass it while sitting in the wrong place. If Agent A's screens were
checked only for drift, the same gap could be there.

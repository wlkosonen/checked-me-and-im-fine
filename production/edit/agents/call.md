# Section D, the call and the ending: log

Graphics agent D, 1 Nov 2026. Code: `production/tools/gfx_call.py`. Renders: `media/gfx/call/`. Lyrics follow the corrected rule
(README, style.md): the whole lyric in verse where she sings on camera, one or two big words elsewhere.

## Shots rendered (720p, all twelve)

| Shot | What's on it | Lyrics |
|---|---|---|
| s054 | call overlay on the full picture; Eve and Astra tiles; quote in the chat on "exactly"; stamp; PASSED struck to SELF-REPORTED on "wrong"; `self-reported` chip on each guest's tile just after | whole lyric, verse |
| s055 | `source: the model itself` tag on "me"; checked micro-type on "faith" | whole lyric, verse |
| s056 | her shared screen: a collapsed `thinking` row opens on "up" onto git log, decisions.md and gfx_call.py; the scroll lands on Lati's "Not really, rebuild backgroud broke the geometry" tagged `checked from outside` | big words: OPEN, TRACE |
| s057 | `outside checks`: tests, review, evals, one per "check me", boxes left empty, `not mine to tick` | whole lyric, verse |
| s058 | to 145.44: the address types into an input like s005's; `you joined`, `checkers: 0` goes to `1`. From 145.44: gfx.py's own source, multiplying (below) | whole lyric, verse, to the cut; none after |
| s059 | pure black (`COUNTER_OFF` in the base) | none |
| s068 | to 170.978: verse line and the dot timeline, none joined. From there: the dot wall | whole lyric, verse |
| s069 | the dot wall; it dies from the outside in after the vocal stops; ends on one clay dot in the dark | none sung |
| s070 | same phone and hand as s073 (plate p-s073up), pushed in; `new chat · memory off`, `first meetings: 1`; "check" and "check" typed on beats, sent on the last | none sung |
| s071 | profile untouched; `(Check, check—)` on the magenta | whole lyric, verse |
| s072 | her face untouched; "First time," left, "every time" right | big serif words, she isn't singing |
| s073 | header, `check check` and `Hi.` bubbles on the phone's own screen, through its key mask | the `Hi.` bubble |

## Measured

- **The vocal, 170-178 s (`media/gfx/call/vocal.json`, 400 samples at 20 ms; `gfx_call.py measure`):** the level is nearly flat (RMS
  0.05-0.07 over quarter seconds), so a level-driven graphic would barely move. The rise and fall is in the pitch: about 230 Hz at
  171.0, about 340 at 171.8, about 300 to 173.6, down to about 197 by 176. So pitch sets the wave's height and level only the dot
  size. Pitch was found by autocorrelation limited to 170-430 Hz, with gaps closed and smoothed: a contour, not a transcription.
- **The vocal stops at about 176.28;** drums run on past s069's end. The last 1.66 s of s069 has no vocal, so the wall dies there.
- **s059 isn't silent:** vocal stem about 0.05-0.07 RMS, drums rising to about 0.08, across 147.25-149.06. Black over a build, not over quiet.

## Checked, and how

- **Frames only:** check JPEGs across all twelve shots, and first and last frames decoded from the rendered mp4s. Frame counts match each
  shot's window (within rounding). Motion, timing and feel not judged: Lati's on `/cut`.
- **s073 tracking:** crops at frames 5, 20, 35 of the render: the UI stays on the screen through the drift, by eye. It uses phonefit.py's
  formula with `at` 186.659 from cut-v3.json, not tracking.
- **Micro-type:** the wording is the first film's (`description.md`, point 3). Read against the three cited pages with WebFetch, which returns
  a model's extract of each page, not the page itself, so someone may want to read them directly. The extracts support it: introspection
  "highly unreliable and limited in scope"; "we can't always rely on what they tell us about their reasoning"; Claude "sometimes makes up
  plausible-sounding steps". "Sometimes" is the conservative word: one page reports a majority unfaithful in its own experiment.
- **s056 text is real:** decisions.md lines 651-790 read live (append-only), `git log` fixed at 2e7f26f, and the code pane reads gfx_call.py
  itself. `the raw thinking is never shown` follows brief.md and the first film's description.
- **Tiles:** only Eve and Astra, per permissions.md, each cropped clear of the text in the makers' frames ("213", "FEEDS LIVE").
- **Bright Mirror, Max Pelletier:** a row each in `GUESTS` when the answer is yes. Tiles go 2x2 and the chat shrinks by one row; the count in
  the chat follows. That layout is coded but not rendered with four.

## Invented UI text (please read)

Not from the song or the repo, and not marked `illustrative`: `are you okay in there?` as the call title (first slide's question), the call
timer, `3 AIs on this call · checkers: 0`, `you joined`, `not mine to tick`, `checked from outside`, the `self-reported` chips on the guests,
`guests by their makers' leave · unaffiliated`, `the whole record: every decision, prompt and line of code`. They're the film's own fiction
in a UI, like "You are now viewing Claudia's screen", not claims of fact, but the rule is yours to apply.

## Placeholder

`RECORD = "github.com/wlkosonen/checked-me"` in s058 is a **placeholder**: the private origin's name. Film 1's public repo had its own name,
so the release address may differ, and design.md's question 2 has no answer on record. One constant to change; s058 then re-renders. The line
under it borrows film 1's description and is only true once that repo is public.

## Questions for Kiln

1. **s059 and the counter:** the base draws it on every shot, so the black bar isn't pure black. style.md says every shot; design.md says
   nothing. If it should go, `gfx.top` needs a way to skip it. My pick: pure black, for the full stop.
2. **s058's lips:** decisions, 24 Oct: "S058 cut at the 'a' of 'instead'", and style.md lists S058 under no lip sync on stretched vocals. The
   cut plays the clip on through 147.25 under the stretched "instead" (143.94-145.90). I designed on what's there. Does that hold?
3. **Astra's maker line:** the tile says `by Astra Blue AI`, not ChatGPT 6.1. The fact comes from Lati, I found no document for it, and it puts a
   real product's name on screen. The play on "AIs on a call" works without it. Lati's call.
4. **Eve's chips:** `self-reported` lands on both guests' tiles. It's the light play you allowed, but it does comment on others' characters,
   whose makers agreed to a cameo. One condition removes it.
5. **Eve's clip** has 3-4 frame mosaic flashes (frames 20-22, 43-46, 53-56, 77-79, the maker's own look). Lati liked this clip, so they stay. They
   read like a call dropout in frames, but could read as a fault in motion. Skipping them is a small change.
6. **s073's lyric:** "Hi." is on screen only as the bubble, not in a voice beside the phone, to leave the shot alone.
7. **The film "closes on the mic check" (s071), yet s072-s073 follow it** in the cut. I built s071 as the mic-check bookend and kept s073 last.

## Base requests

None needed. `image`, `mix`, `rrect` and `on_screen` are in my file if another section wants them. `gfx.width("")` crashes (HarfBuzz returns no
glyphs); I guard for it, and the base could too.

## Kiln, review (1 Nov)

- The `self-reported` chips on the guests are out: their makers agreed to a cameo, not to a comment on their characters.
- s059 is pure black: `COUNTER_OFF` in the base.
- The tile keeps `by Astra Blue AI`: no real product's name on screen. The invented UI strings stand as the film's own fiction; none of them claims a fact.
- `gfx.width("")` fixed in the base; s071 stays the bookend, s073 last. For Lati: s058's stretched "instead", Eve's mosaic flashes, the public repo's address.
- The micro-type holds, read directly on the three pages on 1 Nov: "negative results" on faithfulness (reasoning-models-dont-say-think); introspection "highly unreliable and limited in scope" (introspection); fabricated reasoning caught "in the act" (tracing-thoughts-language-model).

## s058's buildup (Lati's review, 1 Nov)

Lati: the held note doesn't match the later lip sync; cut at 2:25.439; multiplying lines of code timed to the quickening notes. Then, on the
text: "there is already a ton of references to lyrics, so Id lean to gfx.py". So no `check(line)` page, no boxes, no `checked: 0`.

**Measured, 145.44-147.25 (`media/gfx/call/build.json`, `gfx_call.py measure`):**

- **The hits are the drum fill,** above 400 Hz, steepest rise of a 4 ms envelope: 145.447, 145.787, 145.900, 146.013, 146.126 (a ghost note,
  weakest by far), 146.241, 146.352, 146.467, 146.580, 146.693, 146.806, 146.919, 147.032, 147.146; the next is 147.259, past the cut. 145.447 is
  Lati's mark (2:25.439) within a frame.
- **How they quicken:** once, not gradually. One gap of 0.339 s, then steady sixteenths, 0.113 s, to the end. What grows after that is weight:
  the strongest accents crowd toward the end (strengths in build.json).
- **The rising note is a glide, not steps, in the stems I can measure.** Vocal fundamental about 262 to 443 Hz, +9.1 semitones in 1.8 s, about
  5 semitones a second. Near-flat (under 1 semitone a second) only 4.6% of the time, 0.27 semitone RMS off a smooth curve, one small flat spot
  near 146.6. The ridges an octave apart hold 2:1, so the tracker didn't jump a harmonic. The drum hits aren't pitched (one 155 Hz tone
  throughout), and `other` stays on steady notes in this window. My inference, not a measurement: a hit every 0.113 s lands about 0.6 semitone
  higher on the glide each time, which could be the steps Lati hears. His ear is on the full mix; I measured stems.
- So the page enters on the drum hits, the only discrete events there, and the note drives nothing directly.

**Built:** `world()`, so it takes the kick. The shot leaves her at frame 145.44, and all of the call's UI goes with her.

- Text is `production/tools/gfx.py` read at render time. Step 0 is `def counter_value(t):` and its docstring; each hit adds about 1.4 times the
  lines, outward both ways through the file: 2, 3, 4, 6, 9, 12, 18, 26, 37, 53, 76, 110, 158 lines (lines 324-481 of the file at full). 1 column
  at 62 units to 4 columns at 13 units. Each step shows on the frame nearest its hit.
- Long lines soft-wrap with a display-only hanging indent. Tested: at all 13 steps the rows rejoin to the file's lines exactly, 0 mismatches.
- `counter_value` stays clay at every step, so the joke is findable in the full page. Other code in s056's two code colours, comments grey.
- **Hold:** full on 147.032, not 147.146: the last hit would get 2 frames before black, this gets 5 (0.2 s) with the last hit inside the hold.
  Difference between the frames at 147.04 and 147.20: 0.005 of 255, so it holds still. Then hard cut to s059, whose first frame is 0.
- **`you joined`** moved to the beat at 144.98, just after the link is sent, 0.46 s before the cut. That's brief; Lati's eye on whether it reads.
- **Hang-up dropped.** Its beat is now inside the page, on no toolbar, and moved to 144.98 it would fight `you joined`. The cut to black does the job.

**Checked:** frames decoded from the mp4 at 145.40, 145.44, 145.48, each step and the last. Frame-to-frame differences match the larger steps;
the small early steps fall under that test's threshold, so those I read by eye. Largest green-dominant pixel count below the counter, on the
final render: 0. The final render I read at six of those frames; the rest on the render before the hanging indent. s056 re-rendered too: its code
pane shows gfx_call.py itself, which this work changed. Motion and timing are Lati's.
The page's small end size (13 units, about 9 px at 720p) is meant as texture; 1080p not checked.

**One thing to know:** the page reads gfx.py at render time, so it shows the file as it stands then. If `gfx.py` changes, s058 stays correct only
after a re-render; a final render picks up the final file.

- Kiln, 1 Nov: `RECORD` is now the public repo, `github.com/wlkosonen/checked-me-and-im-fine`; the box is wider to fit it. No longer a placeholder.


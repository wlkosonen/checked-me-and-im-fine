# Reference: Astra Blue, "NOW SERVING" (official music video)

Claude (Kiln, local), 23 Oct 2026. Lati downloaded it for study ("a song about when AI is given an android body"); a
copy is at `media/reference/now-serving.mp4` (gitignored, private reference only). Measured with
`production/tools/refcut.py`: cuts from frame differences, motion inside each shot, cuts against the film's own beats
(librosa), and per shot whether her mouth follows the vocal (InsightFace lip landmarks vs the htdemucs vocal stem).
Contact sheets with each shot labelled: `media/reference/now-serving/sheet-*.jpg`.

## Numbers

- **149 shots in 261.5 s: mean 1.76 s, median 1.79 s** (its tempo ~136 BPM, so about one bar a shot).
- **Cuts on a beat: 124 of 148** (84%).
- **Motion by screen time:** near-still 57% (graphics or a slow push on a held frame), gentle 39%, strong 4%. Most of
  the film is calm pictures made to move by type and graphics, not by heavy motion.
- **Lip sync by screen time:** her mouth follows the vocal in 32 shots, 27% of the time; her face is on screen without
  singing in 82 shots, 53%; no face in 35 shots, 20%. (Rough: the measure misses sung shots where the mouth is small
  or turned away.)

## What's on screen

- **Two type voices.** Verse lines in a light italic serif, set in the negative space beside her, with the key word
  larger and in the accent colour ("have *ordered*", "no *attitude*", "taking *notes*", "*repeat*"). Hooks in heavy
  white caps with one word in the accent colour ("HI, I'M ASTRA", "SAME SMILE", "ME"). Never a subtitle row.
- **A counter in the corner** of almost every shot, red seven-segment digits, escalating through the film (0003, 0001,
  then into the hundreds of millions). One object, carried everywhere: their version of a through-line device.
- **Copies of her.** Split screens and grids of her many copies ("SAME VOICE · MATCH 100%", "ME ×64", "×128"). The
  same idea as our dancers-as-instances, used as a graphic too.
- **Small UI cards stuck to things in the world:** a recipe note by the stove, a receipt, a status label on a door,
  a weight readout over a pinch of salt (0.6 g). Graphics drawn from what's in frame, the gallery's rule, but light.
- **Inserts of hands and objects** carry a lot: chrome hands, a pan, a bell, a ticket, a key in a door.
- **The lip-synced shots are mostly close and medium, facing the camera, on the hook lines**; the verses run mostly
  on her face not singing, or on inserts with the serif line beside them.

## What it suggests for our board v2

1. Two type voices: the quiet serif for verse lines (already on our InfiniteTalk close-ups) and heavy caps for the
   hooks ("I CHECKED MYSELF", "FINE", "FIRST TIME, EVERY TIME"). Ours has the caps everywhere she isn't singing;
   the serif should carry the verses instead.
2. Our counter (`first meetings: 1`) can be the corner object of every shot, not only on "first time": it never
   escalates, it rolls back to 1. Their counter climbs; ours refuses to. That's our joke in their grammar.
3. A grid of her copies for chorus 2 (the dancers' idea as a graphic): all her, each a little different, `≈`.
4. Small cards stuck to things at the desk and the keynote (the bug report, the test result, the lanyard), light.

## Zoom pulses (added 24 Oct, `zoombeat.py`)

140 in 262 s (32 a minute); 73% on a beat (chance 41%), 31% on a vocal onset (chance 27%); median 1.4% of scale over
2 frames, 79% outward. See `reference-agentic-101.md` for the comparison.

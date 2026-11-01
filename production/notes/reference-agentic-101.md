# Reference: Javi, "Agentic Engineering 101 – Slopcore edition"

Claude (Kiln, local), 24 Oct 2026. Lati: "its got a lot of stills but, the song itself goes so hard and graphics feed
into that so that one isnt even left wanting them … Notice slight zooms to the beat and vocals." (The description
advertises a course; we study the film's grammar, not its claims.) Copy at `media/reference/agentic-101.mp4`
(gitignored). Measured with `refcut.py` and the new `zoombeat.py`; sheets in `media/reference/agentic-101/`.

It is a Claudia film too (the open character: black bob, clay streak, star clip), and its accent is our clay.

## Numbers

- **147 shots in 271 s: median 1.71 s**, ~136 BPM. Bimodal: 59 shots under a second, 40 of 3 s or more.
- **Cuts on a beat: 86 of 146 (59%).**
- **Motion: near-still 73% of screen time**, gentle 24%, strong 3%. Stiller than NOW SERVING (57%).
- **Lip sync: about 7% of screen time** (8 shots; rough). Her face is on screen without singing 76% of the time.
- **Zoom pulses (`zoombeat.py`): 124 in 271 s, 27 a minute.** 70% land on a beat (chance alone: 41%); 39% on a
  vocal onset (chance: 38%, so no more than chance). Small and quick: median 1% of scale, 1 frame, 63% inward.
- **Control, NOW SERVING:** 140 pulses, 32 a minute, 73% on a beat (chance 41%), 31% on a vocal onset (chance 27%);
  median 1.4%, 2 frames, 79% outward (a punch in on the cut, easing out).

So Lati's ear is right about the beat: both films kick the frame by about 1% on the beat, about every other beat,
and it's a big part of why 60-70% stills don't feel still. The pull to the vocal is weaker than it looks by eye:
vocal onsets are so dense in a pop song that a beat-locked pulse lands on one by chance a third of the time. Where a
word and a beat coincide, the pulse reads as both.

## What's on screen

- **A lower-third line on almost every shot:** the sung words in small white caps, the last word in clay ("FINAL CALL
  IS *MINE*", "RED TESTS FIRST. *EVIDENCE*."). A lyric track, quietly, in every shot.
- **Hooks in huge condensed caps** over the image, one word in clay ("LET *THEM*", "BE THE *GOAT*").
- **Counting copies of her:** "TEN" over a grid of her, "A HUNDRED" over a finer grid, "A THOUSAND STRONG" over a
  mosaic, each on its beat. The same idea as our dancers and NOW SERVING's ×64.
- **A small HUD card in a corner** of most shots (a status, a counter, a checklist), drawn from what the line says.
- **Props that are the lyric:** a quill for "if it can't check its own", a keyboard with NO TYPING ALLOWED, keys
  dissolving into particles, goats for "go farm goats". Literal, fast, funny.

## What it suggests for us

1. **A beat kick on every still and slow shot:** about 1% scale in on the beat, every other beat, 1-2 frames, easing
   back. Cheap in the edit, no GPU. Plan B and the stage fallback lean on stills and dancing; this is what keeps them
   alive. Add it to the edit tool as a default, with Lati's eye on the amount.
2. **Our verse serif line could sit on every shot that isn't a hook**, like their lower third, so the lyrics are
   always there. We have the serif voice; this says use it everywhere, small.
3. **The counting grid fits our chorus 2** (the ≈ dancers): but ours doesn't climb. "first meetings: 1" over one of
   her, then over a grid of her, still 1. Their count escalates; ours refuses to.
4. Their film carries 73% stills on a hard song. Ours can carry more stills than board v2.1 has, if the graphics land
   on the beat; that's plan B's case, measured.

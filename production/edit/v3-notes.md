# Rough cut v3: Lati's notes of 1 Nov, triaged

Claude (Kiln, local), 1 Nov 2026. His words are in `decisions.md` and `review/marks/cut.json`. Measured: frames of
the built shots (frozen spans over 0.3 s), fit sidecars (`media/clips/fit/*.json`), stems. Not judged by eye in motion.

## Wiring: clips exist, no render

| Shot | Note | Do |
|---|---|---|
| s008 | two stills kill the motion | M008 (not wired, "bit different face ... would work") |
| s038 | prefers a motion shot | M038 (not wired, "works") |
| s062 | two stills in a row | M062 (not wired); take its first 1.8 s: before the blue lift and the face drift |
| s041 | (keeps r5-4) | his r5-4; it plays the still now |
| s011 | rule at s016 | Grok dance out: M011 walk (Lati hasn't seen it) |
| s013 | "walk would fit better" | M014: concert stage, dancers behind, she comes toward us (Lati hasn't seen it) |

## Timing: takes we have, no render

| Shot | Note | Measured | Do |
|---|---|---|---|
| s018 | needs motion | frozen 45.90-47.18: its take starts at 47.19 ("green") | s017's fit runs on (it covers 44.04-53.66), s018's take starts at 47.19 |
| s019 | needs motion | still | s018's take runs on to 49.53 (its lips match "green lights on every line", not the rest) |
| s020 | motion starts too late | frozen 49.53-50.41: take starts at "nothing" | back to s017's wide 49.53-50.41, s020 from 50.41 |
| s045 | (not flagged, same fault) | frozen 103.81-105.57 | same fix: s044's take runs on if long enough, s045's take from 105.72 |
| s046 | too many stills | still | s045's lips take runs on to 107.42 |
| s047 | too many stills | still | chorus 1's s020 with the 57.89 s offset, same words; flip it, or s020-reroll2 |
| s048 | too many stills | still | s023 take 3's spin, lips closed, or S021's matching words |
| s061 | two stills in a row | still | s060's take runs on (covers to 154.13), FINE card on "fine" |
| s051 | motion stops before the "hey"s | drums stop at 116.9, beat 116.89 | hold her from 116.89 to s052 at 118.24; a small punch on each "hey" |
| s027, s029 | "fine" frames play until the mouth closes | cells hold at word end + 0.1 s | measure mouth closure per cell, extend |
| s005 | graphics from 14.73 | decided | M041 to 14.73, placeholder card to 16.75 |

## New material

| Shot | Note | Do |
|---|---|---|
| s054, s055 | Teams UI, other AI avatars | code graphics: a generic call UI, no Microsoft marks; fan-made avatars of the other AIs, unaffiliated, makers credited; which ones is open |
| s069 | sustained vocal, pure graphics | graphics, driven by the vocal's own envelope; depth parallax dropped here |
| s073 | on a phone held up by a hand | Krea plate of a hand holding a phone, S073 corner-pinned on the screen, keeps the lip sync |

## Done in cut-v3.json (1 Nov)

Built: s005, s008, s009, s011, s013, s015, s018, s019, s020, s027, s029, s038, s041, s045, s046, s047, s048, s051, s061,
s062, s069. Confirmed by Lati: s013, the s016 rule, s014 stays and runs on over s015. Still to make: the graphics (s005,
s069), the call overlay (s054-s055, fan-made avatars of the other AIs, not invented ones), the s073 phone plate.

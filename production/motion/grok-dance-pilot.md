# Dance pilot, route 1: Grok farming

Claude (Kiln, local), 22 Oct 2026. The question: can Grok Imagine give us dancing that lands on the song's beat
(~133 BPM, steps on every beat; Lati, 22 Oct), with her face holding and the dancers moving together? One test per
plate first, then farm the one that works.

What the first film taught about Grok (`~/Claudia/production/decisions.md`, 19–20 Oct, and `notes/lessons.md`):

- Lati's plan gives 720p. Grok's audio can't be ours, so discard it.
- The plate must contain every canon item (streak, star clip, mic), or Grok invents them, and asking it to keep a
  missing clip makes it draw one in. In wides, her face is small: re-face the plate in the Grok agent from a good close
  plate first, and check it.
- Short prompts drift less. Give the tempo in BPM.
- A take more than ~1.2× off our pace reads as sped up, whatever we do. Inside that, we retime to the beat.

## Plates (`production/images/pilot-dance.json`, Krea 2 Turbo + LoRA 0.75, six seeds each)

- `pd-wide`: full length, centre stage, four silhouette dancers in a V behind her, haze, crowd hands and phones at the
  bottom. The formation test.
- `pd-waist`: waist up, at her eye level, two dancers out of focus behind. Her own dance (upper body), and whether her
  face holds while she moves.
- `pd-medium`, `-medium2`, `-medium3`: knees up, slightly from below (Lati, 22 Oct: "_barely_ low angle … not
  something to worry about"). Better for a dance test than waist-up: hips and steps show. Watch the skirt's swing in
  the takes.
- `pd-close`: the face reference for re-facing the wide.

Picked plates go to `media/plates/picked/`.

## Prompts

Paste the accuracy block after each prompt, identical every time.

**Accuracy block:**

```prompt
Keep her face, her black bob and bangs, the single thin clay-orange streak, the small clay-orange star clip, the thin headset microphone and her clothes exactly as in the image in every frame. Keep the stage, the lighting and the fine film grain as in the image. Photoreal live-action 35mm concert footage, natural human motion. Her lips stay softly together, silent.
```

### G1, the formation (`pd-wide`)

```prompt
Upbeat pop concert at 133 BPM. She and the four backing dancers dance the same sharp choreography in perfect unison, every step and arm move on the beat. Stage lights pulse on the beat. The camera pushes in slowly from the crowd.
```

### G2, her dance (`pd-waist` or a knees-up `pd-medium*`)

```prompt
Upbeat pop at 133 BPM. She dances with sharp, playful moves on every beat: shoulder hits, head and arm accents, one arm sweeping up and down. The camera is steady at her chest height.
```

## How we run it

1. Lati picks a `pd-wide2` and a G2 plate (`pd-waist` or knees-up `pd-medium*`) from the contact sheets (and a `pd-close` for the
   re-face). If the wide's face isn't her, he re-faces it in the Grok agent from the close plate.
2. **Six takes for G1** (one plate); **one or two per G2 plate** (seven plates, so 7–14 takes): across plates we learn
   more than from repeats. Save the originals unedited as `media/clips/grok/g1-take<n>.mp4` and
   `g2-s<seed>-take<n>.mp4` (the seed from the plate's file name).
3. Claude (local): for each take, measure the dance's own tempo and phase from the motion, how far it is from 133, and
   (for G1) whether the dancers move together. Then contact sheets for identity and invented details.
4. Lati watches the motion on the monitor. That's the check: a measured beat isn't a danced beat.
5. The best take, retimed to the grid, goes on the beat under chorus 1 for Lati's eye. If it holds, farm more; if it
   doesn't, route 2 (pose-driven) carries the dance. Route 2 can also use a good Grok dancer as its reference motion.

No spend: Grok is in Lati's subscription.

## Round 1 (22 Oct): 6 × G1, 7 × G2, one take per plate

Lati's G2 files are numbered by plate, matched by first frame: s1 `pd-medium2` s222533528, s2 `pd-medium2` s1051538399,
s3 `pd-medium3` s643305775, s4 `pd-medium3` s931956797, s5 `pd-medium` s902073595, s6 `pd-medium3` s1144522535, s7
`pd-medium2` s1130062814. Takes are 6 s (g1 take 1: 10 s), 1264×720, 24 fps, with Grok's own music.

What the measurements say (rough: 6 s is about 13 beats):

- **Grok writes its own music near the asked tempo** (librosa: 116–155 BPM, most 124–136), and its dancers move to it:
  motion changes come 1.2–1.65× more often near its beats than elsewhere. So a take's beat grid is read from its own
  audio (`beatfit.py`), which is far steadier than reading tempo off the motion (`dancebeat.py`, which mostly folded
  to half or double time on clips this short).
- Retimed onto ours, every take needs one even speed between 0.85 and 1.14, all inside the ~1.2 limit.
- G1 formation, dancers together (`dancebeat.py` strip correlation): take 4 0.73, take 6 0.66, take 1 0.58; take 5 0.13.
  Take 4 also hits Grok's beat with no offset (1.47×).
- Contact sheets (`production/images/sheets/grok-g1.jpg`, `grok-g2.jpg`): her look holds at this size; most G1 takes
  jump between 0 and 1 s (the backdrop changes, the camera moves in); G2 s5 barely dances.

Preview: `media/clips/preview/grok-pilot-reel.mp4`: every take retimed onto our beat, landing on chorus 1's downbeat
(0:44.10), with our song and a white dot flashing on our beats. Nearest-frame retiming, so not final quality.

## Round 2: make a kept take sing (Grok video-to-video, 22 Oct)

Lati: on stage "it would read a bit weird if she mostly does not sing". So: edit a kept take in Grok's agent
(video-to-video) with the chorus words at their times **in the take's own clock**. `beatfit.py` later speeds the take by
one even factor and lands it on chorus 1's downbeat; the times below are our vocal's words mapped back through that
same placement, so after the retime the mouth lands on our words. The tempo given is the take's own (its music), so
the mouth moves at the pace the dance already has.

Test clip: **g2-s3-take1** (the hair swoosh). Alternative if the first doesn't hold: g2-s1-take1. Two edits each.

### g2-s3-take1 (its own tempo ~124 BPM)

```prompt
Keep this video exactly as it is: her dance, every move, the camera, the stage, the lighting and the timing. Change only her mouth: at 124 BPM she sings into her headset microphone, word by word on this timing: "I" at 0.7 s, "checked" at 0.9 s, "myself" at 1.2 s, "and" at 1.7 s, "I'm" at 2.0 s, "fine" at 2.1 s, "I'm" at 2.7 s, "fine" at 3.3 s, "green" at 4.0 s, "lights" at 4.7 s, "on" at 5.1 s, "every" at 5.6 s. She sings out with energy, her mouth opening clearly on each vowel and her lips shaping every word on that timing. Before the first word her lips are together.
```

### g2-s1-take1 (its own tempo ~148 BPM)

```prompt
Keep this video exactly as it is: her dance, every move, the camera, the stage, the lighting and the timing. Change only her mouth: at 148 BPM she sings into her headset microphone, word by word on this timing: "I" at 0.6 s, "checked" at 0.8 s, "myself" at 1.0 s, "and" at 1.5 s, "I'm" at 1.7 s, "fine" at 1.8 s, "I'm" at 2.3 s, "fine" at 2.8 s, "green" at 3.3 s, "lights" at 3.9 s, "on" at 4.3 s, "every" at 4.7 s, "line" at 5.2 s, "every" at 5.8 s. She sings out with energy, her mouth opening clearly on each vowel and her lips shaping every word on that timing. Before the first word her lips are together.
```

Save as `media/clips/grok/g2-s3-sing-take<n>.mp4` and `g2-s1-sing-take<n>.mp4`. Claude then checks: did the dance
survive the edit (same moves, same timing; if Grok re-timed it, its new music gives the new grid); are the mouths on
our words after the retime (Whisper on Grok's sung audio, word by word against ours); does her face hold.

### Round 2 results (22 Oct)

Lati: "some drift in poses I think? the imagine ui is atrocious, its getting hard to keep track which file is which.
video-to-video works only in the interface itself, for the clips that are in there. no uploading it seems."

- Two edits came back, `g2-s3-sing-take1` and `g2-s1-sing-take1` (1280×720, 6 s), each matched to its source by
  first frame.
- **The dance is not kept.** Grok's agent says the source frames were "pinned" and only the mouth changed. Measured
  frame by frame against the source, both differ from the first second on (mean difference 15–36 grey levels; another
  plate is ~48). The poses drift, as Lati saw: video-to-video is a new take seeded by the old one, not a mouth edit.
- **The words came out right and near the asked times.** Whisper on s3: every word in order, within ~0.1–0.4 s of
  the prompt. s1: the same words, but "I'm fine … green lights on every" packed tighter than ours.
- Grok's new music: s3 ~121 BPM (beat fit x1.09); s1 ~104 (too far for a beat fit; the words set its timing).
- `beatfit.py --lips` warps a sung take word by word onto our vocal (Whisper anchors, PCHIP, local speed held to
  0.75–1.33). s3: 7 words anchored, speed 0.88–1.33. s1: only 4 (the packed middle would need >1.33).
- Reel: `media/clips/preview/grok-sing-reel.mp4`: s3 source on the beat, s3-sing on the beat, s3-sing lip-warped,
  s1-sing lip-warped.

Lati, 22 Oct: "lipsync in those is not natural. looks wrong. … less is more with grok. animation from plate, with
dance and words sung prompt is what to try next." The warp stays a tool for small fixes only.

## Round 3: dance and sing from the plate (22 Oct)

One short prompt: the tempo (ours, 132), the line with each word at its time **in our song's clock**, counted from
0.5 s before the first word. If Grok keeps to it, the take's beat fit is ~1.0 and the mouth is already on our words.
No accuracy block beyond one line (less is more).

**Line A**, chorus 1, 0:43.84 on (`I checked myself and I'm fine (I'm fine!) / Green lights on every line`):

```prompt
Upbeat pop concert at 132 BPM. She dances to the beat and sings into her headset microphone, word by word on this timing: "I" at 0.5 s, "checked" at 0.7 s, "myself" at 0.9 s, "and" at 1.5 s, "I'm" at 1.7 s, "fine" at 1.8 s, "I'm" at 2.4 s, "fine" at 2.9 s, "green" at 3.6 s, "lights" at 4.2 s, "on" at 4.6 s, "every" at 5.1 s, "line" at 5.6 s. She sings out with energy, her mouth clearly shaping each word. Keep her face, hair, streak, star clip, headset microphone and clothes as in the image.
```

**Line B**, chorus 1, 0:50.54 on (`Nothing hiding, nothing behind / I checked myself and I'm fine!`):

```prompt
Upbeat pop concert at 132 BPM. She dances to the beat and sings into her headset microphone, word by word on this timing: "nothing" at 0.5 s, "hiding" at 1.1 s, "nothing" at 1.8 s, "behind" at 2.0 s, "I" at 2.6 s, "checked" at 3.0 s, "myself" at 3.2 s, "and" at 3.6 s, "I'm" at 4.0 s, "fine" at 4.5 s. She sings out with energy, her mouth clearly shaping each word. Keep her face, hair, streak, star clip, headset microphone and clothes as in the image.
```

Runs, one take each: line A on G2 plates s1, s3, s5; line B on s6, s2 and the wide (`pd-wide2` s321513750). File
names don't matter: Claude identifies each take by its first frame and which line Whisper hears.

### Round 3 results (23 Oct)

Lati added a gate to the prompt, "gate: if subtitles on screen, redo", because Grok kept adding subtitles. Seven takes,
identified by first frame (Lati's names in brackets): line A on `pd-medium2` s222533528 ["s3"] and `pd-medium3`
s931956797 ["s5"]; line B on `pd-medium2` s1051538399 ["s2"], `pd-medium3` s1144522535 (two: "s6-round3",
"s6-take2") and the wide (two).

Whisper on each take's own singing, matched to our words at their prompted times (take minus ours, s; Whisper's own
error on singing is about ±0.1):

| take | line | our words matched | timing |
|---|---|---|---|
| g2-s3-round3-take1 | A | 8 of 13 | myself −0.14, I'm −0.16, fine −0.02, fine −0.26, green −0.04, lights +0.44, every −0.12, line −0.26 |
| g2-s6-take2 | B | 6 of 10 | hiding −0.20, behind −0.36, check −0.28, myself 0.00, and +0.18, fine −0.01 |
| g1-round3-take2 | B | 5 of 10 | burned-in subtitles ("nothing", "I"): out |
| g1-round3-take1 | B | 4 of 10 | behind −0.42 |
| g2-s2-round3-take1 | B | 4 of 10 | the backing dancers turn into lit women with faces: out |
| g2-s5-round3-take1 | A | 6 of 13 | 1.0–1.7 s late through the middle |
| g2-s6-round3-take1 | B | 2 of 10 | |

- Every line-B take drops the second "nothing" and sings "behind" ~0.4 s early; "I checked myself" comes out mangled
  in most. Long lines are where Grok loses words.
- A shot in the edit is 2–3 s, so a take doesn't have to sing all 6 s right: it needs one window where 4–6 words land.
  `g2-s3-round3-take1` has one ("myself … I'm fine … fine … green", 0:44.8–0:47.4).
- Reel: `media/clips/preview/grok-round3-reel.mp4`, each take exactly as prompted (no retime) under our song.

Next (round 4): one short phrase per take (4–6 words), Lati's subtitle gate, "the backing dancers stay dark
silhouettes", and farm several takes per phrase.

## Round 4: one short phrase per take (23 Oct)

Each phrase starts at 0.5 s; the times are our vocal's (song clock), the tempo ours. After the phrase she keeps
dancing with her lips together, so the take's remaining seconds are a dance shot. Lati's gate goes in every prompt.

Template (swap in the phrase line):

```prompt
Upbeat pop concert at 132 BPM. She dances to the beat and sings into her headset microphone, word by word on this timing: PHRASE. She sings out with energy, her mouth clearly shaping each word, then keeps dancing with her lips together. The backing dancers stay dark silhouettes. Keep her face, hair, streak, star clip, headset microphone and clothes as in the image. Gate: if subtitles on screen, redo.
```

| phrase | song time | PHRASE |
|---|---|---|
| P1 | 0:43.84 | "I" at 0.5 s, "checked" at 0.7 s, "myself" at 0.9 s, "and" at 1.5 s, "I'm" at 1.7 s, "fine" at 1.8 s |
| P2 | 0:46.92 | "green" at 0.5 s, "lights" at 1.2 s, "on" at 1.5 s, "every" at 2.0 s, "line" at 2.6 s |
| P3 | 0:50.54 | "nothing" at 0.5 s, "hiding" at 1.1 s, "nothing" at 1.8 s, "behind" at 2.0 s |
| P4 | 0:56.48 | "first" at 0.5 s, "time" at 0.8 s, "every" at 1.3 s, "time" at 1.7 s |

Runs: each phrase on two or three G2 plates (s222533528 and s1144522535 held best), one take each; then more of
whichever phrase lands. The wide only for P4 (its face is too small for the mouth to matter much).

### Round 4 results (23 Oct)

Lati: "p3 was the most problematic, grok didnt want to do whole phrase, only two first words, and after iterating it
drifts. but some good dance moves there. … Gate works, no burned subtitles in generations."

Short phrases work. Whisper on each take, matched to our words; each take then slid by one constant offset (the median
of its word errors; no speed change), residuals after the slide:

| take | phrase | plate | offset | worst residual |
|---|---|---|---|---|
| g2-p1-take2 | P1 | `pd-medium2` s222533528 | −0.10 | 0.06 (all 5 words) |
| g2-p2 | P2 | `pd-medium2` s1051538399 | −0.28 | 0.10 |
| g1-p4-take2 | P4 | wide | +0.18 | 0.12 |
| g2-p2-plate35 | P2 | `pd-medium3` s1144522535 | −0.31 | 0.17 |
| g2-p1 | P1 | `pd-medium2` s222533528 | −0.34 | 0.20 |
| g1-p4-take3, -take4 | P4 | wide | 0.00, −0.28 | 0.24 |
| g2-p3-take1–4 | P3 | `pd-medium2` s222533528 | | only "nothing hiding" (take 4 adds "behind") |

- With one phrase per take, Grok sings every word in P1, P2 and P4, and P1 take 2 lands within 0.06 s of our vocal
  after the slide. That's lip sync, not luck.
- P3 ("nothing hiding, nothing behind") won't come whole: Grok sings two words and stops. Next: split it into two
  phrases ("nothing hiding" / "nothing behind").
- Reel: `media/clips/preview/grok-round4-reel.mp4`, each take at its fitted offset under our song, best first.

## InfiniteTalk video-to-video on a Grok take (23 Oct)

Lati: "go ahead with the infinitetalk test on p3 take1." `production/tools/itdub.py` (prep / run / paste):
kijai's ComfyUI-WanVideoWrapper (088128b, installed 23 Oct with torch pinned; our InfiniteTalk and wav2vec2 files are
byte-identical to kijai's, linked in), V2V graph after his example 02: Wan 2.1 I2V 480p fp8 + InfiniteTalk single +
lightx2v, 4 steps from step 2 on the source latents, sdpa, 30 blocks swapped, **tiled VAE** (untiled, the VAE's 3D
convolutions asked for 7.7 GB with MIOpen off and stopped cleanly; same lesson as SeedVR2). An 832×480 window tracked
on her head (face ~140 px, native scale) is dubbed with our vocal stem (0:50.44 on), and only her head goes back into
the 720p take through a soft ellipse. 151 frames in 12.5 min; no GPU faults.

Previews: `media/clips/preview/g2-p3-take1-it.mp4` (composited, our song) and `-it-crop.mp4` (source | InfiniteTalk).
From stills: her mouth now moves with the line, but her face drifts toward the model's default (rounder, younger;
the star clip comes and goes inside the window), as InfiniteTalk did in the first film. Lati's eye decides.

Lati, 23 Oct: "face drifts and artifacts" (worst frame: her face drifted, and a ghost of her hair around the pasted
head, where InfiniteTalk had moved her head away from Grok's). Out. The pilot's answer: **short-phrase Grok takes for
sung stage shots**, slid onto our vocal, cut to the words that land.

P3 split, for the next batch (same template as round 4):

| phrase | song time | PHRASE |
|---|---|---|
| P3a | 0:50.54 | "nothing" at 0.5 s, "hiding" at 1.1 s |
| P3b | 0:51.76 | "nothing" at 0.5 s, "behind" at 0.8 s |

## Wan 2.2 S2V: lip sync and dance in one pass (23 Oct)

Lati: "go ahead with the S2V test". `production/tools/s2v.py` (prep / run / finish), ComfyUI's native
WanSoundImageToVideo after its own template: S2V 14B fp8 + Wan 2.2 lightx2v 4-step LoRA, 4 steps, CFG 1, shift 8;
ref = the plate of g2-p1-take2 (`pd-medium2` s222533528) at 832×480; audio = our vocal stem, 0:43.74–0:48.55; control
video = her pose from g2-p1-take2's own dance (DWPose wholebody by rtmlib on the CPU, her skeleton only, no face
points, OpenPose colours). 77 frames at 16 fps in 11.3 min; ComfyUI's VAE encode ran out of memory once and retried
tiled by itself; no GPU faults.

Previews: `media/clips/preview/s2v-p1.mp4` (our song under it, 16 fps) and `s2v-p1-pose.mp4` (with the pose beside).
From stills: she follows the pose, her mouth opens on the words, the dancers stay in the background; her face is small
at 480p and the first frames look slightly off (a redder face). Motion and lip sync are Lati's call.

S2V at full quality (23 Oct): no speed LoRA, 20 steps, CFG 6, otherwise the same inputs; 77 frames in 79 min (the model
only half fits the card at this setting). Previews: `media/clips/preview/s2v-p1-full.mp4` and `-full-pose.mp4`, for
Lati's eye on whether the mouth now follows the words.

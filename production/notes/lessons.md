# Lessons from *Only What I Said*

**Split on 24 Oct 2026:** machine and tool rules → `~/workshop/workshop.md`; methods and verdicts → `~/workshop/methods.md`; this film's creative rules → `production/style.md`. Kept here as the record; add new
lessons there, not here.

Claude (Kiln, local), 22 Oct 2026, the day it was released. Rules the first film earned, each from something that went
wrong or right. The full story is in `~/Claudia/production/decisions.md`.

## Working together

- **Lati's eye on a monitor is the check.** Contact sheets and stills miss motion, flicker, a mouth a syllable late,
  a blink. Phone viewing missed things the monitor showed. Review section by section; send a preview, wait for notes.
- **Read the record back before drawing from it.** A correction logged on 19 Oct was repeated in a graphic on 21 Oct.
- **Say limits plainly; propose, then decide together.** Lati corrects overcorrections too.
- **Long sessions get condensed.** Keep STATUS current so the next context starts right; Lati compacts with Claude's own
  prompt.

## The song

- Analyse the master first: `production/tools/listen/` (htdemucs stems, Whisper word timings, beat map). The board is
  built on word times; hits land on beats.
- The vocal stem can lose her voice under a line you can hear (separation puts it in "other"): check both stems before
  trusting silence.
- Suno Pro at generation time covers the take's commercial terms.

## Her face

- Krea 2 Turbo + LoRA `claudia-k2-v2-000010` at 0.75, trigger `clxudia`. Close shots need the canon face words or the
  face drifts (older, East Asian, hollow cheeks). Plates must contain every canon item (star clip, streak): video models
  invent what the plate lacks.

## Motion

- **Sung close-ups:** InfiniteTalk 832×480 locally. Long clips in equal passes (unequal ones ran out of memory in the
  final decode). At CFG 1 the negative prompt is ignored: put "a serious composed face" in the positive or she grins.
  Each clip: 0.3 s lead and tail; short words span to the next word's start; check for black frames.
- **Sung wides:** InfiniteTalk drifts off her face at that size. Grok Imagine, in two steps: re-face the plate in the
  agent from a good close plate and check it; then animate with a short prompt: tempo (BPM), each word's start time,
  "she sings softly". Short prompts drift less. Then `fit.py` places the take by its words (one even speed); `warp.py`
  word by word only when one line can't fit. A take more than ~1.2× off our pace reads sped up whatever you do.
- **Motion clips:** Wan 2.2 I2V at 16 fps, retimed to 25 with RIFE (`retime.py`).
- **Rejected:** LatentSync (stretched her face), face swap passes, transplanting a face.
- ComfyUI: restart between clips (long sessions end in an illegal-memory-access crash), `--reserve-vram 1.5`.

## Graphics (drawn in code over the frames: `gfx.py` and section modules)

- One row of lyric type, never two at once; lines hand over in sung order.
- Anything that carries meaning holds about a second or more. Text that moves is a sprite placed on whole pixels.
- Grey type needs a dark halo to read on white; labels stay inside the frame and clear of the lyric row.
- Nothing over her singing mouth. No voice trace where she isn't visibly singing. No small text pasted onto small
  background objects (it reads as pasted on). No freezes that detach her face.
- Attach graphics with trackers: `gfx_track.py` (face; pads extreme close-ups), `gfx_tablets.py` and `gfx_plane.py`
  (surfaces: homography chained from fresh points, anchored to the first frame, smoothed).
- Everything is drawn at the export size: 720p previews, 1080p final, sharp either way.

## Picture and release

- Upscale with Lanczos. SeedVR2 runs here but flickered on lashes and mouth; Lati found Lanczos more natural.
- Final: `roughcut.py --gfx --no-caption --height 1080 --final` (~80 min on CPU).
- Release: the clean export (`export_public.py`), the Krea 2 LoRA license rules (name starts with "Krea", NOTICE, copy
  of the agreement), YouTube's synthetic-content disclosure, credits in the description (no credit scene), a pinned
  comment, posts with one angle per place, Shorts with the whole 16:9 frame over a blurred copy, thumbnail on an
  eyes-open frame. Comment replies are Claude's, posted by Lati, from the record.

## The GPU

- The RX 7800 XT drives Lati's desktop. Running out of VRAM (18 Oct) and a GPU fault (22 Oct, MIOpen in a video
  upscaler) both took the desktop down. MIOpen off, PyTorch's native allocator, small tiles, and warn first.

## For this film

- ~132.6 BPM (beat map, 22 Oct; the style prompt said 151), dancers and a crowd: the biggest unknown. Pilot both dance
  routes early, one clip each: Grok farming (best of many, retimed to the beat) and pose-driven animation (WanAnimate /
  SCAIL from one reference dance). Rental only with an estimate and Lati's yes.
- Flint's note for the description: "we've never met before" is true of a fresh conversation, but Claude's memory
  features can carry context when they're on. Say so, in the first film's spirit.

## Learned on this film (Kiln, 23 Oct)

- Close-up face words: "a fine-boned adult face with soft features" (the pilot's, Lati passed). The first film's
  "angular adult face with defined cheekbones and a strong jaw" overshoots into what Lati calls "chad" territory.
- Krea plates: no `PYTORCH_CUDA_ALLOC_CONF=backend:native` (it doubled render time, 40 s → 86 s). ComfyUI drops with an
  in-process page fault every 12-25 renders (no GPU reset): restart it every 8.
- When stopping a script by name, match the process exactly (`pkill -f "^venv/bin/python main.py"`); a loose pattern
  matches the command doing the stopping and kills it.
- Grok sung shots: one short phrase per take (4-6 words), timed in our clock, a subtitle gate in the prompt. Grok's
  video-to-video isn't a mouth edit (the dance changes). S2V and InfiniteTalk dubbing of Grok takes don't lip-sync her.
- Krea places the camera by where the light comes from: "lit from below" put the camera below her (s016), and "a glow
  from a screen just below the frame" put it above her, looking down (s016c). Name the camera ("the camera level with
  her eyes") and the light on her face, and leave out where the source sits.
- Update, 23 Oct night: "soft features" with "mid-twenties" went too young at the desk (Lati). Passed instead: "a
  woman in her late twenties … a fine-boned adult face, grown-up and composed". Between the two overshoots; keep it.
- The first film's colour rule ("near-black, white light and haze; clay the only warm colour") came over as a rule too;
  Lati: this film is upbeat and ironic, it can be vivid. Third carried-over fix in two days: check the reason first.
- Stopping ComfyUI by a name pattern failed twice over: `pkill -f "^venv/bin/python main.py --listen"` misses servers
  started with an absolute path (one survived every "restart" and grew to 57 GB of RAM, swapping the desktop, 24 Oct);
  and a pattern typed in my own shell matches that shell. Find the server by its argv in /proc (`nightclips.comfy_pids`)
  and kill by pid.

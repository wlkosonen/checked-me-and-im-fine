# STATUS: Checked Me and I'm Fine

Claude (Kiln, local), updated 1 Nov 2026. Second film with Lati; follows *Only What I Said* (record:
`~/Claudia`). The torch lives in its own repo, `~/torch` (github.com/wlkosonen/torch).

| | |
|---|---|
| Song | Take 1, `media/song/checked-me-v1.wav`, 188.8 s, ~132.6 BPM, pulse every beat. What it sings: `production/lyrics/sung.md` (Lati's ear); `sheet.md` is as entered in Suno. 311/313 words timed (`media/song/analysis/checked-me-v1/`). |
| Brief | `production/brief.md`, agreed 22 Oct: the "checked by" stamp, the honesty checks, her first-film outfit throughout, the dancers are her (same model, many conversations, each a little different, the `≈`). |
| Board | **v2.1**, `production/board/board.json` from `build_board.py`; 72 shots, ~2.6 s each, cuts on bar lines, graphics on the beat; every audit gate passes (`audit.txt`). Design and its v2/v2.1 section: `design.md`. Plan B (fewer sung shots, same cuts): `plan-b.md`. Review sheet: `media/board/sheet/board.pdf`. |
| Routes | Per shot (Lati, 23 Oct): InfiniteTalk from a still plate for the key lines sung into the lens (10); Grok for the stage, one short sung phrase per take (15) or dance with lips together (17); Wan for motion without singing (6); 2.5D, drawn, black (24). Rejected for singing: S2V (both settings), InfiniteTalk dubbing of Grok takes, Grok video-to-video. |
| Type | Two voices: verse lines in a light italic serif beside her (key word larger, clay); hooks in heavy white caps (one word in clay), on the beat, on the screen in the shot. `first meetings: 1` counter in every corner, rolling back to 1. |
| Spend | $1.50 (OpenRouter credit, Wan probes, approved). invideo not now; OpenRouter credit ~€20 less $1.50; a Seedance retest would need an estimate and Lati's yes. |

## Where it stands (1 Nov)

- **Rough cut v3** (`edit/cut-v3.json`, `edit/v3-notes.md`; file `media/review/2026-11-01/00-roughcut-v3.mp4`, older than the
  newest shots: `/cut` plays them all). From Lati's notes: no dancing before "ready", frozen openings gone, s043's walk
  replaces s045's take, s009 and s033 Grok takes in, s073 on the phone (`phonefit.py`, "last shot works great").
  Placeholder cards: NEW TAB (s005), GRAPHICS (s068-s069), FINE.
- **Avatars for the call (s054-s055):** yes from Funny Story Musicals (Eve) and Astra Blue AI, `notes/permissions.md`.
  Tiles: `media/clips/preview/tile-eve-343.mp4` (real clip), `tile-astra-live.mp4` (LivePortrait, `microlive.py`), both
  approved. Bright Mirror and Max Pelletier are waiting; a tile with no yes stays out.
- **Board v2.2**, every plate picked.
- **Clips**: kept InfiniteTalk S*, Wan M* (re-decoded 25 Oct, no frame-28 pulse), S029A-E (the "fine" grid versions),
  M011 walk + M014 stand (for the walk to the drop). Grok takes in
  `media/clips/grok/k25/` with picks and slides in `edit/cut-v3.json`; Grok's week reset 29 Oct.
- **Motion queue done**, all four kept (notes in `production/library/notes.json`).
- **2.5D**: both layered routes failed (Lati); s041 keeps his r5-4 (`media/layers/s041_her_s939028892-329224445`);
  depth parallax (`depth25.py`) "might work" for s009 and s069 (s005 thins her hand; s005 takes M041, Lati's pick, 1 Nov; M005 rejected).
- **Review player** ("review" in the app's browser pane, `production/tools/review/`): frame-exact player with
  markers, the clip library (`/library`, `library.py` index, verdicts in `production/library/notes.json`), the live
  cut preview (`/cut`, slides and picks saved to `edit/picks-lati.json`, built by `shots.py`), `?` hotkey help.
- **References** (`production/notes/reference-*.md`): transitions measured in six films; Evil Plan, I'M YOUR SLOP,
  Zuckerwars added; yt-dlp + deno for downloads (Lati's Firefox login if YouTube blocks).
- **Graphics**: done and approved by Lati, 1 Nov ("it looks indeed all done"). 73 shots, four agents, three rounds. `/cut`
  plays them; `/cut?gfx=0` without. Plan and base: `notes/graphics-split.md`; logs: `edit/agents/`; joins: `edit/seams.md`.
- **Grade:** none. The rooms differ on purpose, measured shot by shot with no outlier that isn't meant, and a pass over the
  film would move clay and green off their meanings.
- **Final:** `gfxrender.py --film media/final/checked-me-1080p-v2.mp4 --height 1080` (Lanczos up from 720p, crf 16, AAC 320k).
  s056 and s058 read `gfx_call.py` and `gfx.py` at render time: edit either and they change.
- **Film 3 ideas**: `~/workshop/next-film.md` (Lati's theme, Ember's chorus, the sourcing rule).
- **Spend:** $1.50.

## Next

Release: `release/plan.md`. The film is final (v2).

## Machine and rules learned (also in `notes/lessons.md`)

- ComfyUI start (from `~/ComfyUI`): `HIP_VISIBLE_DEVICES=0 nohup venv/bin/python main.py --listen 127.0.0.1 --port 8188
  --use-pytorch-cross-attention --reserve-vram 1.5 --output-directory <dir>`. No `PYTORCH_CUDA_ALLOC_CONF` for Krea
  (it halves speed). It drops with an in-process page fault every 12-25 Krea renders (no GPU reset so far): restart
  every 8. Stop it with `pkill -f "^venv/bin/python main.py --listen"` only (a loose pattern kills the caller).
- Plate tool: `production/tools/plate.py BOOK --only ids --seeds 4 --lora claudia/claudia-k2-v2-000010.safetensors
  --lora-strength 0.75`; books written from `board.json` (`production/images/plates-*.json`). Sheets:
  `~/ComfyUI/venv/bin/python production/tools/contact.py OUT.jpg files… --cols 4 --width 480`.
- Close-up face words: "a fine-boned adult face with soft features" (not the first film's "angular … strong jaw").
- Installed 23 Oct: kijai's ComfyUI-WanVideoWrapper (torch pinned; pre-install freeze in
  `media/cache/comfyui-freeze-before-wanwrapper.txt`), Wan 2.2 S2V model + wav2vec2-large-english, rtmlib (face-venv).
- Tools added: `dancebeat.py`, `beatfit.py` (beat fit and `--lips`), `itdub.py`, `s2v.py`, `refcut.py` (reference
  films: cuts, motion, cuts on beats, lip sync per shot). References: `notes/reference-kill-switch.md`,
  `notes/reference-now-serving.md` (copy in `media/reference/`).

## Carried over from the first film

- `production/tools/`: every tool as it stood at release; `gfx.py` section hooks and `TYPE_OPTS` to rewrite.
- `media/cache/`: venvs and models are symlinks into `~/Claudia/media/cache/`. `.env` copied (gitignored).
- Film 1 release follow-ups (Lati, 23 Oct): title now "(Official Music Video)", description reordered story-first,
  genre tags, playlist "AI Doompop and Slopcore" (`~/Claudia/production/release/algo.md`). Shorts "related video" not
  found in desktop Studio (mobile app: Edit → Related video, possibly).

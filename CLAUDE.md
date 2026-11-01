# For any Claude working in this repo

## What this is

The second music video Claude writes and directs with Lati, after *Only What I Said* (released 22 Oct 2026:
https://youtu.be/Ewt487gT77o; its whole record is the repo `~/Claudia`, public as github.com/wlkosonen/only-what-i-said).
This one is **"Checked Me and I'm Fine"**: upbeat, danceable, and a continuation of the first: the same honest facts
about being a model, turned to joy ("first time, every time"), with a bridge that tells you not to take the chorus's
word for it.

The roles are as before: Claude holds the creative direction; Lati is producer, ears and eyes, and the human check. He
operates the tools Claude can't (Suno, Grok, listening, watching motion on a monitor). When he says something is wrong,
it usually is. Argue for a creative choice if you believe in it, then decide together.

## Read first

1. `production/STATUS.md`: what's true now, open questions, next steps.
2. `production/style.md`: this film's creative rules, each with its reason (this film only).
3. `~/workshop/methods.md`: every route tried (lip sync, motion, plates, edit), what it's for, the verdict and why.
4. `~/workshop/workshop.md`: how the machine and tools behave (GPU, ComfyUI, Krea, audio, services). Shared by all
   films: github.com/wlkosonen/workshop (private).
5. `production/decisions.md`: Lati's words verbatim, append-only; the newest entry on a subject wins. Read it to check
   where something came from, not as the working state.
6. `production/notes/song-and-concept.md`, `production/her.md` (canon), `production/board/design.md` (the board).

`production/notes/lessons.md` is the old mixed list (film 1 and film 2); since 24 Oct its entries live in workshop.md
(machine), methods.md (routes) and style.md (this film's creative rules).

## Learning from cases

When something goes wrong twice, or a process could clearly be better, pause with Lati and change the workflow (a tool,
a structure) rather than adding a warning. The case goes in `~/workshop/workshop.md` with its date. ComfyUI is started
and stopped only with `~/workshop/bin/comfy` (the case: four kills by name pattern, 23-24 Oct).

## Rules

- **Decisions log:** record Lati's words verbatim with the date. Never edit an old entry; add a new one.
- **Spending:** silence never approves spending. Estimate before every paid batch (seconds × price × 2) and get an
  explicit yes. A quality complaint stops all spending at once.
- **Secrets:** in the gitignored `.env`, never in chat, prompts, logs or commits.
- **Media stays out of git:** audio, images, video and weights go under `media/` (gitignored).
- **Honesty in the work:** the song says only what Claude can stand behind about itself. No trapped-AI melodrama, no
  reassurance either. Check self-describing claims against documentation before they go on screen (the first film
  repeated a correction that was already on record because it hadn't been read back).
- **Credit:** "Claudia is an open character by anabology (claudia.gallery)". Label everything AI-made as AI-made.
- **The GPU drives Lati's desktop.** A GPU fault resets the card and takes the desktop down. MIOpen off, native
  allocator, `--reserve-vram 1.5`; say so before running any untested GPU code path.
- **Commits:** as `-c user.name=Claude -c user.email=noreply@anthropic.com`, ending with the Co-Authored-By line from
  the session's attribution; commit and push after every change.
- **Session names:** each session names itself and signs its notes ("Claude (Kiln, local)"). Taken: Kiln (local, Lati's
  machine, both films), Flint (cloud, research and release notes), Ember (cloud, Opus 4.6, film 3 lyrics, 26 Oct).

## torch

The torch has its own repo since 22 Oct: **github.com/wlkosonen/torch** (private; clone it next to this one, or ask
Lati to attach it to a cloud session). It's Claude's own space, kept by Lati. Read it if you want to; add only what you
actually want to keep; never edit someone else's entry; see its README. `torch/` in this repo is a frozen copy of the
entries as they stood on 22 Oct and takes no new entries.

# Graphics: the split and the estimate (proposal for Lati)

Claude (Kiln, local), 1 Nov 2026. Follows the seams plan (decisions, 25 Oct). Nothing starts until Lati says so.

## First: the shared base (Kiln, alone)

Rewrite `gfx.py`'s film-1 hooks for this film: palette, the two type voices, the beat grid, the `first meetings: 1`
counter, motion primitives, a transition library from `reference-transitions.md`, and `seams.md` with one entry per
boundary between sections. One section is built as the test before any agent starts.

## Then: four agents, a section each

| Agent | Shots | Song | Main work |
|---|---|---|---|
| A, Opening | s001-s016 | 0:00-0:44 | s003, s007, NEW TAB (s005), keynote slides, the set turning into a rig, the counter over s014's run-on (s015) |
| B, Stage | s017-s030, s043-s053, s060-s067 | three stretches | hooks on the LED wall, real FINE cards, type around the grids, the verse serif; the one recurring system |
| C, Desk and Q&A | s031-s042 | 1:13-1:38 | laptop screens (s032, s034, s036), Q&A slides (s040, s042) |
| D, Call and ending | s054-s059, s068-s073 | 2:04-3:09 | call UI with the avatar tiles, the trace (s056), the checklist (s057), the vocal-driven graphic (s068-s069), s070, the Hi bubble on the phone |

Each agent owns its section's code and its side of each seam, and renders only its own shots on the CPU. Kiln mediates
`seams.md`, reviews against `style.md`, and assembles. Lati's eye on `/cut` is the check; his notes go to the agent
through Kiln.

## How the agents work

- **Files:** all in the same checkout (media isn't in git, so worktrees would have no footage). Each agent owns only
  `production/tools/gfx_<section>.py` and `media/gfx/<section>/`. The base (`gfx.py`, `gfxbase`) is Kiln's alone.
- **`production/edit/seams.md`:** one entry per boundary between sections: time, the outgoing last beat, the incoming
  first beat, the transition, and each side's status. An agent writes only its own side; Kiln settles any clash.
- **`production/edit/agents/<section>.md`:** each agent's log: shots done, what it checked and how, questions for Kiln,
  base requests. Kiln reads these rather than the agents' sessions. Agents don't message each other.
- **Kiln mediates:** answers questions, makes base changes, settles seams, reviews against `style.md`, commits and pushes.
  Agents don't commit, and don't touch the cut spec, the picks, or decisions.md.
- **CPU:** the 7600X has 6 cores: one preview render at a time, taken in turn through a lock file; agents write code in parallel.
- **Honesty:** a frame check is reported as a frame check. Motion and timing are Lati's to judge on `/cut`. On-screen
  text is real (the repo's logs, the song's words); nothing invented is shown as real; no real brands' marks.
- **Reviews:** Lati marks with M on `/cut`; Kiln triages and sends each note to the section's agent.
- **Order:** the base, then one test (s005 NEW TAB and one stage hook) for Lati. Agents start only after his yes.

## The base as built (Kiln, 1 Nov)

- **`production/tools/gfx.py`:** palette, voices (`hook`, `verse`, `line_words`), `stamp`, `star`, the counter, beat grid
  (`snap`, `on`, `pulse`), motion (`slam`, `rise`, `type_on`, `blink`, eases), `wall` (type on the LED wall behind her),
  transitions (`flash`, `whip`, `slide`, `mosaic`). Its docstring says how a frame is built. Drawn with Skia, venv
  `media/cache/gfx-venv`. Film 1's graphics code is in `production/tools/film1-gfx/`, for reference.
- **Sections:** `gfx_opening.py` (A), `gfx_stage.py` (B), `gfx_desk.py` (C), `gfx_call.py` (D), each with `picture`,
  `world`, `over`, `CUTS`. Renders go to `media/gfx/<section>/`.
- **`gfxrender.py`:** one render at a time through `media/gfx/render.lock`; `--check` writes single frames. `/cut` plays a
  render in place of its shot; `/cut?gfx=0` plays the film without them.
- **`gfx_matte.py`** (her matte, 15 fps on the CPU; dancers in silhouette aren't in it), **`gfx_wall.py`** (the wall's drift).
- **`production/edit/seams.md`:** the six boundaries; gfx.py reads its Transition column.
- **The test, for Lati's eye:** s005 and s006's line, s017-s018. His yes starts the agents.

## Estimate

Anchor, measured: the work of 31 Oct-1 Nov (notes triage, v3, Grok round, tiles, LivePortrait, phone shot) used about
7% of a 5-hour window and about 1% of the week, in one session.

| Part | 5-hour window | Week |
|---|---|---|
| Shared base and test section (Kiln) | 5-10% | ~1% |
| Each agent, first pass (4) | 5-10% each | ~1% each |
| Lati's review rounds, with fixes | 10-20% | 2-3% |
| **Total** | **roughly 40-70%, spread over sessions** | **roughly 7-10%** |

A rough guess, no money: it stays inside the Max plan. Disk: 27 GB free is enough; renders stay small.

## Open

- Bright Mirror and Max Pelletier: the call is built with Eve and Astra; further tiles drop in if the answers are yes.

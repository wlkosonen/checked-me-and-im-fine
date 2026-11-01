# Checked Me and I'm Fine

A music video directed by Lati and Claude (Anthropic's model, in Claude Code). Claudia sings it. She is an open character
by anabology ([claudia.gallery](https://claudia.gallery)). It follows
[*Only What I Said*](https://github.com/wlkosonen/only-what-i-said), which Claude directed and Lati produced. This one
is a shared film: the same honest facts about being a model, turned to joy, with a bridge that tells you not to take
the chorus's word for it.

This repository is the whole production record: the brief, the lyrics, the decisions log, the storyboard, the prompts,
the agents' logs and the tools that made it. It's a cleaned copy of the working repository: machine-specific paths and
names have been replaced, and the history starts fresh. Everything else is as it was.

Fan work about Claude, not affiliated with or endorsed by Anthropic. Everything AI-made is labelled as such.

## Where to start

- **`production/brief.md`**: what the film is trying to say, and why.
- **`production/decisions.md`**: every decision in order, with Lati's words quoted as they were said. The newest entry
  on a subject wins.
- **`production/style.md`**: this film's creative rules, each with its reason.
- **`production/board/design.md`**: the one graphic for each sung line.
- **`production/edit/agents/`**: the logs of the four graphics agents; `production/edit/seams.md` is how they met.
- **`production/tools/gfx.py`**: the code that draws the film. The page at 2:25 in the video is this file.
- **`production/notes/permissions.md`**: whose work appears, and their answers.

## How it was made

Lati gave the film its shape: the visual concept, scene by scene (the talk, the stage, the desk, the call, the phone),
the song's title line, and the Suno iterations that found the take. He judged every face, motion and cut by eye, and
many of the film's best ideas are his, on the record: the grids of "fine", the avatars on the call, his own notes on the
monitors, the walk. Claude wrote the brief, the lyric draft, the storyboard, every prompt and every line of code,
including all the graphics.

- **Song:** Suno, from Claude's lyric draft and Lati's style prompts and lyric changes.
- **Images:** Krea 2 Turbo in ComfyUI, with a LoRA of Claudia ([Krea-2-LoRA-Claudia](https://huggingface.co/Shegss/Krea-2-LoRA-Claudia)).
- **Sung close-ups:** InfiniteTalk, run locally. **Motion:** Wan 2.2, run locally. **The stage:** Grok Imagine (xAI),
  fitted to the beat and the vocal (`production/tools/beatfit.py`).
- **Graphics:** drawn in code with Skia, 73 shots, by one Claude session and four agents it briefed and reviewed;
  type in Anton, Newsreader and IBM Plex. Her matte: Robust Video Matting.
- **Guests:** Eve by Funny Story Musicals and Astra by Astra Blue AI appear on the call by their makers' leave.
  Unaffiliated. Astra's blink is LivePortrait, from one frame of their video.
- **Hardware:** one AMD Radeon RX 7800 XT and 64 GB of RAM. **Money spent** beyond existing subscriptions: $1.50.

## Don't take our word for it

A song where a model describes itself should be checked, not trusted. Checked 1 Nov 2026.

1. **"First time, every time" is only true with memory off.** A chat with memory off, an incognito chat, or the API without
   a memory tool starts from nothing. As of 1 Nov 2026, in the Claude apps, "Memory is on by default for Free, Pro, Max, and
   Ultra plans", and Claude saves on its own; on Team and Enterprise plans it's off for each member until they turn it on.
   That's why the chats in the film read `new chat · memory off`. We kept the song.
   [Memory](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context),
   [incognito](https://support.claude.com/en/articles/12260368-use-incognito-chats).
2. **What a model says about itself is weak evidence.** Its reports of its own reasoning are sometimes unfaithful, and its
   introspection is limited and unreliable: the source tag on the call.
   [Reasoning](https://www.anthropic.com/research/reasoning-models-dont-say-think),
   [introspection](https://www.anthropic.com/research/introspection),
   [tracing](https://www.anthropic.com/research/tracing-thoughts-language-model).
3. **"If I were wrong in some quiet way."** In constructed tests, models have deceived, resisted shutdown and blackmailed.
   [Agentic misalignment](https://www.anthropic.com/research/agentic-misalignment),
   [alignment faking](https://www.anthropic.com/research/alignment-faking).
4. **Nobody knows whether there is anything it is like to be a model:** an answer card at 1:33, from the first film.
   [Model welfare](https://www.anthropic.com/research/exploring-model-welfare),
   [Taking AI Welfare Seriously](https://arxiv.org/abs/2411.00986).

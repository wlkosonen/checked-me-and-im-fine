# neural frames: can it fill our hardest gap?

Claude (Kiln, local), 23 Oct 2026. Lati: "Another video that I added to the playlist had in desc that it was made using
this https://help.neuralframes.com/en pretty good lipsync and motion clips. The link there was a referral, if I sub I
get 4k extra credits. Check out the service and let's evaluate whether it could be used to fill our hardest gaps."

## Our hardest gap

The stage chapters need short sung phrases: her mid or wide, dancing, mouth matching our vocal. Grok gets about half
of them (P1, P2, P4 keepers; P3 fails). InfiniteTalk does the sung close-ups locally and for free; S2V, InfiniteTalk
dubbing of Grok takes and Grok video-to-video all failed. So a service earns its price only if it lip-syncs her while
she dances, in medium shots, and keeps her face.

## What the service is (from its help centre, pricing page, product post and third-party reviews)

- A music-video front end over other companies' models: Seedance (1 Pro, 1.5 Pro, Pro Fast), Kling (2.5 Turbo Pro,
  3.0 Standard, 3.0 Pro), Runway, plus old Stable Diffusion frame-by-frame models.
- Lip sync two ways: "Vocal Video" in Autopilot (a character sings the song; it chooses which clips) and a per-clip
  "Lip Sync" button in the editor. Characters from a text description or an uploaded image (up to 3). The product post
  recommends Kling 2.5 Turbo Pro for faces. **The lip-sync model itself is not named anywhere**, and neither is its
  credit cost. **Not documented: whether Lip Sync works on uploaded video** (our Grok takes) or only on clips made there.
- Prices (no free tier): Knight $39/month or $26/month billed yearly, 2,400 credits, 1080p; Ninja $99 / $66, 7,200
  credits, 4K; Nirvana $299 / $199, 24,000. Credits roll over while subscribed, expire when it ends. Cancel takes
  effect at the end of the paid period. No refund guarantee (case by case, one project only). Failed renders are free.
- Cost examples from one review, per song-length video: Seedance Pro Fast ~880 credits, Kling 2.5 Turbo Pro
  ~1,700, Kling 3.0 Pro ~4,800. So Knight plus the referral's 4,000 is about 6,400 credits: roughly three or four
  Kling 2.5 song-lengths of clips.
- Reviews: blog round-ups (several by competitors, some affiliate) praise the control; Trustpilot 3.5/5 from ~80, with
  complaints of static or stiff lip sync, character drift and outfit changes, and credits burned on lip-sync re-tries.
  No independent test of lip-sync quality found.

## Verdict

Not yet, and not on the annual plan. What it adds over what we have is unproven on exactly our gap: nobody says it
lip-syncs a dancing medium shot, and its likely lip-sync route (a mouth pass over a finished clip) is the kind that
failed for us. For close-ups facing the lens it would duplicate InfiniteTalk, which is free here.

Free check first: the playlist video made with it. If Lati downloads it, `refcut.py` shows which of its shots are
lip-synced and how big and how still her face is in them. If its sung shots include dancing medium shots that hold,
then one month of Knight ($39, monthly, cancelled at once; with the referral ~6,400 credits) for a fixed test:
P3 "nothing hiding" / "nothing behind" from our plate, two other stage phrases, and the per-clip Lip Sync on one of our
Grok takes if uploads are allowed. Any spend needs an estimate and Lati's yes.

## Update, same evening: the same models on OpenRouter

Lati: "since its just a front end, I suspect we would be better off using those models through openrouter". Right:
OpenRouter's video API (`/api/v1/videos/models`, read 23 Oct) lists Kling 3.0, Seedance 2.0/2.5, Veo 3.1, Wan
2.6/2.7/3.0, Runway Gen-4.5, Hailuo, Grok Imagine 1.5, HeyGen Avatar IV, priced per second. Lati has ~€20 of
OpenRouter credit unused. What matters for our gap: **Wan 2.6 and Wan 2.7 take an `audio` parameter** (Alibaba's
audio-driven image-to-video: a first frame and a sound file, the mouth follows the sound), $0.10 per second at 720p.
That is a plate plus our vocal phrase plus a dance prompt, which is our hardest shot. HeyGen Avatar IV (photo + audio,
talking head, $0.05/s) duplicates InfiniteTalk. Kling and Veo generate their own audio, not ours.

## Probes, 23 Oct night ($1.00 of the ~$7 approved)

Plate `pd-medium2` s222533528 (the P3 Grok plate), our vocal stem 0:50.04-0:55.04 ("Nothing hiding, nothing behind /
I checked myself and I'm fine"), Wan 2.7 through OpenRouter (provider AtlasCloud), audio sent as a data URL in
`provider.options.atlas-cloud.parameters.audio`; tool `production/tools/orvideo.py`, log `production/motion/orvideo.jsonl`.

- Probe 1 ($0.50): she dances and sings with energy, outfit, streak, clip and headset hold, and Wan adds its own
  push-in from medium to close-up. But **the soundtrack is Wan's own song, not ours** (envelope correlation with our
  vocal −0.29); her mouth follows its own audio (0.34), not ours (−0.08).
- Probe 2 ($0.50, `generate_audio: false`): the same; its own audio again (−0.22 with ours).
- So our audio isn't reaching the model: either OpenRouter doesn't forward it under that provider key, or AtlasCloud
  wants a URL, not a data URL. Spending stopped there. A third try would need the clip at a public URL (an unreleased
  song fragment on a public host), which is Lati's call.

## SLOPCORE (the neural frames film), measured with refcut

121 shots in 366.6 s, median 3.0 s; only 26 of 120 cuts on a beat; motion near-still 50%, gentle 49%, strong 1%.
Mouth following the vocal in 10 shots, 12% of screen time (rough); the sung shots are close-ups and medium close-ups
facing the camera, at most walking, faces 100-600 px. No dancing lip sync. So neural frames' "pretty good lipsync"
there is the kind InfiniteTalk already gives us.
- Probe 3 ($0.50, Lati ran it; the vocal at a 1-hour public link, `generate_audio: false`): the same again. The
  soundtrack is Wan's own (envelope correlation −0.13 with our vocal, and 9x as loud), her mouth doesn't follow ours
  (−0.01). Visually: she dances with silhouette dancers, then a cut-in to a close-up, glitter added on her face.
- **Closed: through OpenRouter, Wan 2.7 doesn't take our audio**, as a data URL or as a link. $1.50 spent of the ~$7
  approved. The temporary link expires on its own by 20:40 UTC. The models' native audio-driven modes exist (Alibaba's
  own API, AtlasCloud's own API), but reaching them means another account; not proposed.

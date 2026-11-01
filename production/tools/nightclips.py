#!/usr/bin/env python3
"""Overnight local clips for this film: InfiniteTalk sung close-ups and Wan 2.2 motion, one after another.

    python3 production/tools/nightclips.py S001,S006,M037 [--retry 1]

Lati, 24 Oct: queue what's needed while he's offline. Each clip comes from board.json's clip list (its window t0-t1
already has the lead and tail) and starts from the shot's current pick in picks.json, read at run time. Sung: the
vocal stem cut to the window (mono, peak -1 dBFS) and the plate prompt plus a singing line ("a serious composed face":
at CFG 1 the negative prompt is ignored, so it goes in the positive, film 1's lesson). Motion: MOTION below, at least
3 s. ComfyUI restarts before every clip (long sessions crash on this card); a black or failed render is retried with a
new seed. Clips land in media/clips/local/ via video.py; a log in media/clips/night.log.
"""
import glob
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMFY = Path.home() / "ComfyUI"
LOG = ROOT / "media/clips/night.log"
STEM = ROOT / "media/song/analysis/checked-me-v1/stems/vocals.wav"
LISTEN = ROOT / "media/cache/listen-venv/bin/python"
HER = ("A woman in her late twenties with pale skin, light freckles across her nose, a fine-boned adult face, grown-up and "
       "composed, a glossy black blunt jaw-length bob, heavy straight bangs, one thin clay-orange streak through the "
       "bangs, a small flat clay-orange eight-pointed star hair clip and a thin headset microphone at her cheek, wearing "
       "a fitted white cotton shirt with short puffed sleeves, black suspender straps and long black leather gloves. ")
SING = (" She sings the words to the camera, her mouth clearly shaping each word, a serious composed face, small natural "
        "head movements.")
MOTION = {
    "M002": HER + "Seen from behind, she walks slowly down the aisle of a dark auditorium between the seat rows, toward "
                  "the glowing cobalt-and-magenta stage ahead. The camera follows behind her at walking pace.",
    "M004": HER + "She stands on a bright, colourful keynote stage in profile, watching the giant screen beside her with "
                  "a small pleased smile, then turns her head to look straight into the camera, lips together. Locked "
                  "camera.",
    "M010": HER + "Close on her on a keynote stage: she turns her head from the glowing screen to the camera with a small "
                  "knowing smirk, lips together. Locked camera.",
    # small motions for stills (Lati, 26 Oct: "turning to point to the screen and such"); front and profile views only
    "M005": HER + "On a bright keynote stage beside the giant glowing screen, she turns her head and shoulders toward "
                  "the screen and points at it with her raised gloved hand, lips together, calm and composed. Locked "
                  "camera.",
    "M008": HER + "She walks a few slow, confident steps downstage toward the camera on a glossy keynote stage, the "
                  "giant glowing screen behind her, lips together. The camera holds steady, low at the front of the "
                  "stage.",
    "M038": HER + "At the lectern on a bright conference stage, she turns her head slowly from the screen to the audience "
                  "with a small composed look, lips together. Locked camera.",
    "M041": HER + "She stands on a bright conference stage and opens one gloved hand toward the audience in a small, "
                  "relaxed presenting gesture, lips together, a calm composed face. Locked camera.",
    "M062": HER + "She stands at the front of a huge concert stage and sways gently with the music, breathing calmly, lips "
                  "together, the white beams sweeping slowly through the haze behind her. The camera holds steady, low.",
    # the walk to the drop without dancing (restructure-v3, Lati 26 Oct: render beforehand)
    "M011": HER + "She walks slowly and confidently toward the camera across a bright keynote stage, the giant glowing "
                  "screen behind her, her arms relaxed at her sides, lips together, a calm composed face. The camera "
                  "holds steady at her chest height as she comes closer.",
    "M014": HER + "She stands still downstage at the edge of a huge concert stage, her arms relaxed at her sides, lips "
                  "together, breathing calmly, the stage lights sweeping slowly through the haze behind her; at the "
                  "end she looks straight into the camera. The camera holds steady, low, looking up at her.",
    "M033": HER + "Seen from behind over her shoulder at her desk at night, she keeps her back to the camera the whole "
                  "time, facing the glowing monitor, typing at the keyboard below the frame, only her shoulders moving "
                  "slightly. The back of her head stays toward the camera. The camera pushes in slowly.",
    "M035": HER + "Her face lit by a laptop screen in a dark cosy room at night; her eyes follow the lines on the screen, "
                  "the glow on her face shifts in colour, lips together, a slow blink. Locked camera.",
    "M037": HER + "She sits at her desk in a colourful cosy room at night, then slowly leans back in her chair and looks "
                  "away from the screen, lips together. The camera pulls back slowly.",
    "M072": HER + "Her face is lit by a phone's cold glow in a dark room; she looks down at the phone, a small private "
                  "smile, lips together, almost still, a slow blink. Locked camera.",
}


def log(msg):
    with LOG.open("a") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")
    print(msg, flush=True)


def comfy_pids():
    """ComfyUI servers on port 8188, however they were started (relative or absolute venv path). The old
    `pkill -f "^venv/bin/python main.py --listen"` missed the ones this script starts with an absolute path, so one
    server lived through every 'restart' and grew to 57 GB of RAM (24 Oct)."""
    pids = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            argv = (d / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        if len(argv) > 3 and argv[0].endswith(b"venv/bin/python") and argv[1] == b"main.py" and b"--listen" in argv:
            pids.append(int(d.name))
    return pids


def comfy_stop():
    for pid in comfy_pids():
        os.kill(pid, signal.SIGTERM)
    time.sleep(6)
    for pid in comfy_pids():
        os.kill(pid, signal.SIGKILL)
    time.sleep(2)


def comfy_restart():
    """Through the workshop's tool, the one way to start and stop ComfyUI (~/workshop/bin/comfy)."""
    subprocess.run([str(Path.home() / "workshop/bin/comfy"), "restart", "--out", str(ROOT / "media/plates")],
                   check=True, stdout=subprocess.DEVNULL)


def cut_vocal(cid, t0, t1):
    out = ROOT / f"media/clips/audio/{cid}.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(LISTEN), "-c", f"""
import soundfile as sf, numpy as np
sr = sf.info({str(STEM)!r}).samplerate
x, sr = sf.read({str(STEM)!r}, start=int({t0} * sr), stop=int({t1} * sr))
x = x.mean(1) if x.ndim > 1 else x
x = x / (np.abs(x).max() + 1e-9) * 10 ** (-1 / 20)
sf.write({str(out)!r}, x.astype('float32'), sr)
"""], check=True)
    return out


def black(cid):
    f = sorted(glob.glob(str(ROOT / f"media/clips/local/{cid}-*.mp4")), key=os.path.getmtime)[-1]
    means = []
    for t in (0.2, 1.0, 1.6):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", f, "-frames:v", "1", "-vf",
                              "scale=64:-2,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
        if raw:
            means.append(sum(raw) / len(raw))
    if means and max(means) < 2:
        (ROOT / "media/clips/local/black").mkdir(parents=True, exist_ok=True)
        os.rename(f, ROOT / "media/clips/local/black" / Path(f).name)
        return True
    return False


def colour_jumps(f):
    """Frames where the clip's mean colour jumps far more than it moves elsewhere. Case (25 Oct): temporal decode tiles
    put a colour pulse at frame 28 in every motion clip for two nights; the black check passed them all, Lati's eye
    caught it. Flags only (a jump can be a real light change); the log line says which frames to look at."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-vf", "scale=64:36,format=rgb24", "-f", "rawvideo",
                          "-"], capture_output=True).stdout
    n = 64 * 36 * 3
    means = [[sum(raw[i + c:i + n:3]) / (n / 3) for c in range(3)] for i in range(0, len(raw) - n + 1, n)]
    d = [sum(abs(a - b) for a, b in zip(means[i], means[i - 1])) for i in range(1, len(means))]
    if not d:
        return []
    med = sorted(d)[len(d) // 2]
    return [i + 1 for i, x in enumerate(d) if x > 6 and x > 4 * max(med, 1)]


def check_colour(cid, files):
    for f in files:
        jumps = colour_jumps(ROOT / f if not str(f).startswith("/") else f)
        if jumps:
            log(f"{cid}: COLOUR JUMP at frame(s) {jumps} in {Path(f).name}: look before keeping")


def again(seeds):
    """Re-run recorded clips by seed: same id, image, prompt, frames and seed, so the same motion comes back through
    the current decode (25 Oct: the temporal-tile colour pulse at frame 28). A new file gets the next counter."""
    runs = [json.loads(l) for l in (ROOT / "production/motion/local-runs.jsonl").read_text().splitlines() if l.strip()]
    for seed in seeds:
        r = next(x for x in runs if x["seed"] == int(seed))
        log(f"{r['id']}: again, seed {seed}, {Path(r['image']).name}")
        comfy_restart()
        p = subprocess.run(["python3", str(ROOT / "production/tools/video.py"), r["kind"], "--image", r["image"],
                            "--prompt", r["prompt"], "--seconds", str((r["frames"] - 1) / 16), "--seed", seed,
                            "--id", r["id"]], capture_output=True, text=True, timeout=3 * 3600)
        if p.returncode:
            log(f"{r['id']}: failed: {(p.stderr or p.stdout).strip()[-600:]}")
        else:
            meta = json.loads(p.stdout.strip().splitlines()[-1])
            log(f"{r['id']}: done in {meta['seconds'] / 60:.0f} min, {meta['files']}")
            check_colour(r['id'], meta['files'])
    subprocess.run([str(Path.home() / "workshop/bin/comfy"), "stop"], stdout=subprocess.DEVNULL)
    log("queue finished")


def main():
    if sys.argv[1] == "--again":  # nightclips.py --again SEED,SEED (motion clips only)
        return again(sys.argv[2].split(","))
    ids = sys.argv[1].split(",")
    retry = int(sys.argv[sys.argv.index("--retry") + 1]) if "--retry" in sys.argv else 1
    b = json.loads((ROOT / "production/board/board.json").read_text())
    clips = {c["id"]: c for c in b["clips"]}
    plates = {p["plate"]: p["prompt"] for p in b["plates"]}
    for cid in MOTION:  # a still shot with no clip on the board: its own window and its picked plate
        sh = next((x for x in b["shots"] if x["id"] == "s" + cid[1:]), None)
        if cid not in clips and sh:
            clips[cid] = {"id": cid, "kind": "motion", "start": f"plate:{sh['plate']}", "t0": sh["t0"], "t1": sh["t1"]}
    # the "fine" grids (Lati, 25 Oct): five versions of her, each singing both chants (s027's five "fine"s and s029's
    # four, 65.86-70.86), cut in the edit to her own word
    for p in json.loads((ROOT / "production/images/plates-fine4.json").read_text()):
        k = p["id"][-1]
        clips[f"S029{k.upper()}"] = {"id": f"S029{k.upper()}", "kind": "sung", "start": f"plate:{p['id']}",
                                     "t0": 65.40, "t1": 71.40}
        plates[p["id"]] = p["prompt"]
    for cid in ids:
        picks = json.loads((ROOT / "production/board/picks.json").read_text())  # re-read: picks may change
        c = clips[cid]
        plate = c["start"].split(":", 1)[1]
        image = (picks.get(plate) or {}).get("file")
        if not image:
            log(f"{cid}: no pick for {plate}, skipped")
            continue
        secs = round(c["t1"] - c["t0"], 3)
        if c["kind"] == "sung":
            audio = cut_vocal(cid, c["t0"], c["t1"])
            args = ["sung", "--image", str(ROOT / image), "--audio", str(audio), "--seconds", str(secs),
                    "--prompt", plates[plate] + SING]
        else:
            args = ["motion", "--image", str(ROOT / image), "--seconds", str(max(secs, 3.0)), "--prompt", MOTION[cid]]
        for attempt in range(1 + retry):
            log(f"{cid}: attempt {attempt + 1}, {secs} s, {Path(image).name}")
            try:
                comfy_restart()
                r = subprocess.run(["python3", str(ROOT / "production/tools/video.py"), *args, "--id", cid],
                                   capture_output=True, text=True, timeout=3 * 3600)
                if r.returncode:
                    log(f"{cid}: failed: {(r.stderr or r.stdout).strip()[-600:]}")
                    continue
                if black(cid):
                    log(f"{cid}: black frames, moved aside")
                    continue
                meta = json.loads(r.stdout.strip().splitlines()[-1])
                log(f"{cid}: done in {meta['seconds'] / 60:.0f} min, {meta['files']}")
                check_colour(cid, meta['files'])
                break
            except Exception as e:  # keep the queue going
                log(f"{cid}: error {e!r}")
    subprocess.run([str(Path.home() / "workshop/bin/comfy"), "stop"], stdout=subprocess.DEVNULL)
    log("queue finished")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build finished shots for the rough cut from a cut spec: Grok takes, the held-"fine" card, the "fine" grids.

    media/cache/listen-venv/bin/python production/tools/shots.py production/edit/cut-v3.json [--fit] [--only s027,s029]

--fit first runs beatfit.py --no-dot on every take in the spec's "fits" into media/clips/fit/ (sung takes with
--lips). Then each shot in "shots" becomes media/clips/shot/<sid>.mp4: 1280x720, 25 fps, exactly its board window,
which roughcut.py plays in place of the clip book. Lati's picks from the clip library
(production/edit/picks-lati.json: a clip from its in point at the shot's start) override the spec, unless a pick is
marked "folded" (already built into the spec). The clip book (production/motion/clipbook.json) is rebuilt from
the board's clips that have a file in media/clips/local/. The spec's _about says what each field means.

The grids (Lati, 25 Oct): each "fine" of a chant is sung by a different version of her (S029A-E, InfiniteTalk over
65.40-71.40). A cell comes up on its word, plays while she sings it, then holds where her mouth closes (Lati, 1 Nov;
measured by mouthclose.py, in the cell's third field), so each version says only her own word. The centre version comes up large over the four on the fifth "fine".
"""

import argparse
import glob
import json
import math
import subprocess
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
W, H, FPS = 1280, 720, 25
FIT = ROOT / "media/clips/fit"
SHOT = ROOT / "media/clips/shot"
GRID_T0 = 65.40  # S029A-E start here in song time
_frames = {}


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def frames(path):
    if path not in _frames:
        c = av.open(str(path))
        _frames[path] = ([f.to_image() for f in c.decode(video=0)], float(c.streams.video[0].average_rate))
    return _frames[path]


def take_frame(src, T, seg):
    """The take's frame for song time T."""
    kind, name = src.split(":", 1)
    if kind == "still":  # a picture with a slow push-in over seg["seconds"], from song time seg["at"]
        im = cover(Image.open(ROOT / name).convert("RGB"), W, H)
        z = 0.03 * max(0.0, T - seg["at"]) / seg["seconds"]
        dx, dy = W * z / 2, H * z / 2
        return im.resize((W, H), Image.BICUBIC, box=(dx, dy, W - dx, H - dy))
    T = min(T, seg.get("hold", T)) + seg.get("offset", 0.0) - seg.get("shift", 0.0)
    if kind == "fit":
        span = json.loads((FIT / f"{name}.json").read_text())
        fr, rate = frames(FIT / f"{name}.mp4")
        i = round((T - span["t0"]) * rate)
    elif kind == "file":  # any clip by its path (Lati's picks in the library), its time 0 at song time seg["at"]
        fr, rate = frames(ROOT / name)
        i = round((T - seg["at"]) * rate * seg.get("speed", 1.0))
    else:  # raw: the take as it is, its time 0 at song time seg["at"]
        fr, rate = frames(ROOT / f"media/clips/grok/k25/{name}.mp4")
        i = round((T - seg["at"]) * rate)
    im = cover(fr[max(0, min(len(fr) - 1, i))], W, H)
    return ImageOps.mirror(im) if seg.get("flip") else im


def punch(im, T, times, amount=0.04, tau=0.07):
    """A hit on each time: zoomed in at once, easing back, as the cut pulse does."""
    past = [T - x for x in times if T >= x]
    z = amount * math.exp(-min(past) / tau) if past else 0
    if z < 0.001:
        return im
    dx, dy = W * z / 2, H * z / 2
    return im.resize((W, H), Image.BICUBIC, box=(dx, dy, W - dx, H - dy))


def card(word):
    im = Image.new("RGB", (W, H), (8, 8, 8))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype("DejaVuSans-Bold.ttf", 300)
    if d.textlength(word, font=f) > W * 0.9:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", round(300 * W * 0.9 / d.textlength(word, font=f)))
    x0, y0, x1, y1 = d.textbbox((0, 0), word, font=f)
    d.text(((W - (x1 - x0)) / 2 - x0, (H - (y1 - y0)) / 2 - y0), word, fill=(250, 250, 250), font=f)
    return im


def version(cid, T, w0, w1, flip=False):
    """Version cid at song time T: live while she sings her word, held at w1, where her mouth closes."""
    f = sorted(glob.glob(str(ROOT / f"media/clips/local/{cid}-*.mp4")))
    fr, rate = frames(Path(f[-1]))
    t = min(T, w1) - GRID_T0
    im = fr[max(0, min(len(fr) - 1, round(t * rate)))]
    return ImageOps.mirror(im) if flip else im


def grid(g, T):
    im = Image.new("RGB", (W, H), (8, 8, 8))
    cw, ch, gap = W // 2, H // 2, 4
    for k, cell in enumerate(g["cells"]):
        cid, w0, w1 = cell[:3]
        if T < w0 - 0.04:  # comes up on its word (a frame early, so it's there when the word lands)
            continue
        x, y = (k % 2) * cw, (k // 2) * ch
        im.paste(cover(version(cid, T, w0, w1, "flip" in cell), cw - gap, ch - gap), (x + gap // 2, y + gap // 2))
    if g.get("fill") and T >= g["fill"][1] - 0.04:  # the last "fine" takes the whole grid, over the cells (Lati, 1 Nov)
        cell = g["fill"]
        return cover(version(cell[0], T, cell[1], cell[2], "flip" in cell), W, H)
    if g.get("centre") and T >= g["centre"][1] - 0.04:
        cid, w0, w1 = g["centre"]
        cw2, ch2 = round(W * 0.56), round(H * 0.56)
        c = cover(version(cid, T, w0, w1), cw2, ch2)
        x, y = (W - cw2) // 2, (H - ch2) // 2
        ImageDraw.Draw(im).rectangle((x - 6, y - 6, x + cw2 + 5, y + ch2 + 5), fill=(8, 8, 8))
        im.paste(c, (x, y))
    return im


def build(sid, spec, shot):
    segs = spec.get("segments") or [spec]
    t0, t1 = float(shot["t0"]), float(shot["t1"])
    out = av.open(str(SHOT / f"{sid}.mp4"), "w")
    vs = out.add_stream("libx264", rate=FPS)
    vs.width, vs.height, vs.pix_fmt = W, H, "yuv420p"
    vs.options = {"crf": "18", "preset": "veryfast"}
    for n in range(round(t0 * FPS), round(t1 * FPS)):
        T = n / FPS
        seg = next((s for s in segs if T < s.get("until", 1e9)), segs[-1])
        if "card" in seg:
            im = card(seg["card"])
        elif "grid" in seg:
            im = grid(GRIDS[seg["grid"]], T)
        else:
            im = take_frame(seg["src"], T, seg)
        if "punch" in seg:
            im = punch(im, T, seg["punch"])
        for p in vs.encode(av.VideoFrame.from_image(im)):
            out.mux(p)
    for p in vs.encode():
        out.mux(p)
    out.close()


def clipbook(b):
    have = {Path(f).name.split("-")[0] for f in glob.glob(str(ROOT / "media/clips/local/*.mp4"))}
    book = [{"id": c["id"], "kind": c["kind"], "shots": c.get("shots", []), "t0": c["t0"], "t1": c["t1"]}
            for c in b["clips"] if c["id"] in have]
    (ROOT / "production/motion/clipbook.json").write_text(json.dumps(book, indent=1) + "\n")
    return [e["id"] for e in book]


def main():
    global GRIDS
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    cut = json.loads((ROOT / a.spec).read_text())
    GRIDS = cut.get("grids", {})
    b = json.loads((ROOT / "production/board/board.json").read_text())
    shots = {s["id"]: s for s in b["shots"]}
    picks = ROOT / "production/edit/picks-lati.json"  # Lati's picks from the clip library override the spec
    for p in json.loads(picks.read_text()) if picks.exists() else []:
        if p.get("folded"):
            continue
        t0 = float(shots[p["shot"]]["t0"])
        at = t0 - p["in"] if p.get("in") is not None else p["offset"] if p.get("offset") is not None else t0
        if (ROOT / p["clip"]).resolve() == (SHOT / f"{p['shot']}.mp4").resolve():
            cut["shots"].pop(p["shot"], None)  # the shot's own built file (a layered shot): keep it as it is
            continue
        cut["shots"][p["shot"]] = {"src": f"file:{p['clip']}", "at": at, "note": f"Lati's pick ({p['at']})"}
    if a.fit:
        for f in cut["fits"]:
            subprocess.run([str(ROOT / "media/cache/listen-venv/bin/python"), str(ROOT / "production/tools/beatfit.py"),
                            str(ROOT / f"media/clips/grok/k25/{f['take']}.mp4"), "--at", str(f["at"]), "--no-dot",
                            "--out-dir", "media/clips/fit"] + (["--lips"] if f.get("lips") else []), check=True)
    SHOT.mkdir(parents=True, exist_ok=True)
    only = set(a.only.split(",")) - {""}
    for sid, spec in cut["shots"].items():
        if only and sid not in only:
            continue
        build(sid, spec, shots[sid])
        print(sid, "->", f"media/clips/shot/{sid}.mp4", spec.get("note", ""))
    print("clip book:", ", ".join(clipbook(b)))


if __name__ == "__main__":
    main()

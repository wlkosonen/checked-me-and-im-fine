#!/usr/bin/env python3
"""The clip library: one index of every clip, for finding and swapping takes (Lati, 26 Oct: "If I wanted to change one
dance clip to another, I'd have to go through folders by hand … We need a system.").

    media/cache/listen-venv/bin/python production/tools/library.py        # (CPU; cached, so re-runs are quick)

Scans the kept local clips (InfiniteTalk S*, Wan M*), superseded ones, every Grok take (the 25 Oct kit takes and the
pilot), and the layered 2.5D shots. Per clip: source, kind (sung / dance / motion / layers), the shot it was made for
and that shot's framing and place, length, Grok's own tempo, how much it moves (mean frame difference), the words
Whisper hears in sung Grok takes, Lati's verdict and its status (production/library/notes.json), and which shots use
it now (the cut list, the clip book, the grids, the layered shots). Writes production/library/clips.json and an
8-frame filmstrip per clip to media/library/strips/. The review player's library page reads both.
"""
import json
import re
import subprocess
from pathlib import Path

import av
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "production/library/clips.json"
STRIPS = ROOT / "media/library/strips"
CACHE = ROOT / "media/library/cache.json"
PLACES = [("mic", ("lips",)), ("black", ("black",)), ("phone", ("phone screen", "phone light", "in the phone")),
          ("call", ("call", "shared screen")), ("desk", ("desk", "laptop")),
          ("keynote", ("keynote", "slide", "podium", "lectern", "corporate", "hall", "answer cards")),
          ("concert", ("concert", "stage", "led wall", "dancers", "crowd", "rig", "arena"))]


def place(shot):
    st = shot["set"].lower()
    return next((p for p, keys in PLACES if any(k in st for k in keys)), st)


def probe(path):
    c = av.open(str(path))
    s = c.streams.video[0]
    fps = float(s.average_rate)
    frames = [f.to_ndarray(format="rgb24") for f in c.decode(video=0)]
    return fps, frames


def strip(frames, out):
    idx = np.linspace(0, len(frames) - 1, 8).round().astype(int)
    tiles = []
    for i in idx:
        f = frames[i]
        h, w = f.shape[:2]
        s = 108 / h
        t = cv2.resize(f, (round(w * s), 108), interpolation=cv2.INTER_AREA)
        if t.shape[1] > 192:  # centre-crop to 16:9 tiles
            x = (t.shape[1] - 192) // 2
            t = t[:, x:x + 192]
        else:
            t = cv2.copyMakeBorder(t, 0, 0, 0, 192 - t.shape[1], cv2.BORDER_CONSTANT)
        tiles.append(t)
    cv2.imwrite(str(out), cv2.cvtColor(np.hstack(tiles), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 82])


def energy(frames):
    g = [cv2.resize(cv2.cvtColor(f, cv2.COLOR_RGB2GRAY), (64, 36)).astype(np.float32) for f in frames]
    d = [float(np.mean(np.abs(g[i] - g[i - 1]))) for i in range(1, len(g))]
    return round(float(np.median(d)) if d else 0.0, 2)


def bpm(path):
    import librosa
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", "22050", "-f", "f32le",
                          "-"], capture_output=True).stdout
    if len(raw) < 22050 * 4:
        return None
    y = np.frombuffer(raw, dtype=np.float32)
    if float(np.abs(y).max()) < 1e-3:
        return None
    t, _ = librosa.beat.beat_track(y=y, sr=22050)
    return round(float(np.atleast_1d(t)[0]), 1)


_whisper = None


def heard(path):
    global _whisper
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = os.environ["HIP_VISIBLE_DEVICES"] = ""
    import whisper
    if _whisper is None:
        _whisper = whisper.load_model("turbo", device="cpu", download_root=str(ROOT / "media/cache/listen-models/whisper"))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le",
                          "-"], capture_output=True).stdout
    if not raw:
        return ""
    r = _whisper.transcribe(np.frombuffer(raw, np.float32).copy(), language="en", fp16=False)
    return r["text"].strip()


def main():
    board = json.loads((ROOT / "production/board/board.json").read_text())
    shots = {s["id"]: s for s in board["shots"]}
    notes = {k: v for k, v in json.loads((ROOT / "production/library/notes.json").read_text()).items() if k[0] != "_"}
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    STRIPS.mkdir(parents=True, exist_ok=True)

    used = {}  # clip id -> shots

    def use(cid, sid):
        used.setdefault(cid, set()).add(sid)
    cut = json.loads((ROOT / "production/edit/cut-v3.json").read_text())
    picks = ROOT / "production/edit/picks-lati.json"
    for sid, sp in list(cut["shots"].items()) + ([(p["shot"], p) for p in json.loads(picks.read_text())]
                                                 if picks.exists() else []):
        for seg in sp.get("segments") or [sp]:
            src = seg.get("src") or seg.get("clip") or ""
            name = src.split(":", 1)[-1]
            name = re.sub(r"-(beat|lips)$", "", Path(name).stem)
            if name:
                use(name, sid)
            if seg.get("grid"):
                for c in cut["grids"][seg["grid"]]["cells"] + [cut["grids"][seg["grid"]].get("centre") or []]:
                    if c:
                        use(c[0], sid)
    book = {e["id"]: e for e in json.loads((ROOT / "production/motion/clipbook.json").read_text())}
    for cid, e in book.items():
        for sid in e.get("shots", []):
            if sid not in cut["shots"]:
                use(cid, sid)

    files = []
    for f in sorted((ROOT / "media/clips/local").glob("*.mp4")):
        files.append((f, "infinitetalk" if f.name[0] == "S" else "wan", False))
    for f in sorted((ROOT / "media/clips/local/superseded").glob("*.mp4")):
        files.append((f, "infinitetalk" if f.name[0] == "S" else "wan", True))
    for f in sorted((ROOT / "media/clips/grok/k25").glob("*.mp4")):
        files.append((f, "grok", False))
    for f in sorted((ROOT / "media/clips/grok").glob("*.mp4")):
        files.append((f, "grok-pilot", False))
    for f in sorted((ROOT / "media/clips/shot").glob("*.mp4")):
        if (ROOT / f"media/layers/{f.stem}_room_00001_.png").exists():
            files.append((f, "layers", False))

    out = []
    for f, source, superseded in files:
        rel = str(f.relative_to(ROOT))
        stem = f.stem
        key = f"{rel}:{f.stat().st_mtime:.0f}"
        c = cache.get(key, {})
        m = re.match(r"([sS]\d{3})", stem) or re.match(r"[SM](\d{3})", stem)
        made_for = None
        if source in ("grok", "layers"):
            made_for = stem[:4].lower()
        elif source in ("infinitetalk", "wan"):
            cid = re.match(r"([SM]\d{3}[A-E]?)", stem).group(1)
            bc = next((x for x in board["clips"] if x["id"] == cid), None)
            made_for = (bc["shots"][0] if bc else "s" + cid[1:4]) if not cid.startswith("S029") or len(cid) == 4 else "s029"
        sh = shots.get(made_for) if made_for else None
        if source == "grok":
            kind = "sung" if sh and sh["route"] == "grok" else "dance"
        elif source == "grok-pilot":
            kind = "sung" if re.search(r"-p\d|sing", stem) else "dance"
        else:
            kind = {"infinitetalk": "sung", "wan": "motion", "layers": "layers"}[source]
        if "frames" not in c or not (STRIPS / f"{stem}.jpg").exists():
            fps, frames = probe(f)
            strip(frames, STRIPS / f"{stem}.jpg")
            h, w = frames[0].shape[:2]
            c.update(frames=len(frames), fps=fps, w=w, h=h, energy=energy(frames))
        if source.startswith("grok") and "bpm" not in c:
            c["bpm"] = bpm(f)
        if source.startswith("grok") and kind == "sung" and "heard" not in c:
            c["heard"] = heard(f)
        cache[key] = c
        nk = max((k for k in notes if stem.startswith(k)), key=len, default=None)
        note = notes.get(nk, {})
        status = note.get("status") or ("reject" if superseded else "keep" if source in ("infinitetalk", "wan", "layers")
                                        else "spare")
        if superseded:  # an old take of a clip that has a newer one; its verdict belongs to the new one
            status, note = "reject", {"note": "superseded by a newer take"}
        cid = re.sub(r"-(fast|hq).*", "", stem)
        users = [] if superseded else sorted(used.get(stem, set()) | used.get(cid, set()) |
                                             ({made_for} if source == "layers" else set()))
        out.append({"id": stem, "path": rel, "source": source, "kind": kind, "made_for": made_for,
                    "framing": sh["framing"] if sh else None, "place": place(sh) if sh else None,
                    "seconds": round(c["frames"] / c["fps"], 2), "fps": round(c["fps"], 2), "size": f"{c['w']}x{c['h']}",
                    "energy": c["energy"], "bpm": c.get("bpm"), "heard": c.get("heard"),
                    "status": status if not users or status == "reject" else "in cut", "verdict": note.get("note"),
                    "reviewed": bool(nk) or superseded,  # Lati has a verdict, a note or a "seen" on it (notes.json)
                    "used_by": users, "strip": f"media/library/strips/{stem}.jpg"})
        print(f"{stem:42} {source:12} {kind:7} {out[-1]['status']:7} {','.join(users)}", flush=True)
    CACHE.write_text(json.dumps(cache))
    OUT.write_text(json.dumps({"clips": out}, indent=1) + "\n")
    print(len(out), "clips ->", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()

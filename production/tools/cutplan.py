#!/usr/bin/env python3
"""What plays in each shot: the one answer, used by the live cut preview and by gfxrender.py."""

import json
from pathlib import Path
from time import mktime, strptime

ROOT = Path(__file__).resolve().parents[2]
PICKS = ROOT / "production/edit/picks-lati.json"


def gfx_file(sid):
    f = sorted((ROOT / "media/gfx").glob(f"*/{sid}.mp4"))
    return f[0] if f else None


def plan(gfx=True):
    """Lati's pick, else the built shot (shots.py, layers.py), else the kept clip from the clip book, else the picked
    plate as a still. at = song time of the file's time 0. With gfx, a shot's graphics render (gfxrender.py) plays
    instead, unless a pick is newer than it: a pick tried on /cut shows at once, and the next render takes it in."""
    board = json.loads((ROOT / "production/board/board.json").read_text())
    picks = {p["shot"]: p for p in (json.loads(PICKS.read_text()) if PICKS.exists() else []) if not p.get("folded")}
    plates = json.loads((ROOT / "production/board/picks.json").read_text())
    book = {e["id"]: e for e in json.loads((ROOT / "production/motion/clipbook.json").read_text())}
    out = []
    for s in board["shots"]:
        t0, t1, sid = float(s["t0"]), float(s["t1"]), s["id"]
        e = {"id": sid, "t0": t0, "t1": t1, "route": s["route"], "framing": s["framing"]}
        p, built, cid = picks.get(sid), ROOT / f"media/clips/shot/{sid}.mp4", s.get("clip")
        g = gfx_file(sid) if gfx else None
        if g and not (p and mktime(strptime(p["at"], "%Y-%m-%d %H:%M:%S")) > g.stat().st_mtime):
            e.update(kind="video", file=str(g.relative_to(ROOT)), at=t0, src="gfx")
        elif p:
            e.update(kind="video", file=p["clip"], src="pick",
                     at=t0 - p["in"] if p.get("in") is not None else p["offset"] if p.get("offset") is not None else t0)
        elif built.exists():
            e.update(kind="video", file=str(built.relative_to(ROOT)), at=t0, src="shot")
        elif cid in book:
            f = sorted((ROOT / "media/clips/local").glob(f"{cid}-*.mp4"))
            e.update(kind="video", file=str(f[-1].relative_to(ROOT)), at=book[cid]["t0"], src="clip")
        elif (plates.get(s.get("plate") or "") or {}).get("file"):
            e.update(kind="image", file=plates[s["plate"]]["file"], src="still")
        else:
            e.update(kind="none", src="none")
        out.append(e)
    return {"duration": board["duration"], "shots": out}

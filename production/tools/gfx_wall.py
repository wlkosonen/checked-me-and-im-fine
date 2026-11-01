#!/usr/bin/env python3
"""How the stage wall drifts in a shot, so a graphic on it stays on it.

    media/cache/gfx-venv/bin/python production/tools/gfx_wall.py s017 s018 --ref 513

The stage takes keep a white band along the foot of the wall, and their camera creeps. This finds the band's top edge
in every frame and writes the shift from --ref (the edge's height in 720p pixels on the frame the wall's quad was set
on) to media/cache/gfx/plane-<sid>.json, as gfx.plane() reads it. Vertical only: the sides moved under 6 px in s017-s018,
measured. Smoothed between cuts inside a shot; a jump of more than 10 px is a change of take and is kept.
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfxrender  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
UNITS = 1080 / 720
FPS = 25


def edge(g, last):
    ys = (g[:, 200:1000] > 205).mean(axis=1)
    ys[:380] = 0
    hit = np.flatnonzero(ys > 0.5)
    return float(hit[0]) if len(hit) else last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots", nargs="+")
    ap.add_argument("--ref", type=float, required=True)
    a = ap.parse_args()
    film = gfxrender.Film()
    board = {s["id"]: s for s in json.loads((ROOT / "production/board/board.json").read_text())["shots"]}
    for sid in a.shots:
        ys, last = [], a.ref
        t0, t1 = float(board[sid]["t0"]), float(board[sid]["t1"])
        for n in range(round(t0 * FPS), round(t1 * FPS)):
            last = edge(cv2.cvtColor(film.picture(sid, n / FPS), cv2.COLOR_RGB2GRAY), last)
            ys.append(last)
        ys = np.array(ys)
        cuts = [0] + [i + 1 for i in np.flatnonzero(np.abs(np.diff(ys)) > 10)] + [len(ys)]
        for i, j in zip(cuts, cuts[1:]):  # a straight line through each stretch: the edge is read to the pixel, the drift is slow
            if j - i > 3:
                x = np.arange(i, j)
                ys[i:j] = np.polyval(np.polyfit(x, ys[i:j], 2), x)
        H = [[[1, 0, 0], [0, 1, float((y - a.ref) * UNITS)], [0, 0, 1]] for y in ys]
        out = ROOT / f"media/cache/gfx/plane-{sid}.json"
        out.write_text(json.dumps({"t": [round(t0 * FPS + i) / FPS for i in range(len(ys))], "H": H}))
        print(sid, "edge", round(ys[0], 1), "->", round(ys[-1], 1), "takes", len(cuts) - 1)


if __name__ == "__main__":
    main()

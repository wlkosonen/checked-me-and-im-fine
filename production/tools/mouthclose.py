#!/usr/bin/env python3
"""When does her mouth close after a sung word? For the "fine" grids (Lati, 1 Nov: "Fine" frames should play until her
mouth is closed).

    media/cache/face-venv/bin/python production/tools/mouthclose.py production/edit/cut-v3.json

For each grid cell, reads the InfiniteTalk version around its word, measures the lip gap (InsightFace 106 points, inner
lips, as a share of the face height) and prints the first time after the word's end that the gap is near its closed
level, or the smallest gap if she never closes before the window ends. CPU.
"""
import glob
import json
import sys
from pathlib import Path

import av
import numpy as np
from insightface.app import FaceAnalysis

ROOT = Path(__file__).resolve().parents[2]
GRID_T0, LOOK = 65.40, 0.8


def gaps(app, cid):
    f = sorted(glob.glob(str(ROOT / f"media/clips/local/{cid}-*.mp4")))[-1]
    c = av.open(f)
    rate = float(c.streams.video[0].average_rate)
    out = []
    for i, fr in enumerate(c.decode(video=0)):
        faces = app.get(fr.to_ndarray(format="bgr24"))
        if not faces:
            out.append(np.nan)
            continue
        fc = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
        out.append(float(np.linalg.norm(fc.landmark_2d_106[71] - fc.landmark_2d_106[53]) / (fc.bbox[3] - fc.bbox[1])))
    return np.array(out), rate


def main():
    app = FaceAnalysis(name="buffalo_l", root=str(ROOT / "media/cache/face"), providers=["CPUExecutionProvider"],
                       allowed_modules=["detection", "landmark_2d_106"])
    app.prepare(ctx_id=-1, det_size=(640, 640))
    grids = json.loads((ROOT / sys.argv[1]).read_text())["grids"]
    cache = {}
    for name, g in grids.items():
        for cell in g["cells"] + ([g["centre"]] if g.get("centre") else []):
            cid, w0, w1 = cell[:3]
            if cid not in cache:
                cache[cid] = gaps(app, cid)
            gap, rate = cache[cid]
            closed = np.nanpercentile(gap, 10) * 1.4  # her closed level in this clip, with a margin
            a, b = round((w0 - GRID_T0) * rate), min(round((w1 + LOOK - GRID_T0) * rate), len(gap) - 1)
            ws = round((w1 - GRID_T0) * rate)
            after = [i for i in range(ws, b + 1) if gap[i] <= closed]
            i = after[0] if after else ws + int(np.nanargmin(gap[ws:b + 1]))
            print(f"{name} {cid} word {w0}-{w1} closed<={closed:.3f} -> {GRID_T0 + i / rate:.2f}"
                  f"{'' if after else ' (never closes, smallest gap)'} gap {[round(float(x), 3) for x in gap[ws:b + 1:2]]}")


if __name__ == "__main__":
    main()

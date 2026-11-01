#!/usr/bin/env python3
"""Measure how a reference music video gets from one shot to the next: hard cut, zoom through the cut, flash, black
frame, blur, or a gradual transition (dissolve, wipe, morph).

    media/cache/face-venv/bin/python production/tools/transitions.py media/reference/NAME.mp4     # (CPU)

Lati, 25 Oct: "Cuts between scenes are not abrupt … NOW SERVING shifts between scenes via slight zoom in-zoom out
pulse. KILL SWITCH has transitions done in graphics." For the graphics brief: what kinds, how often, how long.

- Hard cuts: as refcut.py (a frame difference far above its neighbours).
- Zoom through a cut: frame-to-frame scale from tracked corners (LK flow, a similarity fit) over the 6 frames before
  and after; "zoom" when the frames push in by more than 1.5% into the cut or ease back by more than 1.5% after it.
- Flash / black: mean brightness within a frame of the cut 25 levels above / below the shots either side.
- Blur: sharpness (Laplacian variance) within 2 frames of the cut under 40% of the shots either side.
- Gradual: a run of 3-15 frames whose differences are all high but none a hard cut, where the frames before and
  after the run differ like two shots. A wipe, dissolve or morph; the sheet shows which.
Writes media/reference/NAME/transitions.json and a sheet of the gradual ones (start, middle, end).
"""
import json
import sys
from pathlib import Path

import av
import cv2
import numpy as np

W, H = 320, 180


def load(path):
    c = av.open(str(path))
    fps = float(c.streams.video[0].average_rate)
    g = [cv2.resize(f.to_ndarray(format="gray"), (W, H), interpolation=cv2.INTER_AREA) for f in c.decode(video=0)]
    return fps, g


def scale_step(a, b):
    p = cv2.goodFeaturesToTrack(a, 120, 0.01, 8)
    if p is None or len(p) < 12:
        return 1.0
    q, st, _ = cv2.calcOpticalFlowPyrLK(a, b, p, None)
    ok = st.ravel() == 1
    if ok.sum() < 10:
        return 1.0
    m, _ = cv2.estimateAffinePartial2D(p[ok], q[ok])
    return float(np.hypot(m[0, 0], m[1, 0])) if m is not None else 1.0


def main():
    src = Path(sys.argv[1])
    out = src.parent / src.stem
    out.mkdir(exist_ok=True)
    fps, g = load(src)
    gf = [x.astype(np.float32) for x in g]
    d = np.array([0.0] + [float(np.mean(np.abs(gf[i] - gf[i - 1]))) for i in range(1, len(g))])
    bright = np.array([float(x.mean()) for x in g])
    sharp = np.array([float(cv2.Laplacian(x, cv2.CV_32F).var()) for x in g])
    cuts = [0]
    for i in range(1, len(d)):
        loc = np.concatenate([d[max(1, i - 6):i], d[i + 1:i + 7]])
        med = float(np.median(loc)) if len(loc) else 0.0
        if d[i] > 18 and d[i] > 4 * med + 6 and i - cuts[-1] > 5:
            cuts.append(i)
    rows = []
    for i in cuts[1:]:
        if i < 8 or i > len(g) - 8:
            continue
        pre = np.prod([scale_step(g[k - 1], g[k]) for k in range(i - 5, i)])     # into the cut
        post = np.prod([scale_step(g[k - 1], g[k]) for k in range(i + 1, i + 6)])  # after it
        side_b = np.median(np.concatenate([bright[i - 8:i - 2], bright[i + 2:i + 8]]))
        side_s = np.median(np.concatenate([sharp[i - 8:i - 2], sharp[i + 2:i + 8]]))
        near_b = bright[i - 1:i + 2]
        kinds = []
        if pre > 1.015 or post < 1 / 1.015:
            kinds.append("zoom")
        if near_b.max() > side_b + 25:
            kinds.append("flash")
        if near_b.min() < side_b - 25 and near_b.min() < 20:
            kinds.append("black")
        if sharp[i - 2:i + 3].min() < 0.4 * side_s:
            kinds.append("blur")
        rows.append({"t": round(i / fps, 3), "kind": kinds or ["hard"], "zoom_in": round(float(pre), 4),
                     "zoom_after": round(float(post), 4)})
    # gradual: runs of high difference with no hard cut inside
    base = float(np.median(d))
    hi = d > max(6.0, 3 * base)
    grad, k = [], 1
    cutset = set(cuts)
    while k < len(d):
        if hi[k] and k not in cutset:
            j = k
            while j + 1 < len(d) and hi[j + 1] and (j + 1) not in cutset:
                j += 1
            if 3 <= j - k + 1 <= 15 and k > 1 and j + 2 < len(g):
                if float(np.mean(np.abs(gf[j + 1] - gf[k - 1]))) > 25:
                    grad.append({"t0": round(k / fps, 3), "t1": round((j + 1) / fps, 3), "frames": j - k + 1})
            k = j + 1
        k += 1
    from collections import Counter
    count = Counter(x for r in rows for x in r["kind"])
    res = {"source": src.name, "fps": fps, "cuts": len(rows), "kinds": dict(count), "gradual": grad, "rows": rows}
    (out / "transitions.json").write_text(json.dumps(res, indent=1))
    if grad:
        want = []
        for gr in grad[:24]:
            a, b = round(gr["t0"] * fps) - 1, round(gr["t1"] * fps)
            want += [a, (a + b) // 2, b]
        keep = {}  # only the frames the sheet needs: decoding all of a 1080p film in colour would take ~36 GB
        for n, f in enumerate(av.open(str(src)).decode(video=0)):
            if n in want:
                keep[n] = cv2.resize(f.to_ndarray(format="rgb24"), (320, 180))
            if n > max(want):
                break
        tiles = []
        for gi, gr in enumerate(grad[:24]):
            for idx in want[gi * 3:gi * 3 + 3]:
                im = keep.get(idx, np.zeros((180, 320, 3), np.uint8)).copy()
                cv2.putText(im, f"{gr['t0']:.1f}s", (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                tiles.append(im)
        rows_im = [np.hstack(tiles[r:r + 3]) for r in range(0, len(tiles), 3)]
        cv2.imwrite(str(out / "transitions-gradual.jpg"), cv2.cvtColor(np.vstack(rows_im), cv2.COLOR_RGB2BGR))
    print(f"{src.name}: {len(rows)} cuts: " + ", ".join(f"{k} {v}" for k, v in count.most_common())
          + f"; gradual transitions: {len(grad)} (" + ", ".join(f"{x['t0']:.1f}s/{x['frames']}f" for x in grad[:12])
          + (")" if len(grad) <= 12 else " …)"))


if __name__ == "__main__":
    main()

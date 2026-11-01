#!/usr/bin/env python3
"""Find shots of an avatar that can sit in a call tile: one large face, turned to us, a steady camera, little singing.

    media/cache/face-venv/bin/python production/tools/avatarscan.py media/reference/avatars/NAME.mp4 [--top 8]    # CPU

Lati, 1 Nov: the call's avatars move a little, so each tile plays a short piece of its maker's own video. Reads the
video at 3 fps; hard cuts split it into shots; each stretch of at least 2.5 s in a shot is scored on face size,
how frontal it is, stillness and a closed mouth. Writes media/reference/avatars/NAME-scan.jpg, one candidate per row,
with its start time: Lati's eye picks.
"""
import argparse
from pathlib import Path

import av
import cv2
import numpy as np
from insightface.app import FaceAnalysis

ROOT = Path(__file__).resolve().parents[2]
RATE, MIN_S = 3, 2.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--min-s", type=float, default=MIN_S)
    ap.add_argument("--min-face", type=float, default=0.28)
    a = ap.parse_args()
    app = FaceAnalysis(name="buffalo_l", root=str(ROOT / "media/cache/face"), providers=["CPUExecutionProvider"],
                       allowed_modules=["detection", "landmark_2d_106"])
    app.prepare(ctx_id=-1, det_size=(320, 320))
    c = av.open(str(ROOT / a.video))
    fps = float(c.streams.video[0].average_rate)
    step = round(fps / RATE)
    rows, thumbs = [], []
    for i, f in enumerate(c.decode(video=0)):
        if i % step:
            continue
        im = cv2.resize(f.to_ndarray(format="bgr24"), (640, 360))
        faces = [x for x in app.get(im) if x.det_score > 0.6]
        g = cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (160, 90)).astype(np.float32)
        r = {"t": i / fps, "g": g, "n": len(faces), "h": 0.0, "front": 9.0, "gap": 0.0}
        if faces:
            x = max(faces, key=lambda q: q.bbox[3] - q.bbox[1])
            eye = (x.kps[0] + x.kps[1]) / 2
            r["h"] = float((x.bbox[3] - x.bbox[1]) / 360)
            r["front"] = float(abs(x.kps[2][0] - eye[0]) / max(np.linalg.norm(x.kps[0] - x.kps[1]), 1))
            r["gap"] = float(np.linalg.norm(x.landmark_2d_106[71] - x.landmark_2d_106[53]) / (x.bbox[3] - x.bbox[1]))
        rows.append(r)
        thumbs.append(im)
    d = [0.0] + [float(np.abs(rows[i]["g"] - rows[i - 1]["g"]).mean()) for i in range(1, len(rows))]
    cuts = [i for i in range(1, len(d)) if d[i] > 18]  # a hard cut
    edges = [0] + cuts + [len(rows)]
    n = round(a.min_s * RATE)
    found = []
    for a0, b0 in zip(edges, edges[1:]):
        for s in range(a0, b0 - n + 1, 2):
            w = rows[s:s + n]
            if any(r["n"] != 1 for r in w):
                continue
            h, fr, gap = np.mean([r["h"] for r in w]), np.mean([r["front"] for r in w]), np.mean([r["gap"] for r in w])
            move = float(np.mean(d[s + 1:s + n]))
            if h < a.min_face or fr > 0.22 or not 0.15 < move < 7:
                continue  # small, turned away, a frozen frame, or too much camera
            found.append((min(h, 0.6) * 3 - fr * 4 - move * 0.12 - gap * 3, s, h, fr, gap, move))
    found.sort(reverse=True)
    picks = []
    for f in found:
        if all(abs(rows[f[1]]["t"] - rows[p[1]]["t"]) > 6 for p in picks):
            picks.append(f)
        if len(picks) == a.top:
            break
    out = []
    for f in picks:
        s = f[1]
        print(f"{rows[s]['t']:7.2f} s  face {f[2]:.2f}  turn {f[3]:.2f}  mouth {f[4]:.2f}  move {f[5]:.1f}")
        row = [cv2.resize(thumbs[s + k], (320, 180)) for k in (0, n // 3, 2 * n // 3, n - 1)]
        cv2.putText(row[0], f"{rows[s]['t']:.1f}s", (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        out.append(np.hstack(row))
    p = ROOT / a.video.replace(".mp4", "-scan.jpg")
    if out:
        cv2.imwrite(str(p), np.vstack(out), [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(len(rows), "samples,", len(cuts), "cuts,", len(found), "windows ->", p.name)


if __name__ == "__main__":
    main()

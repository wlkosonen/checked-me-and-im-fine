#!/usr/bin/env python3
"""Depth parallax on a picked plate: the classic "3D photo" move, with nothing cut out or painted.

    ~/ComfyUI/venv/bin/python production/tools/depth25.py s009 s069 [--push 0.03] [--drift 0.012]   # CPU

Lati, 26 Oct, after both layered routes failed (cut-outs with halos, rooms with broken geometry, limbs cut off):
keep his picked plate whole. Depth Anything V2 (small, on the CPU) estimates how near each pixel is; each frame pushes
in and drifts sideways, near pixels more than far ones, through one smooth warp of the original image. The depth map
is softened so edges stretch a little rather than tear. Writes media/layers/preview/<sid>_depth.mp4 over the shot's
board window (1280x720, 25 fps) and the depth map to media/layers/<sid>_depth.png.
"""
import argparse
import json
from pathlib import Path

import av
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
W, H, FPS = 1280, 720, 25


def cover(im, interp=cv2.INTER_LANCZOS4):
    h, w = im.shape[:2]
    s = max(W / w, H / h)
    im = cv2.resize(im, (round(w * s), round(h * s)), interpolation=interp)
    y, x = (im.shape[0] - H) // 2, (im.shape[1] - W) // 2
    return im[y:y + H, x:x + W]


def depth_of(img_rgb):
    import torch
    from PIL import Image
    from transformers import pipeline
    pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device="cpu")
    with torch.no_grad():
        d = np.array(pipe(Image.fromarray(img_rgb))["depth"], dtype=np.float32)
    d = cv2.resize(d, (img_rgb.shape[1], img_rgb.shape[0]), interpolation=cv2.INTER_CUBIC)
    d = (d - d.min()) / max(d.max() - d.min(), 1e-6)  # 1 = nearest
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sids", nargs="+")
    ap.add_argument("--push", type=float, default=0.03, help="extra push-in for the nearest pixels over the shot")
    ap.add_argument("--drift", type=float, default=0.012, help="sideways drift of the nearest pixels, frame fraction")
    a = ap.parse_args()
    board = json.loads((ROOT / "production/board/board.json").read_text())
    shots = {s["id"]: s for s in board["shots"]}
    picks = json.loads((ROOT / "production/board/picks.json").read_text())
    (ROOT / "media/layers/preview").mkdir(parents=True, exist_ok=True)
    for sid in a.sids:
        src = cv2.cvtColor(cv2.imread(str(ROOT / picks[f"p-{sid}"]["file"])), cv2.COLOR_BGR2RGB)
        img = cover(src)
        d = depth_of(img)
        cv2.imwrite(str(ROOT / f"media/layers/{sid}_depth.png"), (d * 255).astype(np.uint8))
        d = cv2.GaussianBlur(d, (0, 0), 7)  # soft depth: edges stretch a little instead of tearing
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        cx, cy = W / 2, H / 2
        s = shots[sid]
        n = round((s["t1"] - s["t0"]) * FPS)
        out = av.open(str(ROOT / f"media/layers/preview/{sid}_depth.mp4"), "w")
        vs = out.add_stream("libx264", rate=FPS)
        vs.width, vs.height, vs.pix_fmt = W, H, "yuv420p"
        vs.options = {"crf": "18", "preset": "veryfast"}
        for i in range(n):
            k = i / max(n - 1, 1)
            k = k * k * (3 - 2 * k) * 0.6 + k * 0.4
            z = 1 + 0.012 * k + a.push * k * d          # everything pushes in a little, near pixels more
            dx = -a.drift * W * k * (d - 0.3)            # near pixels drift one way, far ones barely
            mx = cx + (xx - cx) / z - dx
            my = cy + (yy - cy) / z
            fr = cv2.remap(img, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            for p in vs.encode(av.VideoFrame.from_ndarray(fr, format="rgb24")):
                out.mux(p)
        for p in vs.encode():
            out.mux(p)
        out.close()
        print(f"{sid}: {n} frames -> media/layers/preview/{sid}_depth.mp4", flush=True)


if __name__ == "__main__":
    main()

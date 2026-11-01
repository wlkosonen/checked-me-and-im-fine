#!/usr/bin/env python3
"""Her matte (and her dancers'), so a graphic can sit behind them on the wall: Robust Video Matting on the CPU.

    media/cache/gfx-venv/bin/python production/tools/gfx_matte.py s017 s018 ...

Reads the shot as /cut plays it (cutplan.py) and writes media/cache/gfx/matte-<sid>.mp4, the matte as a grey 1280x720
video, frame for frame with the shot. RVM carries state from frame to frame, so the edge doesn't boil. Model:
PeterL1n/RobustVideoMatting, mobilenetv3, media/cache/gfx-models/ (a tool here, not shipped; GPL-3.0).
"""

import sys
import time
from pathlib import Path

import av
import numpy as np
import onnxruntime as ort

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
import gfxrender  # noqa: E402

ROOT = gfx.ROOT
MODEL = ROOT / "media/cache/gfx-models/rvm_mobilenetv3_fp32.onnx"
OUT = ROOT / "media/cache/gfx"
DOWN = 0.5  # RVM's downsample ratio: the internal size, 640x360 here


def run(sid, film):
    s0 = gfx.SHOTS[sid]
    frames = [film.picture(sid, n / 25) for n in range(round(float(s0["t0"]) * 25), round(float(s0["t1"]) * 25))]
    so = ort.SessionOptions()
    so.intra_op_num_threads = 6
    s = ort.InferenceSession(str(MODEL), so, providers=["CPUExecutionProvider"])
    rec = [np.zeros((1, 1, 1, 1), np.float32) for _ in range(4)]
    ratio = np.array([DOWN], np.float32)
    h, w = frames[0].shape[:2]
    out = av.open(str(OUT / f"matte-{sid}.mp4"), "w")
    vs = out.add_stream("libx264", rate=25)
    vs.width, vs.height, vs.pix_fmt = w, h, "yuv420p"
    vs.options = {"crf": "12", "preset": "veryfast"}
    # settle the recurrent state on the first frame, so the shot's first frames are as good as the rest
    for f in frames[:1] * 6 + frames:
        x = (f.astype(np.float32) / 255).transpose(2, 0, 1)[None]
        r = s.run(None, {"src": x, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": ratio})
        pha, rec = r[1], r[2:]
        yield_a = np.clip(pha[0, 0] * 255, 0, 255).astype(np.uint8)
        yield yield_a, vs, out
    for p in vs.encode():
        out.mux(p)
    out.close()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    lock = gfxrender.take_lock()  # noqa: F841  held to the end: a matte is a render
    film = gfxrender.Film()
    for sid in sys.argv[1:]:
        t = time.time()
        n = 0
        for a, vs, out in run(sid, film):
            n += 1
            if n <= 6:
                continue
            f = av.VideoFrame.from_ndarray(np.dstack([a, a, a]), format="rgb24")
            for p in vs.encode(f):
                out.mux(p)
        print(sid, n - 6, "frames", f"{(n - 6) / (time.time() - t):.1f} fps")


if __name__ == "__main__":
    main()

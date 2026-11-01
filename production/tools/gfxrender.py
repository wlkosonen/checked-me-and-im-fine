#!/usr/bin/env python3
"""Render shots with their graphics, for /cut and for the final.

    media/cache/gfx-venv/bin/python production/tools/gfxrender.py s005 s017 [--check 15.5,16.4] [--height 1080]
    media/cache/gfx-venv/bin/python production/tools/gfxrender.py --film media/final/checked-me-1080p.mp4 --height 1080

Each shot becomes media/gfx/<section>/<sid>.mp4 (25 fps, exactly its window), which /cut then plays in its place. With
--check, no video: the frames at those song times go to media/gfx/<section>/check/ as JPEGs. The shot's picture is
whatever /cut would play without graphics (cutplan.py), with the beat kick and the cut pulse of the rough cut.

One render at a time: the 7600X has six cores and several agents, so a render waits for media/gfx/render.lock.
"""

import argparse
import fcntl
import math
import sys
import time
from fractions import Fraction
from pathlib import Path

import av
import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cutplan  # noqa: E402
import gfx  # noqa: E402
import roughcut  # noqa: E402

ROOT = gfx.ROOT
FPS = gfx.FPS


def zoom(f, z):
    """The frame scaled up by z about its centre, as roughcut.py does it."""
    if z < 1.0005:
        return f
    h, w = f.shape[:2]
    M = np.float32([[z, 0, w * (1 - z) / 2], [0, z, h * (1 - z) / 2]])
    return cv2.warpAffine(f, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


class Film:
    def __init__(self, height=720):
        self.h, self.w = height, round(height * 16 / 9 / 2) * 2
        self.plan = {e["id"]: e for e in cutplan.plan(gfx=False)["shots"]}
        self.order = [s["id"] for s in gfx.BOARD["shots"]]
        self.kicks = roughcut.kick_beats(2)
        self.kicks = self.kicks[self.kicks >= 13.074 - 1e-3]
        shots = gfx.BOARD["shots"]
        self.cuts = np.array([float(s["t0"]) for p, s in zip(shots, shots[1:]) if roughcut.place(s) != roughcut.place(p)
                              and "black" not in (roughcut.place(s), roughcut.place(p))])
        self.cache = {}

    def cover(self, a):
        h, w = a.shape[:2]
        s = max(self.w / w, self.h / h)
        a = cv2.resize(a, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LANCZOS4)
        y, x = (a.shape[0] - self.h) // 2, (a.shape[1] - self.w) // 2
        return a[y:y + self.h, x:x + self.w]

    def source(self, sid):
        e = self.plan[sid]
        key = e.get("file")
        if key not in self.cache:
            if len(self.cache) >= 3:
                self.cache.pop(next(iter(self.cache)))
            if e["kind"] == "video":
                c = av.open(str(ROOT / key))
                rate = float(c.streams.video[0].average_rate)
                self.cache[key] = ([self.cover(f.to_ndarray(format="rgb24")) for f in c.decode(video=0)], rate)
            elif e["kind"] == "image":
                self.cache[key] = ([self.cover(np.array(Image.open(ROOT / key).convert("RGB")))], 0.0)
            else:
                self.cache[key] = ([np.zeros((self.h, self.w, 3), np.uint8)], 0.0)
        return self.cache[key]

    def picture(self, sid, T):
        e = self.plan[sid]
        fr, rate = self.source(sid)
        if e["kind"] == "image":  # a still: the slow 3% push of the rough cut
            return zoom(fr[0], 1 + 0.03 * (T - e["t0"]) / max(e["t1"] - e["t0"], 1e-3))
        if not rate:
            return fr[0]
        at = round(e["at"] * FPS) / FPS if e["src"] == "shot" else e["at"]  # a built shot starts on the grid
        # floor, not round: round() goes to even on a half frame, and every other frame would show twice
        return fr[max(0, min(len(fr) - 1, math.floor((T - at) * rate + 0.5 + 1e-6)))]

    def under(self, sid, T):
        """The frame up to the transition: picture, section picture and world layer, kick, cut pulse."""
        f = gfx.scene(sid, T, self.picture(sid, T).copy())
        k = self.kicks[self.kicks <= T + 1e-6]
        z = 1 + 0.012 * float(np.exp(-(T - k[-1]) / 0.12)) if len(k) else 1.0
        c = self.cuts[self.cuts <= T + 1e-6]
        z *= 1 + 0.025 * float(np.exp(-(T - c[-1]) / 0.07)) if len(c) else 1.0
        return zoom(f, z)

    def frame(self, sid, T):
        f = self.under(sid, T)
        tr = gfx.transition(sid)
        t0 = float(gfx.SHOTS[sid]["t0"])
        if tr and T < t0 + tr[1] / FPS - 1e-6:
            prev = self.order[self.order.index(sid) - 1]
            A = self.under(prev, float(gfx.SHOTS[prev]["t1"]) - 1 / FPS)
            f = gfx.TRANSITIONS[tr[0]](A, f, ((T - t0) * FPS + 1) / (tr[1] + 1), T)
        return gfx.top(sid, T, f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots", nargs="*")
    ap.add_argument("--check", default="", help="song times: write these frames as JPEGs, no video")
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--crf", default="18")
    ap.add_argument("--film", default="", help="render the whole film with the song's audio to this file (see whole())")
    a = ap.parse_args()
    lock = take_lock()  # noqa: F841  held to the end
    film = Film(a.height)
    if a.film:
        return whole(film, a.film)
    for sid in a.shots:
        d = ROOT / "media/gfx" / gfx.section_of(sid)
        d.mkdir(exist_ok=True)
        s = gfx.SHOTS[sid]
        t0, t1 = float(s["t0"]), float(s["t1"])
        if a.check:
            (d / "check").mkdir(exist_ok=True)
            for T in [float(x) for x in a.check.split(",")]:
                if t0 <= T < t1:
                    p = d / "check" / f"{sid}-{T:07.3f}.jpg"
                    Image.fromarray(film.frame(sid, round(T * FPS) / FPS)).save(p, quality=90)
                    print(p.relative_to(ROOT))
            continue
        tmp = d / f".{sid}.tmp.mp4"
        out = av.open(str(tmp), "w", format="mp4")
        vs = out.add_stream("libx264", rate=FPS)
        vs.width, vs.height, vs.pix_fmt = film.w, film.h, "yuv420p"
        vs.options = {"crf": a.crf, "preset": "veryfast"}
        began = time.time()
        n0, n1 = round(t0 * FPS), round(t1 * FPS)
        for n in range(n0, n1):
            for p in vs.encode(av.VideoFrame.from_ndarray(film.frame(sid, n / FPS), format="rgb24")):
                out.mux(p)
        for p in vs.encode():
            out.mux(p)
        out.close()
        tmp.replace(d / f"{sid}.mp4")
        print(sid, "->", (d / f"{sid}.mp4").relative_to(ROOT), f"{(n1 - n0) / (time.time() - began):.1f} fps", flush=True)


def whole(film, path):
    """The film, one file: every shot in order at the output size, encoded for delivery (crf 16, slow), with the master."""
    out = av.open(str(ROOT / path), "w")
    vs = out.add_stream("libx264", rate=FPS)
    vs.width, vs.height, vs.pix_fmt = film.w, film.h, "yuv420p"
    vs.options = {"crf": "16", "preset": "slow"}
    as_ = out.add_stream("aac", rate=48000)
    as_.layout = "stereo"
    as_.bit_rate = 320000
    began = time.time()
    done = 0
    for sid in film.order:
        s = gfx.SHOTS[sid]
        for n in range(round(float(s["t0"]) * FPS), round(float(s["t1"]) * FPS)):
            for p in vs.encode(av.VideoFrame.from_ndarray(film.frame(sid, n / FPS), format="rgb24")):
                out.mux(p)
            done += 1
        print(sid, done, f"{done / (time.time() - began):.1f} fps", flush=True)
    for p in vs.encode():
        out.mux(p)
    song = av.open(str(ROOT / "media/song/checked-me-v1.wav"))
    rs = av.AudioResampler(format="fltp", layout="stereo", rate=48000)
    pcm = np.concatenate([g.to_ndarray() for f in song.decode(audio=0) for g in rs.resample(f)], axis=1)
    pcm = np.ascontiguousarray(pcm[:, :round(done / FPS * 48000)])
    for i in range(0, pcm.shape[1], 1024):
        af = av.AudioFrame.from_ndarray(np.ascontiguousarray(pcm[:, i:i + 1024]), format="fltp", layout="stereo")
        af.sample_rate, af.pts, af.time_base = 48000, i, Fraction(1, 48000)
        for p in as_.encode(af):
            out.mux(p)
    for p in as_.encode():
        out.mux(p)
    out.close()
    print(path, f"{done} frames, {(time.time() - began) / 60:.1f} min")


def take_lock():
    """Wait for the one render slot. Keep what this returns: the slot is held until it's released at exit."""
    (ROOT / "media/gfx").mkdir(exist_ok=True)
    lock = open(ROOT / "media/gfx/render.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("waiting for the render lock", flush=True)
        fcntl.flock(lock, fcntl.LOCK_EX)
    return lock


if __name__ == "__main__":
    main()

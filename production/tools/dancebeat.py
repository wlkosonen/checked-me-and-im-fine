#!/usr/bin/env python3
"""Measure a dance clip's own tempo and phase from its motion, and how far it is from the song's beat.

    media/cache/face-venv/bin/python production/tools/dancebeat.py media/clips/grok/g1-take*.mp4 [--bpm 133] [--parts 3]

CPU only. For each clip: dense optical flow (Farneback) on a 320-px-wide copy, minus the median flow (the camera's own
move), gives how much the bodies move in each frame. Its autocorrelation over 60-300 BPM gives the dance's tempo; the
candidate nearest the song's beat (x0.5, x1, x2 allowed) is the one reported, with the retime factor that would put it
on the grid (song bpm / dance bpm; past ~1.2 it reads as sped up). With --parts N the frame is cut into N vertical
strips (dancers left, her in the middle, dancers right for the wide) and each strip's motion is correlated with the
others: near 1 means they move together. Writes media/clips/analysis/<clip>.dance.json and prints one line per clip.

A measured beat isn't a danced beat: this ranks takes for Lati's eye, it doesn't replace it.
"""

import argparse
import json
from pathlib import Path

import av
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "media/clips/analysis"


def motion(path, parts, width=320):
    """Per-frame body motion (camera move removed), for the whole frame and per vertical strip; and the fps."""
    c = av.open(str(path))
    s = c.streams.video[0]
    fps = float(s.average_rate)
    prev, whole, strips = None, [], []
    for f in c.decode(video=0):
        g = f.to_ndarray(format="gray")
        h = int(round(g.shape[0] * width / g.shape[1]))
        g = cv2.resize(g, (width, h), interpolation=cv2.INTER_AREA)
        if prev is not None:
            fl = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            fl -= np.median(fl.reshape(-1, 2), axis=0)
            m = np.hypot(fl[..., 0], fl[..., 1])
            whole.append(float(np.mean(m)))
            strips.append([float(np.mean(b)) for b in np.array_split(m, parts, axis=1)])
        prev = g
    return fps, np.array(whole), np.array(strips)


def tempo(x, fps, lo=60, hi=300):
    """Tempo candidates from the autocorrelation of the motion's changes; returns [(bpm, strength)] strongest first."""
    d = np.diff(x)
    d = (d - d.mean()) / (d.std() + 1e-9)
    ac = np.correlate(d, d, "full")[len(d) - 1:] / len(d)
    out = []
    for lag in range(max(2, int(fps * 60 / hi)), min(len(ac) - 1, int(fps * 60 / lo)) + 1):
        if ac[lag] > ac[lag - 1] and ac[lag] >= ac[lag + 1] and ac[lag] > 0:
            # parabolic peak for a sub-frame lag
            a, b, c = ac[lag - 1], ac[lag], ac[lag + 1]
            p = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) else 0.0
            out.append((60 * fps / (lag + p), float(b)))
    out = sorted(out, key=lambda t: -t[1])
    return [(refine(ac, 60 * fps / b, fps), s) for b, s in out]


def refine(ac, lag, fps):
    """Sharpen a tempo by the later peaks of the same period (2, 3, 4 lags): one lag is only whole frames apart."""
    lags = [lag]
    for k in (2, 3, 4):
        c = int(round(k * lag))
        if c + 2 >= len(ac):
            break
        i = c - 2 + int(np.argmax(ac[c - 2:c + 3]))
        if 0 < i < len(ac) - 1:
            a, b, d = ac[i - 1], ac[i], ac[i + 1]
            p = 0.5 * (a - d) / (a - 2 * b + d) if (a - 2 * b + d) else 0.0
            lags.append((i + p) / k)
    return 60 * fps / float(np.median(lags))


def nearest(cands, bpm):
    """The candidate whose x0.5/x1/x2 is nearest the song's bpm, weighed by strength."""
    best = None
    for b, s in cands[:6]:
        for k in (0.5, 1, 2):
            r = bpm / (b * k)
            score = s / (1 + 4 * abs(np.log(r)))
            if best is None or score > best["score"]:
                best = {"dance_bpm": b, "as_beats": k, "retime": r, "strength": s, "score": score}
    return best


def phase(x, fps, bpm):
    """Where in the beat the motion changes most (seconds from the clip start to the first such point)."""
    d = np.abs(np.diff(x))
    period = 60 * fps / bpm
    bins = np.zeros(32)
    for i, v in enumerate(d):
        bins[int((i % period) / period * 32) % 32] += v
    return float(np.argmax(bins) / 32 * period / fps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--bpm", type=float, default=133.0)
    ap.add_argument("--parts", type=int, default=3)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for p in map(Path, a.clips):
        fps, x, strips = motion(p, a.parts)
        cands = tempo(x, fps)
        best = nearest(cands, a.bpm) if cands else None
        sync = None
        if a.parts > 1 and len(strips) > 8:
            ds = np.diff(strips, axis=0)
            cc = np.corrcoef(ds.T)
            sync = float(np.mean(cc[np.triu_indices(a.parts, 1)]))
        rec = {"clip": str(p), "fps": fps, "seconds": round(len(x) / fps, 2), "song_bpm": a.bpm,
               "candidates": [(round(b, 1), round(s, 3)) for b, s in cands[:6]], "best": best, "sync": sync,
               "phase_s": phase(x, fps, best["dance_bpm"] * best["as_beats"]) if best else None,
               "motion_mean": float(x.mean()) if len(x) else 0.0}
        (OUT / f"{p.stem}.dance.json").write_text(json.dumps(rec, indent=1))
        if best:
            print(f"{p.name}: dance {best['dance_bpm']:.1f} BPM (x{best['as_beats']:g} = beat), retime "
                  f"x{best['retime']:.3f}{'  TOO FAR' if abs(np.log(best['retime'])) > np.log(1.2) else ''}, "
                  f"strength {best['strength']:.2f}, sync {sync if sync is None else round(sync, 2)}, "
                  f"motion {rec['motion_mean']:.2f}")
        else:
            print(f"{p.name}: no periodic motion found")


if __name__ == "__main__":
    main()

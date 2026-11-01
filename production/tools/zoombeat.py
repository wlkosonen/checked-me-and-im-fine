#!/usr/bin/env python3
"""Measure zoom pulses in a reference film and whether they land on its beats or its vocal onsets.

    media/cache/face-venv/bin/python production/tools/zoombeat.py media/reference/NAME.mp4      # (CPU)

Run after refcut.py (it reads media/reference/NAME/shots.json, audio.wav and the vocal stem refcut made). Lati, 23 Oct:
"Notice slight zooms to the beat and vocals." Per frame pair inside a shot: ORB features, a similarity transform
(cv2.estimateAffinePartial2D), its scale. A zoom pulse is a short burst where the scale changes faster than the
shot's own drift (a push-in on a still, a punch on a word). For each pulse onset: the nearest beat and the nearest
vocal onset (librosa on the film's audio and on the htdemucs vocal stem). Writes NAME/zooms.json and prints a summary.
"""
import json
import subprocess
import sys
from pathlib import Path

import av
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def scales(src, w=480, h=270):
    c = av.open(str(src))
    fps = float(c.streams.video[0].average_rate)
    orb = cv2.ORB_create(600)
    prev, out = None, []
    for f in c.decode(video=0):
        g = cv2.resize(f.to_ndarray(format="gray"), (w, h), interpolation=cv2.INTER_AREA)
        kp, de = orb.detectAndCompute(g, None)
        s = 1.0
        if prev is not None and de is not None and prev[1] is not None and len(kp) > 20 and len(prev[0]) > 20:
            m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(prev[1], de)
            if len(m) > 20:
                a = np.float32([prev[0][x.queryIdx].pt for x in m])
                b = np.float32([kp[x.trainIdx].pt for x in m])
                M, inl = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC, ransacReprojThreshold=2.0)
                if M is not None and inl is not None and inl.sum() > 15:
                    s = float(np.hypot(M[0, 0], M[1, 0]))
        out.append(s)
        prev = (kp, de)
    return fps, np.log(np.array(out))


def main():
    src = Path(sys.argv[1])
    out = src.parent / src.stem
    shots = json.load(open(out / "shots.json"))["shots"]
    py = ROOT / "media/cache/listen-venv/bin/python"
    stem = ROOT / f"media/song/analysis/ref-{src.stem}/stems/vocals.wav"
    ana = subprocess.run([str(py), "-c", f"""
import librosa, json, numpy as np
y, sr = librosa.load({str(out / 'audio.wav')!r}, sr=22050, mono=True)
_, b = librosa.beat.beat_track(y=y, sr=sr)
v, sr2 = librosa.load({str(stem)!r}, sr=22050, mono=True)
on = librosa.onset.onset_detect(y=v, sr=sr2, units='time', backtrack=False)
print(json.dumps({{"beats": librosa.frames_to_time(b, sr=sr).tolist(), "vocal_onsets": on.tolist()}}))
"""], check=True, capture_output=True, text=True).stdout
    A = json.loads(ana.strip().splitlines()[-1])
    beats, von = np.array(A["beats"]), np.array(A["vocal_onsets"])
    fps, ls = scales(src)
    cuts = [round(s["t0"] * fps) for s in shots] + [len(ls)]
    pulses, zoom_shots = [], 0
    for k in range(len(shots)):
        a, b = cuts[k] + 1, cuts[k + 1]               # skip the cut frame itself
        d = ls[a:b]
        if len(d) < 6:
            continue
        drift = float(np.median(d))
        if abs(np.sum(d)) > 0.03:                     # the shot zooms by more than 3% overall
            zoom_shots += 1
        ex = np.abs(d - drift)
        thr = max(0.004, 4 * float(np.median(np.abs(d - drift))) + 0.002)
        i = 0
        while i < len(d):
            if ex[i] > thr:
                j = i
                while j + 1 < len(d) and ex[j + 1] > thr * 0.5:
                    j += 1
                if j - i <= int(0.4 * fps):          # short: a pulse, not a slow push
                    t = (a + i) / fps
                    pulses.append({"t": round(t, 3), "shot": shots[k]["n"], "frames": j - i + 1,
                                   "zoom": round(float(np.sum(d[i:j + 1] - drift)), 4),
                                   "to_beat": round(float(np.min(np.abs(beats - t))), 3) if len(beats) else None,
                                   "to_vocal": round(float(np.min(np.abs(von - t))), 3) if len(von) else None})
                i = j + 1
            else:
                i += 1
    json.dump({"fps": fps, "pulses": pulses, "zoom_shots": zoom_shots}, open(out / "zooms.json", "w"), indent=1)
    dur = len(ls) / fps
    tol = 1.5 / fps + 0.03
    nb = sum(p["to_beat"] is not None and p["to_beat"] <= tol for p in pulses)
    nv = sum(p["to_vocal"] is not None and p["to_vocal"] <= tol for p in pulses)
    either = sum((p["to_beat"] or 9) <= tol or (p["to_vocal"] or 9) <= tol for p in pulses)
    print(f"{len(pulses)} zoom pulses in {dur:.0f} s ({len(pulses) / dur * 60:.0f}/min); shots with an overall zoom "
          f">3%: {zoom_shots}/{len(shots)}")
    if pulses:
        print(f"  on a beat (±{tol * 1000:.0f} ms): {nb} ({nb / len(pulses):.0%}); on a vocal onset: {nv} "
              f"({nv / len(pulses):.0%}); either: {either} ({either / len(pulses):.0%})")
        # what chance would give: share of the timeline within tol of a beat / of an onset
        grid = np.arange(0, dur, 0.01)
        cb = float(np.mean(np.min(np.abs(beats[None] - grid[:, None]), 1) <= tol)) if len(beats) else 0
        cv = float(np.mean(np.min(np.abs(von[None] - grid[:, None]), 1) <= tol)) if len(von) else 0
        print(f"  by chance alone: beat {cb:.0%}, vocal onset {cv:.0%}")
        z = np.array([p["zoom"] for p in pulses])
        print(f"  pulse size: median {np.median(np.abs(z)) * 100:.1f}% scale; in {np.mean(z > 0):.0%}, out "
              f"{np.mean(z < 0):.0%}; median length {np.median([p['frames'] for p in pulses]):.0f} frames")


if __name__ == "__main__":
    main()

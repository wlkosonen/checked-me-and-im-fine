#!/usr/bin/env python3
"""Measure a reference music video: its cuts, motion, cuts against its beats, and where her mouth follows the vocal.

    media/cache/face-venv/bin/python production/tools/refcut.py media/reference/NAME.mp4      # (CPU)

For studying other films' grammar (Lati, 23 Oct: the gallery guide is one way, not the rule). Writes
media/reference/NAME/ (gitignored): shots.json, a contact sheet per 24 shots (one mid-shot frame each, numbered, with
duration and labels), and prints a summary.

- Cuts: grey 160x90 frames; a cut where the frame difference jumps far above its neighbours.
- Motion per shot: mean frame difference inside the shot (still < 3, gentle 3-8, strong > 8).
- Beats: librosa beat track on the film's own audio; a cut counts as on the beat within 1.5 frames.
- Lip sync per shot: htdemucs vocal stem envelope vs her mouth opening (InsightFace 106-point landmarks, lip gap /
  face height) at 12 fps; a shot with a face is "sung" if the correlation is clearly positive, "face, not sung" if a
  face is there but the mouth doesn't follow, "no face" otherwise. Rough: a guide for looking, not a verdict.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import av
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def frames_gray(path, w=160, h=90):
    c = av.open(str(path))
    fps = float(c.streams.video[0].average_rate)
    out = [cv2.resize(f.to_ndarray(format="gray"), (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)
           for f in c.decode(video=0)]
    return fps, out


def cuts_from(g):
    d = np.array([0.0] + [float(np.mean(np.abs(g[i] - g[i - 1]))) for i in range(1, len(g))])
    cuts = [0]
    for i in range(1, len(d)):
        loc = np.concatenate([d[max(1, i - 6):i], d[i + 1:i + 7]])
        med = float(np.median(loc)) if len(loc) else 0.0
        if d[i] > 18 and d[i] > 4 * med + 6 and i - cuts[-1] > 5:
            cuts.append(i)
    return d, cuts


def main():
    src = Path(sys.argv[1])
    out = src.parent / src.stem
    out.mkdir(exist_ok=True)
    fps, g = frames_gray(src)
    d, cuts = cuts_from(g)
    n = len(g)
    bounds = cuts + [n]
    # audio: beats and the vocal stem
    wav = out / "audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vn", "-ac", "2", "-ar", "44100", str(wav)], check=True)
    py = ROOT / "media/cache/listen-venv/bin/python"
    take = f"ref-{src.stem}"                     # the listen tools' stem separation (htdemucs), as for our song
    shutil.copy(wav, ROOT / f"media/song/{take}.wav")
    stems = ROOT / f"media/song/analysis/{take}/stems/vocals.wav"
    if not stems.exists():
        subprocess.run([str(py), str(ROOT / "production/tools/listen/stems.py"), take], check=True, cwd=str(ROOT))
    ana = subprocess.run([str(py), "-c", f"""
import librosa, numpy as np, json
y, sr = librosa.load({str(wav)!r}, sr=22050, mono=True)
tempo, b = librosa.beat.beat_track(y=y, sr=sr)
v, sr2 = librosa.load({str(stems)!r}, sr=16000, mono=True)
hop = int(sr2 / 12)
e = np.sqrt(np.convolve(v[:len(v)//hop*hop].reshape(-1, hop).__pow__(2).mean(1), np.ones(2)/2, 'same'))
print(json.dumps({{"tempo": float(np.atleast_1d(tempo)[0]), "beats": librosa.frames_to_time(b, sr=sr).tolist(),
                  "venv": e.tolist()}}))
"""], check=True, capture_output=True, text=True).stdout
    A = json.loads(ana.strip().splitlines()[-1])
    beats = np.array(A["beats"])
    venv = np.array(A["venv"])
    # faces and mouths at 12 fps
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l", root=str(ROOT / "media/cache/face"), providers=["CPUExecutionProvider"],
                       allowed_modules=["detection", "landmark_2d_106"])
    app.prepare(ctx_id=-1, det_size=(640, 640))
    step = max(1, round(fps / 12))
    mouth = {}
    c = av.open(str(src))
    for i, f in enumerate(c.decode(video=0)):
        if i % step:
            continue
        faces = app.get(f.to_ndarray(format="bgr24"))
        if not faces:
            continue
        fc = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
        lm = fc.landmark_2d_106
        fh = fc.bbox[3] - fc.bbox[1]
        gap = np.linalg.norm(lm[71] - lm[53]) if lm is not None else 0  # upper / lower inner lip (106-point scheme)
        mouth[i] = (float(gap / max(fh, 1)), float(fh))
    shots = []
    for k in range(len(cuts)):
        a, b = bounds[k], bounds[k + 1]
        t0, t1 = a / fps, b / fps
        mot = float(np.mean(d[a + 1:b])) if b - a > 1 else 0.0
        on_beat = bool(len(beats) and np.min(np.abs(beats - t0)) <= 1.5 / fps) if k else True
        fr = [mouth[i] for i in range(a, b) if i in mouth]
        face_h = float(np.median([x[1] for x in fr])) if fr else 0.0
        label = "no face"
        corr = None
        if len(fr) >= max(4, 0.5 * (b - a) / step) and face_h > 40:
            idx = [i for i in range(a, b) if i in mouth]
            m = np.array([mouth[i][0] for i in idx])
            ve = np.array([venv[min(len(venv) - 1, int(i / fps * 12))] for i in idx])
            if m.std() > 1e-4 and ve.std() > 1e-6:
                corr = float(np.corrcoef(m, ve)[0, 1])
            label = "sung" if (corr is not None and corr > 0.35 and m.std() > 0.01) else "face, not sung"
        shots.append({"n": k + 1, "t0": round(t0, 2), "dur": round(t1 - t0, 2), "motion": round(mot, 2),
                      "motion_kind": "still" if mot < 3 else ("gentle" if mot < 8 else "strong"),
                      "cut_on_beat": on_beat, "face_px": round(face_h), "mouth_vs_vocal": corr, "label": label})
    json.dump({"source": str(src), "fps": fps, "tempo": A["tempo"], "shots": shots}, open(out / "shots.json", "w"), indent=1)
    # contact sheets: one mid-shot frame per shot
    c = av.open(str(src))
    want = {(bounds[k] + bounds[k + 1]) // 2: k for k in range(len(cuts))}
    thumbs = {}
    for i, f in enumerate(c.decode(video=0)):
        if i in want:
            thumbs[want[i]] = cv2.resize(f.to_ndarray(format="bgr24"), (320, 180), interpolation=cv2.INTER_AREA)
    for p in range(0, len(shots), 24):
        sheet = np.zeros((6 * 180, 4 * 320, 3), np.uint8)
        for j, s in enumerate(shots[p:p + 24]):
            im = thumbs[s["n"] - 1].copy()
            tag = f"{s['n']} {s['dur']:.1f}s {s['motion_kind'][0]} {'SUNG' if s['label'] == 'sung' else ('face' if s['label'] != 'no face' else '')}"
            cv2.rectangle(im, (0, 0), (220, 22), (0, 0, 0), -1)
            cv2.putText(im, tag, (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            sheet[(j // 4) * 180:(j // 4 + 1) * 180, (j % 4) * 320:(j % 4 + 1) * 320] = im
        cv2.imwrite(str(out / f"sheet-{p // 24 + 1:02d}.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
    dur = n / fps
    by = lambda key, val: sum(s["dur"] for s in shots if s[key] == val)
    durs = sorted(s["dur"] for s in shots)
    print(f"{len(shots)} shots in {dur:.1f} s: mean {dur / len(shots):.2f} s, median {durs[len(durs) // 2]:.2f} s; "
          f"tempo ~{A['tempo']:.0f} BPM; cuts on a beat {sum(s['cut_on_beat'] for s in shots[1:])}/{len(shots) - 1}")
    for kind in ("still", "gentle", "strong"):
        print(f"  motion {kind}: {by('motion_kind', kind) / dur:.0%} of screen time")
    for lab in ("sung", "face, not sung", "no face"):
        print(f"  {lab}: {sum(s['label'] == lab for s in shots)} shots, {by('label', lab) / dur:.0%} of screen time")


if __name__ == "__main__":
    main()

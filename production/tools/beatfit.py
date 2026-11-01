#!/usr/bin/env python3
"""Put a Grok dance take on the song's beat, by the beat of Grok's own soundtrack, for a preview with our audio.

    media/cache/listen-venv/bin/python production/tools/beatfit.py media/clips/grok/g1-take-4.mp4 [...] [--at 44.10]

Grok writes its own music near the tempo in the prompt, and its dancers move to that music. So the take's beat grid
comes from its own audio (librosa beats, a straight line fitted through them), not from the motion. The take is
retimed by one even speed (song BPM / take BPM) and shifted so that its beat, plus the phase where the motion hits
hardest (motion vs Grok's beat), lands on our downbeat at --at (default: chorus 1, 0:44.10). Nearest-frame retiming
at 25 fps: a preview, not the final (the final uses RIFE in-betweens). A small white dot in the corner flashes on our
beats. Writes media/clips/preview/<take>-beat.mp4 and prints the speed and offset.

A take more than ~1.2x off reads as sped up; past that the take is skipped. Lati's eye is the check.

--lips: for a take where she sings our words (Grok's own voice). After the beat fit, Whisper hears the take's words;
each is matched in order to our words inside the take's span, and a monotone curve (PCHIP) through those anchors maps
song time to take time, so each mouth shape lands on our word. Anchors forcing a local speed outside 0.75-1.33 are
dropped (past that it reads sped up); outside the anchors the beat fit holds. Writes <take>-lips.mp4 next to it.
"""

import argparse
import difflib
import re
import json
import subprocess
from pathlib import Path

import av
import cv2
import librosa
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SONG = ROOT / "media/song/checked-me-v1.wav"
BEATS = ROOT / "media/song/analysis/checked-me-v1/beats.json"
OUT = ROOT / "media/clips/preview"
FPS = 25


def take_beats(path):
    """Grok's own beat: period and first beat time from a straight line through its audio beats."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", "22050", "-f", "f32le",
                          "-"], check=True, capture_output=True).stdout
    y, sr = np.frombuffer(raw, dtype=np.float32), 22050
    oe = librosa.onset.onset_strength(y=y, sr=sr)
    _, b = librosa.beat.beat_track(onset_envelope=oe, sr=sr)
    t = librosa.frames_to_time(b, sr=sr)
    k = np.arange(len(t))
    period, t0 = np.polyfit(k, t, 1)
    return float(period), float(t0 % period), t


def frames(path):
    c = av.open(str(path))
    fps = float(c.streams.video[0].average_rate)
    return fps, [f.to_ndarray(format="rgb24") for f in c.decode(video=0)]


def motion_phase(fr, fps, period, t0):
    """Offset (s) after Grok's beat where the motion changes hardest, folded into one beat."""
    prev, m = None, []
    for a in fr:
        g = cv2.resize(cv2.cvtColor(a, cv2.COLOR_RGB2GRAY), (320, 180), interpolation=cv2.INTER_AREA)
        if prev is not None:
            fl = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            fl -= np.median(fl.reshape(-1, 2), axis=0)
            m.append(np.mean(np.hypot(fl[..., 0], fl[..., 1])))
        prev = g
    d = np.abs(np.diff(np.array(m), 2))
    t = (np.arange(len(d)) + 1.5) / fps
    offs = np.linspace(0, period, 24, endpoint=False)
    sc = []
    for o in offs:
        ph = ((t - t0 - o) % period) / period
        sc.append(d[(ph < 0.12) | (ph > 0.88)].mean() / d.mean())
    k = int(np.argmax(sc))
    return float(offs[k]), float(sc[k])


def heard(path):
    """Whisper's words in the take's own audio: [(word, start s)]."""
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = os.environ["HIP_VISIBLE_DEVICES"] = ""
    import whisper
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le",
                          "-"], check=True, capture_output=True).stdout
    m = whisper.load_model("turbo", device="cpu", download_root=str(ROOT / "media/cache/listen-models/whisper"))
    r = m.transcribe(np.frombuffer(raw, np.float32).copy(), word_timestamps=True, language="en", fp16=False)
    return [(w["word"], float(w["start"])) for sg in r["segments"] for w in sg["words"]]


def norm(w):
    return re.sub(r"[^a-z']", "", w.lower()).replace("checked", "check")


def lip_map(take_words, song_words, T0, speed):
    """Anchors (song time, take time) for words heard in the take matched in order to ours; PCHIP through them."""
    from scipy.interpolate import PchipInterpolator
    a = [norm(w) for w, _ in take_words]
    b = [norm(w["w"]) for w in song_words]
    pairs = []
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            ts = take_words[blk.a + k][1]
            if ts <= 0.05:          # whisper puts an unknown first start at 0
                continue
            pairs.append((song_words[blk.b + k]["t0"], ts))
    pairs = sorted(pairs)
    while len(pairs) > 2:
        sp = [(pairs[i + 1][1] - pairs[i][1]) / max(pairs[i + 1][0] - pairs[i][0], 1e-3) for i in range(len(pairs) - 1)]
        bad = [i for i, v in enumerate(sp) if not 0.75 * speed <= v <= 1.33 * speed]
        if not bad:
            break
        i = bad[0]
        pairs.pop(i + 1 if i + 1 < len(pairs) - 1 else i)
    if len(pairs) < 2:
        return None, pairs
    sp = (pairs[1][1] - pairs[0][1]) / max(pairs[1][0] - pairs[0][0], 1e-3)
    if len(pairs) == 2 and not 0.75 * speed <= sp <= 1.33 * speed:  # the loop above leaves two anchors unchecked:
        return None, pairs                                           # s029 came out at x6 (25 Oct)
    xs, ys = np.array([p[0] for p in pairs]), np.array([p[1] for p in pairs])
    f = PchipInterpolator(xs, ys)
    def m(T):
        if T < xs[0]:
            return ys[0] + (T - xs[0]) * speed
        if T > xs[-1]:
            return ys[-1] + (T - xs[-1]) * speed
        return float(f(T))
    return m, pairs


def write(out, fr, fps, T0, T1, src_of, beats, dot=True):
    n = int((T1 - T0) * FPS)
    h, w = fr[0].shape[:2]
    tmp = out.with_suffix(".video.mp4")
    c = av.open(str(tmp), "w")
    s = c.add_stream("libx264", rate=FPS)
    s.width, s.height, s.pix_fmt = w, h, "yuv420p"
    s.options = {"crf": "18"}
    for k in range(n):
        T = T0 + k / FPS
        src = max(0, min(len(fr) - 1, int(round(src_of(T) * fps))))
        img = fr[src].copy()
        if dot and np.min(np.abs(beats - T)) < 0.5 / FPS + 0.02:
            cv2.circle(img, (w - 28, 28), 9, (255, 255, 255), -1)
        for pk in s.encode(av.VideoFrame.from_ndarray(img, format="rgb24")):
            c.mux(pk)
    for pk in s.encode():
        c.mux(pk)
    c.close()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-ss", f"{T0:.3f}", "-t", f"{T1 - T0:.3f}",
                    "-i", str(SONG), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", str(out)], check=True)
    tmp.unlink()
    out.with_suffix(".json").write_text(json.dumps({"t0": round(T0, 4), "t1": round(T1, 4)}))  # song time it covers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--at", type=float, default=44.10, help="song time of the downbeat the take's beat lands on")
    ap.add_argument("--lips", action="store_true", help="also warp word by word onto our vocal (sung takes)")
    ap.add_argument("--no-dot", action="store_true", help="no beat dot (for the edit, not a preview)")
    ap.add_argument("--out-dir", default=None, help="where to write (default media/clips/preview)")
    a = ap.parse_args()
    out_dir = ROOT / a.out_dir if a.out_dir else OUT
    out_dir.mkdir(parents=True, exist_ok=True)
    dot = not a.no_dot
    grid = json.loads(BEATS.read_text())
    beats = np.array(grid["beats"])
    for p in map(Path, a.clips):
        period, t0, _ = take_beats(p)
        fps, fr = frames(p)
        off, hit = motion_phase(fr, fps, period, t0)
        i = int(np.argmin(np.abs(beats - a.at)))
        ours = float(np.median(np.diff(beats[max(0, i - 4):i + 16])))
        speed = period / ours                     # source seconds per song second
        if abs(np.log(speed)) > np.log(1.2):
            print(f"{p.name}: take {60 / period:.1f} BPM vs ours {60 / ours:.1f}: x{speed:.3f}, too far for a beat fit"
                  + ("; the words set the timing" if a.lips else "; skipped"))
            if not a.lips:
                continue
            speed, off = 1.0, 0.0
        anchor_src = t0 + off                    # a beat of the take, at its motion's hit
        while anchor_src - period >= 0:
            anchor_src -= period
        dur = len(fr) / fps
        T0 = beats[i] - anchor_src / speed       # song time where the take starts
        T1 = T0 + dur / speed
        out = out_dir / f"{p.stem}-beat.mp4"
        write(out, fr, fps, T0, T1, lambda T: (T - T0) * speed, beats, dot)
        print(f"{p.name}: take {60 / period:.1f} BPM -> ours {60 / ours:.1f}, speed x{speed:.3f}; motion hits "
              f"+{off * 1000:.0f} ms after its beat (x{hit:.2f}); plays {T0:.2f}-{T1:.2f} s of the song -> {out.name}")
        if a.lips:
            words = json.loads((ROOT / "media/song/analysis/checked-me-v1/words.json").read_text())["words"]
            span = [w for w in words if w["t0"] and T0 - 0.5 <= w["t0"] <= T1 + 0.5]
            m, pairs = lip_map(heard(p), span, T0, speed)
            if m is None:
                print(f"  lips: too few matched words ({len(pairs)})")
                continue
            lo = max(T0, pairs[0][0] - pairs[0][1] / speed)
            write(out_dir / f"{p.stem}-lips.mp4", fr, fps, lo, T1, m, beats, dot)
            sp = [(pairs[i + 1][1] - pairs[i][1]) / (pairs[i + 1][0] - pairs[i][0]) for i in range(len(pairs) - 1)]
            print(f"  lips: {len(pairs)} words anchored, local speed {min(sp):.2f}-{max(sp):.2f}; "
                  + ", ".join(f"{t:.2f}->{u:.2f}" for t, u in pairs))


if __name__ == "__main__":
    main()

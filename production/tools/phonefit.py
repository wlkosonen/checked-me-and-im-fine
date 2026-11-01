#!/usr/bin/env python3
"""Put a clip on the green screen of a phone plate, with a slight handheld drift (Lati, 1 Nov: s073).

    ~/ComfyUI/venv/bin/python production/tools/phonefit.py PLATE.png CLIP.mp4 OUT.mp4 [--focus 0.5] [--width 300]

The screen is found by its green: the keyed area is the mask, so the notch and rounded corners stay the phone's own, and
its corners pin the clip in perspective. The clip covers the screen, centred on --focus (0-1 across the clip). --width
shows that many clip pixels across; a landscape clip on an upright phone then runs short, and its edges are mirrored and
softened to fill the screen. A little
of the screen's light falls on the plate. The whole frame then drifts on slow sine waves, as a held phone does, zoomed
a touch so the edges stay covered. Writes 1280x720 at the clip's frame rate.
"""
import argparse
import math

import av
import cv2
import numpy as np

W, H = 1280, 720
ZOOM = 1.035


def screen(plate):
    """The key mask (0-1) and the screen's four corners: top-left, top-right, bottom-right, bottom-left."""
    hsv = cv2.cvtColor(plate, cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, (35, 60, 80), (85, 255, 255))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    m = np.uint8(lab == big) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    box = cv2.boxPoints(cv2.minAreaRect(cv2.findNonZero(m)))
    s, d = box.sum(1), box[:, 0] - box[:, 1]
    corners = np.float32([box[np.argmin(s)], box[np.argmax(d)], box[np.argmax(s)], box[np.argmin(d)]])
    mask = cv2.GaussianBlur(cv2.dilate(m, np.ones((3, 3), np.uint8)), (0, 0), 0.8).astype(np.float32) / 255
    return mask, corners


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plate")
    ap.add_argument("clip")
    ap.add_argument("out")
    ap.add_argument("--focus", type=float, default=0.5)
    ap.add_argument("--width", type=float, default=0)
    a = ap.parse_args()
    im = cv2.imread(a.plate)
    s = max(W / im.shape[1], H / im.shape[0])
    im = cv2.resize(im, (round(im.shape[1] * s), round(im.shape[0] * s)), interpolation=cv2.INTER_AREA)
    y0, x0 = (im.shape[0] - H) // 2, (im.shape[1] - W) // 2
    plate = im[y0:y0 + H, x0:x0 + W]
    mask, q = screen(plate)
    sw, sh = np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[3] - q[0])
    print(f"screen {sw:.0f}x{sh:.0f}, area {mask.mean() * 100:.1f}% of the frame, corners {q.round().tolist()}")
    inp = av.open(a.clip)
    rate = inp.streams.video[0].average_rate
    out = av.open(a.out, "w")
    vs = out.add_stream("libx264", rate=rate)
    vs.width, vs.height, vs.pix_fmt = W, H, "yuv420p"
    vs.options = {"crf": "17", "preset": "medium"}
    for i, f in enumerate(inp.decode(video=0)):
        fr = f.to_ndarray(format="bgr24")
        ch, cw = fr.shape[:2]
        k = sw / a.width if a.width else max(sw / cw, sh / ch)  # cover the screen, centred on the focus
        vw, vh = sw / k, sh / k
        pad = max(0, math.ceil((vh - ch) / 2))
        if pad:
            fr = cv2.copyMakeBorder(fr, pad, pad, 0, 0, cv2.BORDER_REFLECT_101)  # softened, or the rows read as streaks
            soft = cv2.GaussianBlur(fr, (0, 0), 14)
            ramp = np.ones(fr.shape[0], np.float32)
            ramp[:pad] = ramp[-pad:] = 0
            ramp = cv2.GaussianBlur(ramp[None], (0, 0), pad / 2)[0][:, None, None]
            fr = (fr * ramp + soft * (1 - ramp)).astype(np.uint8)
            ch += 2 * pad
        x = max(0, min(cw - vw, cw * a.focus - vw / 2))
        y = (ch - vh) / 2
        src = np.float32([[x, y], [x + vw, y], [x + vw, y + vh], [x, y + vh]])
        warped = cv2.warpPerspective(fr, cv2.getPerspectiveTransform(src, q), (W, H), flags=cv2.INTER_CUBIC)
        comp = plate.astype(np.float32) * (1 - mask[..., None]) + warped.astype(np.float32) * mask[..., None]
        glow = cv2.GaussianBlur(warped.astype(np.float32) * mask[..., None], (0, 0), 28)  # the screen's light on the hand
        comp = np.clip(comp + glow * 0.10 * (1 - mask[..., None]), 0, 255).astype(np.uint8)
        t = i / float(rate)
        dx = 6 * math.sin(2 * math.pi * t / 2.3 + 0.4) + 2.5 * math.sin(2 * math.pi * t / 0.97 + 1.1)
        dy = 4.5 * math.sin(2 * math.pi * t / 1.9 + 2.0) + 2.0 * math.sin(2 * math.pi * t / 1.13)
        rot = 0.28 * math.sin(2 * math.pi * t / 2.7 + 0.9)
        M = cv2.getRotationMatrix2D((W / 2, H / 2), rot, ZOOM)
        M[:, 2] += (dx, dy)
        res = cv2.warpAffine(comp, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        for p in vs.encode(av.VideoFrame.from_ndarray(res, format="bgr24")):
            out.mux(p)
    for p in vs.encode():
        out.mux(p)
    out.close()
    print("wrote", a.out, i + 1, "frames at", float(rate))


if __name__ == "__main__":
    main()

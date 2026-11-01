#!/usr/bin/env python3
"""Bring one portrait frame to life for a call tile: blinks and a tiny head drift, lips locked (Lati, 1 Nov).

    ~/LivePortrait/venv/bin/python production/tools/microlive.py FRAME.png OUT.mp4 --crop 1020:574:450:30 [--seconds 6]

LivePortrait on the CPU (the display card stays out of it), driven by numbers instead of a driving video: her expression
stays the source frame's, so the mouth can't move; only the head rotation and the eyelids change. The head moves in sine
waves that complete whole cycles, so the clip loops without a seam. --blinks: seconds from the start. Writes 640x360,
25 fps. --test N renders only N frames and prints the time per frame.
"""
import argparse
import math
import sys
import time
from pathlib import Path

LP = Path.home() / "LivePortrait"
sys.path.insert(0, str(LP))

import cv2
import imageio
import numpy as np
import torch

from src.config.crop_config import CropConfig
from src.config.inference_config import InferenceConfig
from src.live_portrait_wrapper import LivePortraitWrapper
from src.utils.camera import get_rotation_matrix
from src.utils.crop import paste_back, prepare_paste_back
from src.utils.cropper import Cropper
from src.utils.retargeting_utils import calc_eye_close_ratio

FPS = 25


def blink(t, times, down=0.09, shut=0.05, up=0.17):
    """1 = open, 0 = shut, at time t: quick down, slower up, as an eyelid moves."""
    v = 1.0
    for b in times:
        d = t - b
        if 0 <= d < down:
            v = min(v, 1 - d / down)
        elif down <= d < down + shut:
            v = 0.0
        elif down + shut <= d < down + shut + up:
            v = min(v, (d - down - shut) / up)
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frame")
    ap.add_argument("out")
    ap.add_argument("--crop", required=True, help="W:H:X:Y of the tile in the frame")
    ap.add_argument("--seconds", type=float, default=6.0)
    ap.add_argument("--blinks", default="1.3,4.2")
    ap.add_argument("--yaw", type=float, default=1.3, help="degrees")
    ap.add_argument("--pitch", type=float, default=0.8)
    ap.add_argument("--roll", type=float, default=0.6)
    ap.add_argument("--test", type=int, default=0)
    a = ap.parse_args()
    cw, ch, cx, cy = (int(v) for v in a.crop.split(":"))
    times = [float(v) for v in a.blinks.split(",") if v]
    cfg = InferenceConfig(flag_force_cpu=True, flag_use_half_precision=False, device_id=0)
    wrap = LivePortraitWrapper(cfg)
    crop_cfg = CropConfig(flag_force_cpu=True, device_id=0)
    crop_cfg.insightface_root = str(LP / "pretrained_weights/insightface")
    crop_cfg.landmark_ckpt_path = str(LP / "pretrained_weights/liveportrait/landmark.onnx")
    cropper = Cropper(crop_cfg=crop_cfg, flag_force_cpu=True)
    img = cv2.cvtColor(cv2.imread(a.frame), cv2.COLOR_BGR2RGB)
    info = cropper.crop_source_image(img, cropper.crop_cfg)
    lmk = info["lmk_crop"]
    src_eye = float(np.mean(calc_eye_close_ratio(lmk[None])))
    mask = prepare_paste_back(cfg.mask_crop, info["M_c2o"], dsize=(img.shape[1], img.shape[0]))
    with torch.no_grad():
        I_s = wrap.prepare_source(info["img_crop_256x256"])
        kp = wrap.get_kp_info(I_s)
        f_s = wrap.extract_feature_3d(I_s)
        x_s = wrap.transform_keypoint(kp)
    print(f"source eye ratio {src_eye:.3f}, pose {float(kp['pitch']):.1f} {float(kp['yaw']):.1f} {float(kp['roll']):.1f}", flush=True)
    n = round(a.seconds * FPS)
    w = imageio.get_writer(a.out, fps=FPS, codec="libx264", quality=None, ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p"], macro_block_size=1)
    t0 = time.time()
    R_s = get_rotation_matrix(kp["pitch"], kp["yaw"], kp["roll"])
    for i in range(n if not a.test else a.test):
        t = i / FPS if not a.test else i * a.seconds / a.test
        k = 2 * math.pi * t / a.seconds
        yaw, pitch, roll = a.yaw * math.sin(k), a.pitch * math.sin(2 * k + 0.7), a.roll * math.sin(k + 1.9)
        with torch.no_grad():
            R_d = get_rotation_matrix(kp["pitch"] + pitch, kp["yaw"] + yaw, kp["roll"] + roll)
            x_d = kp["scale"] * (kp["kp"] @ (R_d @ R_s.permute(0, 2, 1) @ R_s) + kp["exp"]) + kp["t"]
            o = blink(t, times)
            if o < 1:
                ratio = wrap.calc_combined_eye_ratio([[src_eye * o]], lmk)
                x_d = x_d + wrap.retarget_eye(x_s, ratio)
            x_d = wrap.stitching(x_s, x_d)
            out = wrap.parse_output(wrap.warp_decode(f_s, x_s, x_d)["out"])[0]
        full = paste_back(out, info["M_c2o"], img, mask)
        w.append_data(cv2.resize(full[cy:cy + ch, cx:cx + cw], (640, 360), interpolation=cv2.INTER_AREA))
        if i % 25 == 0:
            print(f"frame {i}: {(time.time() - t0) / (i + 1):.2f} s each", flush=True)
    w.close()
    print("done:", a.out, f"{time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()

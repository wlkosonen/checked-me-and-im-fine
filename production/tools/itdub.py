#!/usr/bin/env python3
"""InfiniteTalk video-to-video on a Grok dance take: re-sing her mouth to our vocal, keep Grok's dance.

    media/cache/face-venv/bin/python production/tools/itdub.py prep  TAKE.mp4 --at 50.44      # crop + audio
    HIP_VISIBLE_DEVICES=0 ~/ComfyUI/venv/bin/python production/tools/itdub.py run TAKE.mp4 # ComfyUI must be up
    media/cache/face-venv/bin/python production/tools/itdub.py paste TAKE.mp4               # composite + preview

prep: conforms the take to 25 fps, tracks her face (InsightFace) and cuts an 832x480 window around her head and
shoulders at the take's own scale (her face keeps its ~140 px), smoothed so the window moves like a slow operator.
Also cuts our vocal stem for the take's slot in the song (--at, song seconds where the take starts) to 16 kHz.
run: kijai's ComfyUI-WanVideoWrapper V2V InfiniteTalk graph (after its example_workflows/..._V2V_InfiniteTalk_example
_02): Wan 2.1 I2V 480p fp8 + InfiniteTalk single + lightx2v, 4 steps from step 2 on the source latents (so the source
motion holds), sdpa attention, block swap. Frames come back as PNGs.
paste: puts only her head back into the 720p take through a soft ellipse around the tracked face, so everything
outside it is Grok's own pixels, and muxes our song under it.

Everything goes to media/clips/it/<take>/.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SONG = ROOT / "media/song/checked-me-v1.wav"
VOCALS = ROOT / "media/song/analysis/checked-me-v1/stems/vocals.wav"
COMFY_IN = Path.home() / "ComfyUI/input"
W, H, FPS = 832, 480, 25


def outdir(take):
    d = ROOT / "media/clips/it" / Path(take).stem
    d.mkdir(parents=True, exist_ok=True)
    return d


def prep(a):
    import av
    import numpy as np
    from insightface.app import FaceAnalysis
    from scipy.ndimage import gaussian_filter1d
    d = outdir(a.take)
    conf = d / "25fps.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.take, "-map", "0:v:0", "-vf", f"fps={FPS}", "-c:v",
                    "libx264", "-crf", "12", str(conf)], check=True)
    frames = [f.to_ndarray(format="rgb24") for f in av.open(str(conf)).decode(video=0)]
    fh, fw = frames[0].shape[:2]
    app = FaceAnalysis(name="buffalo_l", root=str(ROOT / "media/cache/face"), providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(640, 640))
    cx, cy, fs = [], [], []
    for f in frames:
        faces = app.get(f[:, :, ::-1])
        if faces:
            b = max(faces, key=lambda x: x.det_score).bbox
            cx.append((b[0] + b[2]) / 2); cy.append((b[1] + b[3]) / 2); fs.append(b[3] - b[1])
        else:
            cx.append(np.nan); cy.append(np.nan); fs.append(np.nan)
    cx, cy, fs = (np.array(v, float) for v in (cx, cy, fs))
    ok = ~np.isnan(cx)
    idx = np.arange(len(cx))
    for v in (cx, cy, fs):
        v[~ok] = np.interp(idx[~ok], idx[ok], v[ok])
    sx = gaussian_filter1d(cx, 4, mode="nearest")
    sy = gaussian_filter1d(cy, 4, mode="nearest")
    # head a little above centre, shoulders below
    x0 = np.clip(np.round(sx - W / 2), 0, fw - W).astype(int)
    y0 = np.clip(np.round(sy - H * 0.38), 0, fh - H).astype(int)
    crop = d / "crop.mp4"
    c = av.open(str(crop), "w")
    s = c.add_stream("libx264", rate=FPS)
    s.width, s.height, s.pix_fmt, s.options = W, H, "yuv420p", {"crf": "10"}
    for f, x, y in zip(frames, x0, y0):
        for p in s.encode(av.VideoFrame.from_ndarray(np.ascontiguousarray(f[y:y + H, x:x + W]), format="rgb24")):
            c.mux(p)
    for p in s.encode():
        c.mux(p)
    c.close()
    n = len(frames)
    aud = d / "vocal.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a.at:.3f}", "-t", f"{n / FPS:.3f}", "-i", str(VOCALS),
                    "-ac", "1", "-ar", "16000", str(aud)], check=True)
    COMFY_IN.mkdir(exist_ok=True)
    stem = Path(a.take).stem
    for src, name in ((crop, f"it-{stem}-crop.mp4"), (aud, f"it-{stem}-vocal.wav")):
        (COMFY_IN / name).unlink(missing_ok=True)
        shutil.copy(src, COMFY_IN / name)   # ComfyUI rejects symlinks out of its input folder
    json.dump({"take": a.take, "at": a.at, "frames": n, "size": [fw, fh], "x0": x0.tolist(), "y0": y0.tolist(),
               "cx": cx.tolist(), "cy": cy.tolist(), "face": fs.tolist(), "detected": int(ok.sum())},
              open(d / "track.json", "w"))
    print(f"{n} frames at {FPS} fps, face found in {int(ok.sum())}, face height median {np.median(fs):.0f} px; "
          f"crop -> {crop}, vocal {a.at:.2f}-{a.at + n / FPS:.2f} s -> {aud}")


def graph(stem, n, prompt, seed):
    crop, vocal = f"it-{stem}-crop.mp4", f"it-{stem}-vocal.wav"
    return {
        "1": {"class_type": "WanVideoVAELoader", "inputs": {"model_name": "wan_2.1_vae.safetensors", "precision": "bf16"}},
        "2": {"class_type": "MultiTalkModelLoader", "inputs": {"model": "Wan2_1-InfiniteTalk-Single_fp16.safetensors"}},
        "3": {"class_type": "WanVideoBlockSwap", "inputs": {"blocks_to_swap": 30, "offload_img_emb": False,
                                                             "offload_txt_emb": False, "use_non_blocking": False,
                                                             "vace_blocks_to_swap": 0, "prefetch_blocks": 0,
                                                             "block_swap_debug": False}},
        "4": {"class_type": "WanVideoLoraSelect", "inputs": {
            "lora": "lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors", "strength": 1.0}},
        "5": {"class_type": "WanVideoModelLoader", "inputs": {
            "model": "Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors", "base_precision": "bf16",
            "quantization": "fp8_e4m3fn_scaled", "load_device": "offload_device", "attention_mode": "sdpa",
            "block_swap_args": ["3", 0], "lora": ["4", 0], "multitalk_model": ["2", 0]}},
        "6": {"class_type": "WanVideoTextEncodeCached", "inputs": {
            "model_name": "umt5_xxl_fp16.safetensors", "precision": "bf16", "positive_prompt": prompt,
            "negative_prompt": "bright tones, overexposed, static, blurred details, subtitles, worst quality, low "
                               "quality, JPEG compression residue, ugly, deformed, disfigured, poorly drawn face, "
                               "extra fingers, messy background, text",
            "quantization": "disabled", "use_disk_cache": False, "device": "gpu"}},
        "7": {"class_type": "LoadVideo", "inputs": {"file": crop}},
        "8": {"class_type": "GetVideoComponents", "inputs": {"video": ["7", 0]}},
        "9": {"class_type": "ImageFromBatch", "inputs": {"image": ["8", 0], "batch_index": 0, "length": 1}},
        "10": {"class_type": "CLIPVisionLoader", "inputs": {"clip_name": "clip_vision_h.safetensors"}},
        "11": {"class_type": "WanVideoClipVisionEncode", "inputs": {
            "clip_vision": ["10", 0], "image_1": ["9", 0], "strength_1": 1.0, "strength_2": 1.0, "crop": "center",
            "combine_embeds": "average", "force_offload": True, "tiles": 0, "ratio": 0.5}},
        "12": {"class_type": "WanVideoImageToVideoMultiTalk", "inputs": {
            "vae": ["1", 0], "width": W, "height": H, "frame_window_size": 81, "motion_frame": 9,
            "force_offload": False, "colormatch": "disabled", "start_image": ["9", 0], "tiled_vae": True,
            "clip_embeds": ["11", 0], "mode": "infinitetalk"}},
        "13": {"class_type": "WanVideoEncode", "inputs": {
            "vae": ["1", 0], "image": ["8", 0], "enable_vae_tiling": True, "tile_x": 272, "tile_y": 272,
            "tile_stride_x": 144, "tile_stride_y": 128, "noise_aug_strength": 0.0, "latent_strength": 1.0}},
        "14": {"class_type": "LoadAudio", "inputs": {"audio": vocal}},
        "15": {"class_type": "Wav2VecModelLoader", "inputs": {
            "model": "wav2vec2-chinese-base_fp16.safetensors", "base_precision": "fp16", "load_device": "main_device"}},
        "16": {"class_type": "MultiTalkWav2VecEmbeds", "inputs": {
            "wav2vec_model": ["15", 0], "audio_1": ["14", 0], "normalize_loudness": True, "num_frames": n,
            "fps": float(FPS), "audio_scale": 1.0, "audio_cfg_scale": 1.0, "multi_audio_type": "para"}},
        "17": {"class_type": "WanVideoSampler", "inputs": {
            "model": ["5", 0], "image_embeds": ["12", 0], "text_embeds": ["6", 0], "samples": ["13", 0],
            "multitalk_embeds": ["16", 0], "steps": 4, "cfg": 1.0, "shift": 11.0, "seed": seed,
            "force_offload": True, "scheduler": "dpm++_sde", "riflex_freq_index": 0, "denoise_strength": 1.0,
            "batched_cfg": False, "rope_function": "comfy", "start_step": 2, "end_step": -1,
            "add_noise_to_samples": True}},
        "18": {"class_type": "WanVideoDecode", "inputs": {
            "vae": ["1", 0], "samples": ["17", 0], "enable_vae_tiling": True, "tile_x": 272, "tile_y": 272,
            "tile_stride_x": 144, "tile_stride_y": 128}},
        "19": {"class_type": "SaveImage", "inputs": {"images": ["18", 0], "filename_prefix": f"it/{stem}/f"}},
    }


def run(a):
    import time
    import urllib.request
    stem = Path(a.take).stem
    tr = json.load(open(outdir(a.take) / "track.json"))
    g = graph(stem, tr["frames"], a.prompt, a.seed)
    req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=json.dumps({"prompt": g}).encode(),
                                 headers={"Content-Type": "application/json"})
    pid = json.loads(urllib.request.urlopen(req).read())["prompt_id"]
    t0 = time.time()
    while True:
        time.sleep(5)
        h = json.load(urllib.request.urlopen(f"http://127.0.0.1:8188/history/{pid}"))
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                sys.exit(json.dumps(st.get("messages", []))[:3000])
            if st.get("completed"):
                break
    print(f"done in {time.time() - t0:.0f} s")


def paste(a):
    import av
    import cv2
    import numpy as np
    d = outdir(a.take)
    tr = json.load(open(d / "track.json"))
    pngs = sorted((ROOT / "media/clips/it/it" / Path(a.take).stem).glob("f_*.png"))  # ComfyUI writes <out>/it/<take>/
    frames = [f.to_ndarray(format="rgb24") for f in av.open(str(d / "25fps.mp4")).decode(video=0)]
    n = min(len(frames), len(pngs))
    out = d / f"{Path(a.take).stem}-it.video.mp4"
    c = av.open(str(out), "w")
    s = c.add_stream("libx264", rate=FPS)
    fh, fw = frames[0].shape[:2]
    s.width, s.height, s.pix_fmt, s.options = fw, fh, "yuv420p", {"crf": "16"}
    for k in range(n):
        g = cv2.cvtColor(cv2.imread(str(pngs[k])), cv2.COLOR_BGR2RGB)
        x0, y0, fsz = tr["x0"][k], tr["y0"][k], tr["face"][k]
        cx, cy = tr["cx"][k] - x0, tr["cy"][k] - y0
        m = np.zeros((H, W), np.float32)
        cv2.ellipse(m, (int(cx), int(cy + fsz * 0.05)), (int(fsz * 0.62), int(fsz * 0.72)), 0, 0, 360, 1.0, -1)
        m = cv2.GaussianBlur(m, (0, 0), fsz * 0.08)[..., None]
        img = frames[k].copy()
        reg = img[y0:y0 + H, x0:x0 + W].astype(np.float32)
        img[y0:y0 + H, x0:x0 + W] = (reg * (1 - m) + g.astype(np.float32) * m).astype(np.uint8)
        for p in s.encode(av.VideoFrame.from_ndarray(img, format="rgb24")):
            c.mux(p)
    for p in s.encode():
        c.mux(p)
    c.close()
    final = ROOT / "media/clips/preview" / f"{Path(a.take).stem}-it.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out), "-ss", f"{tr['at']:.3f}", "-t", f"{n / FPS:.3f}",
                    "-i", str(SONG), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", str(final)], check=True)
    out.unlink()
    # the raw crop result next to the source crop, for comparing the face alone
    side = ROOT / "media/clips/preview" / f"{Path(a.take).stem}-it-crop.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i",
                    str(pngs[0].parent / "f_%05d_.png"), "-i", str(d / "crop.mp4"), "-ss", f"{tr['at']:.3f}",
                    "-t", f"{n / FPS:.3f}", "-i", str(SONG), "-filter_complex", "[1:v][0:v]hstack[v]", "-map", "[v]",
                    "-map", "2:a", "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-shortest", str(side)], check=True)
    print(f"{n} frames -> {final}  and side by side (source | InfiniteTalk) -> {side}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["prep", "run", "paste"])
    ap.add_argument("take")
    ap.add_argument("--at", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--prompt", default="a young woman with a black bob and a headset microphone sings and dances "
                                         "energetically on a concert stage, clear mouth movements, stage lights")
    a = ap.parse_args()
    {"prep": prep, "run": run, "paste": paste}[a.step](a)


if __name__ == "__main__":
    main()

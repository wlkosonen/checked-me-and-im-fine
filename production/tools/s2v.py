#!/usr/bin/env python3
"""Wan 2.2 S2V: her plate sings our vocal while dancing a pose taken from a Grok take (lip sync and dance in one pass).

    media/cache/face-venv/bin/python production/tools/s2v.py prep NAME --plate PLATE.png --take TAKE.mp4 --at 43.74
    python3 production/tools/s2v.py run NAME [--steps 4] [--seed 7]          # ComfyUI must be up
    media/cache/face-venv/bin/python production/tools/s2v.py finish NAME

prep: the take's pose, frame by frame at S2V's 16 fps for one 77-frame chunk (4.81 s) from song time --at (the take
placed where its words land on ours): DWPose wholebody by rtmlib on the CPU, drawn OpenPose-style on black, her only (the
backing dancers' skeletons dropped), body and hands only (no face points, so the mouth is left to the audio). Also the plate resized to 832x480, and our vocal stem
for the same 4.81 s. Copies go into ComfyUI's input folder.
run: ComfyUI's native S2V graph (after its template video_wan2_2_14B_s2v): S2V 14B fp8 + the Wan 2.2 lightx2v 4-step
LoRA, shift 8, 4 steps at CFG 1, wav2vec2-large-english, ref_image = the plate, control_video = the pose; tiled VAE
decode (untiled 3D convolutions run out of memory here with MIOpen off). Frames come back as PNGs.
finish: frames -> 16 fps mp4 with our song under it, and a side-by-side with the pose.

Everything goes to media/clips/s2v/<name>/.
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
W, H, FPS, N = 832, 480, 16, 77
PROMPT = ("A young woman with a glossy black bob, one thin clay-orange streak in her bangs, a small clay-orange star hair "
          "clip and a thin headset microphone sings energetically into her microphone and dances on a concert stage, "
          "white stage lights and haze behind her, her mouth clearly shaping every word.")
NEG = ("bright tones, overexposed, static, blurred details, subtitles, text, worst quality, low quality, JPEG artifacts, "
       "ugly, deformed, disfigured, poorly drawn face, poorly drawn hands, extra fingers, fused fingers, messy background, "
       "many people in the background")


def outdir(name):
    d = ROOT / "media/clips/s2v" / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def prep(a):
    import av
    import cv2
    import numpy as np
    from rtmlib import Wholebody, draw_skeleton
    d = outdir(a.name)
    c = av.open(a.take)
    st = c.streams.video[0]
    fps = float(st.average_rate)
    src = [f.to_ndarray(format="bgr24") for f in c.decode(video=0)]
    body = Wholebody(mode="balanced", to_openpose=True, backend="onnxruntime", device="cpu")
    pose = d / "pose.mp4"
    out = av.open(str(pose), "w")
    s = out.add_stream("libx264", rate=FPS)
    s.width, s.height, s.pix_fmt, s.options = W, H, "yuv420p", {"crf": "12"}
    found = 0
    for k in range(N):
        t = k / FPS                                   # the take starts at --at
        img = cv2.resize(src[min(len(src) - 1, int(round(t * fps)))], (W, H), interpolation=cv2.INTER_AREA)
        kp, sc = body(img)
        canvas = np.zeros_like(img)
        if len(kp):
            found += 1
            sc = sc.copy()
            ok = sc[:, :18] > 0.3                     # keep only her: the person whose body points span the most height
            span = [np.ptp(kp[i, :18][ok[i], 1]) if ok[i].sum() > 2 else 0 for i in range(len(kp))]
            i = int(np.argmax(span))
            kp, sc = kp[i:i + 1], sc[i:i + 1]
            sc[:, 24:92] = 0                          # openpose order: 18 body, 6 feet, 68 face, 42 hands; drop the face
            canvas = draw_skeleton(canvas, kp, sc, openpose_skeleton=True, kpt_thr=0.3)
        for p in s.encode(av.VideoFrame.from_ndarray(canvas, format="bgr24")):
            out.mux(p)
    for p in s.encode():
        out.mux(p)
    out.close()
    ref = cv2.imread(a.plate)
    h0, w0 = ref.shape[:2]
    scale = max(W / w0, H / h0)
    r = cv2.resize(ref, (round(w0 * scale), round(h0 * scale)), interpolation=cv2.INTER_AREA)
    y, x = (r.shape[0] - H) // 2, (r.shape[1] - W) // 2
    cv2.imwrite(str(d / "ref.png"), r[y:y + H, x:x + W])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a.at:.3f}", "-t", f"{N / FPS:.4f}", "-i", str(VOCALS),
                    "-ac", "1", "-ar", "16000", str(d / "vocal.wav")], check=True)
    COMFY_IN.mkdir(exist_ok=True)
    for f, n in (("pose.mp4", "pose"), ("ref.png", "ref"), ("vocal.wav", "vocal")):
        shutil.copy(d / f, COMFY_IN / f"s2v-{a.name}-{n}{Path(f).suffix}")
    json.dump({"name": a.name, "plate": a.plate, "take": a.take, "at": a.at, "frames": N, "fps": FPS,
               "pose_found": found}, open(d / "prep.json", "w"), indent=1)
    print(f"pose in {found}/{N} frames; song {a.at:.2f}-{a.at + N / FPS:.2f} s -> {d}")


def graph(name, steps, seed, lora=True, cfg=1.0, tag=""):
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.2_s2v_14B_fp8_scaled.safetensors",
                                                     "weight_dtype": "default"}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {
            "model": ["1", 0], "lora_name": "wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors",
            "strength_model": 1.0}},
        "3": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["2", 0], "shift": 8.0}},
        "4": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp16.safetensors", "type": "wan",
                                                     "device": "default"}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": PROMPT, "clip": ["4", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["4", 0]}},
        "7": {"class_type": "VAELoader", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
        "8": {"class_type": "AudioEncoderLoader", "inputs": {"audio_encoder_name": "wav2vec2_large_english_fp16.safetensors"}},
        "9": {"class_type": "LoadAudio", "inputs": {"audio": f"s2v-{name}-vocal.wav"}},
        "10": {"class_type": "AudioEncoderEncode", "inputs": {"audio_encoder": ["8", 0], "audio": ["9", 0]}},
        "11": {"class_type": "LoadImage", "inputs": {"image": f"s2v-{name}-ref.png"}},
        "12": {"class_type": "LoadVideo", "inputs": {"file": f"s2v-{name}-pose.mp4"}},
        "13": {"class_type": "GetVideoComponents", "inputs": {"video": ["12", 0]}},
        "14": {"class_type": "WanSoundImageToVideo", "inputs": {
            "positive": ["5", 0], "negative": ["6", 0], "vae": ["7", 0], "width": W, "height": H, "length": N,
            "batch_size": 1, "audio_encoder_output": ["10", 0], "ref_image": ["11", 0], "control_video": ["13", 0]}},
        "15": {"class_type": "KSampler", "inputs": {
            "model": ["3", 0], "positive": ["14", 0], "negative": ["14", 1], "latent_image": ["14", 2], "seed": seed,
            "steps": steps, "cfg": 1.0, "sampler_name": "uni_pc", "scheduler": "simple", "denoise": 1.0}},
        "16": {"class_type": "VAEDecodeTiled", "inputs": {"samples": ["15", 0], "vae": ["7", 0], "tile_size": 256,
                                                          "overlap": 64, "temporal_size": 32, "temporal_overlap": 8}},
        "17": {"class_type": "SaveImage", "inputs": {"images": ["16", 0], "filename_prefix": f"s2v/{name}{tag}/f"}},
    }
    if not lora:                                  # full quality: no speed LoRA, 20 steps at CFG 6 (the template's)
        g["3"]["inputs"]["model"] = ["1", 0]
        del g["2"]
    g["15"]["inputs"]["cfg"] = cfg
    return g


def run(a):
    import time
    import urllib.request
    g = graph(a.name, a.steps, a.seed, lora=not a.full, cfg=6.0 if a.full else 1.0, tag="-full" if a.full else "")
    req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=json.dumps({"prompt": g}).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        pid = json.loads(urllib.request.urlopen(req).read())["prompt_id"]
    except urllib.error.HTTPError as e:
        sys.exit(e.read().decode()[:3000])
    t0 = time.time()
    while True:
        time.sleep(5)
        h = json.load(urllib.request.urlopen(f"http://127.0.0.1:8188/history/{pid}"))
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                sys.exit("ERROR " + json.dumps(st.get("messages", []))[-3000:])
            if st.get("completed"):
                break
    print(f"done in {time.time() - t0:.0f} s")


def finish(a):
    d = outdir(a.name)
    p = json.load(open(d / "prep.json"))
    tag = "-full" if a.full else ""
    frames = sorted((ROOT / "media/clips/it/s2v" / (a.name + tag)).glob("f_*.png"))  # ComfyUI's --output-directory is media/clips/it
    if not frames:
        sys.exit("no frames found")
    prev = ROOT / "media/clips/preview"
    out = prev / f"s2v-{a.name}{tag}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(frames[0].parent / "f_%05d_.png"),
                    "-ss", f"{p['at']:.3f}", "-t", f"{N / FPS:.4f}", "-i", str(SONG), "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    str(out)], check=True)
    side = prev / f"s2v-{a.name}{tag}-pose.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(frames[0].parent / "f_%05d_.png"),
                    "-i", str(d / "pose.mp4"), "-ss", f"{p['at']:.3f}", "-t", f"{N / FPS:.4f}", "-i", str(SONG),
                    "-filter_complex", "[0:v][1:v]hstack[v]", "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-crf",
                    "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(side)], check=True)
    print(f"{len(frames)} frames -> {out} and {side}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["prep", "run", "finish"])
    ap.add_argument("name")
    ap.add_argument("--plate")
    ap.add_argument("--take")
    ap.add_argument("--at", type=float, default=0.0)
    ap.add_argument("--steps", type=int, default=4)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--full", action="store_true", help="no speed LoRA: 20 steps at CFG 6")
    a = ap.parse_args()
    {"prep": prep, "run": run, "finish": finish}[a.step](a)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Repaint a picked plate's background with more detail, keeping her pixels exactly (Lati, 24 Oct: backgrounds read
barren next to the references).

    python3 production/tools/repaint.py PLATE.png --id p-s031r --prompt "..." [--seeds 4] [--denoise 0.9] [--grow 12]

In one ComfyUI graph: BiRefNet (ComfyUI's own Remove Background node, models/background_removal/birefnet.safetensors)
finds the foreground; the mask grows by --grow px so her edges stay hers; Krea 2 Turbo (+ her LoRA, so hair at the
edge stays hers) repaints only the background through SetLatentNoiseMask at --denoise; then the original plate is
composited back over the foreground with a feathered mask, so her face and clothes are the picked pixels. Saves the
repaint and the mask (prefix_mask) into ComfyUI's output directory; logs to production/images/renders.jsonl.
"""
import argparse
import json
import random
import shutil
import time
from pathlib import Path

from plate import LOG, get, post

INPUT = Path.home() / "ComfyUI/input"
# Only the harmonize pass names her (it repaints the whole frame lightly); the background pass describes the room alone,
# since any person in its prompt gets painted into the room as a second figure (24 Oct).
HER = ("clxudia, a woman in her late twenties, a fine-boned adult face, grown-up and composed, a glossy black blunt "
       "jaw-length bob, one thin clay-orange streak, a small clay-orange star hair clip, a thin headset microphone, a "
       "fitted white shirt with short puffed sleeves, black suspender straps, long black leather gloves. ")


def graph(img, prompt, seed, prefix, denoise, grow, lora, lora_strength, harmonize=0.0, steps=8):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8_scaled.safetensors",
                                                     "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_bf16.safetensors", "type": "krea2",
                                                     "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
        "10": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": lora,
                                                              "strength_model": lora_strength}},
        "20": {"class_type": "LoadImage", "inputs": {"image": img}},
        "21": {"class_type": "LoadBackgroundRemovalModel", "inputs": {"bg_removal_name": "birefnet.safetensors"}},
        "22": {"class_type": "RemoveBackground", "inputs": {"bg_removal_model": ["21", 0], "image": ["20", 0]}},
        "23": {"class_type": "GrowMask", "inputs": {"mask": ["22", 0], "expand": grow, "tapered_corners": True}},
        "24": {"class_type": "InvertMask", "inputs": {"mask": ["23", 0]}},
        "25": {"class_type": "VAEEncode", "inputs": {"pixels": ["20", 0], "vae": ["3", 0]}},
        "26": {"class_type": "SetLatentNoiseMask", "inputs": {"samples": ["25", 0], "mask": ["24", 0]}},
        "7": {"class_type": "KSampler", "inputs": {"model": ["10", 0], "positive": ["4", 0], "negative": ["5", 0],
                                                   "latent_image": ["26", 0], "seed": seed, "steps": steps,
                                                   "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple",
                                                   "denoise": denoise}},
        "8": {"class_type": "VAEDecodeTiled", "inputs": {"samples": ["7", 0], "vae": ["3", 0], "tile_size": 512,
                                                         "overlap": 64, "temporal_size": 64, "temporal_overlap": 8}},
        "27": {"class_type": "FeatherMask", "inputs": {"mask": ["23", 0], "left": 8, "top": 8, "right": 8,
                                                       "bottom": 8}},
        "28": {"class_type": "ImageCompositeMasked", "inputs": {"destination": ["8", 0], "source": ["20", 0],
                                                                "x": 0, "y": 0, "resize_source": False,
                                                                "mask": ["27", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["28", 0], "filename_prefix": prefix}},
        "40": {"class_type": "VAEEncode", "inputs": {"pixels": ["28", 0], "vae": ["3", 0]}},
        "44": {"class_type": "CLIPTextEncode", "inputs": {"text": HER + prompt, "clip": ["2", 0]}},
        "45": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["44", 0]}},
        "41": {"class_type": "KSampler", "inputs": {"model": ["10", 0], "positive": ["44", 0], "negative": ["45", 0],
                                                    "latent_image": ["40", 0], "seed": seed, "steps": steps,
                                                    "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple",
                                                    "denoise": max(harmonize, 0.01)}},
        "42": {"class_type": "VAEDecodeTiled", "inputs": {"samples": ["41", 0], "vae": ["3", 0], "tile_size": 512,
                                                          "overlap": 64, "temporal_size": 64, "temporal_overlap": 8}},
        "43": {"class_type": "SaveImage", "inputs": {"images": ["42", 0], "filename_prefix": prefix + "_h"}},
        "29": {"class_type": "MaskToImage", "inputs": {"mask": ["23", 0]}},
        "30": {"class_type": "SaveImage", "inputs": {"images": ["29", 0], "filename_prefix": prefix + "_mask"}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plate")
    ap.add_argument("--id", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--seeds", type=int, default=4)
    ap.add_argument("--denoise", type=float, default=0.9)
    ap.add_argument("--grow", type=int, default=-6, help="px; negative erodes, so the repaint covers her old edge "
                    "(a positive grow kept the old background's rim as a halo, 24 Oct)")
    ap.add_argument("--harmonize", type=float, default=0.0, help="also save a light full-frame pass (_h) at this "
                    "denoise, so the room's light reaches her; changes her pixels slightly")
    ap.add_argument("--lora", default="claudia/claudia-k2-v2-000010.safetensors")
    ap.add_argument("--lora-strength", type=float, default=0.75)
    a = ap.parse_args()
    name = f"repaint-{Path(a.plate).name}"
    shutil.copy(a.plate, INPUT / name)       # ComfyUI rejects symlinked inputs
    # BiRefNet needs ~2.3 GB on a new image; with Krea resident that runs out of memory (24 Oct), so unload first
    post("/free", {"unload_models": True, "free_memory": True})
    for _ in range(a.seeds):
        seed = random.randrange(2**31)
        prefix = f"{a.id}_s{seed}"
        t0 = time.time()
        g = graph(name, a.prompt, seed, prefix, a.denoise, a.grow, a.lora, a.lora_strength, a.harmonize)
        if a.harmonize <= 0:  # no light pass asked: drop its nodes (they ran anyway and cost ~40 s)
            for k in ("40", "41", "42", "43", "44", "45"):
                g.pop(k)
        pid = post("/prompt", {"prompt": g})["prompt_id"]
        while True:
            time.sleep(2)
            h = get(f"/history/{pid}")
            if pid in h:
                st = h[pid].get("status", {})
                if st.get("status_str") == "error":
                    raise RuntimeError(json.dumps(st.get("messages", []))[:2000])
                if st.get("completed"):
                    files = [i["filename"] for o in h[pid]["outputs"].values() for i in o.get("images", [])]
                    break
        dt = time.time() - t0
        with LOG.open("a") as f:
            f.write(json.dumps({"id": a.id, "seed": seed, "repaint_of": a.plate, "denoise": a.denoise,
                                "grow": a.grow, "harmonize": a.harmonize, "lora": a.lora, "lora_strength": a.lora_strength,
                                "seconds": round(dt, 1), "files": files, "prompt": a.prompt,
                                "at": time.strftime("%Y-%m-%dT%H:%M:%S")}) + "\n")
        print(f"{a.id}  seed {seed}  {dt:5.1f}s  {files}", flush=True)


if __name__ == "__main__":
    main()

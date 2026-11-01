#!/usr/bin/env python3
"""Layered 2.5D for a still shot: her cut-out over the room behind her, moving at different depths (parallax).

    python3 production/tools/layers.py fill s005 [s008 ...]                     # GPU, ComfyUI running
    media/cache/face-venv/bin/python production/tools/layers.py move s005 [...]  # CPU

Lati, 26 Oct: the keynote shots read as cut-outs pasted on a stage; Evil Plan's layered 2.5D answers that
(notes/reference-evil-plan.md). fill: BiRefNet finds her in the shot's picked plate; Krea paints the room where she
stood (her mask grown by 28 px, denoise 1, a room-only prompt from ROOMS: a person named in it would be painted in,
24 Oct); saves media/layers/<sid>_room and <sid>_mask (start ComfyUI with --out media/layers). move: the room drifts
and pushes in slowly, she pushes in faster and drifts the other way, over the shot's board window; writes
media/clips/shot/<sid>.mp4 (1280x720, 25 fps), which roughcut.py plays in place of the still.
"""
import glob
import json
import re
import random
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAYERS = ROOT / "media/layers"
LOOK = "Shot on a digital cinema camera, crisp and clean, vivid colour, a soft glow on the lights."
ROOMS = {
    "s005": "A glossy tech launch keynote stage seen from the side, a giant screen glowing an electric cobalt-to-magenta "
            "gradient, magenta and violet spotlights in light haze, the audience's heads in silhouette at the stage edge.",
    "s008": "A glossy keynote stage seen from the front, a giant screen glowing cobalt-to-magenta, its colours reflected "
            "in the polished stage floor, a row of magenta spotlights in light haze, the audience in silhouette.",
    "s009": "A glossy keynote stage seen from the back of the stage, a giant screen glowing cobalt-to-magenta, magenta "
            "spotlights in light haze, the polished stage floor, the audience in silhouette.",
    "s038": "A bright corporate conference stage, a large screen with a teal border and a yellow slide, a white lectern, "
            "rows of pink, yellow and teal chairs.",
    "s041": "A bright corporate conference stage, a large yellow and teal screen, a pale green lectern with a "
            "microphone, rows of pink, yellow and teal chairs on a wooden floor.",
    "s062": "A huge concert stage, white beams through haze, a bright LED wall with backing dancers in silhouette, the "
            "crowd's raised phones glowing in the foreground.",
    "s069": "A huge arena concert stage seen down the runway, white beams sweeping through haze, backing dancers in "
            "silhouette at the end of the runway, the crowd's phone lights glowing all around.",
}
# room repaint strength over the wiped area; s005's bright screen kept a pale trace of her arm at 0.9 (26 Oct)
DENOISE = {"s005": 1.0}
# per shot: room push, her push, room drift, her drift (fractions of the frame over the shot)
MOVES = {"default": (0.03, 0.07, -0.012, 0.006)}


def plate_of(sid):
    return ROOT / json.loads((ROOT / "production/board/picks.json").read_text())[f"p-{sid}"]["file"]


def fill(sids):
    """The room behind her, in three steps (26 Oct: painting straight over her left ghosts of her shape, because the
    sampler started from a picture with her in it): BiRefNet's mask (GPU), her area wiped by smearing the colours
    around it in (OpenCV, CPU), then Krea paints the room into the wiped area (GPU)."""
    import cv2
    import numpy as np
    from plate import get, post

    def run(g):
        pid = post("/prompt", {"prompt": g})["prompt_id"]
        while True:
            time.sleep(2)
            h = get(f"/history/{pid}")
            if pid in h:
                st = h[pid].get("status", {})
                if st.get("status_str") == "error":
                    raise RuntimeError(json.dumps(st.get("messages", []))[:2000])
                if st.get("completed"):
                    return
    inp = Path.home() / "ComfyUI/input"
    for sid in sids:
        t0 = time.time()
        if not latest(f"{sid}_mask_*.png"):
            shutil.copy(plate_of(sid), inp / f"layers-{sid}.png")
            post("/free", {"unload_models": True, "free_memory": True})  # BiRefNet ran out of memory beside Krea (24 Oct)
            run({"20": {"class_type": "LoadImage", "inputs": {"image": f"layers-{sid}.png"}},
                 "21": {"class_type": "LoadBackgroundRemovalModel", "inputs": {"bg_removal_name": "birefnet.safetensors"}},
                 "22": {"class_type": "RemoveBackground", "inputs": {"bg_removal_model": ["21", 0], "image": ["20", 0]}},
                 "29": {"class_type": "MaskToImage", "inputs": {"mask": ["22", 0]}},
                 "30": {"class_type": "SaveImage", "inputs": {"images": ["29", 0], "filename_prefix": f"{sid}_mask"}}})
        plate = cv2.imread(str(plate_of(sid)))
        mask = cv2.imread(latest(f"{sid}_mask_*.png"), cv2.IMREAD_GRAYSCALE)
        grown = cv2.dilate((mask > 40).astype(np.uint8) * 255, np.ones((3, 3), np.uint8), iterations=14)
        wiped = cv2.inpaint(plate, grown, 21, cv2.INPAINT_TELEA)
        cv2.imwrite(str(inp / f"layers-{sid}-wiped.png"), wiped)
        cv2.imwrite(str(inp / f"layers-{sid}-hole.png"), cv2.GaussianBlur(grown, (0, 0), 6))
        cv2.imwrite(str(LAYERS / f"{sid}_wiped.png"), wiped)
        seed = random.randrange(2**31)
        run({
            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8_scaled.safetensors",
                                                         "weight_dtype": "default"}},
            "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_bf16.safetensors", "type": "krea2",
                                                         "device": "default"}},
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
            "4": {"class_type": "CLIPTextEncode", "inputs": {"text": f"{ROOMS[sid]} {LOOK}", "clip": ["2", 0]}},
            "5": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
            "20": {"class_type": "LoadImage", "inputs": {"image": f"layers-{sid}-wiped.png"}},
            "21": {"class_type": "LoadImageMask", "inputs": {"image": f"layers-{sid}-hole.png", "channel": "red"}},
            "25": {"class_type": "VAEEncode", "inputs": {"pixels": ["20", 0], "vae": ["3", 0]}},
            "26": {"class_type": "SetLatentNoiseMask", "inputs": {"samples": ["25", 0], "mask": ["21", 0]}},
            "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0],
                                                       "latent_image": ["26", 0], "seed": seed, "steps": 8, "cfg": 1.0,
                                                       "sampler_name": "euler", "scheduler": "simple", "denoise": DENOISE.get(sid, 0.9)}},
            "8": {"class_type": "VAEDecodeTiled", "inputs": {"samples": ["7", 0], "vae": ["3", 0], "tile_size": 512,
                                                             "overlap": 64, "temporal_size": 64, "temporal_overlap": 8}},
            "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": f"{sid}_room2"}},
        })
        print(f"{sid}: room in {time.time() - t0:.0f} s (seed {seed})", flush=True)


def stage(sids, seeds=2):
    """Lati's order (26 Oct): the empty room first, then her painted into it. Krea renders the room with nobody in it
    (whole geometry, nothing painted over); then Krea with her LoRA paints her only where she stood in the picked
    plate (BiRefNet's mask of it, grown, so her pose can settle), lit by that room. Saves <sid>_empty_s<seed> and
    <sid>_her_s<room seed>-<seed> for Lati to pick; the empty room is the back layer, her cut from the pick the front."""
    import cv2
    import numpy as np
    from plate import get, graph, post
    board = json.loads((ROOT / "production/board/board.json").read_text())
    prompts = {p["plate"]: p["prompt"] for p in board["plates"]}
    shots = {s["id"]: s for s in board["shots"]}
    lora = "claudia/claudia-k2-v2-000010.safetensors"

    def run(g):
        pid = post("/prompt", {"prompt": g})["prompt_id"]
        while True:
            time.sleep(2)
            h = get(f"/history/{pid}")
            if pid in h:
                st = h[pid].get("status", {})
                if st.get("status_str") == "error":
                    raise RuntimeError(json.dumps(st.get("messages", []))[:2000])
                if st.get("completed"):
                    return [i["filename"] for o in h[pid]["outputs"].values() for i in o.get("images", [])]
    inp = Path.home() / "ComfyUI/input"
    for sid in sids:
        mask = cv2.imread(latest(f"{sid}_mask_*.png"), cv2.IMREAD_GRAYSCALE)
        where = cv2.dilate((mask > 40).astype(np.uint8) * 255, np.ones((3, 3), np.uint8), iterations=18)
        cv2.imwrite(str(inp / f"layers-{sid}-where.png"), cv2.GaussianBlur(where, (0, 0), 8))
        her = prompts[shots[sid]["plate"]].replace("clxudia", "clxudia") + f" The room: {ROOMS[sid]}"
        for _ in range(seeds):
            rs = random.randrange(2**31)
            room = run(graph(f"{ROOMS[sid]} An empty stage before the show. {LOOK}", 1344, 768, rs, f"{sid}_empty_s{rs}"))[0]
            shutil.copy(LAYERS / room, inp / f"layers-{sid}-empty-{rs}.png")
            for _ in range(seeds):
                hs = random.randrange(2**31)
                g = graph(her, 1344, 768, hs, f"{sid}_her_s{rs}-{hs}", lora=lora, lora_strength=0.75)
                g["20"] = {"class_type": "LoadImage", "inputs": {"image": f"layers-{sid}-empty-{rs}.png"}}
                g["21"] = {"class_type": "LoadImageMask", "inputs": {"image": f"layers-{sid}-where.png", "channel": "red"}}
                g["22"] = {"class_type": "VAEEncode", "inputs": {"pixels": ["20", 0], "vae": ["3", 0]}}
                g["23"] = {"class_type": "SetLatentNoiseMask", "inputs": {"samples": ["22", 0], "mask": ["21", 0]}}
                ks = next(k for k, n in g.items() if n["class_type"] == "KSampler")
                g[ks]["inputs"]["latent_image"] = ["23", 0]
                g[ks]["inputs"]["denoise"] = 1.0
                run(g)
            print(f"{sid}: room s{rs} and {seeds} of her in it", flush=True)


def masks(names):
    """BiRefNet's mask of each image of her painted into a room (stage), saved as <name>_m, for the front layer."""
    from plate import get, post
    inp = Path.home() / "ComfyUI/input"
    post("/free", {"unload_models": True, "free_memory": True})
    for n in names:
        shutil.copy(LAYERS / f"{n}_00001_.png", inp / f"layers-{n}.png")
        pid = post("/prompt", {"prompt": {
            "20": {"class_type": "LoadImage", "inputs": {"image": f"layers-{n}.png"}},
            "21": {"class_type": "LoadBackgroundRemovalModel", "inputs": {"bg_removal_name": "birefnet.safetensors"}},
            "22": {"class_type": "RemoveBackground", "inputs": {"bg_removal_model": ["21", 0], "image": ["20", 0]}},
            "29": {"class_type": "MaskToImage", "inputs": {"mask": ["22", 0]}},
            "30": {"class_type": "SaveImage", "inputs": {"images": ["29", 0], "filename_prefix": f"{n}_m"}}}})["prompt_id"]
        while pid not in get(f"/history/{pid}"):
            time.sleep(1)
        print(n, "mask", flush=True)


def latest(pattern):
    f = sorted(glob.glob(str(LAYERS / pattern)), key=lambda p: Path(p).stat().st_mtime)
    return f[-1] if f else None


def move(sids):
    import av
    import cv2
    import numpy as np
    W, H, FPS = 1280, 720, 25
    shots = {s["id"]: s for s in json.loads((ROOT / "production/board/board.json").read_text())["shots"]}

    def cover(im):
        h, w = im.shape[:2]
        s = max(W / w, H / h)
        im = cv2.resize(im, (round(w * s), round(h * s)), interpolation=cv2.INTER_LANCZOS4)
        y, x = (im.shape[0] - H) // 2, (im.shape[1] - W) // 2
        return im[y:y + H, x:x + W]

    def warp(im, z, dx, cx, cy):
        m = np.float32([[z, 0, (1 - z) * cx + dx], [0, z, (1 - z) * cy]])
        return cv2.warpAffine(im, m, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

    for name in sids:
        sid = name[:4]
        if "_her_" in name:  # Lati's order: the empty room behind, her painted into it in front
            rs = re.search(r"_her_s(\d+)-", name).group(1)
            plate = cover(cv2.cvtColor(cv2.imread(str(LAYERS / f"{name}_00001_.png")), cv2.COLOR_BGR2RGB)).astype(np.float32)
            room = cover(cv2.cvtColor(cv2.imread(latest(f"{sid}_empty_s{rs}_*.png")), cv2.COLOR_BGR2RGB)).astype(np.float32)
            raw = cv2.imread(latest(f"{name}_m_*.png"), cv2.IMREAD_GRAYSCALE)
        else:
            plate = cover(cv2.cvtColor(cv2.imread(str(plate_of(sid))), cv2.COLOR_BGR2RGB)).astype(np.float32)
            room = cover(cv2.cvtColor(cv2.imread(latest(f"{sid}_room*.png")), cv2.COLOR_BGR2RGB)).astype(np.float32)
            raw = cv2.imread(latest(f"{sid}_mask_*.png"), cv2.IMREAD_GRAYSCALE)
        if "_her_" in name:
            # room-first: the room behind her edge is the same room, so no erosion (it thinned her fingertips to
            # nothing, Lati 26 Oct); BiRefNet's faint fingertips are lifted to solid instead
            raw = np.clip((raw.astype(np.float32) - 20) * 2.2, 0, 255).astype(np.uint8)
            raw = cv2.GaussianBlur(raw, (0, 0), 0.8)
        else:
            # her edge pulled in 2 px and softened, so no strip of the old background travels with her (26 Oct: halo)
            raw = cv2.GaussianBlur(cv2.erode(raw, np.ones((3, 3), np.uint8), iterations=2), (0, 0), 1.2)
        mask = cover(raw).astype(np.float32) / 255
        ys, xs = np.nonzero(mask > 0.5)
        cx, cy = float(xs.mean()), float(ys.mean())  # she grows from her middle (from her feet, s069's head left the frame)
        zb, zf, db, df = MOVES.get(sid, MOVES["default"])
        s = shots[sid]
        n = round((s["t1"] - s["t0"]) * FPS)
        dest = ROOT / (f"media/layers/preview/{name}.mp4" if "_her_" in name else f"media/clips/shot/{sid}.mp4")
        dest.parent.mkdir(parents=True, exist_ok=True)
        out = av.open(str(dest), "w")
        vs = out.add_stream("libx264", rate=FPS)
        vs.width, vs.height, vs.pix_fmt = W, H, "yuv420p"
        vs.options = {"crf": "18", "preset": "veryfast"}
        for i in range(n):
            k = i / max(n - 1, 1)
            k = k * k * (3 - 2 * k) * 0.6 + k * 0.4  # gentle ease, never fully stopped
            bg = warp(room, 1 + zb * k, db * W * k, W / 2, H / 2)
            fg = warp(plate, 1 + zf * k, df * W * k, cx, cy)
            a = warp(mask, 1 + zf * k, df * W * k, cx, cy)[..., None]
            im = (fg * a + bg * (1 - a)).clip(0, 255).astype(np.uint8)
            for p in vs.encode(av.VideoFrame.from_ndarray(im, format="rgb24")):
                out.mux(p)
        for p in vs.encode():
            out.mux(p)
        out.close()
        print(f"{name}: {n} frames -> {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    cmd, sids = sys.argv[1], sys.argv[2:]
    LAYERS.mkdir(parents=True, exist_ok=True)
    (ROOT / "media/clips/shot").mkdir(parents=True, exist_ok=True)
    {"fill": fill, "stage": stage, "masks": masks, "move": move}[cmd](sids)

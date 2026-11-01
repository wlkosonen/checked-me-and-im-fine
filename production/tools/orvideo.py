#!/usr/bin/env python3
"""Image (+ audio) to video through OpenRouter's video API. Paid: every run needs Lati's yes and an estimate.

    python3 production/tools/orvideo.py --model alibaba/wan-2.7 --image PLATE --audio CLIP.mp3 --seconds 5 \
        --prompt "..." --out media/clips/or/NAME.mp4

POST /api/v1/videos with the plate as the first frame; the audio (our vocal) goes to the provider as its `audio`
parameter, so the mouth follows our song (Wan 2.6 / 2.7 audio-driven mode). Polls every 20 s, downloads, and logs the
request, job id, status and cost to production/motion/orvideo.jsonl. The key comes from .env (OPENROUTER_API_KEY) and
is never printed.
"""
import argparse
import base64
import json
import mimetypes
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API = "https://openrouter.ai/api/v1"
LOG = ROOT / "production/motion/orvideo.jsonl"


def key():
    for line in (ROOT / ".env").read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("no OPENROUTER_API_KEY in .env")


def call(path, body=None, raw=False):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {key()}", "Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=120).read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode()[:800]}")
    return r if raw else json.loads(r)


def data_url(p):
    mime = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(Path(p).read_bytes()).decode()}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--image", required=True)
    ap.add_argument("--audio")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--seconds", type=int, default=5)
    ap.add_argument("--resolution", default="720p")
    ap.add_argument("--provider", default="atlas-cloud")
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-gen-audio", action="store_true", help="generate_audio false (else the model sings its own)")
    a = ap.parse_args()
    body = {"model": a.model, "prompt": a.prompt, "duration": a.seconds, "resolution": a.resolution,
            "aspect_ratio": "16:9",
            "frame_images": [{"type": "image_url", "image_url": {"url": data_url(a.image)}, "frame_type": "first_frame"}]}
    if a.no_gen_audio:
        body["generate_audio"] = False
    if a.audio:
        aud = a.audio if a.audio.startswith("https://") else data_url(a.audio)  # AtlasCloud may want a URL
        body["provider"] = {"options": {a.provider: {"parameters": {"audio": aud}}}}
    rec = {"t": time.strftime("%Y-%m-%d %H:%M:%S"), "model": a.model, "image": a.image,
           "audio": "temporary URL" if a.audio and a.audio.startswith("https://") else a.audio,
           "prompt": a.prompt, "seconds": a.seconds, "resolution": a.resolution, "out": a.out}
    job = call("/videos", body)
    rec["job"] = job.get("id")
    print("job", job.get("id"), job.get("status"), flush=True)
    while True:
        time.sleep(20)
        st = call(f"/videos/{job['id']}")
        if st["status"] in ("completed", "failed"):
            break
        print(" ", st["status"], flush=True)
    rec.update(status=st["status"], usage=st.get("usage"), error=st.get("error"))
    if st["status"] == "completed":
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_bytes(call(f"/videos/{job['id']}/content?index=0", raw=True))
    with open(LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(st["status"], "cost", (st.get("usage") or {}).get("cost"), st.get("error") or a.out)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""The Shorts, cut from the final film.

    media/cache/gfx-venv/bin/python production/tools/shorts.py [media/final/checked-me-1080p-v2.mp4]

The 16:9 frame sits whole over a blurred, enlarged copy of itself, as in film 1: cropping to 9:16 would cut the graphics off.
Under the picture, in the counter's pill, "full video on the channel" (Lati, 1 Nov), inside Shorts' safe area: YouTube's title
covers the bottom of the frame and its buttons the right edge.
"""

import subprocess
import sys
from pathlib import Path

import gfx
from gfx import INK, WHITE, Canvas, width
from PIL import Image

ROOT = gfx.ROOT
OUT = ROOT / "media/final/shorts"
SHORTS = {
    "short-1-im-fine": (42.272, 56.799),
    "short-1a-the-walk": (96.581, 109.22),
    "short-1b-fine-fine-fine": (64.05, 73.094),
    "short-2-your-notes": (73.094, 87.569),
    "short-3-you-checked-me": (141.802, 158.097),
}
LINE, PX, Y = "full video on the channel", 50, 1352


def card(path):
    c = Canvas(1080, 1920, 1.0)
    w = width(LINE, "mono", PX)
    x0 = (1080 - w) / 2 - 40  # a little left of centre: Shorts' buttons sit on the right
    c.rect(x0 - 28, Y - PX - 14, x0 + w + 28, Y + 22, INK, alpha=0.72, r=12)
    c.text(LINE, x0, Y, "mono", PX, WHITE)
    Image.fromarray(c.a).save(path)


def main():
    film = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "media/final/checked-me-1080p-v2.mp4")
    OUT.mkdir(exist_ok=True)
    pill = OUT / "line.png"
    card(pill)
    for name, (a, b) in SHORTS.items():
        fg = ("[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.12[bg];[b]scale=1080:-2[fg];"
              "[bg][fg]overlay=0:(H-h)/2[m];[m][1:v]overlay=0:0:alpha=premultiplied,format=yuv420p[v];"
              f"[0:a]afade=t=out:st={b - a - 0.15:.3f}:d=0.15[au]")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(a), "-to", str(b), "-i", str(film),
                        "-i", str(pill), "-filter_complex", fg, "-map", "[v]", "-map", "[au]", "-r", "25", "-c:v", "libx264",
                        "-crf", "18", "-preset", "slow", "-c:a", "aac", "-b:a", "256k", str(OUT / f"{name}.mp4")], check=True)
        print(name)
    pill.unlink()


if __name__ == "__main__":
    main()

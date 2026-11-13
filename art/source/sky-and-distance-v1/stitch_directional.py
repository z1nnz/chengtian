"""Crossfade two painted directional source images into a 4K opaque arc strip.

Usage: python stitch_directional.py SK03
The selected sources are stored in a sibling ID directory.  Output includes
the whole 4096x1024 strip, two exact 2048x1024 halves and mobile reduction.
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image


ID = sys.argv[1]
if ID not in {"SK03", "SK04", "SK05", "SK06"}:
    raise ValueError("Expected SK03, SK04, SK05 or SK06")
BASE = Path(__file__).resolve().parent
SRC = BASE / ID
OUT = BASE.parents[1] / "exports" / "sky-and-distance-v1" / ID
OUT.mkdir(parents=True, exist_ok=True)


def source(side: str) -> np.ndarray:
    im = Image.open(SRC / f"{ID}_{side}_selected.png").convert("RGB")
    if im.size != (1672, 941):
        raise ValueError(f"Unexpected source dimensions: {im.size}")
    return np.asarray(im.crop((0, 105, 1672, 849)).resize((2304, 1024), Image.Resampling.LANCZOS), dtype=np.float32)


a, b = source("left"), source("right")
canvas = np.empty((1024, 4096, 3), dtype=np.float32)
canvas[:, :1792] = a[:, :1792]
t = np.linspace(0, 1, 512, dtype=np.float32)[None, :, None]
t = t * t * (3 - 2 * t)
canvas[:, 1792:2304] = a[:, 1792:2304] * (1 - t) + b[:, :512] * t
canvas[:, 2304:] = b[:, 512:]

sky = np.array([211, 226, 237], dtype=np.float32)[None, None, :]
fade = np.clip((np.arange(1024, dtype=np.float32)[:, None, None] - 35) / 165, 0, 1)
canvas = sky * (1 - fade) + canvas * fade
if ID == "SK06":
    # SK06 wraps a full circle: blend both outer edges to the same column.
    shared = (canvas[:, 0, :] + canvas[:, -1, :]) * 0.5
    edge = np.linspace(0, 1, 256, dtype=np.float32)[None, :, None]
    edge = edge * edge * (3 - 2 * edge)
    canvas[:, :256] = shared[:, None, :] * (1 - edge) + canvas[:, :256] * edge
    canvas[:, -256:] = canvas[:, -256:] * (1 - edge) + shared[:, None, :] * edge
im = Image.fromarray(np.uint8(np.clip(canvas, 0, 255)), "RGB")
im.save(OUT / f"{ID}_panorama_4096x1024.png", optimize=True)
im.crop((0, 0, 2048, 1024)).save(OUT / f"{ID}_left_2048x1024.png", optimize=True)
im.crop((2048, 0, 4096, 1024)).save(OUT / f"{ID}_right_2048x1024.png", optimize=True)
im.resize((2048, 512), Image.Resampling.LANCZOS).save(OUT / f"{ID}_mobile_2048x512.png", optimize=True)
print(OUT)

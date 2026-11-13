"""Assemble two approved SK02 painted sources into one opaque 4:1 skyline.

The 512px overlapping region is crossfaded; the final canvas is then split
into two exact 2048px halves for engine import.  Source PNGs are kept beside
this script so the result can be regenerated without an external cache.
"""

from pathlib import Path

import numpy as np
from PIL import Image


BASE = Path(__file__).resolve().parent
SRC = BASE / "SK02"
OUT = BASE.parents[1] / "exports" / "sky-and-distance-v1" / "SK02"
OUT.mkdir(parents=True, exist_ok=True)


def prepare(name: str) -> np.ndarray:
    im = Image.open(SRC / name).convert("RGB")
    if im.size != (1672, 941):
        raise ValueError(f"Unexpected source dimensions: {im.size}")
    # 1672/744 and 2304/1024 are close; no large horizontal distortion.
    return np.asarray(im.crop((0, 105, 1672, 849)).resize((2304, 1024), Image.Resampling.LANCZOS), dtype=np.float32)


left = prepare("SK02_left_selected.png")
right = prepare("SK02_right_selected.png")
out = np.empty((1024, 4096, 3), dtype=np.float32)
out[:, :1792] = left[:, :1792]
mix = np.linspace(0, 1, 512, dtype=np.float32)[None, :, None]
mix = mix * mix * (3 - 2 * mix)
out[:, 1792:2304] = left[:, 1792:2304] * (1 - mix) + right[:, :512] * mix
out[:, 2304:] = right[:, 512:]

# Opaque sky-colour fade; no alpha edge or clip artefacts on the arc.
sky = np.array([211, 226, 237], dtype=np.float32)[None, None, :]
rows = np.arange(1024, dtype=np.float32)[:, None, None]
fade = np.clip((rows - 35) / 165, 0, 1)
out = sky * (1 - fade) + out * fade
result = Image.fromarray(np.uint8(np.clip(out, 0, 255)), "RGB")
result.save(OUT / "SK02_north_near_4096x1024.png", optimize=True)
result.crop((0, 0, 2048, 1024)).save(OUT / "SK02_north_near_left_2048x1024.png", optimize=True)
result.crop((2048, 0, 4096, 1024)).save(OUT / "SK02_north_near_right_2048x1024.png", optimize=True)
result.resize((2048, 512), Image.Resampling.LANCZOS).save(OUT / "SK02_north_near_mobile_2048x512.png", optimize=True)
print(OUT)

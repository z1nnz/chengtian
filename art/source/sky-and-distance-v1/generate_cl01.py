"""Paint four soft cloud-sea cards for the distant world boundary.

Each card has feathered lateral edges and is intended to overlap its neighbour;
the file is not a cutout skyline and must use alpha blending, not alpha clip.
"""

from pathlib import Path

import numpy as np
from PIL import Image


W, H = 2048, 1024
OUT = Path(__file__).resolve().parents[2] / "exports" / "sky-and-distance-v1" / "CL01"
OUT.mkdir(parents=True, exist_ok=True)
X = np.linspace(0, 1, W, dtype=np.float32)[None, :]
Y = np.linspace(0, 1, H, dtype=np.float32)[:, None]


def field(seed: int, gx: int, gy: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    small = rng.integers(0, 256, (gy, gx), dtype=np.uint8)
    return np.asarray(Image.fromarray(small).resize((W, H), Image.Resampling.BICUBIC), dtype=np.float32) / 255.0 - 0.5


def smoothstep(v: np.ndarray) -> np.ndarray:
    v = np.clip(v, 0, 1)
    return v * v * (3 - 2 * v)


for n in range(1, 5):
    seed = 110810 + n * 11
    rng = np.random.default_rng(seed)
    shape = np.zeros((H, W), dtype=np.float32)
    for _ in range(12):
        cx = rng.uniform(-0.08, 1.08)
        cy = rng.uniform(0.38, 0.72)
        sx = rng.uniform(0.10, 0.24)
        sy = rng.uniform(0.065, 0.14)
        shape = np.maximum(shape, np.exp(-(((X - cx) / sx) ** 2 + ((Y - cy) / sy) ** 2) * 1.9))
    broad = field(seed + 1, 17, 8)
    middle = field(seed + 2, 57, 22)
    detail = field(seed + 3, 126, 39)
    density = np.clip(shape * 0.84 + broad * 0.30 + middle * 0.13 + detail * 0.055 - 0.18, 0, 1)
    # The soft body extends downwards to become a sea, with no rectangular edge.
    body = smoothstep((Y - 0.49) / 0.22) * 0.46
    density = np.maximum(density, body * (0.85 + broad * 0.2))
    top_bottom = smoothstep((Y - 0.14) / 0.16) * (1 - smoothstep((Y - 0.87) / 0.13))
    sides = smoothstep(X / 0.075) * smoothstep((1 - X) / 0.075)
    alpha = np.uint8(np.clip(density * top_bottom * sides * 195, 0, 190))
    light = np.clip((0.6 - Y) * 26 + broad * 18 + middle * 8, -20, 20)
    rgb = np.empty((H, W, 3), dtype=np.uint8)
    rgb[:, :, 0] = np.uint8(np.clip(224 + light, 0, 255))
    rgb[:, :, 1] = np.uint8(np.clip(234 + light, 0, 255))
    rgb[:, :, 2] = np.uint8(np.clip(238 + light, 0, 255))
    out = np.dstack((rgb, alpha))
    Image.fromarray(out, "RGBA").save(OUT / f"CL01_cloud_sea_{n:02}.png", optimize=True)
print(OUT)

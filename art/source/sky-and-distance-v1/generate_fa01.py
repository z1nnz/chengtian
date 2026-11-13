"""Three distant waterfall flow textures and one soft foot-spray texture.

Flow maps are 1024x2048 RGBA. V first and last rows match exactly so a
downward-scrolling material can repeat.  The visible water never touches the
horizontal edges of its plane.
"""

from pathlib import Path

import numpy as np
from PIL import Image


W, H = 1024, 2048
OUT = Path(__file__).resolve().parents[2] / "exports" / "sky-and-distance-v1" / "FA01"
OUT.mkdir(parents=True, exist_ok=True)
X = np.arange(W, dtype=np.float32)[None, :]
Y = np.arange(H, dtype=np.float32)[:, None]


def turbulence(seed: int, gx: int, gy: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    pixels = rng.integers(0, 256, (gy, gx), dtype=np.uint8)
    pixels[-1] = pixels[0]
    data = np.asarray(Image.fromarray(pixels).resize((W, H), Image.Resampling.BICUBIC), dtype=np.float32) / 255.0 - 0.5
    data[-1] = data[0]
    return data


for n in (1, 2, 3):
    seed = 110840 + n * 8
    broad = turbulence(seed, 21, 45)
    fine = turbulence(seed + 1, 89, 120)
    filament = turbulence(seed + 2, 360, 245)
    phase = (Y / H) * np.pi * 8
    center = W * (0.49 + 0.025 * np.sin(phase + n)) + broad * 33
    width = 165 + 20 * np.sin(phase * 0.5 + n * 0.7)
    dist = np.abs(X - center) / width
    soft_edge = np.clip((1.15 - dist) / 0.35, 0, 1)
    # Longitudinal bright threads remain coherent over many pixels of height.
    # Short horizontal breaks are subordinate to the downward visual flow.
    stream = np.sin(X / (8.0 + n) + np.sin(phase) * 0.65 + n * 0.8)
    second_stream = np.sin(X / (21.0 + n * 2) - np.cos(phase * 0.5) * 0.5)
    flecks = np.clip(0.50 + stream * 0.25 + second_stream * 0.16 + fine * 0.13 + filament * 0.045, 0, 1)
    alpha = np.uint8(np.clip(soft_edge * (0.30 + flecks * 0.60) * 220, 0, 208))
    rgb = np.empty((H, W, 3), dtype=np.uint8)
    rgb[:, :, 0] = np.uint8(np.clip(188 + flecks * 55 + broad * 12, 0, 255))
    rgb[:, :, 1] = np.uint8(np.clip(217 + flecks * 35 + broad * 7, 0, 255))
    rgb[:, :, 2] = np.uint8(np.clip(226 + flecks * 26 + broad * 6, 0, 255))
    rgba = np.dstack((rgb, alpha))
    rgba[-1] = rgba[0]
    Image.fromarray(rgba, "RGBA").save(OUT / f"FA01_flow_{n:02}.png", optimize=True)

spray_h = 512
sx = np.linspace(-1, 1, W, dtype=np.float32)[None, :]
sy = np.linspace(-1, 1, spray_h, dtype=np.float32)[:, None]
spray_noise = np.random.default_rng(110849).normal(0, 0.15, (spray_h, W)).astype(np.float32)
mist = np.clip(np.exp(-((sx / 0.58) ** 2 + (sy / 0.60) ** 2) * 1.8) + spray_noise * 0.10, 0, 1)
spray = np.empty((spray_h, W, 4), dtype=np.uint8)
spray[:, :, :3] = [216, 235, 239]
spray[:, :, 3] = np.uint8(mist * 128)
Image.fromarray(spray, "RGBA").save(OUT / "FA01_foot_spray.png", optimize=True)
print(OUT)

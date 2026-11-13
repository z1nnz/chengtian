"""Six repeatable U-axis mountain-waist cloud belts, 2048x512 RGBA."""

from pathlib import Path

import numpy as np
from PIL import Image


W, H = 2048, 512
OUT = Path(__file__).resolve().parents[2] / "exports" / "sky-and-distance-v1" / "CL02"
OUT.mkdir(parents=True, exist_ok=True)
X = np.linspace(0, 1, W, dtype=np.float32)[None, :]
Y = np.linspace(0, 1, H, dtype=np.float32)[:, None]


def periodic_noise(seed: int, gx: int, gy: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    a = rng.integers(0, 256, (gy, gx), dtype=np.uint8)
    a[:, -1] = a[:, 0]
    out = np.asarray(Image.fromarray(a).resize((W, H), Image.Resampling.BICUBIC), dtype=np.float32) / 255.0 - 0.5
    out[:, -1] = out[:, 0]
    return out


for n in range(1, 7):
    seed = 110820 + n * 9
    rng = np.random.default_rng(seed)
    a = periodic_noise(seed + 1, 18, 7)
    b = periodic_noise(seed + 2, 54, 14)
    c = periodic_noise(seed + 3, 131, 28)
    center = 0.48 + np.sin(X * np.pi * 2 * (1 + n % 2) + n) * 0.038 + a * 0.08
    width = 0.095 + (n % 3) * 0.018
    band = np.exp(-((Y - center) / width) ** 2 * 0.8)
    puffs = np.zeros((H, W), dtype=np.float32)
    for _ in range(15):
        cx = rng.uniform(0, 1)
        cy = rng.uniform(0.43, 0.58)
        sx = rng.uniform(0.035, 0.11)
        sy = rng.uniform(0.045, 0.11)
        dx = np.minimum(np.abs(X - cx), 1 - np.abs(X - cx))
        puffs = np.maximum(puffs, np.exp(-((dx / sx) ** 2 + ((Y - cy) / sy) ** 2) * 1.6))
    density = np.clip(band * (0.47 + a * 0.28 + b * 0.18 + c * 0.08) + puffs * 0.38 - 0.06, 0, 0.78)
    edge = np.clip((Y - 0.10) / 0.16, 0, 1) * np.clip((0.91 - Y) / 0.19, 0, 1)
    alpha = np.uint8(np.clip(density * edge * 190, 0, 165))
    alpha[:, -1] = alpha[:, 0]
    light = np.clip((0.55 - Y) * 20 + a * 14 + b * 6, -19, 19)
    rgb = np.empty((H, W, 3), dtype=np.uint8)
    for channel, base in enumerate((225, 235, 239)):
        rgb[:, :, channel] = np.uint8(np.clip(base + light, 0, 255))
    rgb[:, -1, :] = rgb[:, 0, :]
    Image.fromarray(np.dstack((rgb, alpha)), "RGBA").save(OUT / f"CL02_waist_belt_{n:02}.png", optimize=True)
print(OUT)

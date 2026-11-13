"""Two low-opacity, feathered ground-mist cards (2048x512 RGBA)."""

from pathlib import Path

import numpy as np
from PIL import Image


W, H = 2048, 512
OUT = Path(__file__).resolve().parents[2] / "exports" / "sky-and-distance-v1" / "CL03"
OUT.mkdir(parents=True, exist_ok=True)
X = np.linspace(0, 1, W, dtype=np.float32)[None, :]
Y = np.linspace(0, 1, H, dtype=np.float32)[:, None]

for n in (1, 2):
    rng = np.random.default_rng(110830 + n)
    small = rng.integers(0, 256, (9, 24), dtype=np.uint8)
    grain = np.asarray(Image.fromarray(small).resize((W, H), Image.Resampling.BICUBIC), dtype=np.float32) / 255.0 - 0.5
    center = 0.62 if n == 1 else 0.53
    spread = 0.21 if n == 1 else 0.17
    soft = np.exp(-((Y - center - grain * 0.052) / spread) ** 2 * 0.75)
    lateral = np.clip(X / 0.09, 0, 1) * np.clip((1 - X) / 0.09, 0, 1)
    alpha = np.uint8(np.clip((soft * 0.64 + grain * 0.08) * lateral * 78, 0, 58))
    colour = np.empty((H, W, 3), dtype=np.uint8)
    for ch, base in enumerate((205, 222, 228)):
        colour[:, :, ch] = np.uint8(np.clip(base + grain * 11, 0, 255))
    Image.fromarray(np.dstack((colour, alpha)), "RGBA").save(OUT / f"CL03_low_mist_{n:02}.png", optimize=True)
print(OUT)

"""Generate an opaque, sky-fading northern skyline strip for the SK arc.

The output is painted as one 4096x1024 canvas and then split into two exact
2048-pixel halves.  This avoids an independently generated middle seam.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


W, H = 4096, 1024
ROOT = Path(__file__).resolve().parents[2] / "exports" / "sky-and-distance-v1" / "SK01"
ROOT.mkdir(parents=True, exist_ok=True)
SEED = 110801
rng = np.random.default_rng(SEED)


def noise_1d(count: int, scale: int, seed: int) -> np.ndarray:
    local = np.random.default_rng(seed)
    n = max(3, W // scale + 2)
    anchors = local.uniform(-1.0, 1.0, n)
    xp = np.linspace(0, W - 1, n)
    return np.interp(np.arange(W), xp, anchors)


def noise_2d(grid_x: int, grid_y: int, seed: int) -> np.ndarray:
    local = np.random.default_rng(seed)
    data = local.integers(0, 256, (grid_y, grid_x), dtype=np.uint8)
    return np.asarray(Image.fromarray(data).resize((W, H), Image.Resampling.BICUBIC), dtype=np.float32) / 255.0 - 0.5


def ridge(x: np.ndarray, peaks: list[tuple[float, float, float]], base: float, seed: int) -> np.ndarray:
    y = np.full(W, base, dtype=np.float32)
    for i, (center, width, height) in enumerate(peaks):
        # Offset either flank independently: karst towers have asymmetric rock
        # faces, not the repeated triangles of a generic mountain noise pass.
        flank = np.where(x < center, width * (0.55 + (i % 3) * 0.12), width * (0.85 + (i % 2) * 0.17))
        d = np.abs(x - center) / flank
        if i % 3 == 0:
            form = np.exp(-np.power(d, 3.4) * 3.3)  # sheer-sided table peak
        elif i % 3 == 1:
            form = np.exp(-np.power(d, 1.15) * 2.3)  # steep needle
        else:
            form = np.exp(-np.power(d, 2.4) * 2.9)  # broken high ridge
        y -= height * form
    detail = (
        noise_1d(W, 260, seed) * 31
        + noise_1d(W, 75, seed + 1) * 26
        + noise_1d(W, 21, seed + 2) * 11
        + noise_1d(W, 5, seed + 3) * 3
    )
    return np.clip(y + detail, 130, H - 3)


x = np.arange(W, dtype=np.float32)
yy = np.arange(H, dtype=np.float32)[:, None]
sky_top = np.array([211, 227, 235], dtype=np.float32)
sky_bottom = np.array([224, 233, 234], dtype=np.float32)
t = np.clip(yy[:, :, None] / H, 0, 1)
canvas = np.broadcast_to(sky_top * (1 - t) + sky_bottom * t, (H, W, 3)).copy()

# Quiet aerial colour modulation; no recognizable clouds painted into the top.
air = noise_2d(17, 8, SEED + 10)
canvas += air[:, :, None] * np.array([5.0, 6.0, 6.0])

layers = [
    ([(175, 230, 80), (770, 310, 185), (1260, 140, 150), (2080, 390, 245), (3090, 210, 180), (3850, 280, 100)], 695, [174, 195, 205], 0.36, 20),
    ([(410, 190, 250), (1170, 165, 325), (1660, 185, 210), (2740, 300, 335), (3620, 140, 285)], 810, [130, 164, 181], 0.62, 40),
    ([(130, 210, 155), (900, 300, 240), (1520, 135, 180), (2260, 290, 220), (3400, 230, 305), (4010, 250, 140)], 1000, [105, 142, 158], 0.86, 60),
]

for peaks, base, colour, opacity, offset in layers:
    edge = ridge(x, peaks, base, SEED + offset)
    edge_slope = np.gradient(edge)
    height_below = np.maximum(0.0, yy - edge[None, :])
    mask = np.clip(height_below / 7.0, 0, 1) * opacity
    stone = noise_2d(55, 26, SEED + offset + 10) * 13 + noise_2d(230, 38, SEED + offset + 11) * 7
    grooves = np.sin(x / 5.8 + noise_1d(W, 100, SEED + offset + 12) * 4)[None, :] * 2.3
    slope_light = np.clip(-edge_slope[None, :] * 1.5, -11, 11)
    stone += grooves + slope_light
    depth = np.clip(height_below / 480.0, 0, 1)
    ridge_colour = np.asarray(colour, dtype=np.float32)[None, None, :] - depth[:, :, None] * [12, 15, 13]
    ridge_colour = ridge_colour + stone[:, :, None]
    canvas = canvas * (1 - mask[:, :, None]) + ridge_colour * mask[:, :, None]

# Three soft horizontal cloud bands cross the mountain bases.
mist = noise_2d(31, 9, SEED + 90)
for center, spread, strength in [(615, 39, 0.35), (772, 52, 0.47), (925, 58, 0.42)]:
    band = np.exp(-((yy - center - mist * 38) / spread) ** 2) * strength
    band = np.clip(band, 0, 0.62)
    canvas = canvas * (1 - band[:, :, None]) + np.array([224, 233, 233])[None, None, :] * band[:, :, None]

# Top pixels are made exactly sky-coloured so the opaque strip fades upward.
fade = np.clip((yy - 115) / 160.0, 0, 1)
plain_sky = np.broadcast_to(sky_top * (1 - t) + sky_bottom * t, (H, W, 3))
canvas = plain_sky * (1 - fade[:, :, None]) + canvas * fade[:, :, None]
image = Image.fromarray(np.uint8(np.clip(canvas, 0, 255)), "RGB")
image.save(ROOT / "SK01_north_4096x1024.png", optimize=True)
image.crop((0, 0, 2048, H)).save(ROOT / "SK01_north_left_2048x1024.png", optimize=True)
image.crop((2048, 0, W, H)).save(ROOT / "SK01_north_right_2048x1024.png", optimize=True)
image.resize((2048, 512), Image.Resampling.LANCZOS).save(ROOT / "SK01_north_mobile_2048x512.png", optimize=True)
print(ROOT)

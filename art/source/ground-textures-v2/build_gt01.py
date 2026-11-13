"""Build the GT01 sage grass Unity Terrain texture set from selected original art.

Source art is preserved separately; this script performs deterministic edge
periodization, maps and the 3×3 review sheet.  Run with system Python/Pillow.
"""

from pathlib import Path
import json

import numpy as np
from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "references" / "ground-textures-v2" / "GT01" / "source-ai-v002-selected.png"
OUT = ROOT / "exports" / "ground-textures-v2" / "GT01"
OUT.mkdir(parents=True, exist_ok=True)
SIZE = 2048
EDGE = 192


def periodize(data):
    """Feather opposite edge bands to shared colors, then force exact seams."""
    arr = np.asarray(data, dtype=np.float32).copy()
    for i in range(EDGE):
        w = np.cos((i / EDGE) * np.pi / 2) ** 2
        left, right = arr[:, i].copy(), arr[:, -i - 1].copy()
        common = (left + right) / 2
        arr[:, i] = left * (1 - w) + common * w
        arr[:, -i - 1] = right * (1 - w) + common * w
    for i in range(EDGE):
        w = np.cos((i / EDGE) * np.pi / 2) ** 2
        top, bottom = arr[i].copy(), arr[-i - 1].copy()
        common = (top + bottom) / 2
        arr[i] = top * (1 - w) + common * w
        arr[-i - 1] = bottom * (1 - w) + common * w
    arr[:, -1] = arr[:, 0]
    arr[-1] = arr[0]
    return np.uint8(np.clip(arr, 0, 255))


source = Image.open(SOURCE).convert("RGB")
upsized = source.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
# Remove broad lighting/tonal blotches that would repeat every four meters,
# while keeping blade-level details and local dry-grass variation.
low = np.asarray(upsized.filter(ImageFilter.GaussianBlur(170)), dtype=np.float32)
base = np.asarray(upsized, dtype=np.float32)
flattened = np.uint8(np.clip(base - 0.82 * (low - low.mean(axis=(0, 1))), 0, 255))
albedo = periodize(flattened)
Image.fromarray(albedo, "RGB").save(OUT / "GT01_Albedo_2048.png", optimize=True)

grey = np.asarray(Image.fromarray(albedo).convert("L").filter(ImageFilter.GaussianBlur(1.3)), dtype=np.float32) / 255
gy, gx = np.gradient(grey)
nx, ny, nz = -gx * 14, -gy * 14, np.ones_like(grey)
norm = np.sqrt(nx * nx + ny * ny + nz * nz)
normal = np.stack((nx / norm, ny / norm, nz / norm), axis=-1)
normal = np.uint8(np.clip((normal * 0.5 + 0.5) * 255, 0, 255))
normal[:, -1] = normal[:, 0]
normal[-1] = normal[0]
Image.fromarray(normal, "RGB").save(OUT / "GT01_Normal_2048.png", optimize=True)

smooth_grey = np.asarray(Image.fromarray(albedo).convert("L").filter(ImageFilter.GaussianBlur(10)), dtype=np.float32) / 255
mask = np.empty((SIZE, SIZE, 4), dtype=np.uint8)
mask[:, :, 0] = 0              # Metallic
mask[:, :, 1] = np.uint8(np.clip(220 + 25 * smooth_grey, 0, 255))  # AO
mask[:, :, 2] = 0              # Detail mask
mask[:, :, 3] = np.uint8(np.clip(28 + 13 * smooth_grey, 0, 255))   # Smoothness: matte grass
mask[:, -1] = mask[:, 0]
mask[-1] = mask[0]
Image.fromarray(mask, "RGBA").save(OUT / "GT01_MaskURP_2048.png", optimize=True)

small = Image.fromarray(albedo).resize((768, 768), Image.Resampling.LANCZOS)
preview = Image.new("RGB", (2304, 2304))
for row in range(3):
    for col in range(3):
        preview.paste(small, (col * 768, row * 768))
preview.save(OUT / "GT01_3x3-preview.png", optimize=True)

checks = {}
for name, arr in (("albedo", albedo), ("normal", normal), ("mask", mask)):
    checks[name] = {"size": [SIZE, SIZE],
                    "left_right_max_delta": int(np.abs(arr[:, 0].astype(int) - arr[:, -1].astype(int)).max()),
                    "top_bottom_max_delta": int(np.abs(arr[0].astype(int) - arr[-1].astype(int)).max())}
assert all(x["left_right_max_delta"] == 0 and x["top_bottom_max_delta"] == 0 for x in checks.values())
checks["source_size"] = list(source.size)
checks["mean_rgb"] = [round(float(x), 1) for x in albedo.mean(axis=(0, 1))]
(OUT / "validation.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf8")
print(json.dumps(checks, ensure_ascii=False))

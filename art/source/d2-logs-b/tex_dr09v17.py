# DR09 v017：新斷口裸木改暖米黃（不覆寫 DR09_FreshWood_Albedo.png，另存 DR09_FreshWood_v017_Albedo.png）。
# 做法：保留原圖的明暗紋理（纖維條、深色凹縫），只把色相換成暖米黃、整體提亮；最暗的凹縫維持深色。
#   uv run --no-project --offline --with pillow --with numpy python art/source/d2-logs-b/tex_dr09v17.py
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, '..', '..', 'exports', 'd2-logs-b', 'DR09_Shared', 'Textures')
src = np.asarray(Image.open(os.path.join(T, 'DR09_FreshWood_Albedo.png')).convert('RGB')).astype(np.float32) / 255
lum = src @ np.array((.30, .59, .11), np.float32)
m = float(lum.mean())
k = lum / m                                         # 相對明暗（平均 1）
k = np.where(k < 1, k ** 1.15, 1 + (k - 1) * .85)   # 暗縫再壓暗一點、亮面不過曝
warm = np.array((228, 198, 154), np.float32) / 255  # 暖米黃（平均色）
dark = np.array((104, 72, 48), np.float32) / 255     # 凹縫的深褐
t = np.clip((k - .30) / .40, 0, 1)[..., None]
out = dark * (1 - t) * np.clip(k, 0, 1)[..., None] / .8 + warm * t * k[..., None] * .86
out = np.clip(out, 0, 1)
dst = os.path.join(T, 'DR09_FreshWood_v017_Albedo.png')
assert not os.path.exists(dst), '已存在，不覆寫：' + dst
Image.fromarray((out * 255 + .5).astype(np.uint8)).save(dst)
print('saved', dst, (out.reshape(-1, 3).mean(0) * 255).round())

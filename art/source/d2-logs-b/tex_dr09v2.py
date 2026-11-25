# DR09 斷枝堆 v002 的貼圖：審查指出 v001「顏色太暗太冷（深灰黑）」、缺苔和地衣。
# 目標色是從參考圖 art/references/DR09/v001/DR09-threeview.png 的 L 列量的（去掉背景後各類像素的平均）：
#   樹皮 ≈ (118, 96, 75) 暖灰褐；苔 ≈ (110, 106, 58) 橄欖綠；地衣 ≈ 淺灰綠；落葉 ≈ (172, 137, 107)。
# 都是同一張手繪圖在線性空間重新調色另存 *_v002_Albedo.png（筆觸不變、法線沿用原本的），v001 的貼圖不動：
#   DR09_Bark_v002_Albedo   ← DR08_Bark_Albedo（樹皮）
#   DR09_Moss_v002_Albedo   ← DR08_Moss_Albedo（苔）
#   DR09_Lichen_v002_Albedo ← DR08_Moss_Albedo 去飽和、調亮成淺灰綠（放在材質的 Rot 槽，斷枝不用褐腐層）
#   DR09_Soil_v002_Albedo   ← DR08_Soil_Albedo（堆底的落葉土，往橘褐調）
# 用法：uv run --no-project --offline --with pillow --with numpy python tex_dr09v2.py
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(HERE, '..', '..', 'exports', 'd2-logs-b')
SRC = os.path.join(EXP, 'DR08_Shared', 'Textures')
OUT = os.path.join(EXP, 'DR09_Shared', 'Textures')


def load(n):
    return np.asarray(Image.open(os.path.join(SRC, n)).convert('RGB'), np.float64) / 255.0


def regrade(a, target, sat=1.0):
    lin = a ** 2.2
    t = (np.array(target) / 255.0) ** 2.2
    b = np.clip(lin * (t / lin.reshape(-1, 3).mean(0)), 0, 1) ** (1 / 2.2)
    g = (b * np.array((.30, .59, .11))).sum(-1, keepdims=True)
    return np.clip(g + (b - g) * sat, 0, 1)


def save(a, n):
    Image.fromarray(np.round(a * 255).astype(np.uint8)).save(os.path.join(OUT, n))
    print(n, 'mean', (a.reshape(-1, 3).mean(0) * 255).round())


save(regrade(load('DR08_Bark_Albedo.png'), (114, 92, 72), 1.05), 'DR09_Bark_v002_Albedo.png')
save(regrade(load('DR08_Moss_Albedo.png'), (110, 107, 54), 1.08), 'DR09_Moss_v002_Albedo.png')
m = load('DR08_Moss_Albedo.png')
g = (m * np.array((.30, .59, .11))).sum(-1, keepdims=True)
m = np.clip(g + (m - g) * .35, 0, 1)                      # 去掉大部分飽和，只留一點綠
m = (m - m.mean()) * 1.6 + m.mean()                       # 斑點對比大一點（地衣是一塊一塊的殼）
save(regrade(np.clip(m, .02, 1), (160, 166, 142), 1.0), 'DR09_Lichen_v002_Albedo.png')
save(regrade(load('DR08_Soil_Albedo.png'), (118, 86, 60), 1.12), 'DR09_Soil_v002_Albedo.png')

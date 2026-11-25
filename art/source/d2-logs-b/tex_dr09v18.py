# DR09 v018 貼圖（全部另存新檔，不覆寫舊檔）：
#   DR09_FreshWood_v018_Albedo：新斷口裸木，暖米黃偏淡赭；保留原圖纖維明暗，凹縫維持深褐（和灰褐樹皮拉開）。
#   DR09_Moss_v018_Albedo：苔，以 v002 苔為底，加無縫低頻色差（橄欖、黃綠、暗綠三色，約 10–20 cm 一塊；不用螢光綠）。
#   DR09_Bark_v018_Albedo：樹皮，以 v002 為底降低彩度、略偏冷的灰褐（和暖米黃裸木拉開）。
#   DR09_Lichen_v018_Albedo：地衣，扁平殼狀的灰白／灰綠斑（亮、低起伏），帶少量淺色環紋與深色小點；和蓬鬆的苔可區分。
#   uv run --no-project --offline --with pillow --with numpy python art/source/d2-logs-b/tex_dr09v18.py
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, '..', '..', 'exports', 'd2-logs-b', 'DR09_Shared', 'Textures')
N = 1024
rng = np.random.default_rng(1818)


def load(nm):
    return np.asarray(Image.open(os.path.join(T, nm)).convert('RGB')).astype(np.float32) / 255


def save(a, nm):
    p = os.path.join(T, nm)
    if os.path.exists(p):                # 已產生過就略過（不覆寫；同一亂數種子結果相同）
        print('exists, skip', nm)
        return
    Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8)).save(p)
    print('saved', nm, (a.reshape(-1, 3).mean(0) * 255).round())


def pnoise(freq, seed):
    """無縫（週期）低通雜訊，0–1。freq = 一張圖裡大約幾塊。"""
    r = np.random.default_rng(seed).standard_normal((N, N))
    fx = np.fft.fftfreq(N)[:, None] * N
    fy = np.fft.fftfreq(N)[None, :] * N
    k = np.sqrt(fx ** 2 + fy ** 2)
    f = np.fft.ifft2(np.fft.fft2(r) * np.exp(-(k / freq) ** 2)).real
    f = (f - f.mean()) / (f.std() + 1e-9)
    return 1 / (1 + np.exp(-1.6 * f))


lum_w = np.array((.30, .59, .11), np.float32)
# ---- 裸木
src = load('DR09_FreshWood_Albedo.png')
lum = src @ lum_w
k = lum / lum.mean()
k = np.where(k < 1, k ** 1.25, 1 + (k - 1) * .85)
warm = np.array((222, 182, 122), np.float32) / 255     # 暖米黃偏淡赭
ochre = np.array((196, 142, 86), np.float32) / 255     # 淡赭（低頻斑）
dark = np.array((92, 58, 34), np.float32) / 255
o = pnoise(5, 11)[..., None]
base = warm * (1 - .45 * o) + ochre * .45 * o
t = np.clip((k - .30) / .40, 0, 1)[..., None]
wood = dark * (1 - t) * np.clip(k, 0, 1)[..., None] / .8 + base * t * k[..., None] * .88
save(wood, 'DR09_FreshWood_v018_Albedo.png')
# ---- 苔
moss = load('DR09_Moss_v002_Albedo.png')
a, b = pnoise(6, 21), pnoise(9, 22)
olive = np.array((1.00, 1.00, 1.00), np.float32)
yellow = np.array((1.16, 1.14, .80), np.float32)       # 黃綠
darkg = np.array((.62, .70, .58), np.float32)          # 暗綠
wy = np.clip((a - .55) / .25, 0, 1)[..., None]
wd = np.clip((b - .58) / .22, 0, 1)[..., None]
mul = olive * (1 - wy) + yellow * wy
mul = mul * (1 - wd) + darkg * wd
save(moss * mul, 'DR09_Moss_v018_Albedo.png')
# ---- 地衣（扁平殼狀斑）
detail = load('DR09_Lichen_v002_Albedo.png') @ lum_w
detail = (detail - detail.mean()) / (detail.std() + 1e-9)
c1, c2, c3 = pnoise(40, 31), pnoise(70, 32), pnoise(110, 33)
grey = np.array((204, 202, 186), np.float32) / 255     # 灰白（略暖）
greyg = np.array((168, 176, 146), np.float32) / 255    # 灰綠
pale = np.array((224, 226, 214), np.float32) / 255     # 淺色環紋
col = grey * (1 - c1[..., None]) + greyg * c1[..., None]
ring = np.exp(-((c2 - .5) / .035) ** 2)[..., None]        # 細的淺色環
col = col * (1 - .55 * ring) + pale * .55 * ring
dots = (c3 > .86)[..., None] * .55                       # 少量深色小點（子囊盤）
col = col * (1 - dots) + np.array((88, 80, 62), np.float32) / 255 * dots
col = col * (1 + .06 * detail[..., None])                # 很淡的殼面細節（扁平，不蓬鬆）
save(col, 'DR09_Lichen_v018_Albedo.png')
# ---- 樹皮（灰褐）
bark = load('DR09_Bark_v002_Albedo.png')
bl = (bark @ lum_w)[..., None]
gb = bl + (bark - bl) * .72                              # 彩度降到 72%
gb = gb * np.array((1.0, 1.0, 1.0), np.float32) * 1.02
save(gb, 'DR09_Bark_v018_Albedo.png')

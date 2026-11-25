# DR09 v019 貼圖（另存新檔，不覆寫）：
#   DR09_LichenMask_v019：地衣斑片邊緣遮罩（灰階、無縫）。材質裡用「頂點權重 × 1.25 ＋ 遮罩」再變陡，
#   頂點色只決定斑片大概位置（網格稀，單靠頂點色只會是一團糊），邊緣的不規則鋸齒、小缺口由這張遮罩決定（貼圖解析度）。
#   和地衣槽同一組 UV（2 次／公尺）：一張 = 0.5 m；低頻瓣約 3–4 cm、細齒約 1 cm。
#   uv run --no-project --offline --with pillow --with numpy python art/source/d2-logs-b/tex_dr09v19.py
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, '..', '..', 'exports', 'd2-logs-b', 'DR09_Shared', 'Textures')
N = 1024


def pnoise(freq, seed):
    r = np.random.default_rng(seed).standard_normal((N, N))
    fx = np.fft.fftfreq(N)[:, None] * N
    fy = np.fft.fftfreq(N)[None, :] * N
    k = np.sqrt(fx ** 2 + fy ** 2)
    f = np.fft.ifft2(np.fft.fft2(r) * np.exp(-(k / freq) ** 2)).real
    return (f - f.mean()) / (f.std() + 1e-9)


p = os.path.join(T, 'DR09_LichenMask_v019.png')
if os.path.exists(p):
    print('exists, skip', p)
else:
    m = .62 * pnoise(14, 1901) + .30 * pnoise(40, 1902) + .14 * pnoise(110, 1903)
    m = 1 / (1 + np.exp(-2.2 * m / m.std()))
    Image.fromarray((m * 255 + .5).astype(np.uint8), 'L').save(p)
    print('saved', p, round(float(m.mean()), 3), round(float(m.std()), 3))

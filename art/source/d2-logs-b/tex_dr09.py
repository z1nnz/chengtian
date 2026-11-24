# DR09 斷枝堆：斷口、剝皮處、木刺用的淺奶油色新斷木纖維（Codex 依 DR09 細節參考圖畫，原圖 tex_src_dr09/tex_freshwood.png）。
# DR08 的撕裂纖維是灰褐色的朽木，斷枝的新斷口在參考圖是淺奶油色，所以 DR09 另做一張，其餘五層沿用 DR08_Shared。
# 做法和 tex_dr08.py 相同（無縫、縮成 1024、色調、法線），函式直接借 tex_dr08.py。
# 用法：uv run --no-project --offline --with pillow --with numpy python tex_dr09.py
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ns = {'__name__': 'tex_dr08_lib', '__file__': os.path.join(HERE, 'tex_dr08.py')}
exec(compile(open(ns['__file__'], encoding='utf-8').read(), ns['__file__'], 'exec'), ns)
ns['SRC'] = os.path.join(HERE, 'tex_src_dr09')
ns['OUT'] = os.path.join(HERE, '..', '..', 'exports', 'd2-logs-b', 'DR09_Shared', 'Textures')
os.makedirs(ns['OUT'], exist_ok=True)
a = ns['load']('tex_freshwood.png')
a = ns['make_seamless'](a, 31)
a = ns['resize'](a, ns['N'])
a = ns['tone'](a, .80, .78)               # Codex 原圖偏亮偏黃，壓到參考圖斷口的淺奶油
ns['save'](a, 'DR09_FreshWood_Albedo.png')
ns['save'](ns['normal_from'](a, 5.0), 'DR09_FreshWood_Normal.png')
print('mean', (a.reshape(-1, 3).mean(0) * 255).round())

# DR09 樹皮：DR08 的樹皮偏粉紫灰（朽木），斷枝在參考圖是偏橄欖的深灰褐。只改顏色（同一張圖重新調色），法線沿用 DR08_Bark_Normal。
from PIL import Image
b = np.asarray(Image.open(os.path.join(HERE, '..', '..', 'exports', 'd2-logs-b', 'DR08_Shared', 'Textures', 'DR08_Bark_Albedo.png')).convert('RGB'), np.float64) / 255.0
b = b ** 1.22 * np.array((.86, .93, .86))                       # 壓暗、去掉粉紅（Unity 打光下原圖偏灰白）
b = ns['tone'](b, 1.0, .85)
ns['save'](b, 'DR09_Bark_Albedo.png')
print('bark mean', (b.reshape(-1, 3).mean(0) * 255).round())

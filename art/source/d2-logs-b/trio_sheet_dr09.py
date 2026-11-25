# DR09 v011：只有新換的 3 根分叉腐木（W1–W3）的灰模，單獨排一張。
# 來源是 views_dr09v4.py 用固定鏡位渲染的 <tag>_clay_<front|top|tq>.png（和整堆同一組鏡頭、同一座標）；
# 這裡只把每張裁到物件外框（留邊）放大排在一起，方便看形體，不改比例。
#   uv run --no-project --offline --with pillow --with numpy python art/source/d2-logs-b/trio_sheet_dr09.py <版本資料夾> <tag>
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
asset = 'DR09_BranchPile_L'
H = 420
try:
    FONT = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 22)
except OSError:
    FONT = ImageFont.load_default()


def crop_obj(im, skip_left=0, pad=30, tol=22):
    a = np.asarray(im).astype(int)
    h, w, _ = a.shape
    bg = np.median(np.array([a[2, -3], a[-3, -3], a[2, w // 2], a[-3, w // 2], a[h // 2, -3]]), axis=0)
    m = np.abs(a - bg).sum(2) > tol
    m[:, :skip_left] = False
    rows = np.nonzero(m.sum(1) > 2)[0]
    cols = np.nonzero(m.sum(0) > 2)[0]
    return im.crop((max(0, cols[0] - pad), max(0, rows[0] - pad), min(w, cols[-1] + pad), min(h, rows[-1] + pad)))


def main():
    d_, tag = sys.argv[1], sys.argv[2]
    src = os.path.join(ROOT, 'art', 'previews', 'd2-logs-b', asset, d_)
    ims, titles = [], ('正面（正交）', '俯視（正交）', '斜 45°')
    for view, skip in (('front', 300), ('top', 0), ('tq', 0)):
        im = Image.open(os.path.join(src, f'{asset}_{tag}_clay_{view}.png')).convert('RGB')
        if view == 'tq':
            im = im.crop((0, 260, im.width, im.height))          # 去掉天空，地平線上下顏色不同
        c = crop_obj(im, skip)
        ims.append(c.resize((max(1, round(c.width * H / c.height)), H), Image.LANCZOS))
    W = sum(i.width for i in ims) + 12 * 4
    out = Image.new('RGB', (W, H + 120), (18, 18, 18))
    d = ImageDraw.Draw(out)
    d.text((14, 8), 'v011 新換的 3 根分叉腐木（只顯示 W1–W3 與它們的側枝；位置、鏡頭和整堆相同，此圖只裁切放大）',
           fill=(255, 220, 150), font=FONT)
    x = 12
    for im, t in zip(ims, titles):
        d.text((x + 4, 46), t, fill=(235, 235, 235), font=FONT)
        out.paste(im, (x, 80))
        x += im.width + 12
    d.text((14, H + 88), 'W1：中後層左、最高（約 1.25 m）　W2：中後層右（約 1.03 m）　W3：中層橫跨（約 0.83 m）',
           fill=(200, 200, 200), font=FONT)
    p = os.path.join(src, f'{asset}_{tag}_sheet.jpg')
    out.save(p, quality=90)
    print(p, out.size)


main()

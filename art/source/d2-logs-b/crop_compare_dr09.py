# DR09 同寬裁切對照：把參考圖與成品都裁到「堆體本身」的外框（去掉留白、人形尺），縮放到相同寬度上下並排，
# 並量出外框高寬比與外框內的透空比例（背景像素 / 外框面積），讓留白大小不影響判斷。
#   uv run --no-project --offline --with pillow --with numpy python art/source/d2-logs-b/crop_compare_dr09.py <輸出資料夾名> <tag> [<tag> ...]
# 視角：front（參考三視圖 L 列側視 vs 正交正面）、top（參考三視圖 L 列俯視 vs 正交俯視）。成品用 mat 圖（參考圖也有落葉）。
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
asset = 'DR09_BranchPile_L'
PREV = os.path.join(ROOT, 'art', 'previews', 'd2-logs-b', asset)
REF = os.path.join(ROOT, 'art', 'references', 'DR09', 'v001')
W = 1100
try:
    FONT = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 22)
except OSError:
    FONT = ImageFont.load_default()


def bbox_mask(im, skip_left=0, tol=26):
    """背景色取四角中位數；與背景差超過 tol 的像素算物體；略過左側 skip_left 像素（人形尺）。"""
    a = np.asarray(im).astype(int)
    h, w, _ = a.shape
    corners = np.array([a[2, -3], a[-3, -3], a[2, w // 2], a[-3, w // 2]])
    bg = np.median(corners, axis=0)
    m = np.abs(a - bg).sum(2) > tol
    m[:, :skip_left] = False
    # 去掉零星雜點：列／行的物體像素太少不算
    rows = np.nonzero(m.sum(1) > 3)[0]
    cols = np.nonzero(m.sum(0) > 3)[0]
    y0, y1, x0, x1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
    return (x0, y0, x1, y1), m[y0:y1, x0:x1]


def tile(im, skip_left=0):
    (x0, y0, x1, y1), m = bbox_mask(im, skip_left)
    c = im.crop((x0, y0, x1, y1))
    ar = (y1 - y0) / (x1 - x0)
    void = 1 - m.mean()
    return c.resize((W, max(1, round(W * ar))), Image.LANCZOS), ar, void


def main():
    out_dir, tags = sys.argv[1], sys.argv[2:]
    ref3 = Image.open(os.path.join(REF, 'DR09-threeview.png')).convert('RGB')
    srcs = {'front': ('參考：側視（三視圖 L 列）', ref3.crop((0, 600, 920, 900)), 160),
            'top': ('參考：俯視（三視圖 L 列）', ref3.crop((920, 610, 1536, 910)), 0)}
    for view in ('front', 'top'):
        rows = []
        label, im, skip = srcs[view]
        rows.append((label, *tile(im, skip)))
        for t in tags:
            for d in (out_dir, t.split('_')[0], 'v009', 'v008'):   # 先找該版本自己的資料夾
                p = os.path.join(PREV, d, f'{asset}_{t}_mat_{view}.png')
                if os.path.exists(p):
                    break
            im = Image.open(p).convert('RGB')
            rows.append((f'{t}：{"正面正交" if view == "front" else "俯視正交"}', *tile(im, 260 if view == 'front' else 0)))
        H = sum(r[1].height + 50 for r in rows) + 10
        o = Image.new('RGB', (W + 24, H), (18, 18, 18))
        d = ImageDraw.Draw(o)
        y = 8
        for label, c, ar, void in rows:
            d.text((12, y + 6), f'{label}　外框高寬比 {ar:.2f}　外框內透空 {void * 100:.0f}%', fill=(255, 220, 150), font=FONT)
            o.paste(c, (12, y + 40))
            y += c.height + 50
            print(view, label, 'aspect', round(ar, 3), 'void', round(void, 3))
        p = os.path.join(PREV, out_dir, f'{asset}_samewidth_{view}.jpg')
        o.save(p, quality=90)
        print(p, o.size)


main()

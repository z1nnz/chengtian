# DR11 B 灰模 vs 參考三視圖：兩列對照＋獨立底欄。
# 第一列「世界尺度對照」：參考圖用人形尺換算公尺（1.75 m ≈ 130 px，量自同一張圖），灰模用正交圖的每公尺像素；兩邊同一公尺比例、地線對齊。
# 第二列「等高形狀對照」：兩邊各自縮放到「地線到主體頂」同高，只比形狀比例；不做非等比拉伸。
# - 參考：art/references/DR11/v001/DR11-threeview.png；B 正面裁 x 790–1150、B 側面裁 x 1150–1536；地線第 640 列；
#   木土主體頂（苔面，不含頂上的蕨）約第 435 列。
# - 模型：build_dr11.py 的正交出圖 ofront／oside（附 .json：每公尺像素、地線列）；模型頂由畫面和背景色的差找出。
# - 圖例、說明全部放在底欄，不疊在模型、基線上。
# 用法：python compare_dr11.py <正交圖資料夾> <輸出.png>
import sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

REF = 'D:/yun-jing-d2-logs/art/references/DR11/v001/DR11-threeview.png'
REF_GROUND, REF_TOP = 640, 435
REF_PPM = 130 / 1.75                 # 參考圖每公尺像素（人形尺）
REF_BOX = {'front': (790, 1150), 'side': (1150, 1536)}
H = 380                              # 等高列：地線到主體頂的像素高
WPPM = 140                           # 世界尺度列：每公尺像素
ABOVE, BELOW = 60, 110               # 頂上、地線下留白
F = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 22)
FS = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 19)
BG = (236, 236, 232)


def _crop(im, gy, x0, x1, s, hpx):
    """以地線 gy 為準，裁出地線上 hpx/s、地線下 BELOW/s，縮放 s。"""
    top, bot = int(gy - (hpx + ABOVE) / s), int(gy + BELOW / s)
    c = Image.new('RGB', (x1 - x0, bot - top), im.getpixel((x0 + 2, 2)))       # 超出原圖的部分補背景色（不留黑邊）
    c.paste(im.crop((x0, max(0, top), x1, min(im.height, bot))), (0, max(0, -top)))
    return c.resize((max(1, int(c.width * s)), max(1, int(c.height * s))), Image.LANCZOS)


def ref_panel(view, mode):
    im = Image.open(REF).convert('RGB')
    x0, x1 = REF_BOX[view]
    hm = (REF_GROUND - REF_TOP) / REF_PPM
    s = H / (REF_GROUND - REF_TOP) if mode == 'eq' else WPPM / REF_PPM
    hpx = H if mode == 'eq' else hm * WPPM
    return _crop(im, REF_GROUND, x0, x1, s, hpx), hm


def model_panel(d, view, mode):
    im = Image.open(f'{d}/DR11_B_o{view}.png').convert('RGB')
    meta = json.load(open(f'{d}/DR11_B_o{view}.json'))
    a = np.asarray(im).astype(int)
    gy = meta['ground_row']
    m = np.abs(a - a[2, 2]).sum(-1) > 30
    m[int(gy) - 3:] = False
    top = np.nonzero(m.any(1))[0].min()
    hm = (gy - top) / meta['px_per_m']
    s = H / (gy - top) if mode == 'eq' else WPPM / meta['px_per_m']
    hpx = H if mode == 'eq' else hm * WPPM
    xs = np.nonzero(m.any(0))[0]
    c = _crop(im, gy, max(0, xs.min() - 40), min(im.width, xs.max() + 40), s, hpx)
    return c, hm


def main(d, out):
    rows = []
    for mode, title in (('world', '一、世界尺度對照（同一公尺比例；參考圖以人形尺 1.75 m 約 130 px 換算）'),
                        ('eq', '二、等高形狀對照（各自縮放到地線至木土主體頂同高，只比形狀比例）')):
        panels = []
        for view, name in (('front', '正面'), ('side', '側面')):
            r, hr = ref_panel(view, mode)
            mm, hm = model_panel(d, view, mode)
            panels += [(f'參考 B {name}（約 {hr:.2f} m）', r, hr), (f'灰模 {name}（{hm:.2f} m）', mm, hm)]
        rows.append((mode, title, panels))
    W = max(sum(p.width for _, p, _ in ps) + 20 * (len(ps) + 1) for _, _, ps in rows)
    row_h = [max(p.height for _, p, _ in ps) + 80 for _, _, ps in rows]
    FOOT = 120
    sheet = Image.new('RGB', (W, sum(row_h) + FOOT + 10), BG)
    dr = ImageDraw.Draw(sheet)
    y = 10
    for (mode, title, ps), rh in zip(rows, row_h):
        dr.text((20, y), title, fill=(20, 20, 20), font=F)
        x = 20
        gy = y + 66 + max(p.height for _, p, _ in ps) - BELOW          # 同一列地線對齊在同一高度
        for t, p, hm in ps:
            sheet.paste(p, (x, gy + BELOW - p.height))
            dr.text((x, y + 36), t, fill=(40, 40, 40), font=FS)
            ht = (hm * WPPM) if mode == 'world' else H
            for yy, col in ((gy, (200, 30, 30)), (gy - ht, (30, 90, 200)), (gy - ht / 2, (150, 150, 150))):
                dr.line([(x, yy), (x + p.width, yy)], fill=col, width=2)
            x += p.width + 20
        y += rh
    dr.rectangle([0, y, W, y + FOOT + 10], fill=(222, 222, 216))
    dr.text((20, y + 12), '圖例：紅線＝地線　藍線＝木土主體頂（不含植物）　灰線＝半高。各線只畫在自己那格。', fill=(40, 40, 40), font=FS)
    dr.text((20, y + 44), '參考頂端以苔面為準，不含頂上的蕨；參考圖含苔、蕨、垂根輪廓，灰模為統一粗糙度、未加植物與材質。', fill=(40, 40, 40), font=FS)
    dr.text((20, y + 76), '灰模地線以下為展示用的坑體截面（正式場景埋在地形裡，不會露出）。', fill=(160, 30, 30), font=FS)
    sheet.save(out)
    print('COMPARE', out, sheet.size)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

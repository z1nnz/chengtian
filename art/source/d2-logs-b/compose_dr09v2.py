# DR09 v002「參考圖 vs 成品」並排圖：參考三視圖那一列（側視＋俯視）、成品 LOD0 正面平視＋俯視，再加參考情境圖同一堆的斜角 vs 成品斜角（看立體感）。
# 輸出 art/previews/d2-logs-b/DR09_BranchPile_<v>/v002/DR09_BranchPile_<v>_vs_reference.jpg（v001 的對照圖不動）
#   uv run --no-project --offline --with pillow python art/source/d2-logs-b/compose_dr09v2.py S M L
import os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
REF = os.path.join(ROOT, 'art', 'references', 'DR09', 'v001', 'DR09-threeview.png')
ROWS = {'S': (40, 300), 'M': (300, 580), 'L': (590, 920)}
TQ = os.path.join(ROOT, 'art', 'references', 'DR09', 'v001', 'DR09-threequarter.png')
TQBOX = {'S': (640, 600, 1260, 840), 'M': (30, 410, 790, 730), 'L': (420, 120, 1490, 510)}   # 參考情境圖（斜 45°、人眼高）裡同一堆的位置
H = 420
try:
    FONT = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 22)
except OSError:
    FONT = ImageFont.load_default()


def fit(im, h):
    return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)


def crop_content(im, pad=30):
    """用顏色（樹皮、落葉帶色，背景和地面是灰的）找出物件範圍；地平線、白柱、地面漸層都不算。"""
    from PIL import ImageChops
    r, g, b = im.split()
    hi = ImageChops.lighter(ImageChops.lighter(r, g), b)
    lo = ImageChops.darker(ImageChops.darker(r, g), b)
    box = ImageChops.subtract(hi, lo).point(lambda p: 255 if p > 16 else 0).getbbox()
    if not box:
        return im
    x0, y0, x1, y1 = box
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


for v in sys.argv[1:] or ['S', 'M', 'L']:
    asset = f'DR09_BranchPile_{v}'
    ver = os.environ.get('DR9VER', 'v002')
    pre = os.path.join(ROOT, 'art', 'previews', 'd2-logs-b', asset, ver)
    ref = Image.open(REF).convert('RGB')
    y0, y1 = ROWS[v]
    row = fit(ref.crop((0, y0, ref.width, y1)), H)
    front = fit(Image.open(os.path.join(pre, f'{asset}_LOD0_front.png')).convert('RGB'), H)
    top = fit(crop_content(Image.open(os.path.join(pre, f'{asset}_LOD0_top.png')).convert('RGB')), H)
    rtq = fit(Image.open(TQ).convert('RGB').crop(TQBOX[v]), H)
    tq = fit(crop_content(Image.open(os.path.join(pre, f'{asset}_LOD0_tq.png')).convert('RGB'), 40), H)
    tiles = [(row, f'參考圖：DR09 三視圖 {v} 列（側視＋俯視）'), (front, f'成品 {asset} {ver} LOD0：正面平視（白柱 = 1.75 m）'), (top, '成品俯視'),
             (rtq, '參考情境圖：斜 45°、人眼高'), (tq, '成品：斜 45°、人眼高 1.7 m')]
    Wd = sum(t[0].width for t in tiles) + 12 * (len(tiles) + 1)
    out = Image.new('RGB', (Wd, H + 56), (18, 18, 18))
    d = ImageDraw.Draw(out)
    x = 12
    for im, label in tiles:
        out.paste(im, (x, 12))
        d.text((x + 4, H + 20), label, fill=(235, 235, 235), font=FONT)
        x += im.width + 12
    p = os.path.join(pre, f'{asset}_vs_reference.jpg')
    out.save(p, quality=90)
    print(p, out.size)

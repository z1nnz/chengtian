# DR09 斷枝堆：成品和參考圖並排（每種一張）：左 = Codex 參考三視圖那一列（側視＋俯視），右 = 遊戲模型 LOD0 的正前（01_front）和俯視（09_top）。
# 輸出 art/previews/d2-logs-b/DR09_BranchPile_<v>/DR09_BranchPile_<v>_vs_reference.jpg
#   uv run --no-project --offline --with pillow python art/source/d2-logs-b/compose_dr09.py S M L
import os, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
REF = os.path.join(ROOT, 'art', 'references', 'DR09', 'v001', 'DR09-threeview.png')
ROWS = {'S': (40, 300), 'M': (300, 580), 'L': (590, 920)}       # 參考三視圖（1536×1024）裡每種大小那一列的上下範圍
H = 480


def fit(im, h):
    return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)


def crop_content(im, pad=24):
    g = im.convert('L')
    bg = g.getpixel((4, 4))
    box = g.point(lambda p: 255 if abs(p - bg) > 10 else 0).getbbox()
    if not box:
        return im
    x0, y0, x1, y1 = box
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


for v in sys.argv[1:] or ['S', 'M', 'L']:
    asset = f'DR09_BranchPile_{v}'
    pre = os.path.join(ROOT, 'art', 'previews', 'd2-logs-b', asset)
    ref = Image.open(REF).convert('RGB')
    y0, y1 = ROWS[v]
    row = fit(ref.crop((0, y0, ref.width, y1)), H)
    front = fit(crop_content(Image.open(os.path.join(pre, 'turnaround', '01_front.png')).convert('RGB')), H)
    top = fit(crop_content(Image.open(os.path.join(pre, 'turnaround', '09_top.png')).convert('RGB')), H)
    out = Image.new('RGB', (row.width + front.width + top.width + 24, H + 28), (236, 233, 228))
    out.paste(row, (0, 28))
    out.paste(front, (row.width + 12, 28))
    out.paste(top, (row.width + front.width + 24, 28))
    d = ImageDraw.Draw(out)
    d.text((8, 8), f'{asset}  reference (Codex, V4/V6 style)', fill=(40, 40, 40))
    d.text((row.width + 20, 8), 'game model LOD0: front / top (1.75 m ruler)', fill=(40, 40, 40))
    p = os.path.join(pre, f'{asset}_vs_reference.jpg')
    out.save(p, quality=90)
    print(p, out.size)

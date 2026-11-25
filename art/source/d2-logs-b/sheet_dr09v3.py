# DR09 v003 四視角拼圖：灰模一張、材質一張（各 2×2：正面、側面、俯視、四分之三）。
#   uv run --no-project --offline --with pillow python art/source/d2-logs-b/sheet_dr09v3.py L
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
try:
    FONT = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 26)
except OSError:
    FONT = ImageFont.load_default()
NAMES = [('front', '正面（白柱 = 1.75 m）'), ('side', '側面（白柱 = 1.75 m）'), ('top', '俯視'), ('tq', '四分之三：斜 45°、人眼高 1.7 m')]
TW, TH = 1100, 620


def crop_obj(im, pad=40):
    r, g, b = im.split()
    hi = ImageChops.lighter(ImageChops.lighter(r, g), b)
    lo = ImageChops.darker(ImageChops.darker(r, g), b)
    box = ImageChops.subtract(hi, lo).point(lambda p: 255 if p > 14 else 0).getbbox()
    return im if not box else im.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad)))


def fit(im):
    s = min(TW / im.width, TH / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    out = Image.new('RGB', (TW, TH), (205, 203, 199))
    out.paste(im, ((TW - im.width) // 2, (TH - im.height) // 2))
    return out


for v in sys.argv[1:] or ['L']:
    asset = f'DR09_BranchPile_{v}'
    pre = os.path.join(ROOT, 'art', 'previews', 'd2-logs-b', asset, 'v003')
    for mode, title in (('clay', '灰模＋線框'), ('mat', '材質預覽')):
        sheet = Image.new('RGB', (TW * 2 + 36, TH * 2 + 140), (18, 18, 18))
        d = ImageDraw.Draw(sheet)
        d.text((12, 10), f'{asset} v003 {title}', fill=(240, 240, 240), font=FONT)
        for k, (nm, label) in enumerate(NAMES):
            im = Image.open(os.path.join(pre, f'{asset}_{mode}_{nm}.png')).convert('RGB')
            if nm in ('top', 'tq'):
                im = crop_obj(im)
            x, y = 12 + (k % 2) * (TW + 12), 52 + (k // 2) * (TH + 44)
            sheet.paste(fit(im), (x, y))
            d.text((x + 6, y + TH + 6), label, fill=(225, 225, 225), font=FONT)
        p = os.path.join(pre, f'{asset}_v003_{mode}_sheet.jpg')
        sheet.save(p, quality=90)
        print(p, sheet.size)

# DR09 v004 前後對照：每列一個版本（第一列是參考圖），每欄一個視角（正面正交、俯視正交、斜 45°）。
# 成品的圖都是 views_dr09v4.py 固定鏡位出的，不依模型裁切，比例尺在各版本之間一致（斜 45° 用同一個固定框）。
#   uv run --no-project --offline --with pillow python art/source/d2-logs-b/compare_dr09v4.py <clay|mat> <輸出名> v002 v004_greybox ...
import os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
asset = 'DR09_BranchPile_L'
PRE = os.path.join(ROOT, 'art', 'previews', 'd2-logs-b', asset, os.environ.get('DR9OUT', 'v004'))   # 輸出位置；來源圖依序找 v005、v004 資料夾
SRC = [os.path.join(ROOT, 'art', 'previews', 'd2-logs-b', asset, d) for d in ('v026', 'v025', 'v024', 'v023', 'v022', 'v021', 'v020', 'v019', 'v018', 'v017', 'v016', 'v015', 'v014', 'v013', 'v012', 'v011', 'v010', 'v009', 'v008', 'v007', 'v006', 'v005', 'v004')]
REF = os.path.join(ROOT, 'art', 'references', 'DR09', 'v001')
H = 320
TQCROP = (230, 220, 1330, 780)
try:
    FONT = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 22)
except OSError:
    FONT = ImageFont.load_default()
LABEL = {'v026_greybox': 'v026 灰模', 'v026': 'v026 完成', 'v025_greybox': 'v025 灰模', 'v025': 'v025 完成', 'v024_greybox': 'v024 灰模', 'v024': 'v024 完成', 'v023_greybox': 'v023 灰模', 'v023': 'v023 完成', 'v022_greybox': 'v022 灰模', 'v022': 'v022 完成', 'v021_greybox': 'v021 灰模', 'v021': 'v021 完成', 'v020_greybox': 'v020 灰模', 'v020': 'v020 完成', 'v019_greybox': 'v019 灰模', 'v019': 'v019 完成', 'v018_greybox': 'v018 灰模', 'v018': 'v018 完成', 'v017_greybox': 'v017 灰模', 'v017': 'v017 完成', 'v016_greybox': 'v016 灰模', 'v016': 'v016 完成', 'v015_greybox': 'v015 灰模', 'v015': 'v015 完成', 'v014_greybox': 'v014 灰模', 'v014': 'v014 完成', 'v002': 'v002（修整前）', 'v003': 'v003', 'v004_greybox': 'v004 第一階段灰模', 'v004': 'v004 完成', 'v005_greybox': 'v005 灰模', 'v005': 'v005 完成', 'v006_greybox': 'v006 灰模', 'v006': 'v006 完成', 'v007_greybox': 'v007 灰模', 'v007': 'v007 完成', 'v008_greybox': 'v008 灰模', 'v008': 'v008 完成', 'v009_greybox': 'v009 灰模', 'v009': 'v009 完成', 'v010_greybox': 'v010 灰模', 'v010': 'v010 完成', 'v011_trio_greybox': 'v011 新換的 3 根分叉腐木（單獨）', 'v011_greybox': 'v011 灰模', 'v011': 'v011 完成', 'v012_focus_greybox': 'v012 W1＋Q3（單獨）', 'v012_greybox': 'v012 灰模', 'v012': 'v012 完成', 'v013_greybox': 'v013 灰模', 'v013': 'v013 完成'}


def fit(im, h=H):
    return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)


mode, name, tags = sys.argv[1], sys.argv[2], sys.argv[3:]
ref3 = Image.open(os.path.join(REF, 'DR09-threeview.png')).convert('RGB')
rows = [('參考圖（三視圖 L 列、情境圖）', [fit(ref3.crop((0, 600, 920, 900))), fit(ref3.crop((920, 610, 1536, 910))),
                                    fit(Image.open(os.path.join(REF, 'DR09-threequarter.png')).convert('RGB').crop((420, 120, 1490, 510)))])]
for t in tags:
    ims = []
    for view in ('front', 'top', 'tq'):
        fn = f'{asset}_{t}_{mode}_{view}.png'
        im = Image.open(next(os.path.join(d, fn) for d in SRC if os.path.exists(os.path.join(d, fn)))).convert('RGB')
        ims.append(fit(im.crop(TQCROP) if view == 'tq' else im))
    rows.append((LABEL.get(t, t) + ('：灰模＋線框' if mode == 'clay' else '：材質'), ims))
cw = [max(r[1][k].width for r in rows) for k in range(3)]
W = sum(cw) + 12 * 4
out = Image.new('RGB', (W, 44 + len(rows) * (H + 40)), (18, 18, 18))
d = ImageDraw.Draw(out)
for k, t in enumerate(('正面（正交平視，白柱 = 1.75 m）', '俯視（正交）', '斜 45°、人眼高 1.7 m')):
    d.text((12 + sum(cw[:k]) + 12 * k + 4, 10), t, fill=(235, 235, 235), font=FONT)
for j, (label, ims) in enumerate(rows):
    y = 44 + j * (H + 40)
    d.text((16, y + 2), label, fill=(255, 220, 150), font=FONT)
    x = 12
    for k, im in enumerate(ims):
        out.paste(im, (x + (cw[k] - im.width) // 2, y + 34))
        x += cw[k] + 12
out = out.crop((0, 0, W, 44 + len(rows) * (H + 40) + 30))
p = os.path.join(PRE, f'{asset}_{name}.jpg')
out.save(p, quality=90)
print(p, out.size)

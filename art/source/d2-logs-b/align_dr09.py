# DR09 正面形體對照（等寬、等比、底線對齊）：
#   參考圖（三視圖 L 列側視，裁掉左側人物）與成品正面（剪影圖決定外框，略過比例柱）各自裁到物件外框，
#   等比例縮到相同寬度（不做非等比拉伸），底線對齊；畫 0.25 m 格線（以成品實測長度換算），
#   可再讀一份特徵點 JSON（ref／model 各自的點與折線，公尺座標：x 從外框左緣、z 從底線），標在兩張圖與疊圖上。
#   uv run --no-project --offline --with pillow --with numpy python art/source/d2-logs-b/align_dr09.py <版本資料夾> <tag> <長度 m> [clay|mat] [特徵.json]
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
_ov = {'__file__': os.path.join(HERE, 'overlay_dr09.py'), '__name__': 'overlay_dr09'}
exec(compile(open(os.path.join(HERE, 'overlay_dr09.py'), encoding='utf-8').read().replace('\nmain()\n', '\n'), 'overlay_dr09.py', 'exec'), _ov)
PREV, asset, REF = _ov['PREV'], _ov['asset'], _ov['REF']
W = 1400
try:
    F = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 20)
    FS = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 15)
except OSError:
    F = FS = ImageFont.load_default()


def bbox(m):
    rows = np.nonzero(m.sum(1) > 3)[0]
    cols = np.nonzero(m.sum(0) > 3)[0]
    return cols[0], rows[0], cols[-1] + 1, rows[-1] + 1


def fit(im, m, box):
    x0, y0, x1, y1 = box
    c = im.crop(box)
    cm = Image.fromarray((m[y0:y1, x0:x1] * 255).astype(np.uint8))
    H = round(W * c.height / c.width)
    return c.resize((W, H), Image.LANCZOS), np.asarray(cm.resize((W, H), Image.BILINEAR)) > 127


out_dir, tag, Lm = sys.argv[1], sys.argv[2], float(sys.argv[3])
mode = sys.argv[4] if len(sys.argv) > 4 else 'clay'
feat = json.load(open(sys.argv[5], encoding='utf-8')) if len(sys.argv) > 5 else {}
if 'ref_L' in feat:                                                        # 參考特徵依同寬換算（成品長度變了，參考跟著等比縮放）
    _k = Lm / feat['ref_L']
    feat['ref'] = [dict(f, p=[[x * _k, z * _k] for x, z in f['p']]) for f in feat['ref']]
ref_full = Image.open(REF).convert('RGB').crop((150, 600, 920, 884))      # 150 起：排除左側人物
rm = _ov['ref_mask'](ref_full)
ri, rmk = fit(ref_full, rm, bbox(rm))
sil = Image.open(os.path.join(PREV, out_dir, f'{asset}_{tag}_sil_front.png')).convert('RGB')
om = _ov['our_mask'](sil, 0, True)
src = os.path.join(PREV, out_dir, f'{asset}_{tag}_{mode}_front.png')
oi, omk = fit(Image.open(src).convert('RGB'), om, bbox(om))               # 剪影外框不含比例柱（剪影圖只渲染木堆）
px = Lm / W
Hh = max(ri.height, oi.height)
pad, lab = 30, 34
sheet = Image.new('RGB', (W + 2 * pad, 3 * (Hh + lab + 20) + 60), (18, 18, 18))
d = ImageDraw.Draw(sheet)
d.text((pad, 10), f'正面形體對照：各自裁到物件外框（參考排除人物、成品排除比例柱）、等比縮到同寬 = {Lm} m、底線對齊；格線 0.25 m',
       fill=(255, 220, 150), font=F)


def grid(y0, H):
    for k in range(int(Lm / .25) + 1):
        x = pad + k * .25 / px
        d.line([x, y0, x, y0 + Hh], fill=(70, 70, 70) if k % 2 else (110, 110, 110), width=1)
        if k % 2 == 0:
            d.text((x + 2, y0 + Hh + 2), f'{k * .25:.1f}', fill=(150, 150, 150), font=FS)
    for k in range(int(Hh * px / .25) + 1):
        y = y0 + Hh - k * .25 / px
        d.line([pad, y, pad + W, y], fill=(70, 70, 70), width=1)
        d.text((4, y - 9), f'{k * .25:.2f}', fill=(150, 150, 150), font=FS)


def marks(key, y0, col):
    for f in feat.get(key, []):
        pts = [(pad + x / px, y0 + Hh - z / px) for x, z in f['p']]
        if len(pts) > 1:
            d.line(pts, fill=col, width=3)
        for p in pts:
            d.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], outline=col, width=2)
        d.text((pts[0][0] + 7, pts[0][1] - 22), f['n'], fill=col, font=FS)


rows = [('參考（三視圖 L 列側視）', ri, None, 'ref', (255, 120, 90)), (f'{tag}（正面正交，{mode}）', oi, None, 'model', (90, 200, 255))]
for i, (t, im, _, key, col) in enumerate(rows):
    y0 = 50 + i * (Hh + lab + 20) + lab
    d.text((pad, y0 - lab + 4), t, fill=(220, 220, 220), font=F)
    sheet.paste(im, (pad, y0 + Hh - im.height))
    grid(y0, Hh)
    marks(key, y0, col)
# 疊圖：紅＝只有參考、藍＝只有成品、白＝重疊；兩邊特徵點都畫
y0 = 50 + 2 * (Hh + lab + 20) + lab
d.text((pad, y0 - lab + 4), '疊圖：紅＝只有參考、藍＝只有成品、白＝重疊（同寬、底線對齊）；橘線＝參考特徵、藍線＝成品特徵', fill=(220, 220, 220), font=F)
t = np.full((Hh, W, 3), 24, np.uint8)
A = np.zeros((Hh, W), bool); A[Hh - rmk.shape[0]:] = rmk
B = np.zeros((Hh, W), bool); B[Hh - omk.shape[0]:] = omk
t[A & ~B] = (200, 70, 60); t[B & ~A] = (60, 150, 210); t[A & B] = (215, 215, 205)
sheet.paste(Image.fromarray(t), (pad, y0))
grid(y0, Hh)
marks('ref', y0, (255, 150, 60))
marks('model', y0, (60, 120, 255))
iou = (A & B).sum() / max(1, (A | B).sum())
d.text((pad + W - 330, y0 - lab + 4), f'IoU {iou:.3f}　高：參考 {rmk.shape[0] * px:.2f} m／成品 {omk.shape[0] * px:.2f} m', fill=(255, 220, 150), font=FS)
p = os.path.join(PREV, out_dir, f'{asset}_{tag}_align_front.png')
sheet.save(p)
print(p, 'iou', round(float(iou), 3), 'ref_h', round(rmk.shape[0] * px, 3), 'our_h', round(omk.shape[0] * px, 3))

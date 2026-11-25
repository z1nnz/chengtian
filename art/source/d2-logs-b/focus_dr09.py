# DR09 局部目標輪廓對照：參考正面與成品正面各自裁到物件外框（參考排除人物、成品排除比例柱），等比縮到同寬、底線對齊後，
#   裁出指定區域（公尺座標：x 從外框左緣、z 從底線），並排參考／成品，兩邊都描上「參考外輪廓（橘）」與「成品外輪廓（青）」，
#   另附疊圖（紅＝只有參考、藍＝只有成品、白＝重疊）。可同時放多個版本的成品列。
#   uv run --no-project --offline --with pillow --with numpy python art/source/d2-logs-b/focus_dr09.py <輸出資料夾> <輸出 tag> <L> <mode> <區域名:x0,x1,z0,z1> ... -- <版本資料夾/tag> ...
#   例：focus_dr09.py v025 v025pre 4.123 mat break:0,1.3,0,.75 t1:2.3,3.6,.35,1.25 -- v024/v024
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
_ov = {'__file__': os.path.join(HERE, 'overlay_dr09.py'), '__name__': 'overlay_dr09'}
exec(compile(open(os.path.join(HERE, 'overlay_dr09.py'), encoding='utf-8').read().replace('\nmain()\n', '\n'), 'overlay_dr09.py', 'exec'), _ov)
PREV, asset, REF = _ov['PREV'], _ov['asset'], _ov['REF']
W = 1400
F = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 22)
FS = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 15)


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


def _sh(m, r, op):
    o = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                o = op(o, np.roll(np.roll(m, dy, 0), dx, 1))
    return o


def close(m, r=5):                                                         # 形態閉運算：補掉苔／地衣被誤判的小孔，保留大空洞
    return _sh(_sh(m, r, np.logical_or), r, np.logical_and)


def edge(m):
    e = m.copy()
    e[1:-1, 1:-1] = m[1:-1, 1:-1] & ~(m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:])
    e[0, :] = e[-1, :] = e[:, 0] = e[:, -1] = False
    k = np.zeros_like(e)                                                   # 線加粗 2 px
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            k |= np.roll(np.roll(e, dy, 0), dx, 1)
    return k


argv = sys.argv[1:]
cut = argv.index('--')
out_dir, tag, Lm, mode = argv[0], argv[1], float(argv[2]), argv[3]
regs = [(a.split(':')[0], [float(v) for v in a.split(':')[1].split(',')]) for a in argv[4:cut]]
vers = argv[cut + 1:]
px = Lm / W
ref_full = Image.open(REF).convert('RGB').crop((150, 600, 920, 884))
ri, rmk = fit(ref_full, _ov['ref_mask'](ref_full), bbox(_ov['ref_mask'](ref_full)))
mods = []
for v in vers:
    d_, t_ = v.split('/')
    sil = Image.open(os.path.join(PREV, d_, f'{asset}_{t_}_sil_front.png')).convert('RGB')
    om = _ov['our_mask'](sil, 0, True)
    oi, omk = fit(Image.open(os.path.join(PREV, d_, f'{asset}_{t_}_{mode}_front.png')).convert('RGB'), om, bbox(om))
    mods.append((t_, oi, omk))
Hh = max([ri.height] + [m[1].height for m in mods])


def canvas(im, mk):
    c = np.full((Hh, W, 3), 30, np.uint8); c[Hh - im.height:] = np.asarray(im)
    m = np.zeros((Hh, W), bool); m[Hh - mk.shape[0]:] = mk
    return c, close(m)


R, RM = canvas(ri, rmk)
RE = edge(RM)
for name, (x0, x1, z0, z1) in regs:
    X0, X1 = int(x0 / px), int(x1 / px)
    Y0, Y1 = max(0, Hh - int(z1 / px)), Hh - int(z0 / px)
    cols = []
    for t_, im, mk in [('參考', ri, rmk)] + mods:
        c, m = canvas(im, mk)
        e = edge(m)
        c = c.copy()
        c[RE] = (255, 140, 40)
        if t_ != '參考':
            c[e] = (40, 230, 255)
        cols.append((t_, c[Y0:Y1, X0:X1]))
        if t_ != '參考':
            t = np.full(m.shape + (3,), 24, np.uint8)
            t[RM & ~m] = (200, 70, 60); t[m & ~RM] = (60, 150, 210); t[RM & m] = (215, 215, 205)
            sub = (RM | m)[Y0:Y1, X0:X1]; inter = (RM & m)[Y0:Y1, X0:X1]
            cols.append((f'{t_} 疊圖  區域 IoU {inter.sum() / max(1, sub.sum()):.3f}', t[Y0:Y1, X0:X1]))
    w, h = X1 - X0, Y1 - Y0
    k = 900 / w
    sw, sh_ = 900, int(h * k)
    sheet = Image.new('RGB', (sw + 20, len(cols) * (sh_ + 40) + 50), (18, 18, 18))
    d = ImageDraw.Draw(sheet)
    d.text((10, 8), f'{name}：x {x0}–{x1} m、z {z0}–{z1} m（同寬 {Lm} m、底線對齊）；橘線＝參考外輪廓、青線＝成品外輪廓', fill=(255, 220, 150), font=F)
    for i, (t_, a) in enumerate(cols):
        y = 50 + i * (sh_ + 40)
        d.text((10, y), t_, fill=(220, 220, 220), font=F)
        sheet.paste(Image.fromarray(a).resize((sw, sh_), Image.LANCZOS), (10, y + 30))
        for gx in np.arange(np.ceil(x0 / .25) * .25, x1 + 1e-6, .25):          # 0.25 m 格線刻度
            xx = 10 + (gx - x0) / px * k
            d.text((xx + 2, y + 30 + sh_ - 18), f'{gx:.2f}', fill=(150, 150, 150), font=FS)
    p = os.path.join(PREV, out_dir, f'{asset}_{tag}_focus_{name}.png')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    sheet.save(p)
    print(p)

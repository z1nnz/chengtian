# DR09 正面輪廓特徵對照：參考圖與成品剪影各自裁到包圍框、等比例縮到相同寬度（不做非等比拉伸）、底部對齊地面，
# 換算成公尺（以成品實測長度 L 為寬度），找：最高枝端、上緣的主要峰（拱頂、右側分叉等）、被輪廓圍住的主要空洞（地面算封閉邊）。
# 因專案高度上限 1.1 m，成品高寬比比參考低；等比對齊後參考的垂直位置會整體較高，這裡同時列出「佔各自高度的比例」方便比較。
#   uv run --no-project --offline --with pillow --with numpy python art/source/d2-logs-b/feat_dr09.py <版本資料夾> <tag> <成品長度 m>
import os, sys, json
from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.argv += [] if len(sys.argv) > 3 else ['v019', 'v019', '4.56']
HERE = os.path.dirname(os.path.abspath(__file__))
_ov = {'__file__': os.path.join(HERE, 'overlay_dr09.py'), '__name__': 'overlay_dr09'}
exec(compile(open(os.path.join(HERE, 'overlay_dr09.py'), encoding='utf-8').read().replace('\nmain()\n', '\n'), 'overlay_dr09.py', 'exec'), _ov)
ROOT, PREV, asset, REF, W = _ov['ROOT'], _ov['PREV'], _ov['asset'], _ov['REF'], _ov['W']
FONT = _ov['FONT']
out_dir, tag, Lm = sys.argv[1], sys.argv[2], float(sys.argv[3])
ref = Image.open(REF).convert('RGB')
rm, _ = _ov['crop_norm'](_ov['ref_mask'](ref.crop((150, 600, 920, 884))))
om, _ = _ov['crop_norm'](_ov['our_mask'](Image.open(os.path.join(PREV, out_dir, f'{asset}_{tag}_sil_front.png')).convert('RGB'), 0, True))
px = Lm / W                                    # 每像素公尺（同寬 → 同比例）


def holes(m, min_area=.012):
    H, Wd = m.shape
    seen = np.zeros_like(m)
    out = []
    # 外部空白：從上、左、右邊界灌（地面＝底邊不灌）
    q = deque()
    for x in range(Wd):
        if not m[0, x]:
            q.append((0, x))
    for y in range(H):
        for x in (0, Wd - 1):
            if not m[y, x]:
                q.append((y, x))
    for p in q:
        seen[p] = True
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < Wd and not seen[yy, xx] and not m[yy, xx]:
                seen[yy, xx] = True
                q.append((yy, xx))
    for y0 in range(H):
        for x0 in range(Wd):
            if m[y0, x0] or seen[y0, x0]:
                continue
            pts = []
            q = deque([(y0, x0)])
            seen[y0, x0] = True
            while q:
                y, x = q.popleft()
                pts.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < Wd and not seen[yy, xx] and not m[yy, xx]:
                        seen[yy, xx] = True
                        q.append((yy, xx))
            a = np.array(pts)
            area = len(a) * px * px
            if area >= min_area:
                out.append(dict(x=round(float(a[:, 1].mean() * px), 2), z=round(float((H - a[:, 0].mean()) * px), 2), area_m2=round(area, 3),
                                x0=round(float(a[:, 1].min() * px), 2), x1=round(float(a[:, 1].max() * px), 2),
                                z0=round(float((H - a[:, 0].max()) * px), 2), z1=round(float((H - a[:, 0].min()) * px), 2)))
    return sorted(out, key=lambda d: -d['area_m2'])[:7]


def feats(m):
    H = m.shape[0]
    top = np.array([H - np.argmax(c) if c.any() else 0 for c in m.T]) * px
    k = int(top.argmax())
    sm = np.convolve(top, np.ones(31) / 31, 'same')
    peaks = []
    for x in range(20, W - 20):
        if sm[x] == sm[max(0, x - 60):x + 61].max() and sm[x] > .25 * top.max():
            if not peaks or x - peaks[-1][0] > 50:
                peaks.append((x, float(top[x])))
    return dict(height=round(H * px, 3), top_x=round(k * px, 2), top_z=round(float(top[k]), 3),
                peaks=[dict(x=round(x * px, 2), z=round(z, 3), z_frac=round(z / (H * px), 2)) for x, z in peaks], holes=holes(m)), top


fr, tr = feats(rm)
fo, to = feats(om)
res = {'scale_note': f'兩者等比縮到同寬，寬度 = {Lm} m；底部對齊', 'ref': fr, tag: fo}
print(json.dumps(res, ensure_ascii=False, indent=1))
# 標註圖
Hh = max(rm.shape[0], om.shape[0])
sheet = Image.new('RGB', (W + 20, 2 * (Hh + 40) + 50), (18, 18, 18))
d = ImageDraw.Draw(sheet)
d.text((10, 8), f'正面輪廓特徵（等比同寬、底部對齊；寬 = {Lm} m）：紅框＝空洞、黃點＝上緣峰、白十字＝最高點', fill=(255, 220, 150), font=FONT)
for i, (lab, m, f) in enumerate((('參考', rm, fr), (tag, om, fo))):
    y = 44 + i * (Hh + 40)
    t = np.full((Hh, W, 3), 24, np.uint8)
    t[Hh - m.shape[0]:][m] = (190, 190, 190)
    sheet.paste(Image.fromarray(t), (10, y + 24))
    d.text((10, y), lab, fill=(220, 220, 220), font=FONT)
    Z = lambda z: y + 24 + Hh - z / px
    for h in f['holes']:
        d.rectangle([10 + h['x0'] / px, Z(h['z1']), 10 + h['x1'] / px, Z(h['z0'])], outline=(230, 80, 70), width=2)
    for p in f['peaks']:
        d.ellipse([10 + p['x'] / px - 6, Z(p['z']) - 6, 10 + p['x'] / px + 6, Z(p['z']) + 6], outline=(255, 210, 60), width=3)
    cx, cz = 10 + f['top_x'] / px, Z(f['top_z'])
    d.line([cx - 12, cz, cx + 12, cz], fill=(255, 255, 255), width=3)
    d.line([cx, cz - 12, cx, cz + 12], fill=(255, 255, 255), width=3)
p = os.path.join(PREV, out_dir, f'{asset}_{tag}_front_features.png')
sheet.save(p)
json.dump(res, open(p.replace('.png', '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(p)

# DR09 透空量測（v014 起）：不用整個外框算透空，只算「堆體內部」——每一欄從上緣輪廓到地面之間的範圍；
# 另量參考圖兩個主要洞口範圍內的透空：中央拱下洞口、A 左段下方的前側低洞（範圍以參考圖剪影定，換算成木堆寬度、離地高度的比例）。
# 剪影來源同 overlay_dr09.py：參考三視圖 L 列側視（去落葉、去人形），成品用 sil 剪影圖（只有木質本體、不含落葉卡）。
# 兩邊都裁到木堆外框、縮到同寬（1000 px）、底部對齊地面。輸出遮罩圖（灰 = 計算範圍、白 = 木、黑 = 透空、框 = 洞口範圍）與 json。
#   uv run --no-project --offline --with pillow --with numpy python art/source/d2-logs-b/holes_dr09.py <輸出資料夾> <tag>
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
g = {'__name__': 'overlay_lib', '__file__': HERE + '/overlay_dr09.py'}
src = open(HERE + '/overlay_dr09.py', encoding='utf-8').read().replace('\nmain()\n', '\n')
exec(compile(src, g['__file__'], 'exec'), g)
W = g['W']
BOXES = {   # (x0, x1) 佔寬度比例（左→右），(h0, h1) 佔總高比例（離地）
    '中央拱下洞口': ((.29, .46), (.38, .70)),
    '前側低洞（A 左段下方）': ((.12, .28), (.02, .17)),
}


def interior(m):
    top = np.array([np.argmax(c) if c.any() else m.shape[0] for c in m.T])
    rows = np.arange(m.shape[0])[:, None]
    return rows >= top[None, :]


def measure(m):
    H = m.shape[0]
    reg = interior(m)
    out = dict(interior_void=round(float((reg & ~m).sum() / max(reg.sum(), 1)), 3))
    for k, ((x0, x1), (h0, h1)) in BOXES.items():
        c0, c1 = int(x0 * W), int(x1 * W)
        r0, r1 = int(H * (1 - h1)), int(H * (1 - h0))
        box = m[r0:r1, c0:c1]
        out[k] = round(float(1 - box.mean()), 3)
    return out, reg


def tile(m, reg, lab, F):
    H = m.shape[0]
    t = np.full((H, W, 3), 20, np.uint8)
    t[reg & ~m] = (70, 70, 70)
    t[m] = (225, 225, 215)
    im = Image.fromarray(t)
    d = ImageDraw.Draw(im)
    for (x0, x1), (h0, h1) in BOXES.values():
        d.rectangle([int(x0 * W), int(H * (1 - h1)), int(x1 * W), int(H * (1 - h0))], outline=(255, 120, 90), width=3)
    d.text((8, 6), lab, fill=(255, 220, 150), font=F)
    return im


def main():
    out_dir, tag = sys.argv[1], sys.argv[2]
    ref = Image.open(g['REF']).convert('RGB').crop((150, 600, 920, 884))
    rm, _ = g['crop_norm'](g['ref_mask'](ref))
    p = os.path.join(g['PREV'], out_dir, f"{g['asset']}_{tag}_sil_front.png")
    om, _ = g['crop_norm'](g['our_mask'](Image.open(p).convert('RGB'), 0, True))
    res = {}
    tiles = []
    for lab, m in (('參考（側視，去落葉、人形）', rm), (tag, om)):
        r, reg = measure(m)
        res[lab] = r
        tiles.append(tile(m, reg, f'{lab}　內部透空 {r["interior_void"] * 100:.0f}%　' + '　'.join(f'{k} {v * 100:.0f}%' for k, v in r.items() if k != 'interior_void'), g['FONT']))
    Hs = sum(t.height for t in tiles) + 20 * len(tiles) + 60
    sheet = Image.new('RGB', (W + 20, Hs), (12, 12, 12))
    d = ImageDraw.Draw(sheet)
    d.text((10, 8), '透空量測：灰 = 計算範圍內的透空（上緣輪廓到地面之間）、白 = 木、框 = 洞口範圍；不含落葉卡', fill=(220, 220, 220), font=g['FONT'])
    y = 50
    for t in tiles:
        sheet.paste(t, (10, y))
        y += t.height + 20
    po = os.path.join(g['PREV'], out_dir, f"{g['asset']}_{tag}_holes_front.png")
    sheet.save(po)
    json.dump(dict(boxes={k: dict(x=v[0], h=v[1]) for k, v in BOXES.items()}, result=res), open(po[:-4] + '.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False), po)


main()

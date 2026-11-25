# DR09 俯視透空率：核對參考與成品是否用同一定義。overlay_dr09.py 的透空＝1 −（本體像素 ÷ 本體外框矩形），
# 但參考圖去掉落葉（落葉位置變成空洞）、解析度低（565 px 寬，細縫被糊掉）並做 3×3 開運算；成品灰模剪影沒有落葉、沒有土壤貼片、解析度高。
# 這支把各種組合都算一次，並輸出遮罩對照，說明分母與是否計入落葉、地面、陰影。
#   uv run --no-project --offline --with pillow --with numpy python art/source/d2-logs-b/void_dr09.py <版本資料夾> <版本>
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from numpy.lib.stride_tricks import sliding_window_view as sw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
asset = 'DR09_BranchPile_L'
PREV = os.path.join(ROOT, 'art', 'previews', 'd2-logs-b', asset)
REF = os.path.join(ROOT, 'art', 'references', 'DR09', 'v001', 'DR09-threeview.png')
FONT = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 20)
W = 1000


def opening(m, k=3):
    p = np.pad(m, k // 2)
    er = sw(p, (k, k)).all((2, 3))
    p = np.pad(er, k // 2)
    return sw(p, (k, k)).any((2, 3))


def dilate(m, k):
    p = np.pad(m, k // 2)
    return sw(p, (k, k)).any((2, 3))


def erode(m, k):
    p = np.pad(m, k // 2, constant_values=True)
    return sw(p, (k, k)).all((2, 3))


def fill_holes(m):
    """外輪廓內部全部填滿（從邊界往內淹，淹不到的就是內部）。"""
    out = np.zeros_like(m)
    H, Wd = m.shape
    st = [(y, x) for y in range(H) for x in (0, Wd - 1) if not m[y, x]] + [(y, x) for x in range(Wd) for y in (0, H - 1) if not m[y, x]]
    seen = np.zeros_like(m)
    while st:
        y, x = st.pop()
        if seen[y, x] or m[y, x]:
            continue
        seen[y, x] = True
        if y > 0: st.append((y - 1, x))
        if y < H - 1: st.append((y + 1, x))
        if x > 0: st.append((y, x - 1))
        if x < Wd - 1: st.append((y, x + 1))
    return ~seen


def crop(m):
    rows = np.nonzero(m.sum(1) > 2)[0]
    cols = np.nonzero(m.sum(0) > 2)[0]
    return m[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]


def to_w(m, w=W):
    H = max(1, round(w * m.shape[0] / m.shape[1]))
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((w, H), Image.BILINEAR)) > 127


def ref_masks():
    a = np.asarray(Image.open(REF).convert('RGB').crop((925, 615, 1490, 905))).astype(int)
    bg = np.median(np.array([a[3, 3], a[3, -4], a[-4, -4], a[-4, 3]]), axis=0)
    body = np.abs(a - bg).sum(2) > 40
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    sat = (a.max(2) - a.min(2)) / np.maximum(a.max(2), 1)
    leaf = (r > g + 18) & (g > b + 8) & (sat > .38) & (r > 120)
    no_leaf = opening(body & ~leaf)
    with_leaf = opening(body)
    return no_leaf, with_leaf, body.shape[1]


def our_sil(path):
    return np.asarray(Image.open(path).convert('L')) > 90


def stats(m, close_frac=.05):
    c = crop(m)
    c = to_w(c)
    k = max(3, int(W * close_frac) | 1)
    outline = fill_holes(erode(dilate(c, k), k))
    return c, outline, dict(bbox_void=round(1 - c.mean(), 3), outline_void=round(1 - c[outline].mean(), 3),
                            outline_fill=round(outline.mean(), 3), aspect=round(c.shape[0] / c.shape[1], 3))


def main():
    d, v = sys.argv[1], sys.argv[2]
    P = os.path.join(PREV, d)
    rn, rl, ref_px = ref_masks()
    ref_obj_w = crop(rn).shape[1]
    g = our_sil(os.path.join(P, f'{asset}_{v}_greybox_sil_top.png'))
    fp = os.path.join(P, f'{asset}_{v}_sil_top.png')
    full = our_sil(fp) if os.path.exists(fp) else None
    gc = crop(g)
    small = np.asarray(Image.fromarray((gc * 255).astype(np.uint8)).resize((ref_obj_w, max(1, round(ref_obj_w * gc.shape[0] / gc.shape[1]))), Image.BILINEAR)) > 127
    g_ref = opening(small)                                              # 同參考解析度＋同樣 3×3 開運算
    rows = [('參考：去落葉（overlay 原定義）', rn), ('參考：保留落葉', rl),
            (f'{v} 灰模剪影（無落葉、無土壤貼片；overlay 原定義）', g), (f'{v} 灰模剪影，降到參考解析度＋同樣開運算', g_ref),
            (f'{v} 完整剪影（含落葉卡、土壤貼片）', full)]
    rows = [r_ for r_ in rows if r_[1] is not None]
    res, tiles = {}, []
    for lab, m in rows:
        c, ol, st = stats(m)
        res[lab] = st
        t = np.full(c.shape + (3,), 24, np.uint8)
        t[ol & ~c] = (90, 40, 40)                 # 外輪廓內的空隙
        t[c] = (205, 205, 205)
        tiles.append((lab, st, Image.fromarray(t)))
    Hh = max(t[2].height for t in tiles)
    sh = Image.new('RGB', (W + 20, len(tiles) * (Hh + 60) + 180), (18, 18, 18))
    dd = ImageDraw.Draw(sh)
    notes = ['俯視透空率定義核對（同寬 1000 px、上下各自裁到本體外框）。灰＝本體；暗紅＝外輪廓以內的空隙。',
             '外框透空＝1 - 本體 ÷ 外框矩形（overlay 原定義，矩形四角也算空）',
             '輪廓透空＝1 - 本體 ÷ 外輪廓（閉運算 5% 寬後填洞）以內。',
             '兩邊都不計陰影：參考圖是平塗背景；成品是黑底白剪影，不渲染地面與陰影。',
             '土壤貼片只在「完整剪影」裡；該列落葉卡以整張方形卡計入（未扣透明），數字偏高、僅供參考。']
    for k, n in enumerate(notes):
        dd.text((10, 8 + k * 28), n, fill=(255, 220, 150), font=FONT)
    y = 150
    for lab, st, im in tiles:
        dd.text((10, y), f'{lab}｜外框透空 {st["bbox_void"] * 100:.0f}%｜輪廓透空 {st["outline_void"] * 100:.0f}%｜高寬比 {st["aspect"]:.2f}', fill=(220, 220, 220), font=FONT)
        sh.paste(im, (10, y + 30))
        y += Hh + 60
    out = os.path.join(P, f'{asset}_{v}_void_masks.png')
    sh.save(out)
    json.dump(dict(ref_crop_px=ref_px, ref_object_px=ref_obj_w, rows=res), open(os.path.join(P, f'{asset}_{v}_void.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for lab, st in res.items():
        print(lab, st)
    print(out)


main()

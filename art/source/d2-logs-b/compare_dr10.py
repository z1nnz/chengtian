# DR10 第八輪：參考三視圖 vs 灰模剪影的「等高對照」與輪廓量測。
# - 參考圖每棵樹裁出（地線以上），模型剪影裁出（z = 0 以上），兩者等比縮放到同一個高度（像素），根部基線對齊、幹基中心對齊；不做非等比拉伸。
# - 主幹中心線與幹寬：從幹基往上逐列追蹤主幹那一段（避開枝），在 0.05–0.95 高度取樣；單位＝樹高的比例。
# 用法：python compare_dr10.py <剪影資料夾> <輸出前綴> [<第二組剪影資料夾> <標籤1> <標籤2>]
import sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

REF = 'D:/yun-jing-d2-logs/art/references/DR10/v001/DR10-threeview.png'
F = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 20)
FS = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 16)
HS = [.05, .10, .15, .20, .25, .30, .35, .40, .45, .50, .55, .60, .65, .70, .75, .80, .85, .90]


def ref_trees():
    im = np.asarray(Image.open(REF).convert('RGB')).astype(int)
    bg = im[5, 5]
    m = np.abs(im - bg).sum(-1) > 40
    full = np.nonzero(m.mean(1) > .55)[0]                 # 地線
    gy = int(full.min())
    m[gy:] = False
    cols = m[:gy].sum(0)
    split = 1050 + int(np.argmin(cols[1050:1200]))       # B 正、B 側之間
    spans = {'A_front': (27, 334), 'A_side': (350, 590), 'B_front': (654, split), 'B_side': (split, 1508)}
    out = {}
    from PIL import ImageFilter
    mi = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    mi = mi.point(lambda q: 255 if q > 128 else 0)
    ImageDraw.floodfill(mi, (0, 0), 128)                  # 從邊界灌背景，剩下沒灌到的洞補滿（裸木顏色接近背景）
    m = np.asarray(mi) != 128
    m[gy:] = False
    for k, (x0, x1) in spans.items():
        mm = np.zeros_like(m)
        mm[:, x0:x1] = m[:, x0:x1]
        out[k] = (im.astype(np.uint8), mm, gy)
    return out


def model_mask(d, v, view):
    im = np.asarray(Image.open(f'{d}/DR10_{v}_sil_{view}.png').convert('RGBA'))
    meta = json.load(open(f'{d}/DR10_{v}_sil.json'))
    gy = int(round(625 + meta['zc'] * meta['px_per_m']))
    m = im[..., 3] > 128
    m[gy:] = False
    rgb = im[..., :3].copy()
    rgb[~(im[..., 3] > 0)] = (205, 205, 205)
    return rgb, m, gy


def crop(rgb, m, gy):
    ys, xs = np.nonzero(m)
    top = ys.min()
    # 幹基中心：地線上 3% 高度那一列，最長一段的中心
    h = gy - top
    row = m[gy - max(2, int(.03 * h))]
    xs_r = np.nonzero(row)[0]
    runs = np.split(xs_r, np.nonzero(np.diff(xs_r) > 1)[0] + 1)
    rr = max(runs, key=len)
    cx = (rr[0] + rr[-1]) / 2
    return top, gy, cx


def trace(m, top, gy, cx):
    """主幹中心線與寬度：從 8% 高度開始往上，每列取包含前一列中心的那一段；寬度突然變大（併到枝）時用中位寬度夾住。"""
    h = gy - top
    y = gy - int(.08 * h)
    c = cx
    ws = []
    res = {}
    while y > top + 2:
        row = m[y]
        if not row[int(round(c))]:
            nz = np.nonzero(row)[0]
            if len(nz) == 0:
                break
            j = nz[np.argmin(np.abs(nz - c))]
            if abs(j - c) > .04 * h:
                break
            c = j
        l = int(round(c))
        while l > 0 and row[l - 1]:
            l -= 1
        r = int(round(c))
        while r < len(row) - 1 and row[r + 1]:
            r += 1
        w = r - l + 1
        med = np.median(ws[-25:]) if ws else w
        if ws and w > 1.35 * med:                          # 併到枝：中心只小步移動
            nc = c
            w = med
        else:
            nc = (l + r) / 2
        c = c + np.clip(nc - c, -2, 2)
        ws.append(w)
        hh = (gy - y) / h
        res[round(hh, 3)] = ((c - cx) / h, w / h)
        y -= 1
    out = {}
    keys = np.array(list(res.keys()))
    for q in HS:
        if len(keys) and keys.max() >= q:
            k = keys[np.argmin(np.abs(keys - q))]
            out[q] = res[k]
    return out


def panel(rgb, m, gy, H_px, top, cx, tint, prof):
    h = gy - top
    s = H_px / h
    x0 = int(cx - .75 * h)
    x1 = int(cx + .75 * h)
    pad = np.full((h, x1 - x0, 3), 205, np.uint8)
    pm = np.zeros((h, x1 - x0), bool)
    sx0, sx1 = max(0, x0), min(rgb.shape[1], x1)
    pad[:, sx0 - x0:sx1 - x0] = rgb[top:gy, sx0:sx1]
    pm[:, sx0 - x0:sx1 - x0] = m[top:gy, sx0:sx1]
    W = int((x1 - x0) * s)
    img = Image.fromarray(pad).resize((W, H_px), Image.LANCZOS)
    mk = Image.fromarray((pm * 255).astype(np.uint8)).resize((W, H_px), Image.NEAREST)
    return img, np.asarray(mk) > 128


def run(dirs, labels, outp):
    refs = ref_trees()
    H_px = 760
    report = {}
    sheets = []
    for key in ('A_front', 'A_side', 'B_front', 'B_side'):
        v, view = key.split('_')
        mview = 'side2' if view == 'side' else view      # 參考側視圖的彎向對應模型從 -X 看（第八輪判斷）
        rgb, m, gy = refs[key]
        top, gy, cx = crop(rgb, m, gy)
        rp = trace(m, top, gy, cx)
        rimg, rmask = panel(rgb, m, gy, H_px, top, cx, None, rp)
        cells = [('參考', rimg, rmask, rp)]
        for d, lab in zip(dirs, labels):
            mr, mm, mgy = model_mask(d, v, mview)
            mt, mgy, mcx = crop(mr, mm, mgy)
            mp = trace(mm, mt, mgy, mcx)
            mimg, mmask = panel(mr, mm, mgy, H_px, mt, mcx, None, mp)
            cells.append((lab, mimg, mmask, mp))
            report[f'{key}_{lab}'] = {str(q): [round(a, 3), round(b, 3)] for q, (a, b) in mp.items()}
        report[f'{key}_參考'] = {str(q): [round(a, 3), round(b, 3)] for q, (a, b) in rp.items()}
        # 疊圖：參考剪影（紅）＋每個模型剪影的外框
        Wd = rimg.width
        ov = np.full((H_px, Wd, 3), 235, np.uint8)
        ov[rmask] = (225, 150, 140)
        cols = [(20, 90, 200), (20, 150, 60)]
        for i, c in enumerate(cells[1:]):
            mk = c[2]
            w = min(Wd, mk.shape[1])
            e = mk[:, :w] & ~(np.roll(mk[:, :w], 1, 0) & np.roll(mk[:, :w], -1, 0) & np.roll(mk[:, :w], 1, 1) & np.roll(mk[:, :w], -1, 1))
            e = e | np.roll(e, 1, 1)
            ov[:, :w][e] = cols[i % 2]
        ovi = Image.fromarray(ov)
        dr = ImageDraw.Draw(ovi)
        for i, c in enumerate(cells):                    # 中心線
            col = (160, 30, 20) if i == 0 else cols[(i - 1) % 2]
            pts = [(Wd / 2 + a * H_px, H_px - q * H_px) for q, (a, b) in sorted(c[3].items())]
            if len(pts) > 1:
                dr.line(pts, fill=col, width=3)
        cells.append(('疊圖（紅＝參考剪影、線＝模型外框與中心線）', ovi, None, {}))
        sheets.append((key, cells))
    # 版面
    cw = max(c[1].width for _, cells in sheets for c in cells)
    ncol = max(len(cells) for _, cells in sheets)
    canvas = Image.new('RGB', (ncol * (cw + 10) + 10, len(sheets) * (H_px + 50) + 60), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    d.text((12, 12), '等高對照：參考與模型各自等比縮放到同一高度，根部基線、幹基中心對齊（不是同一世界尺度；世界尺度請看原本的並排圖）', fill=(255, 255, 255), font=F)
    names = {'A_front': 'A 正面', 'A_side': 'A 側面', 'B_front': 'B 正面', 'B_side': 'B 側面'}
    y = 50
    for key, cells in sheets:
        for i, (lab, img, _, _) in enumerate(cells):
            x = 10 + i * (cw + 10) + (cw - img.width) // 2
            canvas.paste(img, (x, y + 28))
            d.text((12 + i * (cw + 10), y + 2), f'{names[key]}｜{lab}', fill=(255, 220, 150), font=FS)
        y += H_px + 50
    canvas.save(outp + '.jpg', quality=88)
    json.dump(report, open(outp + '.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # 文字表：中心線偏移、幹寬（樹高比例）
    lines = []
    for key in ('A_front', 'A_side', 'B_front', 'B_side'):
        lines.append(names[key])
        r = report[f'{key}_參考']
        for q in HS:
            row = [f'{q:.2f}', 'ref ' + (f'{r[str(q)][0]:+.3f}/{r[str(q)][1]:.3f}' if str(q) in r else '   -   ')]
            for lab in labels:
                mr = report.get(f'{key}_{lab}', {})
                row.append(lab + ' ' + (f'{mr[str(q)][0]:+.3f}/{mr[str(q)][1]:.3f}' if str(q) in mr else '   -   '))
            lines.append('  '.join(row))
    open(outp + '.txt', 'w', encoding='utf-8').write('\n'.join(lines))
    print(outp, canvas.size)


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) >= 5:
        run([a[0], a[2]], [a[3], a[4]], a[1])
    else:
        run([a[0]], ['模型'], a[1])

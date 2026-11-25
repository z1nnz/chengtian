# DR09 輪廓疊圖：參考圖（三視圖 L 列）與成品灰模／材質圖，裁到木堆本體外框、縮到相同寬度、底部對齊地面，
# 疊出外輪廓與透空，並量：外框高寬比、輪廓重疊率（IoU）、上緣輪廓差（每一欄最高點的平均差，佔寬度的比例）、外框內透空比例。
# 參考圖的落葉（橘褐、飽和度高）、人形尺、地面線不算木堆本體；成品圖略過左側白柱。
# 這些數字只是輔助，不能取代多角度的美術檢查。
#   uv run --no-project --offline --with pillow --with numpy python art/source/d2-logs-b/overlay_dr09.py <輸出資料夾> <tag> [clay|mat]
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
asset = 'DR09_BranchPile_L'
PREV = os.path.join(ROOT, 'art', 'previews', 'd2-logs-b', asset)
REF = os.path.join(ROOT, 'art', 'references', 'DR09', 'v001', 'DR09-threeview.png')
W = 1000
try:
    FONT = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 22)
except OSError:
    FONT = ImageFont.load_default()


def ref_mask(im):
    a = np.asarray(im).astype(int)
    bg = np.median(np.array([a[3, 3], a[3, -4], a[-4, -4], a[-4, 3]]), axis=0)
    m = np.abs(a - bg).sum(2) > 40
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(2), a.min(2)
    sat = (mx - mn) / np.maximum(mx, 1)
    leaf = (r > g + 18) & (g > b + 8) & (sat > .38) & (r > 120)      # 橘褐落葉
    m &= ~leaf
    # 細小殘點（落葉之間的碎片）去掉：3x3 開運算
    from numpy.lib.stride_tricks import sliding_window_view as sw
    p = np.pad(m, 1)
    er = sw(p, (3, 3)).all((2, 3))
    p = np.pad(er, 1)
    m = sw(p, (3, 3)).any((2, 3))
    return m


def our_mask(im, skip_left=0, sil=False):
    a = np.asarray(im).astype(int)
    if sil:                                  # 剪影圖：白色本體、黑背景
        return a.mean(2) > 90
    h, w, _ = a.shape
    bg = np.median(np.array([a[2, -3], a[-3, -3], a[2, w // 2], a[-3, w // 2], a[h // 2, -3]]), axis=0)
    m = np.abs(a - bg).sum(2) > 26
    m[:, :skip_left] = False
    return m


def crop_norm(m, ground_cut=0):
    rows = np.nonzero(m.sum(1) > 3)[0]
    cols = np.nonzero(m.sum(0) > 3)[0]
    y0, y1, x0, x1 = rows[0], rows[-1] + 1 - ground_cut, cols[0], cols[-1] + 1
    c = m[y0:y1, x0:x1]
    H = max(1, round(W * c.shape[0] / c.shape[1]))
    im = Image.fromarray((c * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    return np.asarray(im) > 127, (x0, y0, x1, y1)


def stats(m):
    top = np.array([np.argmax(col) if col.any() else m.shape[0] for col in m.T])
    return dict(aspect=m.shape[0] / m.shape[1], void=1 - m.mean(), top=top)


def main():
    out_dir, tag = sys.argv[1], sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else 'clay'
    ref = Image.open(REF).convert('RGB')
    views = {'front': (ref.crop((150, 600, 920, 884)), 260), 'top': (ref.crop((925, 615, 1490, 905)), 0)}
    res = {}
    for view, (rim, skip) in views.items():
        rm, _ = crop_norm(ref_mask(rim))
        src = None
        for d in (out_dir, tag.split('_')[0]):
            p = os.path.join(PREV, d, f'{asset}_{tag}_{mode}_{view}.png')
            if os.path.exists(p):
                src = p
                break
        om_full = our_mask(Image.open(src).convert('RGB'), skip, mode == 'sil')
        om, box = crop_norm(om_full)
        Hh = max(rm.shape[0], om.shape[0])
        A_ = np.zeros((Hh, W), bool)
        B_ = np.zeros((Hh, W), bool)
        A_[Hh - rm.shape[0]:] = rm                      # 底部對齊（地面）
        B_[Hh - om.shape[0]:] = om
        iou = (A_ & B_).sum() / max((A_ | B_).sum(), 1)
        sr, so = stats(rm), stats(om)
        tr = np.array([np.argmax(c) if c.any() else Hh for c in A_.T])
        to = np.array([np.argmax(c) if c.any() else Hh for c in B_.T])
        prof = float(np.abs(tr - to).mean() / W)
        # 分段上緣差（左→右 8 段，正值 = 成品比參考低）
        seg = [round(float((to[k * W // 8:(k + 1) * W // 8] - tr[k * W // 8:(k + 1) * W // 8]).mean() / W), 3) for k in range(8)]
        res[view] = dict(ref_aspect=round(sr['aspect'], 3), our_aspect=round(so['aspect'], 3), iou=round(float(iou), 3),
                         top_profile_err=round(prof, 3), ref_void=round(sr['void'], 3), our_void=round(so['void'], 3), top_seg_lower=seg)
        rgb = np.full((Hh, W, 3), 24, np.uint8)
        rgb[A_ & ~B_] = (210, 70, 60)       # 只有參考
        rgb[B_ & ~A_] = (60, 170, 220)      # 只有成品
        rgb[A_ & B_] = (225, 225, 210)      # 重疊
        ov = Image.fromarray(rgb)
        d = ImageDraw.Draw(ov)
        for x in range(0, W - 1, 2):
            d.line([(x, int(tr[x])), (x + 2, int(tr[min(x + 2, W - 1)]))], fill=(255, 120, 100), width=2)
            d.line([(x, int(to[x])), (x + 2, int(to[min(x + 2, W - 1)]))], fill=(120, 220, 255), width=2)
        # 並排：參考（遮罩後）、成品、疊圖
        def tile(mm):
            t = np.full((Hh, W, 3), 24, np.uint8)
            t[mm] = (200, 200, 200)
            return Image.fromarray(t)
        sheet = Image.new('RGB', (W + 20, 3 * (Hh + 44) + 70), (18, 18, 18))
        dd = ImageDraw.Draw(sheet)
        r_ = res[view]
        dd.text((10, 8), f'{view}｜參考 高寬比 {r_["ref_aspect"]:.2f} 透空 {r_["ref_void"] * 100:.0f}%　'
                         f'{tag} 高寬比 {r_["our_aspect"]:.2f} 透空 {r_["our_void"] * 100:.0f}%　IoU {r_["iou"]:.2f}　上緣差 {r_["top_profile_err"] * 100:.1f}% 寬',
                fill=(255, 220, 150), font=FONT)
        y = 44
        for lab, im_ in (('參考（去落葉、人形）', tile(A_)), (f'{tag}', tile(B_)), ('疊圖：紅 = 只有參考、藍 = 只有成品、白 = 重疊；線 = 上緣', ov)):
            dd.text((10, y), lab, fill=(220, 220, 220), font=FONT)
            sheet.paste(im_, (10, y + 30))
            y += Hh + 44
        p = os.path.join(PREV, out_dir, f'{asset}_{tag}_{mode}_overlay_{view}.png')
        sheet.save(p)
        print(view, json.dumps(res[view], ensure_ascii=False), p)
    json.dump(res, open(os.path.join(PREV, out_dir, f'{asset}_{tag}_{mode}_overlay.json'), 'w'), indent=1)


main()

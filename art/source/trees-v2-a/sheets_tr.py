"""Comparison sheets for the tree redo v2 package A (trees-v2-a), per the package's acceptance list (section 3):
  <ID>_vs_standard.jpg   the world-tree standard image beside the model, front and left / right 35 deg, same light
  <ID>_ref_vs_model.jpg  the picked three-view (art/references/TR06) beside the model's front / side / back-side views
  <ID>_silhouettes.jpg   black silhouettes front, left 35, right 35, per variant
  <ID>_variants.jpg      A / B / C three-quarter views

    python art/source/trees-v2-a/sheets_tr.py --standard <標準-天空島世界樹.png> TR06
    (the standard image is docs/execution/2026-11-14/tree-method/標準-天空島世界樹.png on feature/qingxi-creek-chapter;
     git show <branch>:<path> | git lfs smudge > standard.png)
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent; REPO = HERE.parents[2]
PV = REPO / 'art' / 'previews' / 'trees-v2-a'; REF = REPO / 'art' / 'references'
args = sys.argv[1:]
std = None
if '--standard' in args:
    i = args.index('--standard'); std = Path(args[i + 1]); del args[i:i + 2]
try:
    FONT = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 30)
except OSError:
    FONT = ImageFont.load_default()


def fit(im, h):
    return im.resize((max(1, int(im.width * h / im.height)), h), Image.LANCZOS)


def row(ims, h, labels=None, pad=12, bg='white'):
    ims = [fit(i.convert('RGB'), h) for i in ims]; W = sum(i.width for i in ims) + pad * (len(ims) + 1); top = 46 if labels else 0
    out = Image.new('RGB', (W, h + top + pad * 2), bg); d = ImageDraw.Draw(out); x = pad
    for k, im in enumerate(ims):
        out.paste(im, (x, top + pad))
        if labels: d.text((x + 6, 8), labels[k], fill=(20, 20, 20), font=FONT)
        x += im.width + pad
    return out


def stack(rows):
    W = max(r.width for r in rows); out = Image.new('RGB', (W, sum(r.height for r in rows)), 'white'); y = 0
    for r in rows: out.paste(r, (0, y)); y += r.height
    return out


def crop_alpha_free(im, bgtol=10):
    """Crop a render to its content (the background is the flat sky colour of the top-left pixel)."""
    rgb = im.convert('RGB'); bg = rgb.getpixel((2, 2)); px = rgb.load(); w, h = rgb.size; xs, ys = [], []
    for y in range(0, h, 4):
        for x in range(0, w, 4):
            p = px[x, y]
            if max(abs(p[c] - bg[c]) for c in range(3)) > bgtol: xs.append(x); ys.append(y)
    if not xs: return rgb
    m = 20; return rgb.crop((max(min(xs) - m, 0), max(min(ys) - m, 0), min(max(xs) + m, w), min(max(ys) + m, h)))


def img(stem):
    return Image.open(next(PV / f'{stem}{e}' for e in ('.jpg', '.png') if (PV / f'{stem}{e}').exists()))


for sid in args:
    vs = sorted(p.stem.split('_three_quarter')[0] for p in PV.glob(f'{sid}_*_three_quarter.*') if '_clay' not in p.stem and '_wire' not in p.stem)
    main = vs[0]
    if std and std.exists():
        s = Image.open(std).convert('RGB'); s = s.crop((int(s.width * .06), int(s.height * .28), int(s.width * .94), int(s.height * .56)))
        views = [crop_alpha_free(img(f'{main}_{v}')) for v in ('left35', 'front', 'right35')]
        stack([row([s], 620, ['標準：天空島世界樹']), row(views, 620, [f'{main} 左 35°', f'{main} 正面', f'{main} 右 35°'])]).save(PV / f'{sid}_vs_standard.jpg', quality=88)
    pick = {'TR04': 3, 'TR06': 1, 'TR07': 2, 'TR08': 1, 'TR09': 5}.get(sid, 1)   # the picked three-view (art/references/<ID>/prompt.txt)
    ref = REF / sid / f'{sid}_option{pick}.png'
    if ref.exists():
        r = Image.open(ref)
        views = [crop_alpha_free(img(f'{main}_{v}')) for v in ('front', 'side', 'right35')]
        stack([row([r], 520, [f'三視圖 option {pick}']), row(views, 520, [f'{main} 正面', f'{main} 側面', f'{main} 右 35°'])]).save(PV / f'{sid}_ref_vs_model.jpg', quality=88)
    stack([row([Image.open(PV / f'{v}_silhouette_{k}.png') for k in ('front', 'left35', 'right35')], 420, [f'{v} 正面', '左 35°', '右 35°']) for v in vs]).save(PV / f'{sid}_silhouettes.jpg', quality=88)
    row([crop_alpha_free(img(f'{v}_front')) for v in vs], 640, [f'{v}（正面）' for v in vs]).save(PV / f'{sid}_variants.jpg', quality=88)
    print(sid, 'sheets written for', vs)

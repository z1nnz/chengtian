"""trees-v2 review sheets from the preview renders (Pillow, no Blender).

  uv run --offline --no-project --with pillow python art/source/trees-v2/compose_review.py <render dir> <out dir> <SP> <ID> [<ID> ...]

<render dir>/<ID>/ holds preview_trees_v2.py output. Writes into <out dir>:
  <ID>/  every render copied as is
  <ID>/<ID>_vs_standard.png  the work pack's standard image (docs/execution/2026-11-14/tree-method/標準-天空島世界樹.png) beside the
                             front, left 35 and right 35 renders (same sun and sky for all)
  <ID>/<ID>_silhouettes.png  the three black silhouettes (front, right 35, top)
  <SP>_variants_front.png    every variant's front render side by side
"""
import sys, shutil
from pathlib import Path
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[3]
STD = REPO / 'docs/execution/2026-11-14/tree-method/標準-天空島世界樹.png'


def row(images, h, gap=16, bg=(232, 232, 228)):
    ims = [im.convert('RGB').resize((round(im.width * h / im.height), h), Image.LANCZOS) for im in images]
    out = Image.new('RGB', (sum(i.width for i in ims) + gap * (len(ims) + 1), h + gap * 2), bg); x = gap
    for im in ims: out.paste(im, (x, gap)); x += im.width + gap
    return out


def trim_black(im):
    """The standard image is a phone screenshot: keep the picture, drop the black bars (and the buttons on them) above and below."""
    g = im.convert('L'); w, h = g.size; px = g.load()
    rows = [y for y in range(h) if sum(px[x, y] for x in range(0, w, 8)) / len(range(0, w, 8)) > 40]
    return im.crop((0, rows[0], w, rows[-1] + 1)) if rows else im


def label(im, texts, h):
    d = ImageDraw.Draw(im); x = 16
    for t, w in texts:
        d.rectangle((x, 16, x + 8 + 9 * len(t), 40), fill=(20, 20, 20)); d.text((x + 4, 20), t, fill=(240, 240, 240)); x += w + 16
    return im


def main():
    a = sys.argv[sys.argv.index('compose_review.py') + 1:] if 'compose_review.py' in sys.argv else sys.argv[1:]
    src, out, sp, ids = Path(a[0]), Path(a[1]), a[2], a[3:]
    fronts = []
    for aid in ids:
        s = src / aid; o = out / aid; o.mkdir(parents=True, exist_ok=True)
        for f in s.glob('*.png'): shutil.copy2(f, o / f.name)
        views = [Image.open(s / f'{aid}_{v}.png') for v in ('front', 'l35', 'r35')]
        std = trim_black(Image.open(STD))
        sheet = row([std] + views, 900)
        widths = [round(i.width * 900 / i.height) for i in [std] + views]
        label(sheet, list(zip(('standard', 'front', 'left 35', 'right 35'), widths)), 900).save(o / f'{aid}_vs_standard.png')
        sil = row([Image.open(s / f'{aid}_sil_{v}.png') for v in ('front', 'r35', 'top')], 900, bg=(255, 255, 255))
        sil.save(o / f'{aid}_silhouettes.png')
        fronts.append(views[0])
    row(fronts, 1100).save(out / f'{sp}_variants_front.png')
    print('COMPOSED', out)


if __name__ == '__main__':
    main()

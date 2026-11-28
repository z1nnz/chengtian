"""VH04 against the concept art: the same shop in A1_concept_2_entry (the right side of the road) beside the model from the same side,
eye height, warm low sun (review_vh04.py 'street'); and the Codex three-quarter reference beside the model's front.

  1. blender -b <blend> --python art/source/village-houses-b/review_vh04.py -- <previews>/VH04_StreetShop/review street front
  2. uv run --no-project --with pillow python art/source/village-houses-b/vs_vh04.py <repo root> <concept_2 png>
The concept image lives on the feature/qingxi-creek-chapter branch (docs/execution/2026-11-28/images/, Git LFS); pass its local path.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(sys.argv[1]); concept = Path(sys.argv[2])
pre = root / 'art/previews/village-houses-b/VH04_StreetShop'
ref = root / 'art/references/VH04'
F = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 26)
c2 = Image.open(concept)
s = c2.width / 1672
rows = [
    (c2.crop((int(1040 * s), int(110 * s), int(1672 * s), int(640 * s))), Image.open(pre / 'review' / 'review_street.png').crop((300, 0, 1536, 1000)),
     '概念圖 2（村口往北）右邊的店屋', '遊戲模型 LOD0，同一側、眼高、低角度暖光'),
    (Image.open(ref / 'VH04-threequarter.png'), Image.open(pre / 'review' / 'review_front.png'),
     'Codex 三視圖組的街景參考', '遊戲模型 LOD0，正對店面'),
]
H = 600
out = []
for a, b, ta, tb in rows:
    a = a.resize((int(a.width * H / a.height), H), Image.LANCZOS)
    b = b.resize((int(b.width * H / b.height), H), Image.LANCZOS)
    out.append((a, b, ta, tb))
W = max(a.width + b.width for a, b, _, _ in out) + 60
sheet = Image.new('RGB', (W, len(out) * (H + 70) + 20), (236, 236, 232))
d = ImageDraw.Draw(sheet)
y = 10
for a, b, ta, tb in out:
    d.text((20, y), ta, fill=(30, 30, 30), font=F)
    d.text((40 + a.width, y), tb, fill=(30, 30, 30), font=F)
    sheet.paste(a, (20, y + 44)); sheet.paste(b, (40 + a.width, y + 44))
    y += H + 70
dst = pre / 'VH04_StreetShop_vs_concept.jpg'
sheet.save(dst, quality=90)
print('VS', dst, sheet.size)

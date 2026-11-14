"""合併同場景渲染結果。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[3]
variant = sys.argv[1]
out = root / 'art/previews/core-d2-models-v1/RL01'
canvas = Image.new('RGB', (2000, 740), (34, 36, 36))
draw = ImageDraw.Draw(canvas)
for i, label in enumerate((f'RL01_RottenLog_{variant}', 'AL01_RootAltarTerrace')):
    im = Image.open(out / f'{label}_same_setup.png').convert('RGB')
    canvas.paste(im, (i * 1000, 40))
    draw.text((i * 1000 + 24, 13), label, fill=(235, 235, 235))
canvas.save(out / f'RL01_RottenLog_{variant}_vs_AL01.png')

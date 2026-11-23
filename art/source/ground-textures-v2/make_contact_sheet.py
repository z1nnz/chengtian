"""Build a visual overview of the eight terrain albedos for art review."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2] / "exports" / "ground-textures-v2"
LABELS = [
    "GT01 sage grass", "GT02 dirt road", "GT03 forest floor", "GT04 creek pebbles",
    "GT05 valley rock", "GT06 tea soil", "GT07 paddy mud", "GT08 granite paving",
]
SIZE = 512
HEADER = 36
sheet = Image.new("RGB", (SIZE * 4, (SIZE + HEADER) * 2), (35, 39, 37))
draw = ImageDraw.Draw(sheet)

for index, label in enumerate(LABELS):
    code = f"GT{index + 1:02d}"
    tile = Image.open(ROOT / code / f"{code}_Albedo_2048.png").convert("RGB")
    tile = tile.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    x = (index % 4) * SIZE
    y = (index // 4) * (SIZE + HEADER)
    draw.text((x + 12, y + 11), label, fill=(240, 238, 230))
    sheet.paste(tile, (x, y + HEADER))

sheet.save(ROOT / "GT01-GT08-contact-sheet.png", optimize=True)

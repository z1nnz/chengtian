# DR10 灰模前後對照：上排參考圖（A 正、A 側、B 正、B 側），下面每一列是一組 gray_dr10.py 的固定鏡位輸出（正、側），最後附四分之三。
# 用法：uv run --no-project --with pillow python gray_sheet_dr10.py <輸出.jpg> <標籤=資料夾> [<標籤=資料夾> ...]
import os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, '..', '..', 'references', 'DR10', 'v001', 'DR10-threeview.png')
try:
    FONT = ImageFont.truetype('C:/Windows/Fonts/msjh.ttc', 24)
except OSError:
    FONT = ImageFont.load_default()
W = 1600


def main(out, sets):
    ref = Image.open(REF).convert('RGB')
    ref = ref.resize((W, round(ref.height * W / ref.width)), Image.LANCZOS)
    rows = [(ref, '參考圖：A 正、A 側、B 正、B 側')]
    for label, d in sets:
        tiles = [Image.open(f'{d}/DR10_{v}_gray_{t}.png').convert('RGB') for v in 'AB' for t in ('front', 'side')]
        h = round(W / 4 * tiles[0].height / tiles[0].width)
        row = Image.new('RGB', (W, h))
        for i, im in enumerate(tiles):
            row.paste(im.resize((W // 4, h), Image.LANCZOS), (i * (W // 4), 0))
        rows.append((row, f'{label}：固定鏡位（長鏡頭近似正交，A、B 同比例，白柱 1.75 m）'))
        tq = [Image.open(f'{d}/DR10_{v}_gray_tq.png').convert('RGB') for v in 'AB']
        h2 = W // 2
        row2 = Image.new('RGB', (W, h2))
        for i, im in enumerate(tq):
            row2.paste(im.resize((W // 2, h2), Image.LANCZOS), (i * (W // 2), 0))
        rows.append((row2, f'{label}：四分之三固定鏡位（A 左、B 右）'))
    H = sum(r.height + 44 for r, _ in rows) + 12
    c = Image.new('RGB', (W + 24, H), (18, 18, 18))
    d = ImageDraw.Draw(c)
    y = 12
    for im, lab in rows:
        c.paste(im, (12, y))
        d.text((16, y + im.height + 8), lab, fill=(235, 235, 235), font=FONT)
        y += im.height + 44
    c.save(out, quality=88)
    print(out, c.size)


if __name__ == '__main__':
    main(sys.argv[1], [a.split('=', 1) for a in sys.argv[2:]])
